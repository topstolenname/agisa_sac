"""Pub/Sub triggered function to emit synthetic time pulses."""

from __future__ import annotations

import base64
import json
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
TOPIC = "synthetic-time"


def tick(event, context):
    count = int(base64.b64decode(event["data"]).decode("utf-8"))
    payload = json.dumps({"pulse": count}).encode("utf-8")
    topic_path = publisher.topic_path(context.project, TOPIC)
    publisher.publish(topic_path, payload)
