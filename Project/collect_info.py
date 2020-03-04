import pandas as pd
from math import radians, cos, sin, asin, sqrt, ceil

agencies_url = 'http://data-phl.opendata.arcgis.com/data\
sets/3265538198254e9fb6a8974745adab51_0.csv'

properties_url = 'https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM\
+real_estate_tax_delinquencies&filename=real_estate_tax_delinquenc\
ies&format=csv&skipfields=cartodb_id,the_geom,the_geom_webmercator'

def create_dfs():
    '''
    Create two data frames, agencies_df and properties_df
    Inputs
        None
    Outputs
        agencies_df and properties_df(Pandas data frame)
    '''
    agencies_df = pd.read_csv(agencies_url)
    properties_df = pd.read_csv(properties_url)

    return agencies_df, properties_df

def data_cleaning(agencies_df, properties_df):
    '''
    Clean dataframe.

    '''
    agencies_df = agencies_df[(agencies_df['FORECLOSURE'] == 'Yes' )] #&
                             # (agencies_df['SPECIALTY'] != any)

    properties_df = properties_df.drop(['return_mail', 'zip_code', 'zip_4', 'unit_type',
        'unit_num', 'co_owner', 'agreement_agency', 'payment_agreement', 
        'mailing_address', 'mailing_city', 'mailing_state', 'mailing_zip',
        'years_in_bankruptcy', 'most_recent_bankrupt_year', 
        'oldest_bankrupt_year', 'principal_sum_bankrupt_years',
        'total_amount_bankrupt_years'], axis=1)

    properties_df = properties_df.dropna(how='any')
    properties_df = properties_df[properties_df['building_category'] == 'residential']

    return agencies_df, properties_df

def append_column_closet_agency(agencies_df, properties_df):
    '''
    Apepend a column which indicate the closest agency from each property.

    Inputs
        agencies_df (pandas framework): agencies dataset
        properties_df (pandas framework):properties dataset
    Output
        properties_df with a column of closest agencies.
    '''
    lst_closest_ags = get_lst_closest_agencies(agencies_df, properties_df)
    properties_df['closest agency'] = lst_closest_ags

    return properties_df


def search_closest_agency(property_id, agencies_df, properties_df):
    '''
    Given Object_id of a property, find out the closest agency ID
    and the distance(meters) to the agency.

    Inputs
        property_id (integer): objectid of a property
        agencies_df (pandas framework): agencies dataset
        properties_df (pandas framework):properties dataset
    '''

    properties_df = properties_df[properties_df['objectid'] == property_id]
    prop_lon, prop_lat = tuple(properties_df[['lon', 'lat']].values.tolist()[0])

    min_distance = 999999.99
    closest_ag_id = 0
    closest_ag_lon = .0
    closest_ag_lat = .0

    # Compute the closest agency and the distance to the agency
    for agencies_row in agencies_df.itertuples(index=False, name=None):
        dist_squared = abs(prop_lon - agencies_row[0])**2 + abs(prop_lat - agencies_row[1])**2
        if dist_squared < min_distance:
            min_distance = dist_squared
            closest_ag_id = agencies_row[2]
            closest_ag_lon = agencies_row[0]
            closest_ag_lat = agencies_row[1]
    
    # Convert the minimum distance into ft.
    ft = haversine(prop_lon, prop_lat, closest_ag_lon, closest_ag_lat)
    return closest_ag_id, ft


def get_lst_closest_agencies(agencies_df, properties_df):
    '''
    Given Object_id of an agency, compute list of the closest agency from each agency.
    '''
    
    lst_closest_ags = []
    for prop_row in properties_df.itertuples(index=False, name=None):
        min_distance = 9999.99
        closest_ag_id = 0
        closest_ag_lon = .0
        closest_ag_lat = .0
        for agencies_row in agencies_df.itertuples(index=False, name=None):
            dist_squared = abs(prop_row[-1] - agencies_row[0])**2 + abs(prop_row[-2] - agencies_row[1])**2
            if dist_squared < min_distance:
                min_distance = dist_squared
                closest_ag_id = agencies_row[2]
               #closest_ag_lon = agencies_row[0]
               #closest_ag_lat = agencies_row[1]

      # ft = haversine(prop_lon, prop_lat, closest_ag_lon, closest_ag_lat)
        lst_closest_ags.append(closest_ag_id)
    
    return lst_closest_ags


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)

    This function is from courses.py in PA2 of capp 30122.
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    ft = m * 3.2808
    return ft
