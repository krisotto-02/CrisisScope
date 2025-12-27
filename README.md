# CrisisScope
This project retrieves and processes open satellite imagery to map NDVI and visualize vegetation change over time.

# Dependencies
The following Python libraries were used in the development of this project, they can be easily downloaded via pip install:
- future
- typing
- matplotlib
- numpy
- sentinelhub
- geopy
Additionally, the user will need a valid client ID to access the Copernicus satellite data. This can be done by creating a profile on https://www.copernicus.eu/en

# Functionality
The project doesn't contain an UI, and thus, must be operated through the main file CrisisScope.py. The operating principles are as follows:
- Assign the desired location to be monitored by defining the variable "city_name"
- Determine the scope of the location's monitoring in kilometers by defining the variable "resolution"
- Choose the desired time-frame of the vegetation monitoring by defining the variable "time_intervals" in the following way, [(first period), (second period)]
- For example: [("2015-01-01", "2015-07-01"), ("2020-01-01", "2020-07-01")]
- Afterwards, run the program. In a few seconds, the vegetation map for both time periods will show up as a graph
