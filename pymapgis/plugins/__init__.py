"""
PyMapGIS Plugin System.

This package provides the interfaces and registry for discovering and loading
external plugins that can extend PyMapGIS functionality, such as adding
new data drivers, processing algorithms, or visualization backends.

To create a plugin, implement one of the abstract base classes defined in
`pymapgis.plugins.interfaces` (e.g., PymapgisDriver, PymapgisAlgorithm)
and register it using setuptools entry points under the appropriate group
(e.g., 'pymapgis.drivers', 'pymapgis.algorithms').

Example entry point in plugin's setup.py or pyproject.toml:

[project.entry-points."pymapgis.drivers"]
my_driver_name = "my_plugin_package.module:MyDriverClass"

Available interfaces and loader functions are exposed here for convenience.
"""

from .interfaces import (
    PymapgisDriver,
    PymapgisAlgorithm,
    PymapgisVizBackend,
)
from .registry import (
    load_driver_plugins,
    load_algorithm_plugins,
    load_viz_backend_plugins,
    PYMAPGIS_DRIVERS_GROUP,
    PYMAPGIS_ALGORITHMS_GROUP,
    PYMAPGIS_VIZ_BACKENDS_GROUP,
)

__all__ = [
    # Interfaces
    "PymapgisDriver",
    "PymapgisAlgorithm",
    "PymapgisVizBackend",
    # Loader functions
    "load_driver_plugins",
    "load_algorithm_plugins",
    "load_viz_backend_plugins",
    # Entry point group constants
    "PYMAPGIS_DRIVERS_GROUP",
    "PYMAPGIS_ALGORITHMS_GROUP",
    "PYMAPGIS_VIZ_BACKENDS_GROUP",
]
