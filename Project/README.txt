Finding Delinquent Property in Philadelphia


PACKAGES
folium
seaborn
matplotlib
googlemaps
docx
pandas
re
datetime
numpy
collections
geopy
sys
os
math

USAGE:
General Note: Over the last few days, we have experienced periodic trouble collecting data from the url.  As such, we have added the ability to read the csv directly from our project folder.  If you run into trouble on the data collection and want to collect data locally, please add 'local' as an extra argument in any call you make using the below usages.

GET DIRECTIONS

python3 execution_script.py docs <new/destination_folder_name> [distance_from_service (mi)]

Notes (GET DIRECTIONS CALL): 
-The above can take a while to run, we generally run with distances 4.0 miles or greater from service.
-The API is googlemaps, which required my credit card in case I exceed my free amount.  I have thousands of calls left, but please don't test with very small distances ad nauseum.

VISUALIZATIONS

python3 execution_script.py viz <new/destination_folder_name>

MAP OF SINGLE PROPERTY

python3 execution_script.py find_property <new/destination_folder_name> [opa_number (int)]

Notes (MAP OF SIGNLE PROPERTY CALL):
The above requires an OPA Number input. OPA Number is an the id for a property with the Phila Department of Revenue
Example OPA Numbers:
In data:
56033810
871299170
884456237
871510530
61027715

Not in data:
100000
1000000
10000000
100000000
1000000000




execution_script.py: called from command line to acquire visualizations, directions, or find a specific property
collect_info.py: functions for putting two datasets into dataframes, cleaning them and compute the closest agencies from properties.
get_directions.py: functions to create and store directions for property delinquencies.
Data_Viz_Map.py: functions for creating interactive maps for real estate property agencies, find the closest agency for each property, clustered delinquency properties and heat map.
analyze_data.py: functions for analyzing data and creating three graphs.

README.txt: this file
