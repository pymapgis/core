# 🚀 Development Setup

## Prerequisites

### System Requirements
- **Python**: 3.10, 3.11, or 3.12
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB+ recommended for large datasets)
- **Storage**: 2GB+ free space for dependencies and cache

### Required Tools
- **Git**: Version control
- **Poetry**: Dependency management and packaging
- **Docker**: Optional, for containerized development
- **VS Code**: Recommended IDE with Python extension

## Environment Setup

### 1. Clone the Repository
```bash
# Clone the main repository
git clone https://github.com/pymapgis/core.git
cd core

# Or clone your fork
git clone https://github.com/yourusername/core.git
cd core
```

### 2. Install Poetry
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry

# Verify installation
poetry --version
```

### 3. Set Up Python Environment
```bash
# Install dependencies
poetry install

# Install with all optional dependencies
poetry install --extras "streaming pointcloud enterprise"

# Activate the virtual environment
poetry shell
```

### 4. Verify Installation
```bash
# Test basic functionality
python -c "import pymapgis as pmg; print(pmg.__version__)"

# Run basic tests
poetry run pytest tests/test_settings.py -v

# Check CLI
poetry run pymapgis info
```

## Development Tools Configuration

### 1. Pre-commit Hooks
```bash
# Install pre-commit hooks
poetry run pre-commit install

# Run hooks manually
poetry run pre-commit run --all-files
```

### 2. Code Formatting and Linting
```bash
# Format code with Black
poetry run black pymapgis/ tests/

# Lint with Ruff
poetry run ruff check pymapgis/ tests/

# Type checking with MyPy
poetry run mypy pymapgis/
```

### 3. Testing Setup
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pymapgis --cov-report=html

# Run specific test categories
poetry run pytest -m "not slow"  # Skip slow tests
poetry run pytest -m integration  # Only integration tests
```

## IDE Configuration

### VS Code Setup
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    }
}
```

### Recommended Extensions
- Python (Microsoft)
- Pylance (Microsoft)
- Python Docstring Generator
- GitLens
- Docker (if using containers)

## Environment Variables

### Development Configuration
Create `.env` file in project root:
```bash
# PyMapGIS Settings
PYMAPGIS_CACHE_DIR=./cache
PYMAPGIS_DEFAULT_CRS=EPSG:4326
PYMAPGIS_LOG_LEVEL=DEBUG

# API Keys (optional)
CENSUS_API_KEY=your_census_api_key_here

# Development flags
PYMAPGIS_DEV_MODE=true
PYMAPGIS_ENABLE_PROFILING=false
```

### Testing Configuration
Create `.env.test`:
```bash
# Test-specific settings
PYMAPGIS_CACHE_DIR=./test_cache
PYMAPGIS_LOG_LEVEL=WARNING
PYMAPGIS_SKIP_SLOW_TESTS=true
```

## Docker Development (Optional)

### Development Container
```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

COPY . .

CMD ["bash"]
```

### Docker Compose for Development
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  pymapgis-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/.venv
    environment:
      - PYMAPGIS_DEV_MODE=true
    ports:
      - "8000:8000"
    command: bash
```

## Database Setup (Optional)

### PostgreSQL with PostGIS
```bash
# Using Docker
docker run --name postgis \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=pymapgis_dev \
  -p 5432:5432 \
  -d postgis/postgis:latest

# Connection string
export DATABASE_URL="postgresql://postgres:password@localhost:5432/pymapgis_dev"
```

### Redis (for caching)
```bash
# Using Docker
docker run --name redis \
  -p 6379:6379 \
  -d redis:alpine

# Connection string
export REDIS_URL="redis://localhost:6379"
```

## Common Development Tasks

### Running Tests
```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/test_vector.py

# With coverage
poetry run pytest --cov=pymapgis

# Skip slow tests
poetry run pytest -m "not slow"

# Run in parallel
poetry run pytest -n auto
```

### Code Quality Checks
```bash
# Format code
poetry run black .

# Check formatting
poetry run black --check .

# Lint code
poetry run ruff check .

# Fix linting issues
poetry run ruff check --fix .

# Type checking
poetry run mypy pymapgis/
```

### Documentation
```bash
# Build documentation
cd docs
mkdocs serve

# Or using Poetry
poetry run mkdocs serve
```

### Performance Profiling
```bash
# Profile a specific function
python -m cProfile -o profile.stats your_script.py

# Analyze profile
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"
```

## Troubleshooting

### Common Issues

#### Poetry Installation Problems
```bash
# Clear Poetry cache
poetry cache clear --all pypi

# Reinstall dependencies
rm poetry.lock
poetry install
```

#### Import Errors
```bash
# Ensure you're in the Poetry environment
poetry shell

# Or run with Poetry
poetry run python your_script.py
```

#### Test Failures
```bash
# Clear test cache
rm -rf .pytest_cache

# Clear coverage data
rm .coverage

# Run tests with verbose output
poetry run pytest -v --tb=long
```

#### Performance Issues
```bash
# Clear PyMapGIS cache
poetry run pymapgis cache clear

# Check cache statistics
poetry run pymapgis cache stats
```

### Getting Help

#### Debug Mode
```python
import pymapgis as pmg
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Your code here
data = pmg.read("census://...")
```

#### Profiling
```python
import pymapgis as pmg

# Enable profiling
pmg.settings.enable_profiling = True

# Your code here
# Profiling data will be collected automatically
```

## Next Steps

### For New Contributors
1. Read [Contributing Guide](./contributing-guide.md)
2. Review [Code Standards](./code-standards.md)
3. Check [Architecture Overview](./architecture-overview.md)
4. Browse [Common Issues](./common-issues.md)

### For Extension Developers
1. Study [Extending PyMapGIS](./extending-pymapgis.md)
2. Review [Plugin System](./plugin-system.md)
3. Check [Custom Data Sources](./custom-data-sources.md)

### For Advanced Development
1. Review [Performance Optimization](./performance-optimization.md)
2. Study [Testing Framework](./testing-framework.md)
3. Check [Deployment Guide](./docker-containers.md)

---

*Next: [Contributing Guide](./contributing-guide.md) for contribution workflow and standards*
