# Plugin System: Listing Available Plugins Example

This example demonstrates how to discover and list available plugins within the PyMapGIS environment using both its Python API and command-line interface (CLI).

## Description

PyMapGIS features a plugin system that allows for its functionality to be extended. This example focuses on how a user can see which plugins are currently registered and available.

The Python script `plugin_list_example.py`:
1.  Imports PyMapGIS and attempts to access its plugin registry (`pymapgis.plugins.plugin_registry`).
2.  Calls a function (e.g., `plugin_registry.list_plugins()` or `pmg.list_plugins()`) to retrieve a list of available plugin names.
3.  Prints the names of these plugins to the console.
4.  If no plugins are found, or if the plugin system interface isn't available as expected, it prints an informative message.

The script also provides the equivalent CLI command for listing plugins.

## How to Run the Python Script

1.  **Ensure PyMapGIS is installed**:
    If you haven't installed PyMapGIS:
    \`\`\`bash
    pip install pymapgis
    \`\`\`
    The availability and behavior of the plugin system might depend on the version of PyMapGIS and its core components.

2.  **Navigate to the example directory**:
    \`\`\`bash
    cd docs/examples/plugin_system_example
    \`\`\`

3.  **Run the script**:
    \`\`\`bash
    python plugin_list_example.py
    \`\`\`

## Expected Script Output

The script will print to the console:
- A header indicating it's the plugin system example.
- A list of available plugin names. This list might be short or empty in a default PyMapGIS installation if plugins are primarily community-contributed or need to be installed separately. It may list core components if they are registered via the plugin system.
- An informative message if no plugins are found or if there's an issue accessing the plugin listing functionality.
- The corresponding CLI command (`pymapgis plugin list`).

Example output might look like:

```
--- PyMapGIS Plugin System Example ---

--- Listing available plugins (API) ---
Available plugins:
- core_data_provider_census
- core_data_provider_tiger
...or...
No plugins are currently registered or reported by the registry.

--- Corresponding CLI Command (for informational purposes) ---
You can list plugins using the PyMapGIS CLI:
  pymapgis plugin list
```

## Using the CLI Command

To list plugins directly from your terminal, use:

\`\`\`bash
pymapgis plugin list
\`\`\`

This command will query the plugin registry and display the names of all detected plugins.
