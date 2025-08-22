# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 16:03:30 2022

@author: Thompson.Knuth
"""

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

pd.set_option("max_colwidth", 200)
pd.set_option("display.precision", 1)
pd.set_option("display.max_columns", 500)
pd.set_option("display.float_format", "{:,.10}".format)

#%%

headers = {'User-Agent': 
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

def flat_cols(cols, rev_order=False):
    if rev_order:
        cols_new = ['_'.join(col[::-1]) if col[1] else col[0] for col in cols]

    else:
        cols_new = ['_'.join(col) if col[1] else col[0] for col in cols]

    return cols_new

#%%

total_defense = []
    
for i in range(1940,2025):
    page = "https://www.pro-football-reference.com/years/" + str(i) + "/defense.htm"
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    column_headers = pageSoup.find_all('tr')[1]
    column_headers = [j.getText() for j in column_headers.find_all('th')]
    
    rows = pageSoup.find_all('tr')[1:]
    
    def_stats = []
    for j in range(len(rows)):
        rowtext = [col.get_text() for col in rows[j].find_all('td')]
        if rowtext == []:
            index = j
        def_stats.append(rowtext)
    a_def_stats = def_stats[0:index]
    a_df = pd.DataFrame(a_def_stats, columns=[column_headers[1:]])
    
    a_df.columns = [str(col).strip('(').strip(')').strip("'").strip(',').strip("'") for col in a_df.columns]
    
    cols = list(a_df.columns)
    first_yds = list(a_df.columns).index('Yds')
    cols[first_yds] = 'Int Yds'
    try:
        second_yds = list(a_df.columns).index('Yds', first_yds + 1)
        cols[second_yds] = 'Fmb Yds'
        a_df.columns = cols
        
    except:
        a_df.columns = cols
    
    a_df['Year']=i
    total_defense.append(a_df)
    print(f"{i} defensive stats added.")
    time.sleep(5)
    
defense_df = pd.concat(total_defense,ignore_index=True)
defense_df = defense_df[~defense_df['Player'].isnull()].copy()

#%%

a_defense_df = defense_df.copy()

for i in a_defense_df.columns:
    a_defense_df[i] = np.where(a_defense_df[i]=='',np.nan,a_defense_df[i])

float_list = ['G','GS','Int','Int Yds','IntTD','Lng','FRTD','Sk','Sfty','Fmb','FR','Fmb Yds','Comb','FF','Solo','Ast','PD','TFL','QBHits']

for i in float_list:
    a_defense_df[i] = a_defense_df[i].astype(float)
    
a_defense_df = a_defense_df[['Player', 'Age', 'Team', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD',
       'Lng', 'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'Comb', 'Solo',
       'Ast', 'TFL', 'QBHits', 'Sfty', 'Awards', 'Year']].copy()

a_defense_df.rename(columns={'Comb':'combo_tkl','Solo':'solo_tkl','Ast':'ast_tkl',
                            'TFL':'tfl','QBHits':'qb_hits','Sfty':'safety','Team':'Tm'},inplace=True)

#%%
# Average set in 2000s for players who appeared in at least 5 games

a_defense_df['G'].mean()

defense_sub = a_defense_df.loc[a_defense_df['G']>=12].copy()

a_defense_sub = defense_sub.loc[(defense_sub['Year']>=2000) & (defense_sub['Year']<=2010)].copy()

for i in a_defense_sub.columns:
    a_defense_sub[i] = np.where(a_defense_sub[i].isna(),0,a_defense_sub[i])

#%%
# a

a_defense_sub['tckl_pg'] = a_defense_sub['combo_tkl']/a_defense_sub['G']

a_defense_sub['tckl_pg'].mean()

x = 1/(a_defense_sub['tckl_pg'].mean()-1)

a_defense_sub['a'] = (a_defense_sub['tckl_pg']-1)*x

a_defense_sub['a'].mean()

#%%
# b

a_defense_sub['ff_pg'] = a_defense_sub['FF']/a_defense_sub['G']

a_defense_sub['ff_pg'].mean()

y = 1/a_defense_sub['ff_pg'].mean()

a_defense_sub['b'] = a_defense_sub['ff_pg']*y

a_defense_sub['b'].mean()

#%%
# c
a_defense_sub['int_pd'] = a_defense_sub['Int']+a_defense_sub['PD']

a_defense_sub['int_pd_pg'] = a_defense_sub['int_pd']/a_defense_sub['G']

a_defense_sub['int_pd_pg'].mean()

z = 1/a_defense_sub['int_pd_pg'].mean()

a_defense_sub['c'] = a_defense_sub['int_pd_pg']*z

a_defense_sub['c'].mean()

#%%
# d

a_defense_sub['tfl_sk'] = a_defense_sub['tfl']+a_defense_sub['Sk']

a_defense_sub['tfl_sk_pg'] = a_defense_sub['tfl_sk']/a_defense_sub['G']

a_defense_sub['tfl_sk_pg'].mean()

v = 1/(a_defense_sub['tfl_sk_pg'].mean() - 0.18)

a_defense_sub['d'] = (a_defense_sub['tfl_sk_pg']-0.18)*v

a_defense_sub['d'].mean()

#%%
# Sub calculation of rating
calc_list = ['a','b','c','d']

for i in calc_list:
    a_defense_sub[i]=np.where(a_defense_sub[i]>2.375,2.375,a_defense_sub[i])
    a_defense_sub[i]=np.where(a_defense_sub[i]<0,0,a_defense_sub[i])

q = (a_defense_sub['a'].mean()+a_defense_sub['b'].mean()+a_defense_sub['c'].mean()+a_defense_sub['d'].mean())/0.667

a_defense_sub['rating_adj'] = ((a_defense_sub['a']+a_defense_sub['b']+a_defense_sub['c']+a_defense_sub['d'])/q)*100

a_defense_sub['rating_adj'].mean()

# Total calculation: input stats
a_defense_df['tckl_pg'] = a_defense_df['combo_tkl']/a_defense_df['G']

a_defense_df['ff_pg'] = a_defense_df['FF']/a_defense_df['G']

a_defense_df['int_pd'] = a_defense_df['Int']+a_defense_df['PD']

a_defense_df['int_pd_pg'] = a_defense_df['int_pd']/a_defense_df['G']

a_defense_df['tfl_sk'] = a_defense_df['tfl']+a_defense_df['Sk']

a_defense_df['tfl_sk_pg'] = a_defense_df['tfl_sk']/a_defense_df['G']

#Coefficient calculations
a_defense_df['a'] = (a_defense_df['tckl_pg']-1)*x

a_defense_df['b'] = a_defense_df['ff_pg']*y

a_defense_df['c'] = a_defense_df['int_pd_pg']*z

a_defense_df['d'] = (a_defense_df['tfl_sk_pg']-0.1)*v

for i in calc_list:
    a_defense_df[i]=np.where(a_defense_df[i]>2.375,2.375,a_defense_df[i])
    a_defense_df[i]=np.where(a_defense_df[i]<0,0,a_defense_df[i])

#Rating
a_defense_df['Rate'] = ((a_defense_df['a']+a_defense_df['b']+a_defense_df['c']+a_defense_df['d'])/q)*100

a_defense_df['Rate'].mean()

#%%
# Categorization vars

a_defense_df['pos_cat'] = a_defense_df['Pos'].astype(str).apply(lambda g: "DL" 
                                                         if any(y in g.lower()
                                                         for y in ['rdt','rde','lde','ldt','re','le','de','dt','rdg','mg','ldg','dl','nt'])
                                                         else "LB" if any(y in g.lower()
                                                         for y in ["rolb","llb",'rilb','mlb','llb','rlb','lilb','lolb','lb'])   
                                                         else "DB" if any (j in g.lower()
                                                         for j in ['rcb','db','fs','ss','lcb','rdh','ldh','s','cb'])
                                                         else np.NaN)
missing_sub = a_defense_df.loc[a_defense_df['pos_cat'].isna()].copy()

zzz = missing_sub['Pos'].astype(str).str.lower().unique()

#%%
# DLine

dline_sub = a_defense_df.loc[a_defense_df['pos_cat']=='DL'].copy()

dline_sub_1 = dline_sub[['Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD', 'Lng',
       'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'combo_tkl', 'solo_tkl',
       'ast_tkl', 'tfl', 'qb_hits', 'safety', 'Year']].copy()

a_dline_sub = dline_sub_1.loc[(dline_sub['G']>=10) & (dline_sub['Year']>=2000) & (dline_sub['Year']<=2010)].copy()

for i in a_dline_sub.columns:
    a_dline_sub[i] = np.where(a_dline_sub[i].isna(),0,a_dline_sub[i])

# a
a_dline_sub['tfl_sk'] = a_dline_sub['tfl']+a_dline_sub['Sk']

a_dline_sub['tfl_sk_pg'] = a_dline_sub['tfl_sk']/a_dline_sub['G']

a_dline_sub['tfl_sk_pg'].mean()

a = 1/(a_dline_sub['tfl_sk_pg'].mean()-0.08)

a_dline_sub['a'] = (a_dline_sub['tfl_sk_pg']-0.08)*a

a_dline_sub['a'].mean()

a_test = a_dline_sub.loc[a_dline_sub['a']>2.375].copy()

# b

a_dline_sub['ff_pg'] = a_dline_sub['FF']/a_dline_sub['G']

a_dline_sub['ff_pg'].mean()

b = 1/(a_dline_sub['ff_pg'].mean()+0.02)

a_dline_sub['b'] = (a_dline_sub['ff_pg']+0.02)*b

a_dline_sub['b'].mean()

b_test = a_dline_sub.loc[a_dline_sub['b']>2.375].copy()

# c

a_dline_sub['tkl_pg'] = a_dline_sub['combo_tkl']/a_dline_sub['G']

a_dline_sub['tkl_pg'].mean()

c = 1/(a_dline_sub['tkl_pg'].mean()-1.2)

a_dline_sub['c'] = (a_dline_sub['tkl_pg']-1.2)*c

a_dline_sub['c'].mean()

c_test = a_dline_sub.loc[a_dline_sub['c']>2.375].copy()

# d

a_dline_sub['pd_pg'] = a_dline_sub['PD']/a_dline_sub['G']

a_dline_sub['pd_pg'].mean()

d = 1/(a_dline_sub['pd_pg'].mean())

a_dline_sub['d'] = (a_dline_sub['pd_pg'])*d

a_dline_sub['d'].mean()

d_test = a_dline_sub.loc[a_dline_sub['d']>2.375].copy()

# Subset rating calc

for i in calc_list:
    a_dline_sub[i]=np.where(a_dline_sub[i]>2.375,2.375,a_dline_sub[i])
    a_dline_sub[i]=np.where(a_dline_sub[i]<0,0,a_dline_sub[i])

q = (a_dline_sub['a'].mean()+a_dline_sub['b'].mean()+a_dline_sub['c'].mean()+a_dline_sub['d'].mean())/0.667

a_dline_sub['rating_adj'] = ((a_dline_sub['a']+a_dline_sub['b']+a_dline_sub['c']+a_dline_sub['d'])/q)*100

a_dline_sub['rating_adj'].mean()

# Overall DLine calculation
for i in ['Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD', 'Lng',
       'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'combo_tkl', 'solo_tkl',
       'ast_tkl', 'tfl', 'qb_hits', 'safety', 'Year']:
    dline_sub[i] = np.where(dline_sub[i].isna(),0,dline_sub[i])

dline_sub['tfl_sk'] = dline_sub['tfl']+dline_sub['Sk']

dline_sub['tfl_sk_pg'] = dline_sub['tfl_sk']/dline_sub['G']

dline_sub['ff_pg'] = dline_sub['FF']/dline_sub['G']

dline_sub['tkl_pg'] = dline_sub['combo_tkl']/dline_sub['G']

dline_sub['pd_pg'] = dline_sub['PD']/dline_sub['G']

dline_sub['a'] = (dline_sub['tfl_sk_pg']-0.08)*a
dline_sub['b'] = (dline_sub['ff_pg']+0.02)*b
dline_sub['c'] = (dline_sub['tkl_pg']-1.2)*c
dline_sub['d'] = (dline_sub['pd_pg'])*d

for i in calc_list:
    dline_sub[i]=np.where(dline_sub[i]>2.375,2.375,dline_sub[i])
    dline_sub[i]=np.where(dline_sub[i]<0,0,dline_sub[i])

dline_sub['rating_adj'] = ((dline_sub['a']+dline_sub['b']+dline_sub['c']+dline_sub['d'])/q)*100

test = dline_sub.loc[(dline_sub['G']>=10) & (dline_sub['Year']>=2010) & (dline_sub['Year']<=2020)].copy()

test['rating_adj'].mean()

#valid from 1999 onwards due to inclusion of tfl

b_dline_sub = dline_sub.loc[dline_sub['Year']>=1999].copy()

c_dline_sub = b_dline_sub.loc[b_dline_sub['G']>=10].copy()

c_dline_sub['rating_adj'].mean()

dline_final = b_dline_sub[['Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD', 'Lng',
       'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'combo_tkl', 'solo_tkl',
       'ast_tkl', 'tfl', 'qb_hits', 'safety', 'Year','pos_cat','a', 'b', 'c', 'd','rating_adj']].copy()


#%%
# Linebacker

lb_sub = a_defense_df.loc[a_defense_df['pos_cat']=='LB'].copy()

lb_sub_1 = lb_sub[['Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD', 'Lng',
       'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'combo_tkl', 'solo_tkl',
       'ast_tkl', 'tfl', 'qb_hits', 'safety', 'Year']].copy()

a_lb_sub = lb_sub_1.loc[(lb_sub_1['G']>=10) & (lb_sub_1['Year']>=2000) & (lb_sub_1['Year']<=2010)].copy()

for i in a_lb_sub.columns:
    a_lb_sub[i] = np.where(a_lb_sub[i].isna(),0,a_lb_sub[i])
    
# a

a_lb_sub['tfl_sk'] = a_lb_sub['tfl']+a_lb_sub['Sk']

a_lb_sub['tfl_sk_pg'] = a_lb_sub['tfl_sk']/a_lb_sub['G']

a_lb_sub['tfl_sk_pg'].mean()

a = 1/(a_lb_sub['tfl_sk_pg'].mean())

a_lb_sub['a'] = (a_lb_sub['tfl_sk_pg'])*a

a_lb_sub['a'].mean()

a_test = a_lb_sub.loc[a_lb_sub['a']>2.375]

# b

a_lb_sub['turnovers'] = a_lb_sub['Int']+a_lb_sub['FF']

a_lb_sub['to_pg'] = a_lb_sub['turnovers']/a_lb_sub['G']

a_lb_sub['to_pg'].mean()

b = 1/(a_lb_sub['to_pg'].mean()+0.015)

a_lb_sub['b'] = (a_lb_sub['to_pg']+0.015)*b

a_lb_sub['b'].mean()

b_test = a_lb_sub.loc[a_lb_sub['b']>2.375].copy()

# c

a_lb_sub['tkl_pg'] = a_lb_sub['combo_tkl']/a_lb_sub['G']

a_lb_sub['tkl_pg'].mean()

c = 1/(a_lb_sub['tkl_pg'].mean()-1.15)

a_lb_sub['c'] = (a_lb_sub['tkl_pg']-1.15)*c

a_lb_sub['c'].mean()

c_test = a_lb_sub.loc[a_lb_sub['c']>2.375].copy()

# d

a_lb_sub['pd_pg'] = a_lb_sub['PD']/a_lb_sub['G']

a_lb_sub['pd_pg'].mean()

d = 1/(a_lb_sub['pd_pg'].mean()+0.04)

a_lb_sub['d'] = (a_lb_sub['pd_pg']+0.04)*d

a_lb_sub['d'].mean()

d_test = a_lb_sub.loc[a_lb_sub['d']>2.375].copy()

# Subset rating calc

for i in calc_list:
    a_lb_sub[i]=np.where(a_lb_sub[i]>2.375,2.375,a_lb_sub[i])
    a_lb_sub[i]=np.where(a_lb_sub[i]<0,0,a_lb_sub[i])

q = (a_lb_sub['a'].mean()+a_lb_sub['b'].mean()+a_lb_sub['c'].mean()+a_lb_sub['d'].mean())/0.667

a_lb_sub['rating_adj'] = ((a_lb_sub['a']+a_lb_sub['b']+a_lb_sub['c']+a_lb_sub['d'])/q)*100

a_lb_sub['rating_adj'].mean()

#Overall calc

for i in ['Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD', 'Lng',
       'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'combo_tkl', 'solo_tkl',
       'ast_tkl', 'tfl', 'qb_hits', 'safety', 'Year']:
    lb_sub[i] = np.where(lb_sub[i].isna(),0,lb_sub[i])

lb_sub['tfl_sk'] = lb_sub['tfl']+lb_sub['Sk']

lb_sub['tfl_sk_pg'] = lb_sub['tfl_sk']/lb_sub['G']

lb_sub['turnovers'] = lb_sub['Int']+lb_sub['FF']

lb_sub['to_pg'] = lb_sub['turnovers']/lb_sub['G']

lb_sub['tkl_pg'] = lb_sub['combo_tkl']/lb_sub['G']

lb_sub['pd_pg'] = lb_sub['PD']/lb_sub['G']

lb_sub['a'] = (lb_sub['tfl_sk_pg'])*a
lb_sub['b'] = (lb_sub['to_pg']+0.015)*b
lb_sub['c'] = (lb_sub['tkl_pg']-1.15)*c
lb_sub['d'] = (lb_sub['pd_pg']+0.04)*d

for i in calc_list:
    lb_sub[i]=np.where(lb_sub[i]>2.375,2.375,lb_sub[i])
    lb_sub[i]=np.where(lb_sub[i]<0,0,lb_sub[i])

lb_sub['rating_adj'] = ((lb_sub['a']+lb_sub['b']+lb_sub['c']+lb_sub['d'])/q)*100

test = lb_sub.loc[(lb_sub['G']>=10) & (lb_sub['Year']>=2010) & (lb_sub['Year']<=2020)].copy()

test['rating_adj'].mean()

#valid from 1999 onwards due to inclusion of tfl

b_lb_sub = lb_sub.loc[lb_sub['Year']>=1999].copy()

c_lb_sub = b_lb_sub.loc[b_lb_sub['G']>=10].copy()

c_lb_sub['rating_adj'].mean()

lb_final = b_lb_sub[['Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD', 'Lng',
       'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'combo_tkl', 'solo_tkl',
       'ast_tkl', 'tfl', 'qb_hits', 'safety', 'Year','pos_cat','a', 'b', 'c', 'd','rating_adj']].copy()


#%%
# Defensive backs

db_sub = a_defense_df.loc[a_defense_df['pos_cat']=='DB'].copy()

db_sub_1 = db_sub[['Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD', 'Lng',
       'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'combo_tkl', 'solo_tkl',
       'ast_tkl', 'tfl', 'qb_hits', 'safety', 'Year']].copy()

a_db_sub = db_sub_1.loc[(db_sub_1['G']>=10) & (db_sub_1['Year']>=2000) & (db_sub_1['Year']<=2010)].copy()

for i in a_db_sub.columns:
    a_db_sub[i] = np.where(a_db_sub[i].isna(),0,a_db_sub[i])
    
# a

a_db_sub['int_pg'] = a_db_sub['Int']/a_db_sub['G']

a_db_sub['int_pg'].mean()

a = 1/(a_db_sub['int_pg'].mean()+0.06)

a_db_sub['a'] = (a_db_sub['int_pg']+0.06)*a

a_db_sub['a'].mean()

a_test = a_db_sub.loc[a_db_sub['a']>2.375].copy()

# b

a_db_sub['pd_pg'] = a_db_sub['PD']/a_db_sub['G']

a_db_sub['pd_pg'].mean()

b = 1/(a_db_sub['pd_pg'].mean()+0.04)

a_db_sub['b'] = (a_db_sub['pd_pg']+0.04)*b

a_db_sub['b'].mean()

b_test = a_db_sub.loc[a_db_sub['b']>2.375].copy()

# c

a_db_sub['tkl_pg'] = a_db_sub['combo_tkl']/a_db_sub['G']

a_db_sub['tkl_pg'].mean()

c = 1/(a_db_sub['tkl_pg'].mean()-1.2)

a_db_sub['c'] = (a_db_sub['tkl_pg']-1.2)*c

a_db_sub['c'].mean()

c_test = a_db_sub.loc[a_db_sub['c']>2.375].copy()

# sub rating calc

for i in calc_list[:-1]:
    a_db_sub[i]=np.where(a_db_sub[i]>2.375,2.375,a_db_sub[i])
    a_db_sub[i]=np.where(a_db_sub[i]<0,0,a_db_sub[i])

q = (a_db_sub['a'].mean()+a_db_sub['b'].mean()+a_db_sub['c'].mean())/0.667

a_db_sub['rating_adj'] = ((a_db_sub['a']+a_db_sub['b']+a_db_sub['c'])/q)*100

a_db_sub['rating_adj'].mean()

#Overall rating calc

for i in ['Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD', 'Lng',
       'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'combo_tkl', 'solo_tkl',
       'ast_tkl', 'tfl', 'qb_hits', 'safety', 'Year']:
    db_sub[i] = np.where(db_sub[i].isna(),0,db_sub[i])
    
db_sub['int_pg'] = db_sub['Int']/db_sub['G']

db_sub['pd_pg'] = db_sub['PD']/db_sub['G']

db_sub['tkl_pg'] = db_sub['combo_tkl']/db_sub['G']

db_sub['a'] = (db_sub['int_pg']+0.05)*a
db_sub['b'] = (db_sub['pd_pg']+0.03)*b
db_sub['c'] = (db_sub['tkl_pg']-1.3)*c

for i in calc_list:
    db_sub[i]=np.where(db_sub[i]>2.375,2.375,db_sub[i])
    db_sub[i]=np.where(db_sub[i]<0,0,db_sub[i])

db_sub['rating_adj'] = ((db_sub['a']+db_sub['b']+db_sub['c']+db_sub['d'])/q)*100

test = db_sub.loc[(db_sub['G']>=10) & (db_sub['Year']>=2010) & (db_sub['Year']<=2020)].copy()

test['rating_adj'].mean()

#valid from 1999 onwards due to inclusion of tfl

b_db_sub = db_sub.loc[db_sub['Year']>=1999].copy()

c_db_sub = b_db_sub.loc[b_db_sub['G']>=10].copy()

c_db_sub['rating_adj'].mean()

db_final = b_db_sub[['Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Int', 'Int Yds', 'IntTD', 'Lng',
       'PD', 'FF', 'Fmb', 'FR', 'Fmb Yds', 'FRTD', 'Sk', 'combo_tkl', 'solo_tkl',
       'ast_tkl', 'tfl', 'qb_hits', 'safety', 'Year','pos_cat','a', 'b', 'c', 'd','rating_adj']].copy()

#%%
# Final defense DF of position specific ratings, adjusted to 2000s standard, nans set to zero for statistical categories
df_list = [dline_final,lb_final,db_final]

dline_final['df_id'] = 'DL'
lb_final['df_id'] = 'LB'
db_final['df_id'] = 'DB'

#%%
# Adjusting rating scale to 0 to 158.3
#Dline
dline_min = dline_final['rating_adj'].min()
dline_range = dline_final['rating_adj'].max()-dline_final['rating_adj'].min()

dline_final['rating_adj_1'] = (dline_final['rating_adj']-dline_min)*(158.3/dline_range)

# DB
db_min = db_final['rating_adj'].min()
db_range = db_final['rating_adj'].max()-db_final['rating_adj'].min()

db_final['rating_adj_1'] = (db_final['rating_adj']-db_min)*(158.3/db_range)

# LB
lb_min = lb_final['rating_adj'].min()
lb_range = lb_final['rating_adj'].max()-lb_final['rating_adj'].min()

lb_final['rating_adj_1'] = (lb_final['rating_adj']-lb_min)*(158.3/lb_range)

#%%

final_defense = pd.concat(df_list,ignore_index=True)

final_defense['pro_bowl'] = final_defense['Player'].astype(str).apply(lambda g: 1 
                                                         if "*" in g.lower()
                                                         else 0)

final_defense['first_all_pro'] = final_defense['Player'].astype(str).apply(lambda g: 1 
                                                         if "+" in g.lower()
                                                         else 0)

final_defense['Player'] = final_defense['Player'].astype(str).str.replace('*','').str.replace('+','')

a_final_defense = final_defense[['Player','Year','Tm','Age','Pos','G','GS','rating_adj_1','df_id','pro_bowl','first_all_pro']].copy()

perfect_defense = final_defense.loc[final_defense['rating_adj_1']==158.3]

# a_final_defense.to_csv(r'C:\Users\thompson.knuth\Desktop\Webscraping Practice\NFL\NFL Defensive Ratings Data Build (2000s) (TK).csv')
