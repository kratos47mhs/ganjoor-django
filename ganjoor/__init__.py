"""
Ganjoor Django Application Initialization

This module initializes the Django application and optionally sets up
OpenTelemetry tracing if the required packages are installed.
"""

import logging

logger = logging.getLogger(__name__)

# Try to initialize OpenTelemetry tracing if available
try:
    from .tracing import init_telemetry

    init_telemetry()
    logger.info("OpenTelemetry tracing initialized successfully")
except ImportError as e:
    logger.warning(
        "OpenTelemetry packages not found. Tracing is disabled. "
        "Install opentelemetry packages to enable distributed tracing. "
        f"Error: {e}"
    )
except Exception as e:
    logger.error(
        f"Failed to initialize OpenTelemetry tracing: {e}. "
        "Continuing without tracing..."
    )
