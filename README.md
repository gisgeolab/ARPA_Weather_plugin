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


Examples:
- If the current date is 23rd February 2023 I can request data from API starting from 1st February 2023 up to 23rd February 2023.
- If the current date is 23rd February 2023 and I need data for 15h January 2023, I must use the 2023 CSV file.
- If the current date is 23rd February 2023 and I need data from 15h January 2023 to 23rd February 2023, you must request January data (from CSV file) separately from February data (from API)

## Plugin
The plugin automatically request data from API or CSV files depending on the selected date.
The CSV files are automatically downloaded by the plugin.
The CSV files are processed using Dask Python library.
- Only dates (start & end dates) in the same year can be processed, since CSV files size is around 2GB and load multiple CSV into memory can be an issue.
- When QGIS is closed, all CSV files downloaded are deleted
- If the CSV for the selected year is already available the CSV file won't be downloaded.

## Add filter outliers in the time series?
