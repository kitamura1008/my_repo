import requests
import json
import sqlite3
import os

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'agency_property_db.sqlite3')
agencies_url = 'https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest\
                /services/HousingCounselingAgencies/FeatureServer/0/quer\
                y?where=1%3D1&objectIds=&time=&geometry=&geometryType=es\
                riGeometryEnvelope&inSR=&spatialRel=esriSpatialRelInters\
                ects&resultType=none&distance=0.0&units=esriSRUnit_Meter\
                &returnGeodetic=false&outFields=*&returnGeometry=true&fe\
                atureEncoding=esriDefault&multipatchOption=xyFootprint&m\
                axAllowableOffset=&geometryPrecision=&outSR=&datumTransf\
                ormation=&applyVCSProjection=false&returnIdsOnly=false&r\
                eturnUniqueIdsOnly=false&returnCountOnly=false&returnExt\
                entOnly=false&returnQueryGeometry=false&returnDistinctVa\
                lues=false&cacheHint=false&orderByFields=&groupByFieldsF\
                orStatistics=&outStatistics=&having=&resultOffset=&resul\
                tRecordCount=&returnZ=false&returnM=false&returnExceeded\
                LimitFeatures=true&quantizationParameters=&sqlFormat=non\
                e&f=pjson&token='
'''
Question
Do we need to use this url(https://services.arcgis.com/fLeGjb7u4uXqeF9q/ar\
cgis/rest/services/HousingCounselingAgencies/FeatureServer/0/query?\
outFields=*&where=1%3D1),and convert from text data to sqlite database??

In the following data, I use json data from the agencies_url. However, 
this json file is the output of the query on the website.
It seems a little wierd to me.
'''

def collect_agencies(url=agencies_url):
    '''
    Request to agency data url, get json data, and make database of sqlite3.
    Input:
        url:agencies_url
   '''
    response = requests.get(url)         # Get agencies data from the url.
    results = response.json()
    agencies_json_data = results['features']

    conn = sqlite3.connect(DATABASE_FILENAME) # Create a DataBase
    cur = conn.cursor()
    cur.execute("CREATE TABLE agencies_data (ID TEXT PRIMARY KEY, Agency,\
                 PHONE_NUMBER, STREET_ADDRESS, ZIP_CODE, URL, LON, LAT)")
    for i in agencies_json_data:
        id_num = i['attributes']['OBJECTID'] 
        agency = i['attributes']['AGENCY']
        phone_num = i['attributes']['PHONE_NUMBER']
        address = i['attributes']['STREET_ADDRESS']
        zip_code = i['attributes']['ZIP_CODE']
        agency_url = i['attributes']['WEBSITE_URL']
        lon = i['geometry']['x']
        lat = i['geometry']['y']
        data_lst = [id_num, agency, phone_num, address, zip_code, agency_url, lon, lat]
        cur.execute('INSERT INTO agencies_data VALUES(?, ?, ?, ?, ?, ?, ?, ?)', data_lst)
        conn.commit()
    conn.close()

# Need to make a function which operate property database 