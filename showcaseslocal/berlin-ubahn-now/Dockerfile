# Berlin U-Bahn Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcaseslocal/berlin-ubahn-now/transit_worker.py showcaseslocal/berlin-ubahn-now/app.py ./
COPY showcaseslocal/berlin-ubahn-now/static/ ./static/
COPY showcaseslocal/berlin-ubahn-now/data/ ./data/

# Create Berlin-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash berlin && \
    chown -R berlin:berlin /app

# Switch to Berlin-specific user
USER berlin

# Expose port (inherited from base)
EXPOSE 8000

# Berlin-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the Berlin transit application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'transit_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
