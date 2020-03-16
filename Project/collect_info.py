from math import radians, cos, sin, asin, sqrt
import pandas as pd

agencies_url = 'http://data-phl.opendata.arcgis.com/data\
sets/3265538198254e9fb6a8974745adab51_0.csv'

properties_url = 'https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM\
+real_estate_tax_delinquencies&filename=real_estate_tax_delinquenc\
ies&format=csv&skipfields=cartodb_id,the_geom,the_geom_webmercator'

def create_dfs(agencies_url, properties_url):
    '''
    Create two data frames, agencies_df and properties_df.

    Outputs
        agencies_df and properties_df(Pandas data frame)
    '''
    agency_df = pd.read_csv(agencies_url)
    prop_df = pd.read_csv(properties_url)

    return agency_df, prop_df

def data_cleaning(agency_df, prop_df):
    '''
    Clean dataframe. Delete unnecessary columns and drop rows including NaN.
    We use only properties for residential.

    Inputs
        agency_df (pandas framework): agencies dataset
        prop_df (pandas framework):properties dataset
    Output
        cleaned agency_df and prop_df.

    '''
    agency_df = agency_df[(agency_df['FORECLOSURE'] == 'Yes')]

    prop_df = prop_df.drop(['return_mail', 'zip_4', 'unit_type',
                            'unit_num', 'co_owner', 'agreement_agency',
                            'payment_agreement', 'mailing_address',
                            'mailing_city', 'mailing_state', 'mailing_zip',
                            'years_in_bankruptcy', 'most_recent_bankrupt_year',
                            'oldest_bankrupt_year', 'principal_sum_bankrupt_years',
                            'total_amount_bankrupt_years'], axis=1)

    prop_df = prop_df.dropna(how='any')
    prop_df = prop_df[prop_df['building_category'] == 'residential']

    return agency_df, prop_df

def append_column_closest_agency(agency_df, prop_df):
    '''
    Apepend a column which indicates the closest agency from each property.

    Inputs
        agency_df (pandas framework): agencies dataset
        prop_df (pandas framework):properties dataset
    Output
        prop_df with a column of closest agencies.
    '''
    lst_closest_ags = get_lst_closest_agencies(agency_df, prop_df)
    prop_df['closest agency'] = lst_closest_ags

    return prop_df


def search_closest_agency(property_id, agency_df, prop_df):
    '''
    Given Object_id of a property and the two dataframe,
    find out the closest agency ID and the distance(miles) to the proper.
    '''
    prop_df = prop_df[prop_df['opa_number'] == property_id]
    prop_lon, prop_lat = tuple(prop_df[['lon', 'lat']].values.tolist()[0])

    min_distance = 999999.99
    closest_ag_id = 0
    closest_ag_lon, closest_ag_lat = .0, .0

    # Compute the closest agency and the distance to the agency
    for agency_row in agency_df.itertuples(index=False, name=None):
        dist_squared = (prop_lon - agency_row[0])**2 + (prop_lat - agency_row[1])**2
        if dist_squared < min_distance:
            min_distance = dist_squared
            closest_ag_id = agency_row[2]
            closest_ag_lon = agency_row[0]
            closest_ag_lat = agency_row[1]

    # Convert the minimum distance into ft.
    mile = haversine(prop_lon, prop_lat, closest_ag_lon, closest_ag_lat)
    return closest_ag_id, mile


def get_lst_closest_agencies(agency_df, prop_df):
    '''
    Given agency dataframe and prop dataframe, compute list of
    the closest agency from every property.
    '''

    lst_closest_ags = []
    for prop_row in prop_df.itertuples(index=False, name=None):
        min_distance = 9999.99
        closest_ag_id = 0

        # Compute the closest agency.
        for agency_row in agency_df.itertuples(index=False, name=None):
            dist_squared = (prop_row[-1] - agency_row[0])**2 + (prop_row[-2] - agency_row[1])**2
            if dist_squared < min_distance:
                min_distance = dist_squared
                closest_ag_id = agency_row[2]

        # Make a list of closest agency from each property.
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
    meter = km * 1000
    mile = meter / 1609.344
    return round(mile, 3)
