# Weather Impact Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcases/weather-impact-now/weather_worker.py showcases/weather-impact-now/app.py ./
COPY showcases/weather-impact-now/static/ ./static/
COPY showcases/weather-impact-now/data/ ./data/

# Create weather-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash weatherimpact && \
    chown -R weatherimpact:weatherimpact /app

# Switch to weather-specific user
USER weatherimpact

# Expose port (inherited from base)
EXPOSE 8000

# Weather-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the weather impact application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'weather_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
