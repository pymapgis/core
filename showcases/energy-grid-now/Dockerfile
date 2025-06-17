# Energy Grid Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcases/energy-grid-now/energy_worker.py showcases/energy-grid-now/app.py ./
COPY showcases/energy-grid-now/static/ ./static/
COPY showcases/energy-grid-now/data/ ./data/

# Create energy-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash energygrid && \
    chown -R energygrid:energygrid /app

# Switch to energy-specific user
USER energygrid

# Expose port (inherited from base)
EXPOSE 8000

# Energy-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the energy grid application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'energy_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
