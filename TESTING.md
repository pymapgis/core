# PyMapGIS Testing Strategy

This document outlines the testing approach for PyMapGIS, designed to balance comprehensive testing with CI/CD reliability.

## Testing Levels

### 1. CI/CD Tests (Always Run)
**Location**: `tests/test_ci_core.py`, `*/test_*_simple.py`
**Purpose**: Essential functionality verification without optional dependencies
**Run with**: `poetry run pytest tests/test_ci_core.py tennessee_counties_qgis/test_tennessee_simple.py examples/arkansas_counties_qgis/test_arkansas_simple.py`

**What they test**:
- Core PyMapGIS imports and basic functionality
- Project structure integrity
- Basic vector operations (with graceful dependency handling)
- Example project structure validation
- Python version compatibility

### 2. Full Test Suite (Local Development)
**Location**: `tests/test_*.py`
**Purpose**: Comprehensive testing including optional dependencies
**Run with**: `poetry run pytest tests/`

**What they test**:
- Advanced raster operations (requires zarr, xarray)
- Streaming functionality (requires kafka-python, paho-mqtt)
- Network analysis (requires osmnx, networkx)
- Visualization (requires pydeck, matplotlib)
- End-to-end integration tests

### 3. Example Integration Tests
**Location**: `*/test_*_counties.py` (standalone scripts)
**Purpose**: Full example validation with real data
**Run with**: `python arkansas_counties_test.py` (individual scripts)

## CI/CD Strategy

### GitHub Actions Workflow
The CI runs only essential tests to avoid dependency hell:

```yaml
- run: poetry run pytest tests/test_ci_core.py tennessee_counties_qgis/test_tennessee_simple.py examples/arkansas_counties_qgis/test_arkansas_simple.py -v
```

### Why This Approach?

1. **Reliability**: CI tests don't fail due to missing optional dependencies
2. **Speed**: Faster CI runs with focused test scope
3. **Maintainability**: Fewer moving parts in CI environment
4. **Coverage**: Still validates core functionality and project structure

## Local Development Testing

### Quick Core Tests
```bash
poetry run pytest tests/test_ci_core.py -v
```

### Full Test Suite
```bash
poetry run pytest tests/ -v
```

### Specific Test Categories
```bash
# Skip slow tests
poetry run pytest -m "not slow"

# Skip tests requiring optional dependencies
poetry run pytest -m "not optional_deps"

# Run only integration tests
poetry run pytest -m "integration"
```

## Test Markers

Tests are marked with categories:
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.optional_deps` - Requires optional dependencies
- `@pytest.mark.ci_skip` - Skip in CI environments

## Adding New Tests

### For CI/CD (Essential Tests)
Add to `tests/test_ci_core.py` or create new `test_*_simple.py` files.
Requirements:
- No optional dependencies
- Fast execution (< 30 seconds)
- Core functionality only

### For Full Suite (Comprehensive Tests)
Add to appropriate `tests/test_*.py` files.
Requirements:
- Mark with appropriate pytest markers
- Handle missing dependencies gracefully
- Include comprehensive error testing

## Troubleshooting

### CI Failures
1. Check if new dependencies were added without updating CI strategy
2. Verify core tests still pass locally: `poetry run pytest tests/test_ci_core.py`
3. Check for import order issues (E402 linting errors)

### Local Test Failures
1. Install optional dependencies: `poetry install --all-extras`
2. Check for missing test data files
3. Verify environment-specific configurations

## Philosophy

**"CI tests should never fail due to missing optional dependencies or complex integrations."**

The goal is to have a robust CI pipeline that validates core functionality while allowing comprehensive testing in development environments.
