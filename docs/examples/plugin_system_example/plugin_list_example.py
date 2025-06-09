import pymapgis as pmg
from pymapgis.plugins import plugin_registry # Assuming this is the correct import

def list_available_plugins():
    """
    Demonstrates how to list available plugins in PyMapGIS using the API.
    """
    print("--- PyMapGIS Plugin System Example ---")

    # --- Using the PyMapGIS Plugin API ---
    print("\n--- Listing available plugins (API) ---")

    try:
        available_plugins = plugin_registry.list_plugins() # Or pmg.plugins.list_plugins()

        if available_plugins:
            print("Available plugins:")
            for plugin_name, plugin_obj in available_plugins.items(): # Assuming it returns a dict
                # The structure of plugin_obj might vary. Adjust accordingly.
                # For this example, let's assume plugin_obj might be the plugin class or a descriptor.
                print(f"- {plugin_name}")
        elif isinstance(available_plugins, list) and len(available_plugins) > 0: # If it's a list of names
            print("Available plugins:")
            for plugin_name in available_plugins:
                print(f"- {plugin_name}")
        else:
            print("No plugins are currently registered or reported by the registry.")
            print("This might mean only core functionalities are active, or no external plugins are installed.")

    except AttributeError:
        print("Error: Could not find 'plugin_registry.list_plugins()'.")
        print("Attempting 'pmg.list_plugins()' if available...")
        try:
            # Alternative common pattern for accessing plugin functions
            if hasattr(pmg, 'list_plugins'):
                available_plugins = pmg.list_plugins()
                if available_plugins:
                    print("Available plugins (via pmg.list_plugins()):")
                    for plugin_name in available_plugins: # Assuming this returns a list of names
                        print(f"- {plugin_name}")
                else:
                    print("No plugins found via pmg.list_plugins().")
            else:
                print("Neither plugin_registry.list_plugins() nor pmg.list_plugins() is available.")
        except Exception as e_alt:
            print(f"Error attempting alternative plugin listing: {e_alt}")
    except Exception as e:
        print(f"An error occurred while trying to list plugins: {e}")
        print("Please ensure your PyMapGIS installation is complete and supports the plugin system.")

    # --- Corresponding CLI Command ---
    print("\n\n--- Corresponding CLI Command (for informational purposes) ---")
    print("You can list plugins using the PyMapGIS CLI:")
    print("  pymapgis plugin list")
    print("\nNote: To run this CLI command, open your terminal/shell.")

if __name__ == "__main__":
    list_available_plugins()
