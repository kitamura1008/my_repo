'''
Linking restaurant records in Zagat and Fodor's list using restraurant
names, cities, and street addresses.

Takayuki Kitamura

'''
import csv
import jellyfish
import pandas as pd

import util

def find_matches(output_filename, mu, lambda_, block_on_city=False):
    '''
    Put it all together: read the data and apply the record linkage
    algorithm to classify the potential matches.

    Inputs:
      output_filename (string): the name of the output file,
      mu (float) : the maximum false positive rate,
      lambda_ (float): the maximum false negative rate,
      block_on_city (boolean): indicates whether to block on the city or not.
    '''
    zagat_filename = "data/zagat.csv"
    fodors_filename = "data/fodors.csv"
    known_links_filename = "data/known_links.csv"
    unmatch_pairs_filename = "data/unmatch_pairs.csv"
    zagat_df = pd.read_csv(zagat_filename, index_col=['index'], dtype=str)
    fodors_df = pd.read_csv(fodors_filename, index_col=['index'], dtype=str)
    known_links_df = pd.read_csv(known_links_filename)
    unmatch_pairs_df = pd.read_csv(unmatch_pairs_filename)

    simil_tpl_dic, same_city_dic = map_simil_tpl(zagat_df,
                                                 fodors_df, block_on_city)
    match_pro_dic = map_pro(known_links_df, simil_tpl_dic)
    unmatch_pro_dic = map_pro(unmatch_pairs_df, simil_tpl_dic)
    sort_pro_tpl_lst = get_pro_tpl_lst(match_pro_dic, unmatch_pro_dic)
    label_dic = map_label(sort_pro_tpl_lst, mu, lambda_)

    if block_on_city:
        simil_tpl_dic = same_city_dic
    label_lst = []
    for pair, simil_tpl in simil_tpl_dic.items():
        zagat_index = pair[0]
        fodors_index = pair[1]
        if simil_tpl in label_dic:
            label = label_dic[simil_tpl]
        else:
            label = 'possible match'
        label_lst.append([zagat_index, fodors_index, label])

    with open(output_filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(label_lst)


### YOUR AUXILIARY FUNCTIONS HERE
def map_simil_tpl(df1, df2, block_on_city):
    '''
    Create a dictionary which maps pairs of restaurant indices to similarity
    tuples. If block_on_city is True, the function create another dictionary
    which has only exactly same cities pairs.

    Inputs:
      df1 (pandas dataframe): a dataset to compare
      df2 (pandas dataframe) : the other dataset to compare
      block_on_city (boolean): indicates whether to block on the city or not

    Outputs:
      simil_tpl_dic (dictionary): a dictionary which maps pairs of restaurant
                                  indices to similarity tuples
      same_city_dic (dictionary): a dictionary which maps pairs of restaurant
                                  indices that have the exactly same cities
                                  to similarity tuples
    '''
    simil_tpl_dic = {}
    same_city_dic = {}
    for row_1 in df1.itertuples():
        for row_2 in df2.itertuples():
            name_score = jellyfish.jaro_winkler(row_1[1], row_2[1])
            city_score = jellyfish.jaro_winkler(row_1[2], row_2[2])
            address_score = jellyfish.jaro_winkler(row_1[3], row_2[3])
            name_simil = util.get_jw_category(name_score)
            city_simil = util.get_jw_category(city_score)
            address_simil = util.get_jw_category(address_score)
            simil_tpl_dic[(row_1[0], row_2[0])] = (name_simil, city_simil,
                                                   address_simil)
            if block_on_city:
                if city_score == 1.0:
                    same_city_dic[(row_1[0], row_2[0])] = (name_simil,
                                                           city_simil,
                                                           address_simil)
    return simil_tpl_dic, same_city_dic


def map_pro(df, simil_tpl_dic):
    '''
    Create a dictionary which maps similarity tuples to match or unmatch
    probabilities.

    Inputs:
      df (pandas dataframe): a known-links dataset or an unmatch dataset
      simil_tpl_dic (pandas dataframe) : the output of map_simil_tpl

    Outputs:
      pro_dic (dictionary): a dictionary which maps similarity tuples to
                            match or unmatch probabilities
    '''
    pro_dic = {}
    denominator = len(df)
    for row in df.itertuples():
        res_index_tpl = (row[1], row[2])
        if simil_tpl_dic[res_index_tpl] in pro_dic:
            pro_dic[simil_tpl_dic[res_index_tpl]] += 1 / denominator
        else:
            pro_dic[simil_tpl_dic[res_index_tpl]] = 1 / denominator
    return pro_dic


def get_pro_tpl_lst(match_pro_dic, unmatch_pro_dic):
    '''
    Create a list of tuples(similarity tuples, match probability,
    unmatch probability) and sort it.

    Inputs:
      match_pro_dic (dictionary): match probabilities dictionary
                                  created by map_pro
      unmatch_pro_dic (dictionary) : unmatch probabilities dictionary
                                     created by map_pro

    Outputs:
      sort_pro_tpl_lst (list): a sorted list of tuples
    '''
    pro_tpl_lst = []
    for match_key in match_pro_dic:
        if match_key in unmatch_pro_dic:
            pro_tpl = (match_key, match_pro_dic[match_key],
                       unmatch_pro_dic[match_key])
        else:
            pro_tpl = (match_key, match_pro_dic[match_key], 0.0)
        pro_tpl_lst.append(pro_tpl)
    for unmatch_key in unmatch_pro_dic:
        if unmatch_key not in match_pro_dic:
            pro_tpl = (unmatch_key, 0.0, unmatch_pro_dic[unmatch_key])
            pro_tpl_lst.append(pro_tpl)
    sort_pro_tpl_lst = util.sort_prob_tuples(pro_tpl_lst)
    return sort_pro_tpl_lst


def map_label(sort_pro_tpl_lst, mu, lambda_):
    '''
    Create a dictionary which maps similarity tuples to labels.

    Inputs:
      sort_pro_tpl_lst (list): the output of get_pro_tpl_lst
      mu (float) : the maximum false positive rate
      lambda_ (float): the maximum false negative rate

    Outputs:
      label_dic (dictionary): a dictionary which maps
                              similarity tuples to labels
    '''
    label_dic = {}
    sum_of_unmatch_pro = 0
    sum_of_match_pro = 0
    for i in reversed(sort_pro_tpl_lst):
        sum_of_match_pro += i[1]
        if sum_of_match_pro > lambda_:
            break
        label_dic[i[0]] = 'unmatch'
    for j in sort_pro_tpl_lst:
        sum_of_unmatch_pro += j[2]
        if sum_of_unmatch_pro > mu:
            break
        label_dic[j[0]] = 'match'

    if len(label_dic) != len(sort_pro_tpl_lst):
        for k in sort_pro_tpl_lst:
            if k[0] not in label_dic:
                label_dic[k[0]] = 'possible match'
            if len(label_dic) == len(sort_pro_tpl_lst):
                break
    return label_dic
