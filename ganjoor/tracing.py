"""
OpenTelemetry Configuration for Ganjoor Django Application

This module sets up complete observability with traces and metrics for the Ganjoor poetry application.
Logging instrumentation is handled by Django's logging configuration.
"""

import os
import logging
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry import trace, metrics


def init_telemetry():
    """
    Initialize OpenTelemetry for the Ganjoor project.

    Sets up complete observability with:
    - Distributed tracing (HTTP requests, database operations, Django operations)
    - Metrics collection (request rates, response times, error rates)
    - Automatic instrumentation for all configured packages
    """
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: "ganjoor-django",
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
    })

    # Initialize tracing
    span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)

    # Initialize metrics
    metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
    metric_reader = PeriodicExportingMetricReader(exporter=metric_exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Instrument Django (automatically instruments many libraries)
    DjangoInstrumentor().instrument(tracer_provider=tracer_provider)

    # Configure Python logging with structured output
    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(levelname)s] %(asctime)s %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(logging.INFO)

    print("✅ OpenTelemetry initialized: traces and metrics enabled")
