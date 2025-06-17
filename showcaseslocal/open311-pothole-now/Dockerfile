# Open311 Pothole Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcaseslocal/open311-pothole-now/pothole_worker.py showcaseslocal/open311-pothole-now/app.py ./
COPY showcaseslocal/open311-pothole-now/static/ ./static/
COPY showcaseslocal/open311-pothole-now/data/ ./data/

# Create pothole-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash potholes && \
    chown -R potholes:potholes /app

# Switch to pothole-specific user
USER potholes

# Expose port (inherited from base)
EXPOSE 8000

# Pothole-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the pothole application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'pothole_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
