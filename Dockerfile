# PyMapGIS Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev \
    libgdal28 \
    libproj19 \
    libgeos-c1v5 \
    libspatialindex6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.6.1

# Create user
RUN groupadd -r pymapgis && useradd -r -g pymapgis pymapgis

# Set work directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-dev

# Copy application code
COPY --chown=pymapgis:pymapgis . .

# Install the package
RUN poetry install --only=main --no-dev

# Switch to non-root user
USER pymapgis

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["poetry", "run", "python", "-m", "pymapgis.serve", "--host", "0.0.0.0", "--port", "8000"]
