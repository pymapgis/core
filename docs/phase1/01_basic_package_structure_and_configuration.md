# Basic Package Structure & Configuration

This document outlines the foundational setup for the PyMapGIS project, covering the repository structure, package configuration, settings management, and CI/CD pipeline for Phase 1.

## 1. GitHub Repository Setup

*   **Initialize Repository:** Create a new public GitHub repository.
*   **`pyproject.toml`:** Choose and configure either Poetry or PDM for dependency management and packaging. This file will define project metadata, dependencies, and build system settings.
*   **`.gitignore`:** Add a comprehensive `.gitignore` file to exclude common Python, IDE, and OS-specific files from version control.
*   **`LICENSE`:** Include an MIT License file.
*   **Basic Package Directory Structure:** Create the main package directory `pymapgis/` with the following initial sub-modules (as empty `__init__.py` files or basic placeholders):
    *   `pymapgis/vector/`
    *   `pymapgis/raster/`
    *   `pymapgis/viz/`
    *   `pymapgis/serve/`
    *   `pymapgis/ml/`
    *   `pymapgis/cli/`
    *   `pymapgis/plugins/`

## 2. Settings Management (`pmg.settings`)

*   **Implementation:** Implement `pmg.settings` using `pydantic-settings`.
*   **Session-Specific Configurations:** Allow for session-specific configurations, primarily:
    *   `cache_dir`: The directory for storing cached data.
    *   `default_crs`: The default Coordinate Reference System to be used.
*   **Configuration Overrides:** Enable settings to be overridden via:
    *   Environment variables (e.g., `PYMAPGIS_CACHE_DIR`).
    *   A `.pymapgis.toml` file in the user's home directory or project root.

## 3. CI/CD with GitHub Actions

*   **Workflow Setup:** Configure basic GitHub Actions workflows for:
    *   **Testing:** Automatically run the test suite (e.g., using `pytest`) on every push and pull request to the main branches.
    *   **Linting:** Enforce code style (e.g., using Black, Flake8) to maintain code quality.
    *   **Type Checking:** Perform static type checking (e.g., using MyPy) to catch type errors early.
```
