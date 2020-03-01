import pandas as pd

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

