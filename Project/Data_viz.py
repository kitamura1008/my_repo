
import folium
import pandas as pd
from collect_info import data_cleaning, create_dfs

def find_location(key):
    latitude = 39.95233
    longitude = -75.16379
    phi_map = folium.Map(location=[latitude, longitude], zoom_start=12)
    agencies_df, properties_df = create_dfs()
    agencies, tax = data_cleaning(agencies_df, properties_df)
    latitudes = list(agencies.Y)
    longitudes = list(agencies.X)
    housing = folium.map.FeatureGroup()

    for lat, lon, i in zip(latitudes, longitudes, agencies.index):
        folium.Marker([lat, lon], popup=agencies.iloc[i, 3:]).add_to(phi_map)
    phi_map.add_child(housing)
    
    for index, row in tax.iterrows():
        if row['objectid'] == key:
            housing.add_child(folium.CircleMarker([row['lat'], row['lon']], popup=row['total_due'],
                                                  radius=20, color='yellow', fill=True, fill_color='red',
                                                  fill_opacity=0.4))
    return phi_map.add_child(housing)

find_location(key).save('data_viz.html')
