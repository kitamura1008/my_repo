import requests
import pandas as pd
from docx import Document
from geopy import distance

my_key = '5b3ce3597851110001cf6248dde0fad6d307455badca9a590c6deb72'
headers = {
    'Accept': 'application/json, application/geo+json,\
            application/gpx+xml, img/png; charset=utf-8',
    'Authorization': my_key,
    'Content-Type': 'application/json; charset=utf-8'}
url = 'https://api.openrouteservice.org/v2/directions/driving-car'

def store_document_info(prop_df, agency_df, min_dist_to_service=2.0):
    agency_dict = agency_df.set_index('OBJECTID').to_dict()
    new_col_dict = {'agency_address':'STREET_ADDRESS','agency_name':'AGENCY',
                    'agency_phone':'PHONE_NUMBER', 'agency_url':'WEBSITE_URL'}
    prop_df = prop_df[['opa_number','street_address', 'owner', 'total_due',
                               'lat','lon','closest agency']]
    prop_df['prop_coords'] = list(zip(prop_df.lon,
                                   prop_df.lat))

    for k, v in new_col_dict.items():
        prop_df[k] = prop_df.apply(lambda x: 
                    agency_dict[v][x['closest agency']], axis=1)
    prop_df['agency_coords'] = prop_df.apply(lambda x:
                            (agency_dict['X'][x['closest agency']], 
                            agency_dict['Y'][x['closest agency']]),
                                                    axis=1)
    prop_df['service_dist'] = prop_df.apply(lambda x: 
                            distance.distance(x.prop_coords, x.agency_coords).miles,
                            axis=1)

    return prop_df[prop_df.service_dist > min_dist_to_service]

#quick check: open interpreter, import file, run below comment
#p_c, a_c = (-74.97728686, 40.09634467),(-75.05874080034742, 40.02787224694022)
#get_directions.get_directions(p_c,a_c)
def get_directions(prop_coords, agency_coords):
    body = {"coordinates":[prop_coords,agency_coords],
            "units": "mi","maneuvers":"false"}
    call = requests.post(url, json=body, headers=headers)
    print(call)
    if not str(call)=='<Response [200]>':
        return 'Directions Unavailable'


    steps = call.json()['routes'][0]['segments'][0]['steps']
    steps_list = []
    for i in steps:
        dist = round(i['distance'],2)
        unit = 'mi'
        if dist < 0.5:
            dist = round(i['distance']*5280)
            unit = 'ft'
        formatted = '{} ({} {})'.format(i['instruction'], dist, unit)
        if dist == 0.0:
            formatted = i['instruction']
        steps_list.append(formatted)

    return steps_list


def write_documents(df, path):
    for row in df.itertuples():
        dirs = get_directions(row.prop_coords, row.agency_coords)
        doc = Document()
        first_paragraph = ("You are receiving this notice because your "
            "property at {} is tax delinquent and we have identified that "
            "you have no housing counseling office in your immediate vicinity. "
            "Your nearest service location is {}. This is approximately {} "
            "mile(s) from your home and directions are enclosed at the bottom "
            "of this notice. While we offer services to help you remain in your "
            "home through this process and to prevent foreclosure, we partner "
            "with housing counseling agencies to offer important supplemental services.\
            ".format(row.street_address, row.agency_name, round(row.service_dist,2)))
    
        doc.add_paragraph(first_paragraph)
        doc.add_heading('Agency Information:', level=1)
        doc.add_paragraph(row.agency_name)
        doc.add_paragraph(row.agency_url)
        doc.add_paragraph(row.agency_phone)
        doc.add_paragraph(row.agency_address)

        doc.add_heading('Directions:', level=1)
        doc.add_paragraph('From {}'.format(row.street_address), style='Intense Quote')
        if len(dirs) <= 1:
            doc.add_paragraph('Directions Unavailable')
        else:
            for step in dirs:
                doc.add_paragraph(step, style='List Bullet')
        doc.save(path+'/'+str(row.opa_number)+'.docx')
