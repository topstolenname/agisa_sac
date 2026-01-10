"""
Handoff Consumer for Networked Orchestration

This module implements a Pub/Sub consumer that processes handoff offers
and claims them with the best-suited agent.
"""

from __future__ import annotations

import asyncio
import json
from typing import Dict, Any, Optional, TYPE_CHECKING, cast

try:
    from google.cloud import firestore, pubsub_v1, storage  # type: ignore
    from opentelemetry import trace

    HAS_GCP = True
except ImportError:
    HAS_GCP = False
    firestore = None  # type: ignore
    pubsub_v1 = None  # type: ignore
    storage = None  # type: ignore
    trace = None  # type: ignore

from ..types.contracts import HandoffClaim, HandoffOffer

if HAS_GCP:
    tracer = trace.get_tracer(__name__)
else:

    class MockTracer:
        """Mock tracer for when OpenTelemetry is not available"""

        class MockSpan:
            def __enter__(self) -> "MockTracer.MockSpan":
                return self

            def __exit__(self, *args: Any) -> None:
                pass

            def set_attribute(self, key: str, value: Any) -> None:
                pass

            def record_exception(self, e: BaseException) -> None:
                pass

        def start_as_current_span(self, name: str) -> "MockSpan":
            return self.MockSpan()

    tracer = MockTracer()  # type: ignore


class HandoffConsumer:
    """
    Consume and claim handoff offers from Pub/Sub.

    Listens to handoff offers on Pub/Sub, evaluates agent capabilities,
    and claims offers with the best-suited agent.
    """

    def __init__(
        self, project_id: str, subscription_id: str, agent_registry: Dict
    ) -> None:
        """
        Initialize the handoff consumer.

        Args:
            project_id: GCP project ID
            subscription_id: Pub/Sub subscription ID
            agent_registry: Dictionary of available agents
        """
        if not HAS_GCP:
            raise ImportError(
                "google-cloud-firestore, google-cloud-pubsub, google-cloud-storage, "
                "and opentelemetry-exporter-gcp-trace are required for HandoffConsumer"
            )

        self.project_id = project_id
        self.subscription_id = subscription_id
        self.agent_registry = agent_registry

        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        self.storage = storage.Client(project=project_id)
        self.db = firestore.Client(project=project_id)

        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_id
        )

        # Event loop for async processing
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def start_consuming(self) -> None:
        """
        Start async consumer loop.

        Listens to Pub/Sub messages and processes handoff offers.
        """
        # Store the event loop for cross-thread task submission
        self._loop = asyncio.get_running_loop()

        def callback(message: pubsub_v1.subscriber.message.Message) -> None:
            """Callback for Pub/Sub messages (runs on background thread)"""
            try:
                # Submit coroutine to event loop from background thread
                if self._loop:
                    asyncio.run_coroutine_threadsafe(
                        self._process_offer(message), self._loop
                    )
            except Exception as e:
                print(f"Error scheduling offer processing: {e}")
                message.nack()

        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, callback=callback
        )

        print(f"Listening for handoff offers on {self.subscription_path}")

        try:
            # Keep the event loop running while subscriber is active
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            streaming_pull_future.result()

    async def _process_offer(self, message: pubsub_v1.subscriber.message.Message) -> None:
        """
        Process individual handoff offer.

        Args:
            message: Pub/Sub message containing handoff offer
        """
        with tracer.start_as_current_span("handoff_process") as span:
            try:
                data = json.loads(message.data.decode("utf-8"))
                offer = HandoffOffer(**data)

                # Find best agent to claim
                claimant = await self._find_best_claimant(offer)

                if claimant:
                    # Publish claim
                    claim = HandoffClaim(
                        run_id=offer.run_id,
                        claimant_agent=claimant.agent_id,
                        claim_reason="best_capability_match",
                        accepted=True,
                    )

                    await self._publish_claim(claim)

                    # Load context and execute
                    try:
                        context = await self._load_context(offer.context_ref)

                        # Store handoff_from for topology tracking before running
                        context["handoff_from"] = offer.from_agent

                        # Run the claimant agent
                        _ = await claimant.run(
                            context.get("last_message", ""), context
                        )

                        # Update the new run document with handoff_from info
                        if "run_id" in context:
                            run_ref = self.db.collection("runs").document(
                                context["run_id"]
                            )
                            run_ref.update({"handoff_from": offer.from_agent})

                    except ValueError as e:
                        # Context missing or invalid - log and ack to prevent retry loop
                        print(f"Skipping offer {offer.run_id}: {e}")
                        span.set_attribute("error", "context_missing")
                        message.ack()
                        return

                message.ack()

            except Exception as e:
                print(f"Error processing handoff: {e}")
                if HAS_GCP:
                    span.record_exception(e)
                message.nack()

    async def _find_best_claimant(self, offer: HandoffOffer) -> Optional[Any]:
        """
        Find agent best suited to handle offer.

        Args:
            offer: HandoffOffer to evaluate

        Returns:
            Best matching agent or None
        """
        required = set(offer.to_capabilities)
        best_agent = None
        best_score = 0.0

        for agent in self.agent_registry.values():
            # Skip if agent is the one making the offer
            if agent.agent_id == offer.from_agent:
                continue

            # Calculate capability match
            agent_caps = set(agent.tools.keys())
            match = len(required & agent_caps)

            if match > 0:
                score = match / len(required) if required else 1.0
                if score > best_score:
                    best_score = score
                    best_agent = agent

        return best_agent if best_score > 0.5 else None

    async def _publish_claim(self, claim: HandoffClaim) -> None:
        """
        Publish claim to Pub/Sub.

        Args:
            claim: HandoffClaim to publish
        """
        topic_path = self.publisher.topic_path(
            self.project_id, "agents.handoff.claims.v1"
        )

        future = self.publisher.publish(topic_path, claim.to_pubsub())
        # Use run_in_executor for google.api_core.future.Future compatibility
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, future.result)

    async def _load_context(self, gcs_uri: str) -> Dict[Any, Any]:
        """
        Load context from GCS.

        Args:
            gcs_uri: GCS URI (gs://bucket/path)

        Returns:
            Context dictionary

        Raises:
            ValueError: If context blob doesn't exist or is invalid
        """
        try:
            # Parse URI: gs://bucket/path
            parts = gcs_uri.replace("gs://", "").split("/", 1)
            bucket_name = parts[0]
            blob_path = parts[1]

            bucket = self.storage.bucket(bucket_name)
            blob = bucket.blob(blob_path)

            content = blob.download_as_text()
            return cast(Dict[Any, Any], json.loads(content))
        except Exception as e:
            # Log and raise - caller should handle
            print(f"Failed to load context from {gcs_uri}: {e}")
            raise ValueError(f"Context not found or invalid: {gcs_uri}") from e
