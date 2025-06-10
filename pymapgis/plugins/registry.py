"""
Plugin registry for PyMapGIS.

This module handles the discovery and loading of plugins through entry points.
Plugins are registered using setuptools entry points under specific group names.
"""

import importlib.metadata
import logging
from typing import Dict, List, Type, Any, TypeVar

from pymapgis.plugins.interfaces import (
    PymapgisDriver,
    PymapgisAlgorithm,
    PymapgisVizBackend,
)

# TypeVar for generic plugin types
_PluginType = TypeVar("_PluginType")

# Logger setup
logger = logging.getLogger(__name__)

# Entry point group names
PYMAPGIS_DRIVERS_GROUP = "pymapgis.drivers"
PYMAPGIS_ALGORITHMS_GROUP = "pymapgis.algorithms"
PYMAPGIS_VIZ_BACKENDS_GROUP = "pymapgis.viz_backends"


def load_plugins(
    group_name: str, base_class: Type[_PluginType]
) -> Dict[str, Type[_PluginType]]:
    """
    Load plugins registered under a specific entry point group.

    Args:
        group_name: The name of the entry point group to scan.
        base_class: The base class that loaded plugins should inherit from.

    Returns:
        A dictionary mapping plugin names (from entry_point.name) to
        the loaded plugin classes.
    """
    plugins: Dict[str, Type[_PluginType]] = {}

    try:
        # For Python 3.10+ and importlib_metadata >= 3.6.0, .select is preferred
        # entry_points = importlib.metadata.entry_points(group=group_name) # type: ignore
        # However, to maintain broader compatibility (e.g. Python 3.8, 3.9)
        # without needing a very recent importlib_metadata backport,
        # we can use the older way of accessing entry points.
        all_entry_points = importlib.metadata.entry_points()
        # Using .get(group_name, []) on the result of all entry_points() is a fallback.
        # For specific groups, importlib.metadata.entry_points(group=group_name)
        # should return an empty sequence if the group doesn't exist (modern behavior).
        # This code handles both new and older importlib_metadata versions.

        # Python 3.10+ / importlib_metadata 3.9.0+ way:
        if hasattr(importlib.metadata, "SelectableGroups"):  # Heuristic for new API
            eps = importlib.metadata.entry_points(group=group_name)
        else:  # Older way for Python < 3.10 or older importlib_metadata
            eps = all_entry_points.get(group_name, [])  # type: ignore

    except Exception as e:  # Catch potential issues with entry_points() itself
        logger.error(f"Could not retrieve entry points for group '{group_name}': {e}")
        return plugins

    for entry_point in eps:
        try:
            plugin_class = entry_point.load()
        except ImportError as e:
            logger.error(
                f"Error loading plugin '{entry_point.name}' from group '{group_name}': {e}"
            )
            continue
        except AttributeError as e:
            logger.error(
                f"Error accessing plugin '{entry_point.name}' in group '{group_name}' (likely an issue with the module or class): {e}"
            )
            continue
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while loading plugin '{entry_point.name}' from group '{group_name}': {e}"
            )
            continue

        if not isinstance(plugin_class, type):
            logger.warning(
                f"Plugin '{entry_point.name}' from group '{group_name}' did not load as a class type. Skipping."
            )
            continue

        if issubclass(plugin_class, base_class) and plugin_class is not base_class:
            if entry_point.name in plugins:
                logger.warning(
                    f"Duplicate plugin name '{entry_point.name}' found in group '{group_name}'. "
                    f"Existing: {plugins[entry_point.name]}, New: {plugin_class}. Overwriting."
                )
            plugins[entry_point.name] = plugin_class
            logger.info(
                f"Successfully loaded plugin '{entry_point.name}' ({plugin_class.__name__}) from group '{group_name}'."
            )
        else:
            logger.warning(
                f"Plugin '{entry_point.name}' ({plugin_class.__name__}) from group '{group_name}' "
                f"is not a valid subclass of {base_class.__name__} or is the base class itself. Skipping."
            )
    return plugins


# Specific loader functions
def load_driver_plugins() -> Dict[str, Type[PymapgisDriver]]:
    """Load all registered PymapgisDriver plugins."""
    return load_plugins(PYMAPGIS_DRIVERS_GROUP, PymapgisDriver)


def load_algorithm_plugins() -> Dict[str, Type[PymapgisAlgorithm]]:
    """Load all registered PymapgisAlgorithm plugins."""
    return load_plugins(PYMAPGIS_ALGORITHMS_GROUP, PymapgisAlgorithm)


def load_viz_backend_plugins() -> Dict[str, Type[PymapgisVizBackend]]:
    """Load all registered PymapgisVizBackend plugins."""
    return load_plugins(PYMAPGIS_VIZ_BACKENDS_GROUP, PymapgisVizBackend)
