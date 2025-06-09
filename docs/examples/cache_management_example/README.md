# Cache Management Example (API and CLI)

This example demonstrates how to manage the PyMapGIS data cache using both its Python API and its command-line interface (CLI). Effective cache management can help save disk space and ensure you are using the most up-to-date data when needed.

## Description

The Python script `cache_cli_api_example.py` showcases the following cache operations via the PyMapGIS API:

1.  **Populate Cache**: It first attempts to read a small dataset (`tiger://rails?year=2022`) to ensure there are items in the cache.
2.  **Get Cache Directory**: Retrieves and prints the file system path where PyMapGIS stores cached data (`pmg.cache.get_cache_dir()`).
3.  **Get Cache Size**: Calculates and prints the total size of the cache (`pmg.cache.get_cache_size()`).
4.  **List Cached Items**: Displays a list of URLs/items currently stored in the cache, along with their size and creation time (`pmg.cache.list_cache()`).
5.  **Clear Cache**: Removes all items from the cache (`pmg.cache.clear_cache()`).
6.  **Verify Clearance**: Checks the cache size and lists items again to confirm the cache has been emptied.

The script also lists the equivalent CLI commands that can be used in a terminal for the same operations.

## How to Run the Python Script

1.  **Ensure PyMapGIS is installed**:
    If you haven't installed PyMapGIS:
    \`\`\`bash
    pip install pymapgis
    \`\`\`

2.  **Navigate to the example directory**:
    \`\`\`bash
    cd docs/examples/cache_management_example
    \`\`\`

3.  **Run the script**:
    \`\`\`bash
    python cache_cli_api_example.py
    \`\`\`

## Expected Script Output

The script will print information to the console, including:
- The path to the cache directory.
- The initial size of the cache (after attempting to cache a sample dataset).
- A list of items found in the cache.
- Confirmation that the cache has been cleared.
- The size of the cache after clearing (should be close to zero).
- A list of corresponding CLI commands for your reference.

## Using the CLI Commands

You can also manage the cache directly from your terminal using the `pymapgis` CLI:

-   **Get cache path**:
    \`\`\`bash
    pymapgis cache path
    \`\`\`

-   **Get cache size**:
    \`\`\`bash
    pymapgis cache size
    \`\`\`

-   **List cached items**:
    \`\`\`bash
    pymapgis cache list
    \`\`\`

-   **Clear all items from cache**:
    \`\`\`bash
    pymapgis cache clear
    \`\`\`

-   **Clean expired items from cache**:
    PyMapGIS uses `requests-cache`, which can also handle cache expiry. The `clean` command typically removes only expired entries based on their original cache headers or settings.
    \`\`\`bash
    pymapgis cache clean
    \`\`\`

Running these commands in your terminal will provide direct feedback from the PyMapGIS CLI.
