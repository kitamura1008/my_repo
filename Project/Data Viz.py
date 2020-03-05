#!/usr/bin/env python
# coding: utf-8

# In[1]:


import folium
import pandas as pd
# Philadephia latitude and longitude values
latitude = 39.95233
longitude = -75.16379

# Create map and display it
phi_map = folium.Map(location=[latitude, longitude], zoom_start=12)

# Display the map
phi_map


# In[2]:


# Read Dataset 
agencies = pd.read_csv('HousingCounselingAgencies.csv', low_memory=False)
tax = pd.read_csv('real_estate_tax_delinquencies.csv', low_memory=False)
agencies.head()


# In[3]:


# add pop-up text to each marker on the map
latitudes = list(agencies.Y)
longitudes = list(agencies.X)
housing = folium.map.FeatureGroup()

for lat, lon, i in zip(latitudes, longitudes, agencies.index):
    folium.Marker([lat, lon], popup=agencies.iloc[i, 3:]).add_to(phi_map)

# add housing to map
phi_map.add_child(housing)


# In[7]:


# Build a function to search real estate tax delinquency key and add location to the interactive map
def find_location(key):
    for index, row in tax.iterrows():
        if row['objectid'] == key:
            housing.add_child(folium.CircleMarker([row['lat'], row['lon']], popup=row['total_due'],
                                                  radius=20, color='yellow', fill=True, fill_color='red',
                                                  fill_opacity=0.4))
    return phi_map.add_child(housing)


# In[8]:


find_location(914577)

phi_map.save('30122 Data Viz.html')




