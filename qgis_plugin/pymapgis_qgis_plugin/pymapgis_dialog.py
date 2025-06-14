# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis, QgsMessageLog, QgsVectorLayer, QgsRasterLayer, QgsProject

import pymapgis
import geopandas as gpd
import xarray as xr
import tempfile
import os
import traceback

PLUGIN_NAME = "PyMapGIS Layer Loader"

class PyMapGISDialog(QDialog):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.uri = None

        self.setWindowTitle(f"{PLUGIN_NAME} Dialog")
        # Set window modality to non-modal, so it doesn't block QGIS UI
        # self.setWindowModality(Qt.NonModal) # This is default for QDialog.show()

        self.layout = QVBoxLayout(self)

        self.uri_label = QLabel("Enter PyMapGIS URI (or path to local file):")
        self.layout.addWidget(self.uri_label)

        self.uri_input = QLineEdit(self)
        self.uri_input.setPlaceholderText("e.g., census://acs?..., /path/to/data.geojson")
        self.uri_input.setMinimumWidth(450)
        self.layout.addWidget(self.uri_input)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.load_button = QPushButton("Load Layer")
        self.load_button.setDefault(True)
        self.load_button.clicked.connect(self.process_uri)
        button_layout.addWidget(self.load_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject) # reject() closes the dialog
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def process_uri(self):
        self.uri = self.uri_input.text().strip()
        if not self.uri:
            self.iface.messageBar().pushMessage(
                "Warning",
                "URI cannot be empty.",
                level=Qgis.Warning,
                duration=3
            )
            QgsMessageLog.logMessage("URI input was empty.", PLUGIN_NAME, Qgis.Warning)
            return

        try:
            QgsMessageLog.logMessage(f"Attempting to load URI: {self.uri}", PLUGIN_NAME, Qgis.Info)
            data = pymapgis.read(self.uri)

            # Generate a base layer name from the URI
            uri_basename = self.uri.split('/')[-1].split('?')[0] # Get last part of path, remove query params
            layer_name_base = os.path.splitext(uri_basename)[0] if uri_basename else "pymapgis_layer"

            # Ensure layer name is unique in the project
            layer_name = layer_name_base
            count = 1
            while QgsProject.instance().mapLayersByName(layer_name): # Check if layer name already exists
                layer_name = f"{layer_name_base}_{count}"
                count += 1

            if isinstance(data, gpd.GeoDataFrame):
                QgsMessageLog.logMessage(f"Data is GeoDataFrame. Processing as vector layer: {layer_name}", PLUGIN_NAME, Qgis.Info)

                # Use context manager for automatic cleanup of temporary directory
                with tempfile.TemporaryDirectory(prefix='pymapgis_qgis_') as temp_dir:
                    # Sanitize layer_name for use as a filename
                    safe_filename = "".join(c if c.isalnum() else "_" for c in layer_name)
                    temp_gpkg_path = os.path.join(temp_dir, safe_filename + ".gpkg")

                    data.to_file(temp_gpkg_path, driver="GPKG")

                    vlayer = QgsVectorLayer(temp_gpkg_path, layer_name, "ogr")
                    if not vlayer.isValid():
                        error_detail = vlayer.error().message() if hasattr(vlayer.error(), 'message') else "Unknown error"
                        self.iface.messageBar().pushMessage("Error", f"Failed to load GeoDataFrame as QgsVectorLayer: {error_detail}", level=Qgis.Critical, duration=5)
                        QgsMessageLog.logMessage(f"Failed QgsVectorLayer: {temp_gpkg_path}. Error: {error_detail}", PLUGIN_NAME, Qgis.Critical)
                        return
                    QgsProject.instance().addMapLayer(vlayer)
                    # Temporary directory and files are automatically cleaned up when exiting this block

                self.iface.messageBar().pushMessage("Success", f"Vector layer '{layer_name}' loaded.", level=Qgis.Success, duration=3)
                QgsMessageLog.logMessage(f"Vector layer '{layer_name}' added to project (temporary files cleaned up)", PLUGIN_NAME, Qgis.Success)
                self.accept()

            elif isinstance(data, xr.DataArray):
                QgsMessageLog.logMessage(f"Data is xarray.DataArray. Processing as raster layer: {layer_name}", PLUGIN_NAME, Qgis.Info)

                # Check for CRS, rioxarray needs it for GeoTIFF export
                if data.rio.crs is None: # data.attrs.get('crs') or data.encoding.get('crs') could be other checks
                    QgsMessageLog.logMessage(f"Raster data for '{layer_name}' is missing CRS information. Cannot save as GeoTIFF.", PLUGIN_NAME, Qgis.Warning)
                    self.iface.messageBar().pushMessage("Warning", "Raster data missing CRS. Cannot load.", level=Qgis.Warning, duration=5)
                    return

                # Ensure rioxarray is available and data has spatial dims
                if not hasattr(data, 'rio'):
                    raise ImportError("rioxarray extension not found on xarray.DataArray. Is rioxarray installed and imported?")

                # Use context manager for automatic cleanup of temporary directory
                with tempfile.TemporaryDirectory(prefix='pymapgis_qgis_') as temp_dir:
                    safe_filename = "".join(c if c.isalnum() else "_" for c in layer_name)
                    temp_tiff_path = os.path.join(temp_dir, safe_filename + ".tif")

                    data.rio.to_raster(temp_tiff_path, tiled=True)

                    rlayer = QgsRasterLayer(temp_tiff_path, layer_name)
                    if not rlayer.isValid():
                        error_detail = rlayer.error().message() if hasattr(rlayer.error(), 'message') else "Unknown error"
                        self.iface.messageBar().pushMessage("Error", f"Failed to load DataArray as QgsRasterLayer: {error_detail}", level=Qgis.Critical, duration=5)
                        QgsMessageLog.logMessage(f"Failed QgsRasterLayer: {temp_tiff_path}. Error: {error_detail}", PLUGIN_NAME, Qgis.Critical)
                        return
                    QgsProject.instance().addMapLayer(rlayer)
                    # Temporary directory and files are automatically cleaned up when exiting this block

                self.iface.messageBar().pushMessage("Success", f"Raster layer '{layer_name}' loaded.", level=Qgis.Success, duration=3)
                QgsMessageLog.logMessage(f"Raster layer '{layer_name}' added to project (temporary files cleaned up)", PLUGIN_NAME, Qgis.Success)
                self.accept()

            else:
                unsupported_type_msg = f"PyMapGIS returned data of type '{type(data).__name__}', which is not yet supported for direct QGIS loading."
                self.iface.messageBar().pushMessage("Warning", unsupported_type_msg, level=Qgis.Warning, duration=5)
                QgsMessageLog.logMessage(unsupported_type_msg, PLUGIN_NAME, Qgis.Warning)

        except ImportError as e:
            import_error_msg = f"Required library not found: {str(e)}. Please ensure PyMapGIS and all dependencies (like rioxarray for rasters) are installed in QGIS Python environment."
            self.iface.messageBar().pushMessage("Error", import_error_msg, level=Qgis.Critical, duration=7)
            QgsMessageLog.logMessage(f"{import_error_msg} - Traceback: {traceback.format_exc()}", PLUGIN_NAME, Qgis.Critical)
        except Exception as e:
            error_msg = f"Error loading data with PyMapGIS: {str(e)}"
            self.iface.messageBar().pushMessage("Error", error_msg, level=Qgis.Critical, duration=7)
            QgsMessageLog.logMessage(f"{error_msg} - Traceback: {traceback.format_exc()}", PLUGIN_NAME, Qgis.Critical)

    def get_uri(self):
        # This method might not be strictly necessary if URI is processed and dialog closed,
        # but good to have if dialog interaction changes.
        return self.uri_input.text().strip()
