# PyMapGIS Plugin Cookiecutter Template Outline

This document outlines the proposed structure and key files for a cookiecutter template designed to help developers create new plugins for PyMapGIS.

## Template Goals

- Provide a standardized starting point for plugin development.
- Include boilerplate for common plugin components.
- Simplify the process of integrating new plugins into the PyMapGIS ecosystem.
- Encourage best practices in plugin structure and packaging.

## Proposed Directory Structure

```
{{cookiecutter.plugin_name}}/
├── {{cookiecutter.package_name}}/                    # Python package for the plugin
│   ├── __init__.py
│   ├── driver.py                                 # Example plugin implementation
│   └── ...                                       # Other plugin modules
├── tests/                                            # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py                               # Pytest fixtures (optional)
│   └── test_{{cookiecutter.package_name}}.py       # Example test file
├── .gitignore
├── LICENSE                                           # Default to MIT or user's choice
├── pyproject.toml                                    # PEP 518/621 packaging and build config
├── README.md                                         # Plugin-specific README
└── tox.ini                                           # (Optional) For local testing across environments
```

## Key Files and Contents

### `pyproject.toml`

- **Purpose**: Defines package metadata, dependencies, and entry points.
- **Key Sections**:
    - `[build-system]`: Specifies build backend (e.g., `setuptools`, `poetry`).
        ```toml
        [build-system]
        requires = ["setuptools>=61.0"]
        build-backend = "setuptools.build_meta"
        backend-path = "."
        ```
    - `[project]`: Core metadata like name, version, description, dependencies.
        ```toml
        [project]
        name = "{{cookiecutter.plugin_name}}"
        version = "0.1.0"
        description = "A PyMapGIS plugin for {{cookiecutter.plugin_purpose}}"
        authors = [
            { name = "{{cookiecutter.author_name}}", email = "{{cookiecutter.author_email}}" },
        ]
        license = { file = "LICENSE" }
        readme = "README.md"
        requires-python = ">=3.8"
        dependencies = [
            "pymapgis>=0.2.0", # Adjust as per current PyMapGIS version
            # other dependencies...
        ]
        ```
    - `[project.entry-points."pymapgis.plugins"]`: Crucial for plugin discovery.
        ```toml
        [project.entry-points."pymapgis.plugins"]
        # Example for a new data source plugin
        {{cookiecutter.plugin_id}} = "{{cookiecutter.package_name}}.driver:{{cookiecutter.plugin_class_name}}"
        ```
        *   `{{cookiecutter.plugin_id}}`: A unique identifier for the plugin (e.g., `my_custom_source`).
        *   `{{cookiecutter.package_name}}.driver:{{cookiecutter.plugin_class_name}}`: Path to the plugin class.

### `{{cookiecutter.package_name}}/__init__.py`

- **Purpose**: Makes the directory a Python package. Can also expose key classes.
- **Content**:
    ```python
    from .driver import {{cookiecutter.plugin_class_name}}

    __all__ = ["{{cookiecutter.plugin_class_name}}"]
    ```

### `{{cookiecutter.package_name}}/driver.py`

- **Purpose**: Contains the main implementation of the plugin.
- **Content Example (for a new Data Source Plugin)**:
    ```python
    from pymapgis.plugins import DataSourcePlugin # Or other relevant base class

    class {{cookiecutter.plugin_class_name}}(DataSourcePlugin):
        """
        A {{cookiecutter.plugin_purpose}}.
        """
        name = "{{cookiecutter.plugin_id}}" # Matches entry point key
        # Required format prefix if this plugin handles specific URI schemes
        # e.g., if it handles "mydata://..." URIs
        # supported_uri_scheme_prefixes = ["mydata"]

        def __init__(self, config=None):
            super().__init__(config)
            # Initialization logic for the plugin

        def read(self, uri: str, **kwargs):
            """
            Read data from the source based on the URI.
            Example: "mydata://some_identifier?param=value"
            """
            # Parse URI, fetch data, return GeoDataFrame or xarray object
            print(f"Reading data from {uri} with {kwargs}")
            # Replace with actual data reading logic
            # import geopandas as gpd
            # return gpd.GeoDataFrame(...)
            raise NotImplementedError("Plugin read method not implemented.")

        def write(self, data, uri: str, **kwargs):
            """
            Write data to the source (if supported).
            """
            print(f"Writing data to {uri} with {kwargs}")
            raise NotImplementedError("Plugin write method not implemented.")

        # Optional: Implement other methods from the interface as needed
        # e.g., list_layers, get_schema, etc.
    ```

### `tests/test_{{cookiecutter.package_name}}.py`

- **Purpose**: Basic tests for the plugin.
- **Content Example**:
    ```python
    import pytest
    from {{cookiecutter.package_name}} import {{cookiecutter.plugin_class_name}}
    # from pymapgis.plugins import PluginRegistry # For testing registration

    def test_plugin_initialization():
        plugin = {{cookiecutter.plugin_class_name}}()
        assert plugin is not None
        assert plugin.name == "{{cookiecutter.plugin_id}}"

    # Example for testing a data source plugin's read method (if possible with mock data/source)
    # def test_plugin_read_mock(mocker):
    #     plugin = {{cookiecutter.plugin_class_name}}()
    #     # Mock external calls if any, or use a test URI
    #     # mock_gdf = mocker.MagicMock(spec=gpd.GeoDataFrame)
    #     # mocker.patch.object(plugin, '_internal_fetch_method', return_value=mock_gdf)
    #     # result = plugin.read("mydata://test_resource")
    #     # assert not result.empty
    #     with pytest.raises(NotImplementedError):
    #        plugin.read("mydata://test")


    # Example test for plugin registration (requires PluginRegistry from PyMapGIS)
    # def test_plugin_registration():
    #     registry = PluginRegistry()
    #     # Assuming the plugin is installed in the environment or entry points are processed
    #     # This test might be more suitable for integration testing
    #     # For now, we can check if the class can be imported
    #     assert "{{cookiecutter.plugin_id}}" in registry.list_plugins() # This depends on how registry is populated
    #     retrieved_plugin = registry.get_plugin("{{cookiecutter.plugin_id}}")
    #     assert retrieved_plugin is not None
    #     assert isinstance(retrieved_plugin, {{cookiecutter.plugin_class_name}})
    ```

### `README.md` (Plugin specific)

- **Purpose**: Instructions on how to install, configure, and use the plugin.
- **Content**:
    - Plugin name and description
    - Installation instructions (e.g., `pip install .` or `pip install {{cookiecutter.plugin_name}}`)
    - Usage examples
    - Configuration options (if any)
    - How to run tests for the plugin

### `LICENSE`

- **Purpose**: Specifies the license under which the plugin is distributed.
- **Content**: Typically MIT License text, but configurable by the user.

## Cookiecutter Variables (`cookiecutter.json`)

This file would be at the root of the cookiecutter template repository, not part of the generated plugin.

```json
{
  "plugin_name": "MyPyMapGISPlugin",
  "package_name": "my_pymapgis_plugin",
  "plugin_id": "my_plugin_id",
  "plugin_class_name": "MyPluginDriver",
  "plugin_purpose": "custom data processing",
  "author_name": "Your Name",
  "author_email": "your.email@example.com",
  "license": ["MIT", "Apache-2.0", "GPL-3.0-or-later"],
  "pymapgis_version": "0.2.0"
}
```

This outline provides a comprehensive starting point for creating a PyMapGIS plugin cookiecutter template.
Further refinements can be made based on feedback and evolving plugin interfaces in PyMapGIS.
```
