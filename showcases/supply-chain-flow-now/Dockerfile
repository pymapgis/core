# Supply Chain Flow Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcases/supply-chain-flow-now/supply_chain_worker.py showcases/supply-chain-flow-now/app.py ./
COPY showcases/supply-chain-flow-now/static/ ./static/
COPY showcases/supply-chain-flow-now/data/ ./data/

# Create supply-chain-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash supplychain && \
    chown -R supplychain:supplychain /app

# Switch to supply-chain-specific user
USER supplychain

# Expose port (inherited from base)
EXPOSE 8000

# Supply chain-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the supply chain flow application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'supply_chain_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
