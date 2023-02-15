# ARPA Meteorological Sensors Plugin

This repositories contains the complete plugin to process ARPA meteorological sensors time series. 

## Installation
In order to use this plugin you need to install Sodapy and Dask libraries.

Open the OSGeo4W Shell and type the following command.

You can use this plugin without API token (check whether it is necessary. Token allows access to all datasets on Open Data Lombardia on Socrata API without limits).

```
>> pip install sodapy
```
```
>> pip install pandas
```

```
>> pip install dask
```

This plugin allows to obtain relevant statistics and multipoint layers for different sensors.

TO DO: option to save time series for advanced users that need to request data.

## ARPA data structure
The data available from ARPA Lombardia can be requested from the Open Data Lombardia catalog.
Sensors information are obtainable from API.

It must be noted that the data are available in 2 different ways:
1) Current month data are avaiable from the Socrata API;
2) Previous months/years data are available from CSV files that must be downloaded first.



## Plugin
The plugin automatically request data from API or CSV files depending on the selected date.
The user is allowed to select the dates in the correct time range.

The CSV files are automatically downloaded by the plugin.

Sensors information are converted into a DataFrame using Pandas.
Data from the API are converted into a DataFrame using Pandas.
The CSV files are processed using Dask Python library.

- Only dates (start & end dates) in the same year can be processed, since CSV files size is around 2GB and load multiple CSV into memory can be an issue.
- When QGIS is closed, all CSV files downloaded are deleted
- If the CSV for the selected year is already available the CSV file won't be downloaded.

## Add filter outliers in the time series?
