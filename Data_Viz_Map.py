#!/usr/bin/env python
# coding: utf-8


import folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd
from collect_info import create_dfs, data_cleaning

def get_data():
    '''
    Load data from cleaned dataframe
    
    return: cleaned dataframes for agencies and tax delinquencies.
    '''
    
    agencies_df, properties_df = create_dfs()
    agencies, tax = data_cleaning(agencies_df, properties_df)
    
    return agencies, tax


def phi_map():
    '''
    Generate an interactive map for Philadephia city, with housing counceling agenies added.
    
    return: An interactive map for Philadephia with agencies.
    '''
    
    agencies, tax = get_data()
    latitude = 39.95233
    longitude = -75.16379
    phi_map = folium.Map(location=[latitude, longitude], zoom_start=12)
    latitudes = list(agencies.Y)
    longitudes = list(agencies.X)
    housing = folium.map.FeatureGroup()

    for lat, lon, i in zip(latitudes, longitudes, agencies.AGENCY):
        folium.Marker([lat, lon], popup=i).add_to(phi_map)
    phi_map.add_child(housing)
    
    return phi_map


def find_location(key):
    '''
    Build a function for searching real estate tax delinquencies properties, and plot it on the interactive map.
    
    Input: Real estate property's object ID
    
    return: An interactive map for with searched property located,
    showing summary of the property's tax status with mouse on.
    '''
    
    agencies, tax = get_data()
    housing = folium.map.FeatureGroup()
    search = tax[tax['objectid'] == key]
    housing.add_child(folium.CircleMarker([search.lat, search.lon], popup=search.total_due,
                                                  radius=20, color='yellow', fill=True, fill_color='red',
                                                  fill_opacity=0.4))

    return phi_map().add_child(housing)


def clustered_map(show_number):
    '''
    Build clustered real estate tax delinquencies properties, and plot it on the interactive map.
    
    Input: Expected number of real estate tax delinquencies properties on the map
    
    return: An interactive map with delinquencies status, clustered by blocks/neibourhoods,
    we can click on it to interactively explore to further layers for children's details.
    '''
    
    agencies, tax = get_data()
    limit = show_number
    tax = tax.iloc[0:limit, :].fillna(0)
    map = phi_map()
    cluster = MarkerCluster().add_to(map)
    for index, row in tax.iterrows():
        cluster.add_child(folium.CircleMarker([row['lat'], row['lon']], popup=row['total_due']))
    housing = folium.map.FeatureGroup()
    
    return map.add_child(housing)


def heat_map(show_number):
    '''
    Build heat map for clustered real estate tax delinquencies properties, and plot it on the interactive map.
    
    Input: Expected number of real estate tax delinquencies properties on the map
    
    return: An interactive map with delinquencies heat map,
    we can zoom in and zoom out to see different levels of heat maps.
    '''
    
    agencies, tax = get_data()
    limit = show_number
    tax = tax.iloc[0:limit, :].fillna(0)
    map = phi_map()
    heat_data = []
    for index, row in tax.iterrows():
        heat_data.append([row['lat'], row['lon']])
    HeatMap(heat_data).add_to(map)
    
    return map


phi_map().save("phi_map.html")

find_location(997161).save("find_location.html")

clustered_map(10000).save("clustered_map.html")

heat_map(5000).save("heat_map.html")

