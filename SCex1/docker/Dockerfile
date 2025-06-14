# Supply Chain Optimization Example - Docker Image
# Simplified version without local PyMapGIS dependency
FROM python:3.11-slim

LABEL maintainer="Nicholas Karlson <nicholaskarlson@gmail.com>"
LABEL description="Supply Chain Optimization Example using PyMapGIS"
LABEL version="0.1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r scuser && useradd -r -g scuser -d /home/scuser -m scuser

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY pyproject.toml ./
RUN pip install poetry==1.8.3 && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Copy application code
COPY --chown=scuser:scuser src/ ./src/
COPY --chown=scuser:scuser data/ ./data/
COPY --chown=scuser:scuser scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/output /app/logs /tmp \
    && chown -R scuser:scuser /app /tmp

# Switch to non-root user
USER scuser

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - start the API server
CMD ["python", "-m", "src.main", "server", "--host", "0.0.0.0", "--port", "8000"]
