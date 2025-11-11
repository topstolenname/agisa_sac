"""
OpenTelemetry Setup for Google Cloud Trace

This module provides initialization for OpenTelemetry with Google Cloud Trace
backend for distributed tracing of agent execution.
"""

try:
    import google.auth
    from opentelemetry import trace
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False
    trace = None
    TracerProvider = None
    CloudTraceSpanExporter = None
    BatchSpanProcessor = None
    Resource = None


def setup_tracing(project_id: str, service_name: str = "agisa-sac"):
    """
    Initialize OpenTelemetry with Google Cloud Trace backend.

    This configures the global tracer provider to export spans to Google Cloud Trace,
    enabling distributed tracing of agent execution across the system.

    Args:
        project_id: GCP project ID
        service_name: Service name for resource identification

    Returns:
        Tracer instance for creating spans

    Raises:
        ImportError: If OpenTelemetry or Cloud Trace dependencies are not installed

    Example:
        >>> from agisa_sac.observability import setup_tracing
        >>> tracer = setup_tracing("my-gcp-project")
        >>> with tracer.start_as_current_span("my_operation"):
        ...     # Your code here
        ...     pass
    """
    if not HAS_OTEL:
        raise ImportError(
            "opentelemetry-api, opentelemetry-sdk, and "
            "opentelemetry-exporter-gcp-trace are required for tracing. "
            "Install with: pip install opentelemetry-api opentelemetry-sdk "
            "opentelemetry-exporter-gcp-trace"
        )

    # Create resource with service identification
    resource = Resource.create(
        {"service.name": service_name, "service.version": "1.0.0"}
    )

    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # Get GCP credentials
    credentials, _ = google.auth.default()

    # Create Cloud Trace exporter
    exporter = CloudTraceSpanExporter(project_id=project_id, credentials=credentials)

    # Add batch processor for efficient export
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Return tracer for immediate use
    return trace.get_tracer(__name__)


def setup_local_tracing(service_name: str = "agisa-sac"):
    """
    Initialize OpenTelemetry with console exporter for local development.

    This configures the tracer to output spans to the console, useful for
    local development and debugging without GCP dependencies.

    Args:
        service_name: Service name for resource identification

    Returns:
        Tracer instance for creating spans

    Raises:
        ImportError: If OpenTelemetry dependencies are not installed

    Example:
        >>> from agisa_sac.observability import setup_local_tracing
        >>> tracer = setup_local_tracing()
        >>> with tracer.start_as_current_span("test_operation"):
        ...     print("This span will be logged to console")
    """
    if not HAS_OTEL:
        raise ImportError(
            "opentelemetry-api and opentelemetry-sdk are required for tracing. "
            "Install with: pip install opentelemetry-api opentelemetry-sdk"
        )

    from opentelemetry.sdk.trace.export import ConsoleSpanExporter

    # Create resource
    resource = Resource.create(
        {"service.name": service_name, "service.version": "1.0.0-dev"}
    )

    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # Add console exporter for local development
    tracer_provider.add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )

    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)

    return trace.get_tracer(__name__)
