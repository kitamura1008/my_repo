#!/usr/bin/env python
# coding: utf-8


import folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd
from collect_info import create_dfs, data_cleaning, search_closest_agency


def all_agencies_map(path, agency_df, show=False):
    '''
    Generate an interactive map for Philadephia city,
    with housing counceling agenies added.

    Imput: agency dataframe
    
    return: An interactive map for Philadephia with agencies.
    '''
    
    # Make a map around the whole philly city.
    philly_map = folium.Map(location=[40.0000, -75.16379], zoom_start=12)
    housing = folium.map.FeatureGroup()

    for row in agency_df.itertuples(index=False):
        folium.Marker([row.Y, row.X], popup=row.AGENCY).add_to(philly_map)
    philly_map.add_child(housing)
    
    if show:
        return philly_map

    philly_map.save(path+'/agency_plot.html')



def find_location(key, agency_df, prop_df):
    '''
    Build a function for searching real estate tax delinquencies properties,
    and plot it on the interactive map.
    
    Input: Real estate property's object ID, agency dataset and property dataset
    
    return: An interactive map for with searched property located,
    showing summary of the property's tax status with mouse on.
    '''

    housing = folium.map.FeatureGroup()
    prop = prop_df[prop_df['objectid'] == key]

    # Make a philly_map with zoom and centered at the targetted property.
    philly_map = folium.Map(location=[float(prop.lat), float(prop.lon)], zoom_start=14)

    # Mark all the agencies.
    column_names = agency_df.columns
    for row in agency_df.itertuples(index=False):
        popup_words = (column_names[3] + ': ' + str(row[3]) + '\n' +
                       column_names[4] + ': ' + str(row[4]) + '\n' +
                       column_names[6] + ': ' + str(row[6]))
        folium.Marker([row.Y, row.X], popup=popup_words).add_to(philly_map)
    philly_map.add_child(housing)    
    
    # Find out the closest agency.
    closest_ag_id, mile = search_closest_agency(key, agency_df, prop_df)

    # Mark the closest agency from the property with blue cercle 
    agency = agency_df[agency_df['OBJECTID'] == closest_ag_id]
    housing.add_child(folium.CircleMarker([agency.Y, agency.X],
        popup=agency['AGENCY'], radius=10, color='blue', fill=True, 
        fill_color='blue', fill_opacity=0.4))

    # Mark the property with red cercle
    popup_sentence = "This is your property. " + str(mile) + " mile(s) to the closest agency"
    housing.add_child(folium.CircleMarker([prop.lat, prop.lon],
        popup=popup_sentence, radius=10, color='red',
        fill=True, fill_color='red', fill_opacity=0.4))

    location = philly_map.add_child(housing)
    location.save(path+'/matched_agency_location.html')


def clustered_map(path, agency_df, prop_df):
    '''
    Build clustered real estate tax delinquencies properties, and plot it on the interactive map.
    
    Input: Expected number of real estate tax delinquencies properties on the map
    
    return: An interactive map with delinquencies status, clustered by blocks/neibourhoods,
    we can click on it to interactively explore to further layers for children's details.
    '''

    # Create a map with all agencies
    philly_map = all_agencies_map(path, agency_df, show=True)

    # Plot props and show clusters
    cluster = MarkerCluster().add_to(philly_map)
    for row in prop_df.itertuples(index=False):
        cluster.add_child(folium.CircleMarker([row.lat, row.lon], popup=row.total_due))
    housing = folium.map.FeatureGroup()
    
    clustered = philly_map.add_child(housing)
    clustered.save(path+'/property_cluster.html')


def heat_map(path, agency_df, prop_df):
    '''
    Build heat map for clustered real estate tax delinquencies properties, 
    and plot it on the interactive map.
    
    Input: 
        Expected number of real estate tax delinquencies properties on the map
    
    return: An interactive map with delinquencies heat map,
    we can zoom in and zoom out to see different levels of heat maps.
    '''

    # Create a map with all agencies
    philly_map = all_agencies_map(path, agency_df, show=True)

    # Add heat data.
    heat_data = []
    for row in prop_df.itertuples(index=False):
        heat_data.append([row.lat, row.lon])
    HeatMap(heat_data).add_to(philly_map)
    
    philly_map.save(path+'/property_heat.html')



#FYI (for testing)
'''
all_agencies_map(agency_df).save("phi_map.html")

find_location(997161, agency_df, prop_df).save("find_location.html")

clustered_map(10000, agency_df, prop_df).save("clustered_map.html")

heat_map(5000, agency_df, prop_df).save("heat_map.html")
'''
