"""Simplified BigQuery client wrapper for AGI-SAC exports."""

from __future__ import annotations

try:
    from google.cloud import bigquery

    HAS_GOOGLE_CLOUD_BIGQUERY = True
except Exception:  # pragma: no cover - optional dependency
    bigquery = None
    HAS_GOOGLE_CLOUD_BIGQUERY = False
from typing import Any, Iterable


def insert_rows(table_id: str, rows: Iterable[dict]) -> None:
    """Insert rows into a BigQuery table."""
    if not HAS_GOOGLE_CLOUD_BIGQUERY:
        raise ImportError("google-cloud-bigquery is required for insert_rows")
    client = bigquery.Client()
    errors = client.insert_rows_json(table_id, list(rows))
    if errors:
        raise RuntimeError(f"BigQuery insert errors: {errors}")


def query(sql: str) -> list[dict[str, Any]]:
    """Run a query and return the results as dictionaries."""
    if not HAS_GOOGLE_CLOUD_BIGQUERY:
        raise ImportError("google-cloud-bigquery is required for query")
    client = bigquery.Client()
    query_job = client.query(sql)
    return [dict(row) for row in query_job.result()]
