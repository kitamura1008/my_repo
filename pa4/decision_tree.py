'''
CAPP30122 W'20: Building decision trees

Tetsuo Fujino
Takayuki Kitamura
'''

import math
import sys
import pandas


def go(training_filename, testing_filename):
    '''
    Construct a decision tree using the training data and then apply
    it to the testing data.

    Inputs:
      training_filename (string): the name of the file with the
        training data
      testing_filename (string): the name of the file with the testing
        data

    Returns (list of strings or pandas series of strings): result of
      applying the decision tree to the testing data.
    '''
    train_df = pandas.read_csv(training_filename, dtype=object)
    test_df = pandas.read_csv(testing_filename, dtype=object)

    decision_tree = construct_decision_tree(train_df)

    df_columns = tuple(test_df.columns)
    rv = [decision_tree.predict(row, df_columns)
          for row in test_df.itertuples(index=False, name=None)]
    return rv


def construct_decision_tree(df):
    '''
    Construct a decision tree node.

    Inputs:
        df (pandas data frame): training dataset

    Returns (Node object): decision tree node
    '''
    label = decide_label(df)
    node = Node(label)

    # Base case 1
    if len(df.columns) == 1 or len(df.iloc[:, -1].unique()) == 1:
        return node

    max_gain_ratio, split_attribute = search_best_split(df)

    # Base case 2
    if max_gain_ratio == 0.0:
        return node

    # Recursive case
    node.set_split_attribute(split_attribute)
    children_dic = {}
    category_lst = df[split_attribute].unique()
    for category in category_lst:
        new_df = df[(df[split_attribute] == category)]
        new_df = new_df[new_df.columns[new_df.columns != split_attribute]]
        # Recursion to make children
        child_node = construct_decision_tree(new_df)
        children_dic[category] = child_node
    node.set_children(children_dic)
    return node


def decide_label(df):
    '''
    decide label of the node
    Inputs:
        df (pandas data frame)

    Returns (strings) : a label of a node
    '''
    value_counts = df.iloc[:, -1].value_counts()

    label0 = value_counts.index[0]
    label = label0

    if len(value_counts) != 1:
        label1 = value_counts.index[1]
        if value_counts[0] == value_counts[1]:
            label = min(label0, label1)

    return label


class Node():
    '''
    Class for representing a dicision tree node.
    '''
    def __init__(self, label):
        '''
        Construct a data structure to hold the node.
        Inputs:
            label(string): a label of the node.
        '''
        self.label = label
        self.split_attribute = None
        self.children = None

    def set_split_attribute(self, split_attribute):
        '''
        Set split attribute.
        '''
        setattr(self, 'split_attribute', split_attribute)

    def set_children(self, children_dic):
        '''
        Set children(dicitionary, key:split_attribute, value:child tree node).
        '''
        setattr(self, 'children', children_dic)

    def predict(self, row, df_columns):
        '''
        Apply a row in a test dataset and predict a result

        Inputs
            row (tuple): tuple of values in a row of test dataset
            df_columns (tuple): tuple of names of columns of test data frame

        Output: label predicted from dicision tree and row in test dataset
        '''
        if self.children is None:
            return self.label
        index = df_columns.index(self.split_attribute)
        key = row[index]
        child = self.children.get(key)
        if child is None:
            return self.label
        return child.predict(row, df_columns)


def search_best_split(df):
    '''
    Get the largest gain ratio and an attribute to split on.

    Inputs
        df (pandas dataframe)

    Outputs
        max_gain_ratio (float): the largest gain ration
        split_attribute (string): an attribute of a node to split on
    '''
    max_gain_ratio = 0.0
    split_attribute = None
    possible_attributes = list(df.columns[:-1])
    for attribute in possible_attributes:
        gini = calculate_gini(df)
        gain, split_info = calculate_gain_and_split_info(attribute, df, gini)
        gain_ratio = calculate_gain_ratio(gain, split_info)
        if gain_ratio >= max_gain_ratio:
            max_gain_ratio = gain_ratio
            split_attribute = attribute
    return max_gain_ratio, split_attribute


def calculate_gini(df):
    '''
    Calculate gini coefficient.

    Inputs
        df (pandas dataframe)

    Outputs
        gini (float): gini coefficient
    '''
    gini = 1
    total = len(df)
    value_counts = df.iloc[:, -1].value_counts()

    for i in range(len(value_counts.index)):
        p = value_counts[i] / total
        gini -= p ** 2
    return gini


def calculate_gain_and_split_info(attribute, df, gini):
    '''
    Calculate gain and split information.

    Inputs
        attribute (string): split attribute for this calculation
        df (pandas dataframe)
        gini (float): gini coefficient

    Outputs
        gain (float): increase in purity
        split_info (float): split information
    '''
    gini_set = df.groupby(attribute).apply(calculate_gini)
    weighted_gini_sum = 0
    split_info = 0
    total = len(df)
    for category in list(gini_set.index):
        w = (df[attribute] == category).sum() / total
        weighted_gini_sum += w * gini_set[category]
        split_info += w * math.log(w)
    gain = gini - weighted_gini_sum
    split_info = - split_info
    return gain, split_info


def calculate_gain_ratio(gain, split_info):
    '''
    Calculate gain ratio from gain and split information.

    Inputs
        gain (float): increase in purity
        split_info (float): split information

    Outputs
        gain_ration (float): gain ratio
    '''
    gain_ratio = 0.0
    if split_info != 0.0:
        gain_ratio = gain / split_info
    return gain_ratio


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 {} <training filename> <testing filename>".format(
            sys.argv[0]))
        sys.exit(1)

    for result in go(sys.argv[1], sys.argv[2]):
        print(result)
