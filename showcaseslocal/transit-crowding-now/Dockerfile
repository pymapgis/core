# Transit Crowding Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcaseslocal/transit-crowding-now/transit_worker.py showcaseslocal/transit-crowding-now/app.py ./
COPY showcaseslocal/transit-crowding-now/static/ ./static/
COPY showcaseslocal/transit-crowding-now/data/ ./data/

# Create transit-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash transit && \
    chown -R transit:transit /app

# Switch to transit-specific user
USER transit

# Expose port (inherited from base)
EXPOSE 8000

# Transit-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the transit application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'transit_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
