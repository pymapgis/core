# PyMapGIS Developer Documentation

Welcome to the developer documentation for PyMapGIS!

This section is for those who want to contribute to the development of PyMapGIS, understand its internal workings, or extend its functionalities.

Here you'll find information about:

- **[Architecture](./architecture.md):** A high-level overview of PyMapGIS's structure and components.
- **[Contributing Guide](./contributing_guide.md):** How to set up your development environment, coding standards, and the process for submitting contributions.
- **[Extending PyMapGIS](./extending_pymapgis.md):** Guidance on adding new data sources or other functionalities.

If you are looking for information on how to *use* PyMapGIS, please see our [User Documentation](../index.md).

---

# PyMapGIS Architecture

This document provides a high-level overview of the PyMapGIS library's architecture. Understanding the architecture is crucial for effective contribution and extension.

## Core Components

PyMapGIS is designed with a modular architecture. The key components are:

1.  **`pymapgis.io` (Data I/O)**:
    *   Handles the reading and writing of geospatial data from various sources.
    *   Uses a URI-based system (e.g., `census://`, `tiger://`, `file://`) to identify and access data sources.
    *   Responsible for dispatching requests to appropriate data handlers.

2.  **Data Source Handlers (within `pymapgis.io` or plugins)**:
    *   Specific modules or classes that know how to fetch and parse data from a particular source (e.g., Census API, TIGER/Line shapefiles, local GeoJSON files).
    *   These handlers are registered with the I/O system.

3.  **`pymapgis.acs` / `pymapgis.tiger` (Specific Data Source Clients)**:
    *   Modules that implement the logic for interacting with specific APIs like the Census ACS or TIGER/Line web services.
    *   They handle API-specific parameters, data fetching, and initial parsing.

4.  **`pymapgis.cache` (Caching System)**:
    *   Provides a caching layer for data fetched from remote sources (primarily web APIs).
    *   Helps in reducing redundant API calls and speeding up data retrieval.
    *   Configurable for cache expiration and storage.

5.  **`pymapgis.plotting` (Visualization Engine)**:
    *   Integrates with libraries like Leafmap to provide interactive mapping capabilities.
    *   Offers a simple `.plot` API on GeoDataFrames (or similar structures) for creating common map types (e.g., choropleth maps).

6.  **`pymapgis.settings` (Configuration Management)**:
    *   Manages global settings for the library, such as API keys (if needed), cache configurations, and default behaviors.

## Data Flow Example (Reading Census Data)

1.  **User Call**: `pmg.read("census://acs/acs5?year=2022&variables=B01003_001E")`
2.  **`pymapgis.io`**:
    *   Parses the URI to identify the data source (`census`) and parameters.
    *   Delegates the request to the Census ACS handler.
3.  **Census ACS Handler (e.g., functions in `pymapgis.acs`)**:
    *   Constructs the appropriate API request for the US Census Bureau.
    *   Checks the cache (`pymapgis.cache`) to see if the data is already available and valid.
    *   If not cached or expired, fetches data from the Census API.
    *   Stores the fetched data in the cache.
    *   Parses the API response into a structured format (typically a Pandas DataFrame with a geometry column, i.e., a GeoDataFrame).
4.  **Return**: The GeoDataFrame is returned to the user.

## Extensibility

PyMapGIS is designed to be extensible:

*   **New Data Sources**: Developers can add support for new data sources by creating new data handlers and registering them with the `pymapgis.io` system. This often involves creating a new module similar to `pymapgis.acs` or `pymapgis.tiger` if the source is complex, or a simpler handler if it's straightforward.
*   **New Plotting Functions**: Additional plotting functionalities can be added to `pymapgis.plotting` or by extending the `.plot` accessor.

Understanding these components and their interactions should provide a solid foundation for developing and extending PyMapGIS.

---

# PyMapGIS Contributing Guide

Thank you for considering contributing to PyMapGIS! We welcome contributions of all sizes, from bug fixes to new features. This guide outlines how to set up your development environment, our coding standards, and the contribution workflow.

For a general overview of how to contribute, including our code of conduct, please see the main [CONTRIBUTING.md](../../../CONTRIBUTING.md) file in the root of the repository. This document provides more specific details for developers.

## Development Environment Setup

1.  **Fork the Repository**:
    Start by forking the [main PyMapGIS repository](https://github.com/pymapgis/core) on GitHub.

2.  **Clone Your Fork**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/core.git
    cd core
    ```

3.  **Set up a Virtual Environment**:
    We recommend using a virtual environment (e.g., `venv` or `conda`) to manage dependencies.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

4.  **Install Dependencies with Poetry**:
    PyMapGIS uses [Poetry](https://python-poetry.org/) for dependency management and packaging.
    ```bash
    pip install poetry
    poetry install --with dev  # Installs main and development dependencies
    ```
    This command installs all dependencies listed in `pyproject.toml`, including those required for testing and linting.

5.  **Set Up Pre-commit Hooks**:
    We use pre-commit hooks to ensure code style and quality before commits.
    ```bash
    poetry run pre-commit install
    ```
    This will run linters (like Black, Flake8, isort) automatically when you commit changes.

## Coding Standards

*   **Style**: We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code and use [Black](https://github.com/psf/black) for automated code formatting. Pre-commit hooks will enforce this.
*   **Type Hinting**: All new code should include type hints. PyMapGIS uses them extensively.
*   **Docstrings**: Use [Google-style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for all public modules, classes, and functions.
*   **Imports**: Imports should be sorted using `isort` (handled by pre-commit hooks).

## Testing

PyMapGIS uses `pytest` for testing.

1.  **Running Tests**:
    To run the full test suite:
    ```bash
    poetry run pytest tests/
    ```

2.  **Writing Tests**:
    *   New features must include comprehensive tests.
    *   Bug fixes should include a test that reproduces the bug and verifies the fix.
    *   Tests for a module `pymapgis/foo.py` should typically be in `tests/test_foo.py`.
    *   Use fixtures where appropriate to set up test data.

## Contribution Workflow

1.  **Create a New Branch**:
    Create a descriptive branch name for your feature or bug fix:
    ```bash
    git checkout -b feature/your-feature-name  # For new features
    # or
    git checkout -b fix/issue-description     # For bug fixes
    ```

2.  **Make Your Changes**:
    Write your code and tests. Ensure all tests pass and pre-commit checks are successful.

3.  **Commit Your Changes**:
    Write clear and concise commit messages. Reference any relevant issues.
    ```bash
    git add .
    git commit -m "feat: Add new feature X that does Y"
    # or
    git commit -m "fix: Resolve issue #123 by doing Z"
    ```

4.  **Push to Your Fork**:
    ```bash
    git push origin feature/your-feature-name
    ```

5.  **Open a Pull Request (PR)**:
    *   Go to the PyMapGIS repository on GitHub and open a PR from your fork's branch to the `main` branch of the upstream repository.
    *   Fill out the PR template, describing your changes and why they are needed.
    *   Ensure all CI checks (GitHub Actions) pass.
    *   Project maintainers will review your PR, provide feedback, and merge it once it's ready.

## Documentation

If your changes affect user-facing behavior or add new features, please update the documentation in the `docs/` directory accordingly. This includes:
*   User guide (`docs/user-guide.md`)
*   API reference (`docs/api-reference.md`)
*   Examples (`docs/examples.md`)
*   Relevant developer documentation (`docs/developer/`)

## Questions?

Feel free to open an issue on GitHub or join the discussions if you have any questions or need help.

Thank you for contributing to PyMapGIS!

---

# Extending PyMapGIS

PyMapGIS is designed to be extensible, allowing developers to add support for new data sources, processing functions, or even custom plotting capabilities. This guide provides an overview of how to extend PyMapGIS.

## Adding a New Data Source

The most common extension is adding a new data source. PyMapGIS uses a URI-based system to identify and manage data sources (e.g., `census://`, `tiger://`, `file://`).

### Steps to Add a New Data Source:

1.  **Define a URI Scheme**:
    Choose a unique URI scheme for your new data source (e.g., `mydata://`).

2.  **Create a Data Handler Module/Functions**:
    *   This is typically a new Python module (e.g., `pymapgis/mydata_source.py`) or functions within an existing relevant module.
    *   This module will contain the logic to:
        *   Parse parameters from the URI.
        *   Fetch data from the source (e.g., an API, a database, a set of files).
        *   Process/transform the raw data into a GeoDataFrame (or a Pandas DataFrame if non-spatial).
        *   Handle caching if the data is fetched remotely.

3.  **Register the Handler (Conceptual)**:
    Currently, PyMapGIS's `pmg.read()` function in `pymapgis/io/__init__.py` has a dispatch mechanism (e.g., if-elif-else block based on `uri.scheme`). You'll need to modify it to include your new scheme and call your handler.

    *Example (simplified view of `pymapgis/io/__init__.py` modification)*:
    ```python
    # In pymapgis/io/__init__.py (or a similar dispatch location)
    from .. import mydata_source # Your new module

    def read(uri_string: str, **kwargs):
        uri = urllib.parse.urlparse(uri_string)
        # ... other schemes ...
        elif uri.scheme == "mydata":
            return mydata_source.load_data(uri, **kwargs)
        # ...
    ```

4.  **Implement Caching (Optional but Recommended for Remote Sources)**:
    *   If your data source involves network requests, integrate with `pymapgis.cache`.
    *   You can use the `requests_cache` session provided by `pymapgis.cache.get_session()` or implement custom caching logic.

5.  **Write Tests**:
    *   Create tests for your new data source in the `tests/` directory.
    *   Test various parameter combinations, edge cases, and expected outputs.
    *   If it's a remote source, consider how to mock API calls for reliable testing.

### Example: A Simple File-Based Handler

Let's say you want to add a handler for a specific type of CSV file that always has 'latitude' and 'longitude' columns.

*   **URI Scheme**: `points_csv://`
*   **Handler (`pymapgis/points_csv_handler.py`)**:
    ```python
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point

    def load_points_csv(uri_parts, **kwargs):
        file_path = uri_parts.path
        df = pd.read_csv(file_path, **kwargs)
        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        return gdf
    ```
*   **Registration (in `pymapgis/io/__init__.py`)**:
    ```python
    # from .. import points_csv_handler # Add this import
    # ...
    # elif uri.scheme == "points_csv":
    #     return points_csv_handler.load_points_csv(uri, **kwargs)
    ```

## Adding New Processing Functions

If you want to add common geospatial operations or analyses that can be chained with PyMapGIS objects (typically GeoDataFrames):

1.  **Identify Where It Fits**:
    *   Could it be a standalone function in a utility module?
    *   Should it be an extension method on GeoDataFrames using the Pandas accessor pattern (e.g., `gdf.pmg.my_function()`)? This is often cleaner for chainable operations.

2.  **Implement the Function**:
    *   Ensure it takes a GeoDataFrame as input and returns a GeoDataFrame or other relevant Pandas/Python structure.
    *   Follow coding standards and include docstrings and type hints.

3.  **Accessor Pattern (Example)**:
    If you want to add `gdf.pmg.calculate_density()`:
    ```python
    # In a relevant module, e.g., pymapgis/processing.py
    import geopandas as gpd

    @gpd.GeoDataFrame.アクセスors.register("pmg") # Name your accessor
    class PmgAccessor:
        def __init__(self, gdf):
            self._gdf = gdf

        def calculate_density(self, population_col, area_col=None):
            gdf = self._gdf.copy()
            if area_col:
                gdf["density"] = gdf[population_col] / gdf[area_col]
            else:
                # Ensure area is calculated if not provided, requires appropriate CRS
                if gdf.crs is None:
                    raise ValueError("CRS must be set to calculate area for density.")
                gdf["density"] = gdf[population_col] / gdf.area
            return gdf
    ```
    Users could then call `my_gdf.pmg.calculate_density("population")`.

## Extending Plotting Capabilities

PyMapGIS's plotting is often a wrapper around libraries like Leafmap or Matplotlib (via GeoPandas).

1.  **Simple Plots**: You might add new methods to the `.plot` accessor similar to how `choropleth` is implemented in `pymapgis/plotting.py`.
2.  **Complex Visualizations**: For highly custom or complex visualizations, you might contribute directly to the underlying libraries or provide functions that help users prepare data for these libraries.

## General Guidelines

*   **Maintain Consistency**: Try to follow the existing patterns and API style of PyMapGIS.
*   **Documentation**: Always document new functionalities, both in code (docstrings) and in the user/developer documentation (`docs/`).
*   **Testing**: Comprehensive tests are crucial.

By following these guidelines, you can effectively extend PyMapGIS to meet new requirements and contribute valuable additions to the library.

---

# Contributing to PyMapGIS

Thank you for your interest in contributing to PyMapGIS! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Git for version control

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/core.git
   cd core
   ```

2. **Install dependencies**
   ```bash
   poetry install --with dev
   ```

3. **Install pre-commit hooks**
   ```bash
   poetry run pre-commit install
   ```

4. **Run tests to verify setup**
   ```bash
   poetry run pytest
   ```

## 🔄 Development Workflow

### Branch Strategy

- **`main`**: Production-ready code (protected)
- **`dev`**: Development branch for integration
- **`feature/*`**: Feature branches for new functionality
- **`fix/*`**: Bug fix branches

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new functionality

3. **Run quality checks**
   ```bash
   poetry run pytest          # Run tests
   poetry run ruff check      # Linting
   poetry run black .         # Code formatting
   poetry run mypy pymapgis   # Type checking
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Use type hints where appropriate

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

### Documentation

- Use docstrings for all public functions and classes
- Follow [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) docstrings
- Update README.md for user-facing changes

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pymapgis

# Run specific test file
poetry run pytest tests/test_cache.py

# Run tests matching pattern
poetry run pytest -k "test_cache"
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

Example:
```python
def test_cache_stores_and_retrieves_data():
    """Test that cache can store and retrieve data correctly."""
    cache = Cache()
    cache.put("key", "value")
    assert cache.get("key") == "value"
```

## 📦 Package Structure

```
pymapgis/
├── __init__.py          # Package exports
├── cache.py             # Caching functionality
├── acs.py              # Census ACS data source
├── tiger.py            # TIGER/Line data source
├── plotting.py         # Visualization utilities
├── settings.py         # Configuration
├── io/                 # Input/output modules
├── network/            # Network utilities
├── plugins/            # Plugin system
├── raster/             # Raster data handling
├── serve/              # Server components
├── vector/             # Vector data handling
└── viz/                # Visualization components
```

## 🐛 Reporting Issues

### Bug Reports

Include:
- Python version
- PyMapGIS version
- Operating system
- Minimal code example
- Error messages/stack traces

### Feature Requests

Include:
- Use case description
- Proposed API design
- Examples of usage

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)

### PR Description

Include:
- Summary of changes
- Related issue numbers
- Breaking changes (if any)
- Testing instructions

## 🏷️ Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release PR to `main`
4. Tag release after merge
5. Publish to PyPI

## 💬 Community

- **GitHub Discussions**: For questions and ideas
- **Issues**: For bug reports and feature requests
- **Email**: nicholaskarlson@gmail.com for maintainer contact

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to PyMapGIS! 🗺️✨
