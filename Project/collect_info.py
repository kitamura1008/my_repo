import requests
import json
import sqlite3
import os

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'agency_property_db.sqlite3')
agencies_url = 'http://data-phl.opendata.arcgis.com/datasets/3265538198254e9fb6a8974745adab51_0.geojson'
properties_url = 'https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM+\
                  real_estate_tax_delinquencies&filename=real_estat\
                  e_tax_delinquencies&format=geojson&skipfields=cartodb_id'


def create_tables():
    '''
    Create two tables, agencies information table and properties information
    table
   '''	
    conn = sqlite3.connect(DATABASE_FILENAME)                                 # Create a DataBase
    cur = conn.cursor()
    collect_agencies(conn, cur)
    collect_properties(conn, cur)


### accessory functions ###
def collect_agencies(conn, cur):
    '''
    Get json data and create agencies information table.
    Input:
        conn(connection object)
        cur:(cursor object)
   '''
    agencies_data = request_data(agencies_url)
    cur.execute("CREATE TABLE agencies_table (ID TEXT PRIMARY KEY, Agency,\
                 PHONE_NUMBER, STREET_ADDRESS, ZIP_CODE, URL, LON, LAT)")     # Create a table

    data_category_lst = ['OBJECTID', 'AGENCY', 'PHONE_NUMBER', 
                         'STREET_ADDRESS', 'ZIP_CODE', 'WEBSITE_URL']

    for i in agencies_data:                                                   # Insert info
        data_lst = []
        for data_category in data_category_lst:
            data = i['properties'][data_category]
            data_lst.append(data)
        lon = i['geometry']['coordinates'][0]
        lat = i['geometry']['coordinates'][1]
        data_lst.append(lon)
        data_lst.append(lat)

        cur.execute('INSERT INTO agencies_table VALUES(?, ?, ?, ?, ?, ?, ?, ?)', data_lst)
        conn.commit()


def collect_properties(conn, cur):
    '''
    Get json data and create properties information table.
    Input:
        conn(connection object)
        cur:(cursor object)
   '''
    properties_data = request_data(properties_url)
    cur.execute("CREATE TABLE properties_table (ID TEXT PRIMARY KEY, BUILDING_CODE,\
                 BUILDING_CATEG, DETAIL, OWNER, ADDRESS, ZIP_CODE, LAST_ASSESS_YEAR,\
                 TAXABLE_ASSESS, TOTAL_ASSESS, PRINCIPAL_DUE, PENALTY_DUE, OTHER_DUE,\
                 TOTAL_DUE, LON, LAT)")                                       # Create a table

    data_category_lst = ['objectid', 'building_code', 'building_category', 
                         'detail_building_description', 'owner', 
                         'street_address','zip_code', 'year_of_last_assessment', 
                         'taxable_assessment', 'total_assessment', 'principal_due',
                         'penalty_due', 'other_charges_due', 'total_due']
    for i in properties_data:                                                   # Insert info
        if i['properties']['building_category'] == 'commercial': 
            continue
        data_lst = []
        for data_category in data_category_lst:
            data = i['properties'][data_category]
            data_lst.append(data)
        lon = i['geometry']['coordinates'][0]
        lat = i['geometry']['coordinates'][1]
        data_lst.append(lon)
        data_lst.append(lat)
        
        cur.execute('INSERT INTO properties_table VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
                    , data_lst)
        conn.commit()
    conn.close()


def request_data(url):
	'''
    Request to url, get json data.
    Input:
        url(strings): url which you want to request to
    Output:
        data(dictionary): agencies or properties information 
   '''
    response = requests.get(url)
    results = response.json()
    data = results["features"]
    return data
