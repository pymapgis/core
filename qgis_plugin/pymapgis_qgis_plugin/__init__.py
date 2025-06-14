# -*- coding: utf-8 -*-
"""
This script initializes the PyMapGIS QGIS Plugin.
It provides the classFactory function that QGIS calls to load the plugin.
"""

def classFactory(iface):
    """
    Load PyMapGISPlugin class from file pymapgis_plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    # Import the main plugin class
    from .pymapgis_plugin import PymapgisPlugin
    return PymapgisPlugin(iface)
