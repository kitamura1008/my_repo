print('file opened')
import sys
print('sys imported')
import os
print('os imported')
import collect_info
print('collect_info imported')
import Data_Viz_Map
print('Data_Viz_Map imported')
import analyze_data
import get_directions
print('get_directions imported')

agencies_url = 'http://data-phl.opendata.arcgis.com/data\
sets/3265538198254e9fb6a8974745adab51_0.csv'

properties_url = 'https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM\
+real_estate_tax_delinquencies&filename=real_estate_tax_delinquenc\
ies&format=csv&skipfields=cartodb_id,the_geom,the_geom_webmercator'

def go(args):
    print(args[0],args[1],args[2])
    print(type(args[1]),type(args[2]))
    usage_docs = ("usage: python3 {} <raw data filename> <training filename>"
             " <testing filename> [seed]")
    usage_viz = ("usage: python3 {} <raw data filename> <training filename>"
             " <testing filename> [seed]")
    usage_cust_serve = ("usage: python3 {} <raw data filename> <training filename>"
             " <testing filename> [seed]")
    path = os.getcwd()+'/' +args[2]
    print('here')
    agency, prop = collect_info.create_dfs(agencies_url, properties_url)
    print('dfs made')
    agency, prop = collect_info.data_cleaning(agency, prop)
    print('dfs made')
    prop = collect_info.append_column_closet_agency(agency, prop)
    print('dfs cross walked')
    if args[1] == 'docs':
        print('if passed')
        os.mkdir(new_path)
        prop_clean = get_directions.store_document_info(prop, agency, float(args[3]))
        get_directions.write_documents(prop_clean, new_path)
    if args[1] =='viz':
        os.mkdir(path)
        Data_Viz_Map.all_agencies_map(path, agency)
        Data_Viz_Map.clustered_map(path, agency, prop)
        Data_Viz_Map.heat_map(path, agency, prop)
        #analyze_data.make_total_due_pie(prop)
        #analyze_data.make_agency_bar_chart(
        #    analyze_data.make_closest_agency_table(prop))
        #analyze_data.make_hist_day_since_last_payment(prop)









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