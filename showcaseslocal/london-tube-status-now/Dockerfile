# London Tube Status Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcaseslocal/london-tube-status-now/tube_worker.py showcaseslocal/london-tube-status-now/app.py ./
COPY showcaseslocal/london-tube-status-now/static/ ./static/
COPY showcaseslocal/london-tube-status-now/data/ ./data/

# Create tube-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash tubestatus && \
    chown -R tubestatus:tubestatus /app

# Switch to tube-specific user
USER tubestatus

# Expose port (inherited from base)
EXPOSE 8000

# Tube-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the tube status application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'tube_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
