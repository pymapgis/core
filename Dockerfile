# Multi-stage Dockerfile for PyMapGIS
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

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
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN groupadd -r pymapgis && useradd -r -g pymapgis pymapgis

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/pymapgis/.local/bin:$PATH

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgdal28 \
    libproj19 \
    libgeos-c1v5 \
    libspatialindex6 \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN groupadd -r pymapgis && useradd -r -g pymapgis pymapgis

# Copy Python packages from builder stage
COPY --from=builder /home/pymapgis/.local /home/pymapgis/.local

# Set work directory and copy application
WORKDIR /app
COPY --chown=pymapgis:pymapgis . .

# Switch to non-root user
USER pymapgis

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "pymapgis.serve", "--host", "0.0.0.0", "--port", "8000"]
