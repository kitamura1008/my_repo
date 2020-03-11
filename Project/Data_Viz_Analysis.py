#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collect_info import data_cleaning, create_dfs

agencies, tax = create_dfs()


# In[4]:


tax.head()


# In[5]:


tax.describe()


# In[21]:


sns.distplot(tax['num_years_owed'], kde=True, bins=10)


# In[22]:


sns.distplot(tax['most_recent_bankrupt_year'], kde=True, bins=30);


# In[23]:


sns.relplot(x="num_years_owed", y="total_due", data=tax);


# In[26]:


sns.catplot(x="num_years_owed", y="total_due", kind="point", data=tax);


# In[31]:


sns.jointplot("num_years_owed","total_due", data=tax, kind='reg')


# In[ ]:




