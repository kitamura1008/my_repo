import pandas as pd
import numpy as np
import collect_info
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter


def make_total_due_pie(properties_df):
    '''
    Make a histrgram of the total due and save it as png file.
    
    input:
         agencies_df: agencies_df, which is appended the closest agency
    '''
    # map ranges to the total_due column of properties_df
    range_lst = list(map(determine_range, properties_df['total_due']))
    # count the numbers of ranges
    c = Counter(range_lst)
    counter_lst = c.most_common()

    # make total_due data frame
    total_due_df = pd.DataFrame(counter_lst)
    total_due_df.columns=['total_due_range', 'numbers']
    total_due_df = total_due_df.set_index('total_due_range')

    # make a pie chart which indicates percentages of total_due ranges
    label = total_due_df.index
    title = "{0:.1%} of delinquent residential properties owe {1}".\
            format(total_due_df.iloc[0][0]/sum(total_due_df['numbers']),
                    list(total_due_df.index)[0])
    sns.set_palette("hls", 7)
    plt.pie(total_due_df['numbers'], counterclock=False, startangle=90,
            pctdistance=0.65, wedgeprops={'linewidth': 1, 'edgecolor':"white"},
            autopct=lambda p:'{:.1f}%'.format(p) if p>=3 else '')
    plt.legend(label,fancybox=True,bbox_to_anchor=(1.0,0.4), frameon=False)
    plt.rcParams['font.size'] = 14
    plt.title(title, fontsize = 18)
    plt.savefig('total_due_pie.png', bbox_inches='tight')
    plt.show()


def determine_range(number):
    '''
    Accessary function for make_total_due_hist.
    Determine the range of total due at each property.  

    Input:
        number (int): it represents total due of each property

    Output:
        number (str): it represents the range of the total due
        '''
    if number < 5000:
        number = 'less than $5,000'
    elif number >= 5000 and number < 10000:
        number= '$5,000 - $10,000'
    elif number >= 10000 and number < 15000:
        number = '$10,000 - $15,000'
    elif number >= 15000 and number < 20000:
        number = '$15,000 - $20,000'
    elif number >= 20000 and number < 30000:
        number = '$20,000 - $30,000'
    elif number >= 30000 and number < 40000:
        number = '$30,000 - $40,000'
    else:
    	number = 'more than $40,000'
    return number


def make_closest_agency_table(properties_df):
    '''
    Make a table which shows statstical data according to closest agencies.

    input:
         agencies_df: agencies_df, which is appended the closest agency
    Output:
        closest_agency_table (data frame): the table which shows data according to closest agencies.
    '''
    prop_groupby = properties_df.groupby('closest agency')
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


def make_agency_bar_chart(closest_agency_table):
    x = np.array(closest_agency_table.index)
    x_posi = np.arange(len(x))

    total_due_mean = closest_agency_table['total_due_mean']
    number_of_properties = closest_agency_table['number_of_properties']

    fig = plt.figure(figsize=(13,5))
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.bar(x_posi, total_due_mean, width=0.4, color='r', alpha=0.5, label='total due mean')

    ax2 = ax1.twinx()
    ax2.bar(x_posi + 0.4, number_of_properties, width=0.4, color='b', alpha=0.5,label='number of properties')

    ax1.set_xticks(x_posi + 0.2)
    ax1.set_xticklabels(x)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, frameon=False, fontsize=9)

    ax1.set_title("Total due mean and the number of delinquent properties at each agency", fontsize=16)
    ax1.set_ylabel("Total due mean($)")
    ax2.set_ylabel("The number of delinquent properties")

    plt.savefig('total_due_mean_and_number_of_properties.png', bbox_inches='tight')
    plt.show()
    