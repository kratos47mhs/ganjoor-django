# Build stage
FROM python:3.13-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Production stage
FROM python:3.13-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r django && useradd -r -g django django

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy project files with proper ownership
COPY --chown=django:django . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Use gunicorn for production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--worker-class", "sync", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "50", "ganjoor.wsgi:application"]
