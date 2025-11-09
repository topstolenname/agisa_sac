"""Cloud Function to export scroll data to Cloud Storage."""

from __future__ import annotations

import base64
import json

from google.cloud import storage


def export_scroll(event, context):
    data = base64.b64decode(event["data"]).decode("utf-8")
    payload = json.loads(data)
    bucket_name = payload["bucket"]
    filename = payload["filename"]
    content = payload["content"]

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(content)
    return f"Uploaded {filename} to {bucket_name}"
