import requests
import json
import sqlite3
import os

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'agency_property_db.sqlite3')
agencies_url = 'http://data-phl.opendata.arcgis.com/datasets/3265538198254e9fb6a8974745adab51_0.geojson'
'''
Question
Do we need to use this API url(https://services.arcgis.com/fLeGjb7u4uXqeF9q/ar\
cgis/rest/services/HousingCounselingAgencies/FeatureServer/0/query?\
outFields=*&where=1%3D1),and convert from text data to sqlite database??

In the following data, I use json data from the agencies_url.
'''

def collect_agencies(url=agencies_url):
    '''
    Request to agency data url, get text data, and make database of sqlite3.
    Input:
        url:agencies_url
   '''
    response = requests.get(url)         # Get agencies data from the url.
    results = response.json()
    agencies_data = results["features"]

    conn = sqlite3.connect(DATABASE_FILENAME) # Create a DataBase
    cur = conn.cursor()
    cur.execute("CREATE TABLE agencies_table (ID TEXT PRIMARY KEY, Agency,\
                 PHONE_NUMBER, STREET_ADDRESS, ZIP_CODE, URL, LON, LAT)")     # Create tabole
    for i in agencies_data:                                                   # Insert info
        id_num = i['properties']['OBJECTID'] 
        agency = i['properties']['AGENCY']
        phone_num = i['properties']['PHONE_NUMBER']
        address = i['properties']['STREET_ADDRESS']
        zip_code = i['properties']['ZIP_CODE']
        agency_url = i['properties']['WEBSITE_URL']
        lon = i['geometry']['coordinates'][0]
        lat = i['geometry']['coordinates'][1]
        data_lst = [id_num, agency, phone_num, address, zip_code, agency_url, lon, lat]
        cur.execute('INSERT INTO agencies_table VALUES(?, ?, ?, ?, ?, ?, ?, ?)', data_lst)
        conn.commit()
    conn.close()

# Need to make a function which operate property database 