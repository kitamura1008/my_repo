#!/usr/bin/env python
# coding: utf-8

# In[63]:


import folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd
from collect_info import data_cleaning, create_dfs

def phi_map():
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


# In[64]:


def find_location(key):
    agencies, tax = create_dfs()
    housing = folium.map.FeatureGroup()
    for index, row in tax.iterrows():
        if row['objectid'] == key:
            housing.add_child(folium.CircleMarker([row['lat'], row['lon']], popup=row['total_due'],
                                                  radius=20, color='yellow', fill=True, fill_color='red',
                                                  fill_opacity=0.4))
    return phi_map().add_child(housing)


# In[65]:


def clustered_map(show_number):
    agencies, tax = create_dfs()
    limit = show_number
    tax = tax.iloc[0:limit, :].fillna(0)
    map = phi_map()
    cluster = MarkerCluster().add_to(map)
    for index, row in tax.iterrows():
        cluster.add_child(folium.CircleMarker([row['lat'], row['lon']], popup=row['total_due']))
    housing = folium.map.FeatureGroup()
    return map.add_child(housing)


# In[66]:


def heat_map(show_number):
    agencies, tax = create_dfs()
    limit = show_number
    tax = tax.iloc[0:limit, :].fillna(0)
    map = phi_map()
    heat_data = []
    for index, row in tax.iterrows():
        heat_data.append([row['lat'], row['lon']])
    HeatMap(heat_data).add_to(map)
    return map


# In[67]:


phi_map().save("phi_map.html")


# In[68]:


find_location(997161).save("find_location.html")


# In[69]:


clustered_map(10000).save("clustered_map.html")


# In[70]:


heat_map(5000).save("heat_map.html")


# In[ ]:




