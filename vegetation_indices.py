# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VegetationIndices
                                 A QGIS plugin
 This plugin allow calculate vegetation indices
                              -------------------
        begin                : 2018-05-25
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Alexander Semonchik
        email                : mymail@mail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog
from .vegetation_indices_tool import VITool
# Initialize Qt resources from file resources.py
# import resources
# Import the code for the dialog
from .vegetation_indices_dialog import VegetationIndicesDialog
import os.path


class VegetationIndices:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'VegetationIndices_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Vegetation Indices')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'VegetationIndices')
        self.toolbar.setObjectName(u'VegetationIndices')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('VegetationIndices', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = VegetationIndicesDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/VegetationIndices/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Vegetation Indices'),
            callback=self.run,
            parent=self.iface.mainWindow())

    """--------------CUSTOM FUNCTIONS--------------"""

    # обновление содержимого выпадающих списков
    def update_rasters_boxes(self):

        # очистка списков
        self.clear_boxes(
            self.dlg.redBox,
            self.dlg.nirBox,
            self.dlg.blueBox
        )

        # фомирование нового контента
        layers = list()
        layers.append("Not Set")
        layers = layers + [lay.name() for lay in self.iface.mapCanvas().layers()]

        # добавление нового содежимого в выпадющие списки
        self.add_layers_to_raster_boxes(
            layers,
            self.dlg.redBox,
            self.dlg.nirBox,
            self.dlg.blueBox
        )

    # Добавление списка слоев
    def add_layers_to_raster_boxes(self, layers, *boxes):
        for box in boxes:
            box.addItems(layers)

    def clear_boxes(self, *boxes):
        for box in boxes:
            box.clear()

    # метод выбора файла результирущего растра
    def select_output_file(self):
        filename = QFileDialog.getSaveFileName(
            self.dlg, "Select output file ", "", '*.tif'
        )
        self.dlg.lineEdit.setText(filename)

    def on_ok(self):
        index_name = self.dlg.viBox.currentText()
        red_band = self.iface.mapCanvas().layers()[self.dlg.redBox.currentIndex() - 1]
        nir_band = self.iface.mapCanvas().layers()[self.dlg.nirBox.currentIndex() - 1]
        output = self.dlg.lineEdit.text()
        blue_band = self.iface.mapCanvas().layers()[self.dlg.nirBox.currentIndex() - 1]
        L = self.dlg.lBox.value()
        a = self.dlg.aBox.value()

        self.tool = VITool(
            index_name,
            red_band, nir_band, output,
            blue_band, L, a
        )

        if self.tool.index == "NDVI":
            self.tool.calc_ndvi()
        elif self.tool.index == "RVI":
            self.tool.calc_rvi()
        elif self.tool.index == "SAVI":
            self.tool.calc_savi()
        elif self.tool.index == "ARVI":
            self.tool.calc_arvi()

    """----------END OF CUSTOM FUNCTIONS-----------"""

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Vegetation Indices'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""

        self.update_rasters_boxes()
        self.dlg.viBox.clear()
        self.dlg.viBox.addItems(["NDVI", "RVI", "SAVI", "ARVI"])

        self.dlg.lineEdit.clear()
        # подключение к кнопке выбора
        self.dlg.outputButton.clicked.connect(self.select_output_file)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.on_ok()
            self.dlg.outputButton.clicked.disconnect(self.select_output_file)
