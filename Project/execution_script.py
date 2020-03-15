import sys
import os
import collect_info as ci
import Data_Viz_Map as dvm
import analyze_data as ad
import get_directions as gd


agencies_url = 'http://data-phl.opendata.arcgis.com/data\
sets/3265538198254e9fb6a8974745adab51_0.csv'

properties_url = 'https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM\
+real_estate_tax_delinquencies&filename=real_estate_tax_delinquenc\
ies&format=csv&skipfields=cartodb_id,the_geom,the_geom_webmercator'

def go(args):
    usage_docs = ("usage: python3 {} <raw data filename> <training filename>"
             " <testing filename> [seed]")
    usage_viz = ("usage: python3 {} <raw data filename> <training filename>"
             " <testing filename> [seed]")
    usage_cust_serve = ("usage: python3 {} <raw data filename> <training filename>"
             " <testing filename> [seed]")
    path = os.getcwd()+'/' +args[2]
    print('reading csvs')
    agency, prop = ci.create_dfs(agencies_url, properties_url)
    print('cleaning csvs')
    agency, prop = ci.data_cleaning(agency, prop)
    print('adding closest agency')
    prop = ci.append_column_closest_agency(agency, prop)
    print('dfs cross walked')
    if args[1] == 'docs':
        print('if passed')
        os.mkdir(path)
        prop_clean = gd.store_document_info(prop, agency, float(args[3]))
        gd.write_documents(prop_clean, path)
    if args[1] =='viz':
        dvm.all_agencies_map(path, agency)
        dvm.clustered_map(path, agency, prop)
        dvm.heat_map(path, agency, prop)
        ad.make_total_due_pie(path, prop)
        ad.make_agency_bar_chart(path,
            ad.make_closest_agency_table(prop))
        ad.make_hist_day_since_last_payment(path, prop)
    if args[1] =='find_property':
        dvm.find_location(int(args[2]), path, agency, prop)









if __name__ == "__main__":
    print('entry if, go called')
    go(sys.argv)

'''
def go(args):
   
    Process the arguments and call clean.
    

    usage = ("usage: python3 {} <raw data filename> <training filename>"
             " <testing filename> [seed]")
    if len(args) < 4 or len(args) > 5:
        print(usage.format(args[0]))
        sys.exit(1)

    try:
        if len(args) == 4:
            seed = None
        else:
            seed = int(args[4])
    except ValueError:
        print(usage)
        print("The seed must be an integer")
        sys.exit(1)

    clean(args[1], args[2], args[3], seed)
'''