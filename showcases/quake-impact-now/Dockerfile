# Quake Impact Now - Poetry-based Docker Configuration with PyMapGIS
# Single-stage build for reliability

FROM python:3.11-slim

# Security: Create non-root user first
RUN groupadd -r pymapgis && useradd -r -g pymapgis -s /bin/false pymapgis

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libgdal32 \
    libproj25 \
    libgeos-c1v5 \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VIRTUALENVS_CREATE=false

# Security: Set secure working directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Copy PyMapGIS source code (for development installation)
COPY pymapgis/ ./pymapgis/

# Install dependencies using Poetry
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# Copy showcase application files
COPY showcases/quake-impact-now/quake_impact.py .
COPY showcases/quake-impact-now/app.py .
COPY showcases/quake-impact-now/static/ ./static/

# Security: Create directories with proper permissions
RUN mkdir -p tiles \
    && chown -R pymapgis:pymapgis /app \
    && chmod -R 755 /app

# Security: Switch to non-root user
USER pymapgis

# Security: Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Security: Expose only necessary port
EXPOSE 8000

# Security: Enhanced health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Security: Use production-ready server configuration
CMD ["poetry", "run", "python", "app.py"]
