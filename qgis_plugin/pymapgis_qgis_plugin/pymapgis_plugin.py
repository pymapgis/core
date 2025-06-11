import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import Qgis, QgsMessageLog

PLUGIN_NAME = "PyMapGIS Layer Loader"

class PymapgisPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = "&PyMapGIS Tools"
        self.pymapgis_dialog_instance = None

    def initGui(self):
        """Create the menu entries for the plugin."""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')

        self.add_action(
            icon_path,
            text='Load Layer with PyMapGIS',
            callback=self.run_load_layer_dialog,
            parent=self.iface.mainWindow(),
            status_tip='Load a layer using PyMapGIS'
        )
        self.iface.addPluginToMenu(self.menu, self.actions[0])

    def unload(self):
        """Removes the plugin menu item from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)

        if self.pymapgis_dialog_instance:
            try:
                self.pymapgis_dialog_instance.finished.disconnect(self.on_dialog_close)
                self.pymapgis_dialog_instance.deleteLater()
            except Exception as e:
                QgsMessageLog.logMessage(f"Error during dialog cleanup: {str(e)}", PLUGIN_NAME, Qgis.Warning)
            self.pymapgis_dialog_instance = None

        self.actions = []


    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, status_tip=None, parent=None):
        """Helper function to create and register QAction."""
        action = QAction(QIcon(icon_path), text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if add_to_menu:
            self.actions.append(action)
        return action

    def run_load_layer_dialog(self):
        """Runs the dialog to load a layer."""
        QgsMessageLog.logMessage("run_load_layer_dialog triggered.", PLUGIN_NAME, Qgis.Info)

        try:
            import pymapgis
        except ImportError:
            error_message = "PyMapGIS library not found. Please ensure it is installed in the QGIS Python environment."
            self.iface.messageBar().pushMessage("Error", error_message, level=Qgis.Critical, duration=5)
            QgsMessageLog.logMessage(error_message, PLUGIN_NAME, Qgis.Critical)
            return

        try:
            from .pymapgis_dialog import PyMapGISDialog
        except ImportError as e:
            error_message = f"Failed to import PyMapGISDialog: {str(e)}. Check plugin structure and pymapgis_dialog.py."
            self.iface.messageBar().pushMessage("Error", error_message, level=Qgis.Critical, duration=5)
            QgsMessageLog.logMessage(error_message, PLUGIN_NAME, Qgis.Critical)
            return

        if self.pymapgis_dialog_instance is None:
            QgsMessageLog.logMessage("Creating new PyMapGISDialog instance.", PLUGIN_NAME, Qgis.Info)
            self.pymapgis_dialog_instance = PyMapGISDialog(self.iface, self.iface.mainWindow())
            self.pymapgis_dialog_instance.finished.connect(self.on_dialog_close)

        self.pymapgis_dialog_instance.show()
        self.pymapgis_dialog_instance.activateWindow()
        self.pymapgis_dialog_instance.raise_()

    def on_dialog_close(self):
        """Handles the dialog close event."""
        QgsMessageLog.logMessage("PyMapGISDialog closed.", PLUGIN_NAME, Qgis.Info)
        if self.pymapgis_dialog_instance:
            # Disconnect to avoid issues if closed by window manager vs. accept/reject
            try:
                self.pymapgis_dialog_instance.finished.disconnect(self.on_dialog_close)
            except TypeError: # Signal already disconnected
                pass
            self.pymapgis_dialog_instance.deleteLater() # Recommended to allow Qt to clean up
        self.pymapgis_dialog_instance = None
