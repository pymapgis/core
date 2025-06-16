# Quake Impact Now - Optimized Secure Docker Configuration
# Single-stage build for faster deployment

FROM python:3.11-slim

# Security: Create non-root user first
RUN groupadd -r pymapgis && useradd -r -g pymapgis -s /bin/false pymapgis

# Security: Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Security: Set secure working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Security: Copy application files with proper ownership
COPY --chown=pymapgis:pymapgis quake_impact.py .
COPY --chown=pymapgis:pymapgis app.py .
COPY --chown=pymapgis:pymapgis static/ ./static/

# Security: Create directories with proper permissions
RUN mkdir -p tiles \
    && chown -R pymapgis:pymapgis /app \
    && chmod -R 755 /app

# Security: Switch to non-root user
USER pymapgis

# Security: Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Security: Expose only necessary port
EXPOSE 8000

# Security: Enhanced health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Security: Use production-ready server configuration
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
