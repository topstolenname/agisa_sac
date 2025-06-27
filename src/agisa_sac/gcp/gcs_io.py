"""Utility functions for Google Cloud Storage interactions."""
from __future__ import annotations

from google.cloud import storage
from pathlib import Path
from typing import Union


def upload_file(bucket_name: str, source: Union[str, Path], destination_blob: str) -> None:
    """Upload a file to a bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(str(source))


def download_file(bucket_name: str, blob_name: str, destination: Union[str, Path]) -> None:
    """Download a blob from a bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(str(destination))
