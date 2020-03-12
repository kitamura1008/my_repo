import requests
import pandas as pd
from docx import document
from geopy import distance

my_key = '5b3ce3597851110001cf6248dde0fad6d307455badca9a590c6deb72'
headers = {
    'Accept': 'application/json, application/geo+json,\
            application/gpx+xml, img/png; charset=utf-8',
    'Authorization': my_key,
    'Content-Type': 'application/json; charset=utf-8'}
url = 'https://api.openrouteservice.org/v2/directions/driving-car'

def store_document_info(prop_df, agency_df, min_dist_to_service=0.75):
    doc_data = {}
    agency_dict = agency_df.set_index('OBJECTID').to_dict()
    prop_df = prop_df[['street_address', 'owner', 'total_due',
                               'lat','lon','closest agency']]
    prop_df['prop_coords'] = list(zip(prop_df.lon,
                                   prop_df.lat))
    new_col_dict = {'agency_address':'STREET_ADDRESS','agency_name':'AGENCY',
                    'agency_phone':'PHONE_NUMBER', 'agency_url':'WEBSITE_URL'}

    for k, v in new_col_dict.items():
        prop_df[k] = prop_df.apply(lambda x: agency_dict[v][x['closest agency']], 
                     axis=1)
    prop_df['agency_coords'] = prop_df.apply(lambda x: (agency_dict['X'][x['closest agency']], 
                                                    agency_dict['Y'][x['closest agency']]),
                                                    axis=1)
    prop_df['service_dist'] = prop_df.apply(lambda x: 
                            distance.distance(x.prop_coords, x.agency_coords).miles,
                            axis=1)

    return prop_df[prop_df.service_dist > min_dist_to_service]


def get_directions(prop_coords, agency_coords):
    body = {"coordinates":[prop_coords,agency_coords], "units": "mi","maneuvers":"false"}
    call = requests.post(url, json=body, headers=headers)

    if not 'routes' in call.json().keys():
        return 'Directions Unavailable'

    steps = call.json()['routes'][0]['segments'][0]['steps']
    steps_list = []
    for i in steps:
        dist = round(i['distance'],2)
        unit = 'mi'
        if dist <= 0.47349:
            dist = round(i['distance']*5280)
            unit = 'ft'
        formatted = '{} ({} {})'.format(i['instruction'], dist, unit)
        if dist == 0.0:
            formatted = i['instruction']
        steps_list.append(formatted)

    return steps_list


def write_directions(list_of_dicts, , doc):
    for i in list_of_dicts:
        doc.add_paragraph(i['instriction'], style='List Bullet')
    return doc

write_dirs_ouput = write_dirs(test)
document = Document()
first_paragraph = "You are receiving this notice becuase your property at {} is tax delinquent and your property has been identified\
as having no housing counseling office in your immediate vicinity.  Your nearest service location is {}, located at {}.\
This is approximately {} mile(s) from your home and directions are enclosed at the bottom of this notice.\
While we offer services to help you remain in your home through this process and to prevent foreclosure,\
these housing counseling agencies are important supplements.".format('street address', 'service location',
    'service address', 'DISTANCE')
document.add_heading('Directions:', level=1)

#make bullet list of directions
for i in write_dirs_ouput:
    document.add_paragraph(i, style='List Bullet')


from dataclasses import dataclass

@dataclass
Class Notices:




dist = []
hca_name = []
hca_address = []
hca_number = []
hca_url = []

def dist_test(lat, lon)
        for i in hca.itertuples():
            min_dist = 13000 
            num = 0
            #address = ''
            #hca_number = 
            curr_dist = distance.distance((lat, lon), (i.X, i.Y)).miles
            if curr_dist < min_dist:
                min_dist = curr_dist
                num = i.PHONE_NUMBER
        return (dist, num)
