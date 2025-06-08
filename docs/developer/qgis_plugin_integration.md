# Integrating PyMapGIS with QGIS

This guide provides an overview and conceptual outline for integrating PyMapGIS functionalities into QGIS through a custom plugin.

## Introduction

A QGIS plugin for PyMapGIS could offer a user-friendly graphical interface to leverage PyMapGIS's data reading, processing, and potentially visualization capabilities directly within the QGIS environment. This could streamline workflows for users who prefer a GUI or want to combine PyMapGIS features with QGIS's extensive GIS toolset.

## Core Concepts of QGIS Plugin Development

Developing plugins for QGIS involves understanding its Python API (PyQGIS) and plugin architecture.

### Typical Plugin Structure

A QGIS plugin is typically organized as follows:
- **Main Plugin Directory:** A folder named after your plugin (e.g., `pymapgis_qgis_loader/`).
- **`__init__.py`:** Makes the directory a Python package. It often contains a `classFactory(iface)` function, which QGIS calls to load the main plugin class.
- **`metadata.txt`:** Contains essential metadata for the plugin:
    - `name`: Human-readable name.
    - `qgisMinimumVersion`: Minimum QGIS version compatibility.
    - `description`: What the plugin does.
    - `version`: Plugin version.
    - `author`: Plugin author(s).
    - `email`: Author's email.
    - `category`: Where it appears in the Plugin Manager (e.g., "Vector", "Raster", "Web").
    - `experimental`: `True` or `False`.
    - `deprecated`: `True` or `False`.
    - `icon`: Path to an icon for the plugin (e.g., `icon.png`).
- **Main Plugin File (e.g., `my_plugin.py`):** Defines the main plugin class, which usually inherits from `qgis.gui.QgisPlugin`. Key methods include:
    - `__init__(self, iface)`: Constructor, receives `iface` (an instance of `QgisInterface`).
    - `initGui(self)`: Called when the plugin is loaded. Used to add menu items, toolbar buttons, etc.
    - `unload(self)`: Called when the plugin is unloaded. Used to clean up UI elements.
- **UI Files (`.ui`):** User interface forms designed with Qt Designer. These are XML files.
- **Compiled UI Python Files (e.g., `my_dialog_ui.py`):** Generated from `.ui` files using `pyuic5` (for PyQt5) or `pyside2-uic`.
- **Dialog Logic Files (e.g., `my_dialog.py`):** Python scripts that import the compiled UI, inherit from a Qt dialog class (e.g., `QtWidgets.QDialog`), and implement the dialog's behavior.
- **Resources File (`resources.qrc`):** XML file listing plugin resources like icons. Compiled using `pyrcc5` or `pyside2-rcc` into a Python file (e.g., `resources_rc.py`).

### Core QGIS Python Libraries (PyQGIS)

- **`qgis.core`:** Provides fundamental GIS data structures and operations:
    - `QgsVectorLayer`, `QgsRasterLayer`: For handling vector and raster data.
    - `QgsFeature`, `QgsGeometry`, `QgsField`: For working with vector features.
    - `QgsProject`: Manages the current QGIS project (e.g., `QgsProject.instance()`).
    - `QgsCoordinateReferenceSystem`: For CRS management.
    - Processing algorithms and data providers.
- **`qgis.gui`:** Classes for GUI elements and interaction:
    - `QgisInterface` (`iface`): The main bridge to the QGIS application interface. Used to add layers to the map, show messages, access the map canvas, etc.
    - `QgsMapTool`: Base class for creating custom map interaction tools.
    - `QgsMessageBar`: For displaying non-blocking messages to the user.
- **`qgis.utils`:** Various utility functions, including `iface` access if not passed directly.
- **`PyQt5` (or `PySide2`):** The Qt library bindings used for all GUI elements. Dialogs, widgets, signals, and slots are managed using Qt.

### Adding a Plugin to QGIS

1.  Plugins are typically placed in the QGIS Python plugins directory (e.g., `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/` on Linux, or `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\` on Windows).
2.  The "Plugin Builder 3" plugin within QGIS can be used to generate a basic template for a new plugin.
3.  Enable the plugin through the QGIS Plugin Manager. During development, the "Plugin Reloader" plugin is very helpful.

### Creating UIs with Qt Designer

1.  Use Qt Designer (a separate application, often bundled with Qt development tools or installable via pip: `pip install pyqt5-tools`) to create `.ui` files.
2.  Compile the `.ui` file to a Python file: `pyuic5 input.ui -o output_ui.py`.
3.  Create a Python class that inherits from the generated UI class and a Qt widget (e.g., `QtWidgets.QDialog`). This class implements the dialog's logic.

## Example Plugin Outline: "PyMapGIS Layer Loader"

This conceptual plugin would provide a simple dialog to load data using `pymapgis.read()` and add it to the QGIS map canvas.

### 1. `metadata.txt` (Example)

```ini
[general]
name=PyMapGIS Layer Loader
qgisMinimumVersion=3.10
description=Loads layers into QGIS using pymapgis.read()
version=0.1
author=PyMapGIS Team
email=your_email@example.com
category=Vector
experimental=True
icon=icon.png
```
*(You would need to create an `icon.png`)*

### 2. Main Plugin File (`pymapgis_qgis_plugin.py`) (Conceptual Outline)

```python
from qgis.PyQt.QtWidgets import QAction, QMainWindow
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsMessageLog, Qgis # For logging and message levels

# Import your dialog class (defined in another file)
# from .pymapgis_dialog import PymapgisDialog

class PymapgisPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = "&PyMapGIS Tools" # Main menu entry
        self.toolbar = None # Could add a toolbar

    def initGui(self):
        """Create the menu entries and toolbar icons for the plugin."""
        icon_path = os.path.join(self.plugin_dir, 'icon.png') # Path to your icon

        self.add_action(
            icon_path,
            text='Load Layer with PyMapGIS',
            callback=self.run_load_layer_dialog,
            parent=self.iface.mainWindow()
        )
        # Add the plugin menu and toolbar
        self.iface.addPluginToMenu(self.menu, self.actions[0])
        # self.toolbar = self.iface.addToolBar('PymapgisPluginToolBar')
        # self.toolbar.addAction(self.actions[0])

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            # if self.toolbar: self.toolbar.removeAction(action)
        # if self.toolbar: del self.toolbar

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=False, status_tip=None, parent=None):
        """Helper function to create and register QAction."""
        action = QAction(QIcon(icon_path), text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if add_to_menu:
            self.actions.append(action) # Store for menu management

        # if add_to_toolbar and self.toolbar is not None:
        #    self.toolbar.addAction(action)
        return action

    def run_load_layer_dialog(self):
        """Runs the dialog to load a layer."""
        # This is where you would instantiate and show your dialog
        # from .pymapgis_dialog import PymapgisDialog # Ensure this import works
        # Example:
        # if self.dialog is None: # Create dialog if it doesn't exist
        #    self.dialog = PymapgisDialog(self.iface.mainWindow())
        # self.dialog.show()
        # result = self.dialog.exec_() # For modal dialog
        # if result:
        #    uri_to_load = self.dialog.get_uri()
        #    self.load_data_with_pymapgis(uri_to_load)
        QgsMessageLog.logMessage("PyMapGIS Load Layer dialog would open here.", "PyMapGIS Plugin", Qgis.Info)
        # For now, just a message. Actual dialog implementation is more involved.

    # def load_data_with_pymapgis(self, uri):
    #     try:
    #         import pymapgis as pmg # Attempt to import pymapgis
    #         data = pmg.read(uri) # Call pymapgis.read()
    #
    #         # Logic to add 'data' (e.g., GeoDataFrame) to QGIS
    #         # This usually involves saving to a temporary file (e.g., GPKG)
    #         # and then loading that file into QGIS.
    #         # See "Proof-of-Concept Snippet" below.
    #
    #         self.iface.messageBar().pushMessage("Success", f"PyMapGIS loaded: {uri}", level=Qgis.Success, duration=3)
    #     except ImportError:
    #         self.iface.messageBar().pushMessage("Error", "PyMapGIS library not found in QGIS Python environment.", level=Qgis.Critical)
    #     except Exception as e:
    #         self.iface.messageBar().pushMessage("Error", f"Failed to load data with PyMapGIS: {str(e)}", level=Qgis.Critical)

# In __init__.py:
# def classFactory(iface):
#     from .pymapgis_qgis_plugin import PymapgisPlugin
#     return PymapgisPlugin(iface)
```

### 3. Plugin Dialog (`pymapgis_dialog.py` and UI file) (Conceptual)

- **`pymapgis_dialog_base.ui` (Qt Designer):**
    - A `QDialog` with:
        - A `QLabel` ("Enter PyMapGIS URI:").
        - A `QLineEdit` (e.g., `uriLineEdit`) for user input.
        - A `QPushButton` (e.g., `loadButton`, text: "Load Layer").
        - Standard OK/Cancel buttons.
- **`pymapgis_dialog.py` (Logic):**
    ```python
    # from qgis.PyQt.QtWidgets import QDialog
    # from .compiled_ui_file import Ui_PymapgisDialogBase # Assuming UI file is compiled to this
    # import pymapgis as pmg
    # from qgis.core import QgsVectorLayer, QgsProject, QgsRasterLayer, QgsMessageLog, Qgis
    # import tempfile
    # import os
    # import geopandas as gpd # For type checking

    # class PymapgisDialog(QDialog, Ui_PymapgisDialogBase): # Inherit from QDialog and your UI
    #     def __init__(self, parent=None):
    #         super().__init__(parent)
    #         self.setupUi(self) # Setup UI from compiled file
    #         self.loadButton.clicked.connect(self.process_uri)
    #         self.uri = None

    #     def process_uri(self):
    #         self.uri = self.uriLineEdit.text()
    #         if not self.uri:
    #             QgsMessageLog.logMessage("URI cannot be empty.", "PyMapGIS Plugin", Qgis.Warning)
    #             return

    #         try:
    #             QgsMessageLog.logMessage(f"Attempting to load: {self.uri}", "PyMapGIS Plugin", Qgis.Info)
    #             data = pmg.read(self.uri) # THE CORE CALL

    #             if isinstance(data, gpd.GeoDataFrame):
    #                 # Save GDF to a temporary GeoPackage
    #                 temp_dir = tempfile.mkdtemp()
    #                 temp_gpkg = os.path.join(temp_dir, "temp_layer.gpkg")
    #                 data.to_file(temp_gpkg, driver="GPKG")
    #                 layer_name = os.path.splitext(os.path.basename(self.uri))[0] or "pymapgis_vector_layer"
    #                 vlayer = QgsVectorLayer(temp_gpkg, layer_name, "ogr")
    #                 if not vlayer.isValid():
    #                     QgsMessageLog.logMessage(f"Failed to load GeoDataFrame as QgsVectorLayer: {temp_gpkg}", "PyMapGIS Plugin", Qgis.Critical)
    #                     return
    #                 QgsProject.instance().addMapLayer(vlayer)
    #                 QgsMessageLog.logMessage(f"Loaded vector layer: {layer_name}", "PyMapGIS Plugin", Qgis.Success)

    #             # Add similar handling for xarray.DataArray (save as temp GeoTIFF)
    #             # elif isinstance(data, xr.DataArray):
    #             #    ... save as temp_tiff ...
    #             #    rlayer = QgsRasterLayer(temp_tiff, layer_name)
    #             #    QgsProject.instance().addMapLayer(rlayer)

    #             else:
    #                 QgsMessageLog.logMessage(f"Data type {type(data)} not yet supported for direct QGIS loading.", "PyMapGIS Plugin", Qgis.Warning)

    #             self.accept() # Close dialog if successful
    #         except Exception as e:
    #             QgsMessageLog.logMessage(f"Error loading data: {str(e)}", "PyMapGIS Plugin", Qgis.Critical)
    #             # self.iface.messageBar().pushMessage("Error", f"PyMapGIS error: {str(e)}", level=Qgis.Critical) # If iface is available

    #     def get_uri(self):
    #         return self.uri
    ```

## Dependency Management for PyMapGIS in QGIS

This is the most significant challenge.
- **QGIS Python Environment:** QGIS ships with its own Python environment. This environment might not include PyMapGIS or its specific dependencies (GeoPandas, Xarray, PDAL, NetworkX, etc.) at compatible versions.
- **Strategies:**
    1.  **User Installation (Recommended for initial phase):**
        *   Provide clear instructions for users on how to install PyMapGIS and its dependencies into the Python environment used by their QGIS installation.
        *   Some QGIS versions (especially those bundled with OSGeo4W on Windows or newer standalone installers) might have a `pip` command accessible via their Python console or a shell environment.
        *   Example command might be: `python3 -m pip install pymapgis[all]` (if QGIS Python is accessible as `python3`).
        *   This places the burden on the user but is often the most practical approach for complex dependencies.
    2.  **Using an Existing Conda/Venv Environment:**
        *   The plugin could try to configure `sys.path` at runtime to point to an external Python environment where PyMapGIS is installed.
        *   This is risky due to potential library conflicts (e.g., Qt, GDAL) between the QGIS environment and the external one.
    3.  **Bundling (Very Complex):**
        *   Attempting to bundle PyMapGIS and its dependencies with the plugin is generally not feasible or recommended due to the size and complexity of libraries like GeoPandas, GDAL, etc.
    4.  **Calling PyMapGIS as a Subprocess:**
        *   The plugin executes PyMapGIS operations in a separate Python process (from a known environment).
        *   Data is exchanged via files (e.g., GeoJSON, GeoPackage for vector; GeoTIFF for raster) or standard streams.
        *   This avoids Python environment conflicts but adds overhead and complexity in data transfer and user experience.

**Recommendation:** Start with clear instructions for users to install PyMapGIS into their QGIS Python environment if possible, or guide them on setting up a compatible environment that QGIS can be made aware of (e.g., by modifying `PYTHONPATH` before launching QGIS, though this is advanced).

## Proof-of-Concept Snippet (Illustrative)

This snippet shows how data read by `pymapgis.read()` could be loaded into QGIS, assuming PyMapGIS is importable within the QGIS Python console.

```python
# To be run in QGIS Python Console, assuming PyMapGIS is installed there.
import pymapgis as pmg
import geopandas as gpd
from qgis.core import QgsVectorLayer, QgsProject, QgsApplication
import tempfile
import os

# Example URI (replace with a real one accessible to your QGIS environment)
# For local files, ensure QGIS has permission and paths are correct.
# uri = "file:///path/to/your/data.geojson"
# Or a PyMapGIS specific one:
uri = "census://acs/acs5?year=2022&geography=state&variables=B01003_001E"

try:
    print(f"Attempting to read: {uri}")
    data = pmg.read(uri) # PyMapGIS reads the data

    if isinstance(data, gpd.GeoDataFrame):
        print(f"Data read as GeoDataFrame with {len(data)} features.")

        # QGIS typically loads layers from files. Save GDF to a temporary file.
        # Using GeoPackage is a good choice.
        temp_dir = tempfile.mkdtemp()
        temp_gpkg_path = os.path.join(temp_dir, "pymapgis_temp_layer.gpkg")

        print(f"Saving temporary layer to: {temp_gpkg_path}")
        data.to_file(temp_gpkg_path, driver="GPKG", layer="data_layer")

        # Load the layer into QGIS
        layer_name = "Loaded via PyMapGIS: " + (os.path.basename(uri).split('?')[0] or "layer")
        qgis_vlayer = QgsVectorLayer(temp_gpkg_path + "|layername=data_layer", layer_name, "ogr")

        if not qgis_vlayer.isValid():
            print(f"Error: Failed to create QgsVectorLayer from {temp_gpkg_path}")
        else:
            QgsProject.instance().addMapLayer(qgis_vlayer)
            print(f"Successfully added '{layer_name}' to QGIS project.")

            # Optional: Clean up temp file (or manage temp dir lifecycle)
            # os.remove(temp_gpkg_path)
            # os.rmdir(temp_dir)

    # Add similar blocks for xr.DataArray (saving as temp GeoTIFF)
    # elif isinstance(data, xr.DataArray):
    #    print("Data read as xarray.DataArray. Further conversion needed for QGIS.")
    #    # temp_tiff_path = ...
    #    # data.rio.to_raster(temp_tiff_path)
    #    # qgis_rlayer = QgsRasterLayer(temp_tiff_path, layer_name)
    #    # QgsProject.instance().addMapLayer(qgis_rlayer)


    else:
        print(f"Data read is of type: {type(data)}. Not directly loadable as a standard QGIS layer without further processing.")

except ImportError as ie:
    print(f"ImportError: {ie}. Ensure PyMapGIS and its dependencies are in QGIS Python path.")
except Exception as e:
    print(f"An error occurred: {e}")

```

## Future Possibilities

- **Dedicated Processing Algorithms:** Expose PyMapGIS functions as QGIS Processing algorithms for use in the model builder and batch processing.
- **Interactive Map Tools:** Tools that use PyMapGIS to fetch data based on map clicks or drawn ROIs.
- **Direct Data Source Integration:** Custom data providers that allow QGIS to natively browse and load data via PyMapGIS URI schemes (more advanced).
- **Settings UI:** A dialog to configure PyMapGIS settings (`pmg.settings`) from within QGIS.

This document provides a foundational outline. Actual plugin development would require detailed implementation of UI elements, robust error handling, and careful consideration of the QGIS environment.
```
