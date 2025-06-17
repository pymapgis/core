# Open Food Trucks Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcaseslocal/open-food-trucks-now/truck_worker.py showcaseslocal/open-food-trucks-now/app.py ./
COPY showcaseslocal/open-food-trucks-now/static/ ./static/
COPY showcaseslocal/open-food-trucks-now/data/ ./data/

# Create food-truck-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash foodtrucks && \
    chown -R foodtrucks:foodtrucks /app

# Switch to food-truck-specific user
USER foodtrucks

# Expose port (inherited from base)
EXPOSE 8000

# Food truck-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the food truck application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'truck_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
