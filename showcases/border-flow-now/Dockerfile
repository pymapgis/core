# Border Flow Now - Docker Image
# Real-time CBP border wait times analysis and visualization
# Based on PyMapGIS core with Poetry dependency management

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for geospatial processing
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Install dependencies with Poetry (if available) or fallback to pip
RUN if [ -f "pyproject.toml" ]; then \
        poetry install --no-dev && rm -rf $POETRY_CACHE_DIR; \
    else \
        echo "Poetry configuration not found, using pip fallback"; \
    fi

# Copy requirements.txt and install with pip as fallback
COPY showcases/border-flow-now/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY showcases/border-flow-now/border_worker.py showcases/border-flow-now/app.py ./
COPY showcases/border-flow-now/static/ ./static/
COPY showcases/border-flow-now/data/ ./data/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash borderflow && \
    chown -R borderflow:borderflow /app
USER borderflow

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run data processing first, then start the API server
CMD ["sh", "-c", "python border_worker.py && python app.py"]
