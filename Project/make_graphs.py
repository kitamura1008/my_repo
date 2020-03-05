import pandas as pd
import collect_info
import matplotlib.pyplot as plt
from collections import Counter

class MakeGraph():
    def __init__(self):
        agencies_df, properties_df = collect_info.create_dfs()
        self.agencies_df, self.properties_df = \
        collect_info.data_cleaning(agencies_df, properties_df)

    def make_total_due_hist(self):
         
        fig = plt.figure()
        counter = list(map(self.total_due_counter, self.properties_df['total_due']))
        c = Counter(counter)
        counter_lst = c.most_common()
        first = counter_lst[0][0]
        first_percentage = counter_lst[0][1] / len(self.properties_df)
        second = counter_lst[1][0]
        second_percentage = counter_lst[1][1] / len(self.properties_df)
        title = "Total due: {:.2%} of properties belongs to {}dollars.\n \
                            {:.2%} of properties belongs to {}dollars".format(first_percentage, first, second_percentage, second) 


        plt.hist(self.properties_df["total_due"], range=(0, 50000), bins=20)
        plt.title(title)
        plt.xlabel('total_due($)')
        plt.ylabel('frequency')
        plt.show()

        fig.savefig("total due histgram.png")

    def total_due_counter(self, number):
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