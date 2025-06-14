import pymapgis as pmg
import time

def manage_cache_example():
    """
    Demonstrates using PyMapGIS API and CLI for cache management.
    """
    print("--- PyMapGIS Cache Management Example ---")

    # --- Using the PyMapGIS Cache API ---
    print("\n--- Demonstrating Cache API ---")

    # Get cache directory
    cache_dir = pmg.cache.get_cache_dir()
    print(f"Cache directory (API): {cache_dir}")

    # Make a request to ensure some data is cached
    print("\nMaking a sample data request to populate cache...")
    try:
        # Using a small dataset for quick caching
        _ = pmg.read("tiger://rails?year=2022") # Read some data to cache
        print("Sample data read. Cache should now have some items.")
    except Exception as e:
        print(f"Error reading sample data for caching: {e}")
        print("Proceeding with cache operations, but list/size might be empty if read failed.")

    time.sleep(1) # Give a moment for cache to write

    # Get cache size
    cache_size = pmg.cache.get_cache_size()
    print(f"Cache size (API): {cache_size}")

    # List cached items
    print("\nCached items (API):")
    cached_items = pmg.cache.list_cache()
    if cached_items:
        for item_url, item_details in cached_items.items():
            print(f"- URL: {item_url}, Size: {item_details['size_hr']}, Created: {item_details['created_hr']}")
    else:
        print("No items currently in cache or cache listing failed.")

    # Clear the cache
    print("\nClearing cache (API)...")
    pmg.cache.clear_cache()
    print("Cache cleared (API).")

    # Verify cache is cleared
    cache_size_after_clear = pmg.cache.get_cache_size()
    print(f"Cache size after clear (API): {cache_size_after_clear}")
    cached_items_after_clear = pmg.cache.list_cache()
    if not cached_items_after_clear:
        print("Cache is empty after clearing, as expected.")
    else:
        print(f"Cache still contains items: {len(cached_items_after_clear)} items.")


    # --- Corresponding CLI Commands ---
    print("\n\n--- Corresponding CLI Commands (for informational purposes) ---")
    print("You can perform similar actions using the PyMapGIS CLI:")
    print("\nTo get cache path:")
    print("  pymapgis cache path")
    print("\nTo get cache size:")
    print("  pymapgis cache size")
    print("\nTo list cached items:")
    print("  pymapgis cache list")
    print("\nTo clear the cache:")
    print("  pymapgis cache clear")
    print("\nTo remove expired items from cache:")
    print("  pymapgis cache clean")
    print("\nNote: To run these CLI commands, open your terminal/shell.")

if __name__ == "__main__":
    manage_cache_example()
