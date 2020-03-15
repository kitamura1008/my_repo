import pandas as pd
import numpy as np
import collect_info
import matplotlib.pyplot as plt
from matplotlib import ticker 
import seaborn as sns
from collections import Counter
import datetime as dt

'''
This file contains 5 functions(3 for making figures and 2 for accessaries)
'''

def make_total_due_pie(path, properties_df):
    '''
    Make a pie chart of the total due and save it as png file.
    
    Input:
         props_df: props_df, which is cleand and appended the closest agency
    '''
    # map ranges to the total_due column of props_df
    range_lst = list(map(determine_range, props_df['total_due']))
    # count the numbers of ranges
    c = Counter(range_lst)
    counter_lst = c.most_common()

    # make total_due data frame
    total_due_df = pd.DataFrame(counter_lst)
    total_due_df.columns=['total_due_range', 'numbers']
    total_due_df = total_due_df.set_index('total_due_range')

    # make a pie chart which indicates percentages of total_due ranges
    sns.set()
    sns.set_palette("hls", 7)
    plt.pie(total_due_df['numbers'], counterclock=False, startangle=90,
            pctdistance=0.65, wedgeprops={'linewidth': 1, 'edgecolor':"white"},
            autopct=lambda p:'{:.1f}%'.format(p) if p>=3 else '')
    label = total_due_df.index    
    plt.legend(label,fancybox=True,bbox_to_anchor=(1.0,0.4), frameon=False)
    plt.rcParams['font.size'] = 14

    # set a title
    title = "{0:.1%} of delinquent residential properties owe {1}".\
            format(total_due_df.iloc[0][0]/sum(total_due_df['numbers']),
                    list(total_due_df.index)[0])
    plt.title(title, fontsize = 18)

    plt.savefig(path+'/total_due_pie.png', bbox_inches='tight')


def make_agency_bar_chart(path, closest_agency_table):
    '''
    Make a bar chart of the total due mean and the number of properties at each agency,
    and save it as png file.
    
    Input:
         closest_agency_table(data frame): the output of make_closest_agency_table, 
                                           which shows data according to closest agencies.
    Output:
         None. Create a bar chart, save it ans show it.
    '''
    # prepare data for a figure
    total_due_mean = closest_agency_table['total_due_mean']
    number_of_properties = closest_agency_table['number_of_properties']

    # make bar graph
    sns.set()
    fig = plt.figure(figsize=(13,5))
    ax1 = fig.add_subplot(1, 1, 1)

    x = np.array(closest_agency_table.index)
    x_posi = np.arange(len(x))    
    ax1.bar(x_posi, total_due_mean, width=0.4, color='r', 
    	    alpha=0.5, label='total due mean')

    ax2 = ax1.twinx()
    ax2.bar(x_posi + 0.4, number_of_properties, width=0.4,
    	    color='b', alpha=0.5,label='number of properties')

    ax1.set_xticks(x_posi + 0.2)
    ax1.set_xticklabels(x)
    ax1.grid(b=None)
    ax2.grid(b=None)
    # set a legend
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, frameon=False, fontsize=9)

    # set a title and labels
    ax1.set_title("Total due mean and the number of delinquent properties at each agency",
                   fontsize=16)
    ax1.set_ylabel("Total due mean($)")
    ax2.set_ylabel("The number of delinquent properties")

    plt.savefig(path+'/total_due_mean_and_number_of_properties.png', 
    	         bbox_inches='tight')


def make_hist_day_since_last_payment(path, properties_df):
    '''
    Make a histrgram of days since most last payment, and save it as png file.
    
    Input:
         props_df: props_df, which is cleand and appended the closest agency

    Output:
         None. create a histgram, save it ans show it.
    '''
	# convert str into datetime about most_recent_payment_date
    payment_date_df = list(map(lambda x: dt.datetime.strptime(x, '%Y-%m-%d'),
                                         props_df['most_recent_payment_date']))
    # convert datetime into day
    payment_date_df = list(map(lambda x: dt.datetime.date(x), payment_date_df))

    # create today
    today = dt.date.today() 

    # subtract most_recent_payment_date from today
    days_from_last_payment = list(map(lambda x: (today - x).days, payment_date_df))

    # make a histgram of days_from_last_payment
    sns.set()
    ax = sns.distplot(days_from_last_payment, kde=True, bins =500)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(180)) 
    ax.axes.set_xlim(0, 2000)

    # make a title
    ratio_within_a_year = len([i for i in days_from_last_payment if i <= 365]) \
                          / len(days_from_last_payment)
    title = "{0:.1%} of delinquent residential properties pays within a year".\
            format(ratio_within_a_year)

    # set a title and a label
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('days since most recent payment date')

    plt.savefig(path+'/bar_time_since_payment.png')


# Accessary functions below
def determine_range(number):
    '''
    Accessary function for make_total_due_pie.
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


def make_closest_agency_table(props_df):
    '''
    Accessary function for make_agency_bar_chart.
    Make a table which shows statstical data according to closest agencies.

    Input:
         props_df: props_df, which is cleand and appended the closest agency
    Output:
        closest_agency_table (data frame): the table which shows data according to closest agencies.
    '''
    # set a processing
    processing = {'objectid': len,'total_assessment': np.mean, 
                  'taxable_assessment': np.mean,
                  'total_due': np.mean, 'most_recent_payment_date': np.min}
    
    # do groupby and apply the processing
    prop_groupby = props_df.groupby('closest agency')
    closest_agency_table = prop_groupby.agg(processing)
    closest_agency_table = closest_agency_table.ix[:,['objectid', 'total_assessment',
                                                      'taxable_assessment',
                                                      'total_due', 'most_recent_payment_date']]
    
    # rename columns' name
    rename = {'taxable_assessment': 'taxable_assessment_mean', 
              'total_due': 'total_due_mean',
              'total_assessment': 'total_assessment_mean',
              'objectid': 'number_of_properties',
              'most_recent_payment_date': 'oldest_most_recent_payment_date'}
    closest_agency_table = closest_agency_table.rename(columns=rename)
    
    return closest_agency_table
