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
