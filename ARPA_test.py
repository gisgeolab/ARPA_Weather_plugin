# -*- coding: utf-8 -*-
"""
/***************************************************************************
 arpatest
                                 A QGIS plugin
 Plugin for testing ARPA API
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-12-29
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Emanuele Capizzi
        email                : capizzi.emanuele@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant, QDate
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QFileDialog
from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsPointXY, QgsFeature, Qgis, QgsVectorFileWriter
from qgis.utils import iface
from PyQt5.QtCore import QTextCodec

# Import libraries
from sodapy import Socrata
import pandas as pd
from datetime import datetime, timedelta
import requests
from io import BytesIO
from zipfile import ZipFile
import os
import time
import json
import numpy as np
import dask.dataframe as dd

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .ARPA_test_dialog import arpatestDialog
import os.path

sensors_types = ["Altezza Neve", "Direzione Vento", "Livello Idrometrico", "Precipitazione", "Radiazione Globale", "Temperatura",
                 "Umidità Relativa", "Velocità Vento"]

class arpatest:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
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
            'arpatest_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ARPA test')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('arpatest', message)

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

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ARPA_test/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ARPA test'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ARPA test'),
                action)
            self.iface.removeToolBarIcon(action)

    def test_function(self):
        print("Works!")

    def select_output_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _filter = QFileDialog.getSaveFileName(self.dlg, "Save Layer As", "", "Shapefiles (*.shp);;Geopackages (*.gpkg);;CSV Files (*.csv)", options=options)
        self.dlg.leOutputFileName.setText(filename)

    def connect_ARPA_api(self, token=""):
        """
        Function to connect to ARPA API. Unauthenticated client only works with public data sets, and there is a limit for the requests.
        Note 'None' in place of application token, and no username or password.
        To get all the available data from the API the authentication is required.

        Parameters:
            token (str): the ARPA token obtained from Open Data Lombardia website

        Returns:
            client: client session
        """
        # Connect to Open Data Lombardia using the token
        if token == "":
            print("No token provided. Requests made without an app_token will be subject to strict throttling limits.")
            client = Socrata("www.dati.lombardia.it", None)
        else:
            print("Using provided token.")
            client = Socrata("www.dati.lombardia.it", app_token=token)

        return client

    def ARPA_sensors_info(self, client) -> pd.DataFrame:
        """
        Functions to convert sensors information to Pandas dataframe and fix the data types.

        Parameters:
            sensors_info: object obtained from Socrata with get request

        Returns:
            df: dataframe containing ARPA sensors information
        """

        # Select meteo stations dataset containing positions and information about sensors
        stationsId = "nf78-nj6b"
        sensors_info = client.get_all(stationsId)

        sensors_df = pd.DataFrame(sensors_info)
        sensors_df["idsensore"] = sensors_df["idsensore"].astype("int32")
        sensors_df["tipologia"] = sensors_df["tipologia"].astype("category")
        sensors_df["idstazione"] = sensors_df["idstazione"].astype("int32")
        sensors_df["quota"] = sensors_df["quota"].astype("int16")
        sensors_df["unit_dimisura"] = sensors_df["unit_dimisura"].astype("category")
        sensors_df["provincia"] = sensors_df["provincia"].astype("category")
        sensors_df["storico"] = sensors_df["storico"].astype("category")
        sensors_df["datastart"] = pd.to_datetime(sensors_df["datastart"])
        sensors_df["datastop"] = pd.to_datetime(sensors_df["datastop"])
        sensors_df = sensors_df.drop(
            columns=[":@computed_region_6hky_swhk", ":@computed_region_ttgh_9sm5"])

        return sensors_df

    # def check_dates(self, start_datetime, end_datetime):
    #     """
    #     Check that the start and end dates are in the same year.

    #     Parameters:
    #         start_date (datetime): The start date in the format "YYYY-MM-DD".
    #         end_date (datetime): The end date in the format "YYYY-MM-DD".

    #     Returns:
    #         year (int): The year of the start and end dates.
    #         start_datetime (datetime): The start date as a datetime object.
    #         end_datetime (datetime): The end date as a datetime object.

    #     Raises:
    #         Exception: If the start and end dates are not in the same year.
    #     """
    #     # Get the year of the start and end dates
    #     year = start_datetime.date().year

    #     return year, start_datetime.date(), end_datetime.date()

    def req_ARPA_start_end_date_API(self, client):
        """
        Function to request the start and the end date of data available in the ARPA API.

            Parameters:
                client: the client session

            Returns: 
                start_API_date (str): starting date for available data inside the API.
                end_API_date (str): ending date for available data inside the API.

        """
        try:
            with client:
                # Weather sensors dataset id on Open Data Lombardia
                weather_sensor_id = "647i-nhxk"

                # Query min and max dates
                query = """ select MAX(data), MIN(data) limit 9999999999999999"""

                # Get max and min dates from the list
                min_max_dates = client.get(weather_sensor_id, query=query)[0]

                # Start and minimum dates from the dict obtained from the API
                start_API_date = min_max_dates['MIN_data']
                end_API_date = min_max_dates['MAX_data']

                # Convert to datetime
                start_API_date = datetime.strptime(
                    start_API_date, "%Y-%m-%dT%H:%M:%S.%f")
                end_API_date = datetime.strptime(
                    end_API_date, "%Y-%m-%dT%H:%M:%S.%f")

                return start_API_date, end_API_date
        except Exception as e:
            print(f"An error occurred: {e}")

    def run_startup_datesAPI(self):
        try:

            client = self.connect_ARPA_api()

            start_date_API, end_date_API = self.req_ARPA_start_end_date_API(
                client)
            label_name_start = start_date_API.strftime("%Y-%m-%d %H:%M:%S")
            label_name_end = end_date_API.strftime("%Y-%m-%d %H:%M:%S")
            self.dlg.label_startAPIdate.setText(label_name_start)
            self.dlg.label_endAPIdate.setText(label_name_end)

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self.dlg, "Error", str(e))

    def req_ARPA_data_API(self, client, start_date, end_date, sensors_list):
        """
        Function to request data from available weather sensors in the ARPA API using a query.

            Parameters:
                client: the client session
                start date (str): the start date in yyy-mm-dd format
                end date (str): the end date in yyy-mm-dd format

            Returns: 
                time_series: time series of values requested with the query for all sensors

        """

        # Select the Open Data Lombardia Meteo sensors dataset
        weather_sensor_id = "647i-nhxk"

        # Convert to string in year-month-day format, accepted by ARPA query
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S.%f")

        # Query data
        query = """
        select
            *
        where data >= \'{}\' and data <= \'{}\' limit 9999999999999999
        """.format(start_date, end_date)

        # Get time series and evaluate time spent to request them
        time_series = client.get(weather_sensor_id, query=query)

        # Create dataframe
        df = pd.DataFrame(time_series, columns=['idsensore', 'data', 'valore'])

        # Convert types
        df['valore'] = df['valore'].astype('float32')
        df['idsensore'] = df['idsensore'].astype('int32')
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values(by='data', ascending=True).reset_index(drop=True)

        # Filter with selected sensors list
        try:
            df = df[df['value'] != -9999]
        except:
            df = df[df['valore'] != -9999]
        df = df[df['idsensore'].isin(sensors_list)]

        return df

    def aggregate_group_data(self, df):
        """
        Aggregates ARPA data using statistical aggregration function (mean, max, min etc.). The dataframe is grouped by sensor id (idsensore).

                Parameters:
                    df(dataframe): ARPA dataframe containing the following columns: "idsensore"(int), "data"(datetime) and "valore"(float)

                    agg(str): the statistical aggregation to be performed (mean, max, min etc.)

                Returns:
                    df(dataframe): computed filtered and aggregated dask dataframe
        """

        # df = df.set_index('data') not necessary if not resampling

        grouped = df.groupby('idsensore')['valore'].agg(
            ['mean', 'max', 'min', 'std', 'count'])
        grouped = grouped.reset_index()

        return grouped

    def order_dates(self, df):
        """
        Orders the dates of a dataframe

        Parameters
            df: dataframe containing datetime column

        """
        df = df.sort_values(by='data', ascending=True).reset_index(drop=True)
        return df

# --- RUN ------------

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = arpatestDialog()
            self.dlg.pbOutputSave.clicked.connect(self.select_output_file)

        # Add sensors type
        self.dlg.cbSensorsType.clear()
        self.dlg.cbSensorsType.addItems(
            [str(sensor) for sensor in sensors_types])

        # Add documentation link
        self.dlg.labelLinkDoc.setText(
            '<a href="https://github.com/capizziemanuele/ARPA_Weather_plugin">GitHub Doc</a>')
        self.dlg.labelLinkDoc.setOpenExternalLinks(True)

        # Modifiy initial widgets
        self.run_startup_datesAPI()

        # Options for the calendar (date selection)
        today = QDate.currentDate()
        self.dlg.dtStartTime.setDisplayFormat("dd-MM-yyyy hh:mm:ss")
        self.dlg.dtEndTime.setDisplayFormat("dd-MM-yyyy hh:mm:ss")
        self.dlg.dtStartTime.setDate(today)
        self.dlg.dtEndTime.setDate(today)
        self.dlg.dtStartTime.setCalendarPopup(True)
        self.dlg.dtEndTime.setCalendarPopup(True)

        # Show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()

        if result:

            # Create client
            arpa_token = self.dlg.leToken.text()

            client = self.connect_ARPA_api(arpa_token)

            with client:
                # Dataframe containing sensors info
                sensors_df = self.ARPA_sensors_info(client)

                # Get the selected sensor from the gui
                sensor_sel = self.dlg.cbSensorsType.currentText()

                # Filter the sensors depending on the "tipologia" field (sensor type)
                sensors_list = (
                    sensors_df.loc[sensors_df['tipologia'] == sensor_sel]).idsensore.tolist()

                # Get the start and the end date from the gui
                start_date = self.dlg.dtStartTime.dateTime().toPyDateTime()
                end_date = self.dlg.dtEndTime.dateTime().toPyDateTime()

                # Check that the start and end dates are in the same year
                if start_date.year != end_date.year:
                    QMessageBox.warning(
                        None, "Invalid Date Range", "Dates must be in the same year!")
                    return
                elif start_date > end_date:
                    QMessageBox.warning(
                        None, "Invalid Date Range", "Start date bust be before end date")
                    return

                # Get sensors value time series
                sensors_values = self.req_ARPA_data_API(
                    client, start_date, end_date, sensors_list)

                # Calculate statistics on the whole dataset
                sensor_test_agg = self.aggregate_group_data(
                    sensors_values)

                # Merge the values with the sensors info
                merged_df = pd.merge(
                    sensor_test_agg, sensors_df, on='idsensore')

                merged_df['lng'] = merged_df['lng'].astype('float64')
                merged_df['lat'] = merged_df['lat'].astype('float64')
                merged_df['idsensore'] = merged_df['idsensore'].astype('int32')
                merged_df['tipologia'] = merged_df['tipologia'].astype(str)
                merged_df['datastart'] = merged_df['datastart'].astype(str)

                # print(os.getcwd())
                # merged_df.to_csv('./test.csv', index=False)

                # Create vector layer
                layer = QgsVectorLayer(
                    "Point?crs=EPSG:4326", sensor_sel+' ({start} / {end})'.format(start=start_date, end=end_date), "memory")

                # Add fields for latitude and longitude
                layer.dataProvider().addAttributes([QgsField("idsensore", QVariant.Int), QgsField("mean", QVariant.Double), QgsField("max", QVariant.Double),
                                                    QgsField("min", QVariant.Double), QgsField("std", QVariant.Double), QgsField("count", QVariant.Int),
                                                    QgsField("tipologia", QVariant.String),
                                                    QgsField("unit_dimisura", QVariant.String), QgsField("idstazione", QVariant.Int),
                                                    QgsField("nomestazione", QVariant.String), QgsField("quota", QVariant.Double),
                                                    QgsField("provincia", QVariant.String), QgsField("datastart", QVariant.String),
                                                    QgsField("storico", QVariant.String),
                                                    QgsField("cgb_nord", QVariant.Int), QgsField("cgb_est", QVariant.Int),
                                                    QgsField("lng", QVariant.Double), QgsField("lat", QVariant.Double)])
                layer.updateFields()
                layer.startEditing()
                # Add point geometries to the layer
                features = []

                for index, row in merged_df.iterrows():
                    point = QgsPointXY(row['lng'], row['lat'])
                    feature = QgsFeature()
                    feature.setGeometry(QgsGeometry.fromPointXY(point))
                    feature.setAttributes([QVariant(row['idsensore']), QVariant(row['mean']), QVariant(row['max']),
                                           QVariant(row['min']), QVariant(row['std']), QVariant(row['count']),
                                           QVariant(row['tipologia']), QVariant(row['unit_dimisura']),
                                           QVariant(row['idstazione']), QVariant(row['nomestazione']),
                                           QVariant(row['quota']), QVariant(row['provincia']), QVariant(row['datastart']), 
                                           QVariant(row['storico']), QVariant(row['cgb_nord']),
                                            QVariant(row['cgb_est']), QVariant(row['lng']), QVariant(row['lat'])])
                    features.append(feature)

                layer.addFeatures(features)
                layer.commitChanges()
                # Add the layer to the QGIS project
                QgsProject.instance().addMapLayer(layer)
                layer.updateExtents()

                # Save file as shp/gpkg/csv
                filename = self.dlg.leOutputFileName.text()
                context = QgsProject.instance().transformContext()

                if filename != "":
                    if filename.endswith(".shp"):
                        # Save as a shapefile
                        options = QgsVectorFileWriter.SaveVectorOptions()
                        options.driverName = 'ESRI Shapefile'
                        QgsVectorFileWriter.writeAsVectorFormatV3(layer, filename, context, options)
                    elif filename.endswith(".gpkg"):
                        # Save as a geopackage
                        options = QgsVectorFileWriter.SaveVectorOptions()
                        options.driverName = 'GPKG'
                        QgsVectorFileWriter.writeAsVectorFormatV3(layer, filename, context, options)
                    elif filename.endswith(".csv"):
                        # Save as csv
                        merged_df.to_csv(filename, index=False)
                    
                    # Write message
                    self.iface.messageBar().pushMessage("Success", "Output file written at " + filename, level=Qgis.Success, duration=3)

            pass
