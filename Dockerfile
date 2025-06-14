# Simple PyMapGIS Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create user first
RUN groupadd -r pymapgis && useradd -r -g pymapgis pymapgis

# Set work directory
WORKDIR /app

# Copy requirements and install basic dependencies
COPY pyproject.toml ./

# Install basic Python dependencies without GDAL for now
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    numpy \
    pandas \
    requests \
    pyjwt

# Copy application code
COPY --chown=pymapgis:pymapgis . .

# Switch to non-root user
USER pymapgis

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - simple FastAPI server
CMD ["python", "-c", "import uvicorn; uvicorn.run('pymapgis.serve:app', host='0.0.0.0', port=8000)"]
