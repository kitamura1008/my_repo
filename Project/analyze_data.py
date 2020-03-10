import pandas as pd
import numpy as np
import collect_info
import matplotlib.pyplot as plt
from collections import Counter

class DataAnalyze():
'''
    Class for analyzing data.
'''
    def __init__(self):
        '''
        Construct data frame and table.
        '''
        agencies_df, properties_df = collect_info.create_dfs()
        self.agencies_df, self.properties_df = \
        collect_info.data_cleaning(agencies_df, properties_df)
        self.closest_agency_table = self.make_closest_agency_table()

    def make_total_due_hist(self):
        '''
        Make a histrgram of the total due and save it as png file.
        '''
        fig = plt.figure()
        range_lst = list(map(self.determine_range, self.properties_df['total_due']))
        c = Counter(range_lst)
        counter_lst = c.most_common()
        first = counter_lst[0][0]
        first_percentage = counter_lst[0][1] / len(self.properties_df)
        second = counter_lst[1][0]
        second_percentage = counter_lst[1][1] / len(self.properties_df)
        title = "Total due: {:.2%} of properties belongs to {}dollars.\n \
                            {:.2%} of properties belongs to {}dollars".\
                            format(first_percentage, first, second_percentage, second)
        plt.hist(self.properties_df["total_due"], range=(0, 50000), bins=20)
        plt.title(title)
        plt.xlabel('total_due($)')
        plt.ylabel('frequency')
        fig.savefig("total due histgram.png")
        plt.show()

    def determine_range(self, number):
        '''
        Accessary function for make_total_due_hist.
        Determine the range of total due at each property.  

        Inputs
            number (int): it represents total due of each property

        Output:
            number (int): it represents the range of the total due
        '''
        if number < 5000:
            number = 'no more than 5,000'
        elif number >= 5000 and number < 10000:
            number= '5,000 - 10,000'
        elif number >= 10000 and number < 15000:
            number = '10,000 - 15,000'
        elif number >= 15000 and number < 20000:
            number = '15,000 - 20,000'
        elif number >= 20000 and number < 30000:
            number = '20,000 - 30,000'
        elif number >= 30000 and number < 40000:
            number = '30,000 - 40,000'
        else:
        	number = 'more than 40,000'
        return number

    def make_closest_agency_table(self):
        '''
        Make a table which shows statstical data according to closest agencies.

        Output:
            closest_agency_table (data frame): the table which shows data according to closest agencies.
        '''
        append_prop_df = collect_info.append_column_closet_agency(self.agencies_df, 
                                                                  self.properties_df)
        prop_groupby = append_prop_df.groupby('closest agency')
        processing = {'objectid': len,'total_assessment': np.mean, 
                      'taxable_assessment': np.mean,
                      'total_due': np.mean, 'most_recent_payment_date': np.min}
        closest_agency_table = prop_groupby.agg(processing)
        closest_agency_table = closest_agency_table.ix[:,['objectid', 'total_assessment',
                                                          'taxable_assessment',
                                                          'total_due', 'most_recent_payment_date']]
        rename = {'taxable_assessment': 'taxable_assessment_mean', 
                  'total_due': 'total_due_mean',
                  'total_assessment': 'total_assessment_mean',
                  'objectid': 'number_of_properties',
                  'most_recent_payment_date': 'oldest_most_recent_payment_date'}
        closest_agency_table = closest_agency_table.rename(columns=rename)
        return closest_agency_table
