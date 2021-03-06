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

backup_agencies = 'HousingCounselingAgencies.csv'
backup_properties = 'real_estate_tax_delinquencies.csv'

def go(args):
    usage = ("Directions Usage: python3 {} docs <new_folder_name>"
            " [distance (mi)] \n"
            "Visualization Usage: python3 {} viz <new_folder_name> \n"
            "Property Location Usage: python3 {} find_property <new_folder_name>"
            " [opa_number]")
    agencies = agencies_url
    properties = properties_url
    if args[-1] == 'local':
        agencies = backup_agencies
        properties = backup_properties
    if len(args) < 3 or args[1] not in ['docs', 'viz', 'find_property']:
        return print(usage.format(args[0], args[0], args[0]))
    if len(args)>=4 and 'local' not in args:
        try:
            float(args[3])
        except:
            return print(usage.format(args[0], args[0], args[0]))

    path = os.getcwd()+'/' +args[2]
    if not os.path.exists(path):
        os.mkdir(path)
    print('Collecting and cleaning the data...')
    agency, prop = ci.create_dfs(agencies, properties)
    
    if args[1] =='find_property':
        print('Finding property...')
        check = set(prop.opa_number)
        if int(args[3]) in check:
            dvm.find_location(int(args[3]), path, agency, prop)
            return print('Saved at {}'.format(path))
        return print('OPA Number not in data')

    agency, prop = ci.data_cleaning(agency, prop)
    prop = ci.append_column_closest_agency(agency, prop)

    if args[1] == 'docs':
        print('Creating Documents...')
        prop_clean = gd.store_document_info(prop, agency, float(args[3]))
        gd.write_documents(prop_clean, path)
        return print('Saved at {}'.format(path))

    if args[1] =='viz':
        print('Creating Visualizations...')
        dvm.all_agencies_map(path, agency)
        dvm.clustered_map(path, agency, prop)
        dvm.heat_map(path, agency, prop)
        ad.make_total_due_pie(path, prop)
        ad.make_agency_bar_chart(path,
            ad.make_closest_agency_table(prop))
        ad.make_hist_day_since_last_payment(path, prop)
        return print('Saved at {}'.format(path))


if __name__ == "__main__":
    go(sys.argv)
