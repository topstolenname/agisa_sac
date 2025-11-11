"""
Handoff Consumer for Networked Orchestration

This module implements a Pub/Sub consumer that processes handoff offers
and claims them with the best-suited agent.
"""

import asyncio
import json
from typing import Dict, Optional

try:
    from google.cloud import firestore, pubsub_v1, storage
    from opentelemetry import trace

    HAS_GCP = True
except ImportError:
    HAS_GCP = False
    firestore = None
    pubsub_v1 = None
    storage = None
    trace = None

from ..types.contracts import HandoffClaim, HandoffOffer

if HAS_GCP:
    tracer = trace.get_tracer(__name__)
else:

    class MockTracer:
        """Mock tracer for when OpenTelemetry is not available"""

        def start_as_current_span(self, name):
            class MockSpan:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    pass

            return MockSpan()

    tracer = MockTracer()


class HandoffConsumer:
    """
    Consume and claim handoff offers from Pub/Sub.

    Listens to handoff offers on Pub/Sub, evaluates agent capabilities,
    and claims offers with the best-suited agent.
    """

    def __init__(
        self, project_id: str, subscription_id: str, agent_registry: Dict
    ):
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

    async def start_consuming(self):
        """
        Start async consumer loop.

        Listens to Pub/Sub messages and processes handoff offers.
        """

        def callback(message: pubsub_v1.subscriber.message.Message):
            """Callback for Pub/Sub messages"""
            try:
                asyncio.create_task(self._process_offer(message))
            except Exception as e:
                print(f"Error processing offer: {e}")
                message.nack()

        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, callback=callback
        )

        print(f"Listening for handoff offers on {self.subscription_path}")

        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            streaming_pull_future.result()

    async def _process_offer(self, message: pubsub_v1.subscriber.message.Message):
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
                    context = await self._load_context(offer.context_ref)
                    await claimant.run(context.get("last_message", ""), context)

                message.ack()

            except Exception as e:
                print(f"Error processing handoff: {e}")
                span.record_exception(e) if HAS_GCP else None
                message.nack()

    async def _find_best_claimant(self, offer: HandoffOffer):
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
                score = match / len(required)
                if score > best_score:
                    best_score = score
                    best_agent = agent

        return best_agent if best_score > 0.5 else None

    async def _publish_claim(self, claim: HandoffClaim):
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

    async def _load_context(self, gcs_uri: str) -> Dict:
        """
        Load context from GCS.

        Args:
            gcs_uri: GCS URI (gs://bucket/path)

        Returns:
            Context dictionary
        """
        # Parse URI: gs://bucket/path
        parts = gcs_uri.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        blob_path = parts[1]

        bucket = self.storage.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        content = blob.download_as_text()
        return json.loads(content)
