# ARPA Weather Sensors QGIS Plugin

<img src="icon.png" width="100"> <br>
The ARPA Weather Sensors Plugin is a QGIS plugin designed to help users process time series data from weather sensors provided by the Regional Agency for Environmental Protection of Lombardy ([ARPA Lombardia](https://www.arpalombardia.it/Pages/Meteorologia/Osservazioni-e-Dati/Dati-in-tempo-reale.aspx)). With this plugin, you can easily import ARPA weather sensor data and process it using a variety of algorithms and methods available in QGIS.

## Installation
To use the ARPA Weather Sensors Plugin, you'll need to install a few libraries first. Specifically, you'll need to install [Sodapy](https://github.com/xmunoz/sodapy), [pandas](https://pandas.pydata.org/docs/index.html), and [dask](https://www.dask.org/).

<b>Sodapy</b><br>
Sodapy is a Python library that provides a simple interface for accessing data from the Socrata Open Data API. In the context of the ARPA Weather Sensors Plugin, Sodapy is used to retrieve data from the ARPA Lombardia weather sensors.

<b>pandas</b><br>
pandas is a powerful data analysis library for Python. It provides data structures for efficiently storing and manipulating large datasets, as well as tools for working with missing data, time series data, and more. In the context of the ARPA Weather Sensors Plugin, pandas is used to process and analyze the weather sensor data.

<b>dask</b><br>
dask is a flexible parallel computing library for Python. It allows you to process large datasets in parallel, using a variety of distributed computing strategies. In the context of the ARPA Weather Sensors Plugin, dask is used to speed up the processing of large weather sensor CSV datasets.

### Windows
If you're using Windows, you can install these libraries using the OSGeo4W Shell. Here's how:

1. Open the OSGeo4W Shell.
2. Type the following command to install Sodapy:
```
>> pip install sodapy
```
3. Type the following command to install pandas:
```
>> pip install pandas
```
4. Type the following command to install dask:
```
>> pip install dask
```

ADD MINIMUM VERSIONS

### Linux
If you're using Linux, you can install these libraries using the QGIS Python Console. Here's how:
Install pip (if you don't already have it) using the Terminal:
```
>> apt-get install python3-pip
```
1. Open the QGIS Python Console.
2. Type the following command to import pip:
```
>> import pip 
```
3. Type the following command to install Sodapy:
```
>> pip install sodapy
```
4. Type the following command to install pandas:
```
>> pip install dask
```
5. Type the following command to install dask:
```
>> pip install pandas
```
ADD MINIMUM VERSIONS

---

To use the ARPA Weather Sensors Plugin, you can install it as a ZIP file. Here's how:

1. Download the plugin ZIP file from the GitHub repository from the green box in the top right corner `Code` > `Download ZIP`
2. Open QGIS and go to `Plugins` > `Manage and Install Plugins`...
3. In the `Manage and Install Plugins` dialog box, click on the `Install from ZIP` tab
4. Click the `...` button to browse to the location where you saved the plugin ZIP file, then click `Install Plugin`
5. QGIS will install the plugin and ask if you want to enable it. Click `Yes` to enable the plugin

Once you've installed and enabled the plugin, you can use it to process ARPA Lombardia weather data.

## Usage
Once you have installed the ARPA Weather Sensors Plugin, you can use it to process ARPA Lombardia weather data. The plugin provides a user-friendly interface for selecting and processing weather sensor data.
Open QGIS and search for the plugin in the Plugins toolbar.

### Choosing the Data Source
With this plugin, you have the flexibility to choose whether to retrieve data from the Socrata Open Data API for the current month or from yearly CSV files for older data. You can easily select your preferred data source at the beginning of the process, and the plugin will automatically request data from the API or CSV files based on the selected date range.

It is important to note that using this plugin does not require an API token, but you may need one to access all datasets on Open Data Lombardia on Socrata API without any limitations. Additionally, the CSV files are automatically downloaded by the plugin, and processed using the dask Python library.

There are a few important things to keep in mind when using CSV files with this plugin. Firstly, only dates within the same year can be processed, as the size of the CSV files is around 2GB. Furthermore, when QGIS is closed, all downloaded CSV files are deleted. These files are stored in the tmp folder inside the plugin directory, and a link to the folder is provided by the plugin. Lastly, if the CSV file for the selected year is already available, the CSV folder won't be downloaded.

It is worth noting that sensor information is obtainable from the API. The data is available in two different ways: current month data is available from the Socrata API, while previous months/years data is available from CSV files that must be downloaded first.

### Selecting the Time Range and Sensor Type
Once you have selected the data source, you can choose the time range for which you want to retrieve data, and the type of weather sensor you are interested in. You can also select a province to filter the data by location.

### Removing Outliers
You can choose to remove outliers from the data using one of three functions: None (if you don't want to remove any data), Interquantile Range (IQR) or Z-Score. Selecting one of these functions will help you to identify and remove anomalous data points that may be affecting your analysis.

### Exporting Layer Map and Summary Statistics
The plugin allows you to export a layer map of the selected weather sensor data, along with summary statistics calculated for the selected time range and sensor type.
When processing weather sensor data using this plugin, you can obtain a range of relevant statistics and multipoint layers for different sensors. These include:

- Mean, maximum, minimum, standard deviation, and count: for all variables, except for Wind Direction.
- Mode and count, for Wind Direction, which is expressed in Degree North.
  
These statistics are calculated based on the selected time range and sensor type, and can provide valuable insights into the weather patterns and trends being analyzed.

These statistics can be exported along with the layer map of the sensor data. The summary statistics and layer map provide a more comprehensive view of the sensor data and can be used for further analysis.

### Exporting Time Series Data and Sensor Information
You can export the time series data for the selected sensors in a CSV file, which can be used for further analysis or visualization in other tools. You can also export the selected sensors' information in a CSV file.

## Use Cases??

## Author

Emanuele Capizzi
Email: emanuele.capizzi@polimi.it