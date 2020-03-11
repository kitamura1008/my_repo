
import folium
from folium.plugins import MarkerCluster
import pandas as pd
from collect_info import data_cleaning, create_dfs

def phi_map():
	'''
	Plot an interactive map for the city of Philadephia, with all the Housing
	Counseling Agencies added.

	return: An interactive map

	'''

    latitude = 39.95233
    longitude = -75.16379
    phi_map = folium.Map(location=[latitude, longitude], zoom_start=12)
    agencies, tax = create_dfs()
    latitudes = list(agencies.Y)
    longitudes = list(agencies.X)
    housing = folium.map.FeatureGroup()

    for lat, lon, i in zip(latitudes, longitudes, agencies.index):
        folium.Marker([lat, lon], popup=agencies.iloc[i, 3:]).add_to(phi_map)
    phi_map.add_child(housing)
    return phi_map


def find_location(key):
	'''
	Load Properties tax delinquiencies data, create an interactive map that we
	can use to search any property's object ID, and locate the property on the
	Philadephia interactive map.

	Input: Properties tax delinquiencies object ID.

	return: Interactive map with the searched housing property located

	'''
	
    agencies, tax = create_dfs()
    housing = folium.map.FeatureGroup()
    for index, row in tax.iterrows():
        if row['objectid'] == key:
            housing.add_child(folium.CircleMarker([row['lat'], row['lon']], popup=row['total_due'],
                                                  radius=20, color='yellow', fill=True, fill_color='red',
                                                  fill_opacity=0.4))
    return phi_map().add_child(housing)


def clustered_map(show_number):
	'''
	Cluster all the properties tax delinquiencies on the Philadephia interactive map,
	with neibourhood zoom in, zoom out for details review.

	Input: Number of Properties tax delinquiencies we want to see on the map.

	return: Interactive map with clustered Properties tax delinquiencies distribution in blocks.

	'''
	
    agencies, tax = create_dfs()
    limit = show_number
    tax = tax.iloc[0:limit, :].fillna(0)
    map = phi_map()
    cluster = MarkerCluster().add_to(map)
    for index, row in tax.iterrows():
        cluster.add_child(folium.CircleMarker([row['lat'], row['lon']], popup=row['total_due']))
    housing = folium.map.FeatureGroup()
    return map.add_child(housing)


phi_map().save("phi_map.html")

find_location(997161).save("find_location.html")

clustered_map(10000).save("clustered_map.html")

