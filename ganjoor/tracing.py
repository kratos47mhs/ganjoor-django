import os
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.distro import OpenTelemetryDistro
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor

def init_telemetry():
    """
    Initializes OpenTelemetry for the Ganjoor project.
    """
    # Set the service name
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: "ganjoor-django"
    })

    # Initialize the OTLP span exporter
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)

    # Initialize the TracerProvider
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

    # Instrument Django
    DjangoInstrumentor().instrument(tracer_provider=tracer_provider)

    print("Telemetry initialized.")
