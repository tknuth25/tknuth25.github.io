# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:48:03 2022

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
#Quarterback data scrape

url = 'https://www.pro-football-reference.com/years/2019/passing.htm'

headers = {'User-Agent': 
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

total_data = []
    
for i in range(1932,2025):
    page = "https://www.pro-football-reference.com/years/" + str(i) + "/passing.htm"
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    column_headers = pageSoup.find_all('tr')[0]
    column_headers = [j.getText() for j in column_headers.find_all('th')]
    
    rows = pageSoup.find_all('tr')[1:]
    qb_stats = []
    for j in range(len(rows)):
        rowtext = [col.get_text() for col in rows[j].find_all('td')]
        if rowtext == []:
            index = j
        if i==1932:
            index = len(rows)
        qb_stats.append(rowtext)
    a_qb_stats = qb_stats[0:index]
    data = pd.DataFrame(a_qb_stats, columns=[column_headers[1:]])
    data['Year']=i
    total_data.append(data)
    print(f"{i} passing stats added.")
    time.sleep(5)

#%%
# formatting qb data

total_data1 = total_data.copy()

for i in range(len(total_data1)):
    if i <= 61:
        total_data1[i]['1D'] = np.nan
        total_data1[i]['QBR'] = np.nan
        
    if 61 < i <= 73:
        total_data1[i]['QBR'] = np.nan
        
    total_data1[i].columns = [str(col).strip('(').strip(')').strip("'").strip(',').strip("'") for col in total_data1[i].columns]
    
    # rush and pass yard differentiation
    if i>15:
        cols = list(total_data1[i].columns)
        first_yds = list(total_data1[i].columns).index('Yds')
        second_yds = list(total_data1[i].columns).index('Yds', first_yds + 1)
    
        cols[first_yds] = 'Pass Yds'
        cols[second_yds] = 'Rush Yds'
        total_data1[i].columns = cols
    if i<=15:
        cols = list(total_data1[i].columns)
        first_yds = list(total_data1[i].columns).index('Yds')
    
        cols[first_yds] = 'Pass Yds'
        total_data1[i].columns = cols
    
    
qb_df = pd.concat(total_data1,ignore_index=True)
qb_df = qb_df[~qb_df['Player'].isnull()].copy()

#%%
a_qb_df = qb_df.copy()

for i in a_qb_df.columns:
    a_qb_df[i] = np.where(a_qb_df[i]=='',np.nan,a_qb_df[i])

float_list = ['Age','G','GS','Cmp','Att','Cmp%','Pass Yds','TD','TD%','Int','Int%','1D','Lng',
              'Y/A','AY/A','Y/C','Y/G','QBR','Rate','Sk','Rush Yds','Sk%','NY/A','ANY/A','4QC','GWD',
              'Year','1D','QBR']

for i in float_list:
    a_qb_df[i] = a_qb_df[i].astype(float)
    
a_qb_df.columns = ['Player', 'Age', 'Tm', 'Pos', 'G', 'GS', 'Cmp', 'Att', 'Cmp%',
       'Pass Yds', 'TD', 'TD%', 'Int', 'Int%', 'Lng', 'Y/A', 'AY/A', 'Y/C',
       'Y/G', 'Rate', '4QC', 'GWD', 'Awards', 'Year', '1D', 'QBR', 'Yds',
       'Rush Yds', 'QBrec', 'Sk', 'Sk%', 'NY/A', 'ANY/A', 'Succ%']
    
#%%
# Passer Rating: adjusted to place mean in 2000s

qb_sub = a_qb_df.loc[(a_qb_df['Year']>=2000) & (a_qb_df['Year']<=2010)].copy()

qb_sub['Att'].mean()

a_qb_sub = qb_sub.loc[qb_sub['Att']>=50].copy()

#%%
# a

a_qb_sub['cmp_att'] = a_qb_sub['Cmp']/a_qb_sub['Att']

a_qb_sub['cmp_att'].mean()

x = 1/(a_qb_sub['cmp_att'].mean()-0.3)

a_qb_sub['a'] = (a_qb_sub['cmp_att']-0.3)*x

a_qb_sub['a'].mean()

a_test = a_qb_sub.loc[a_qb_sub['a']>2.375]

#%%
# b

a_qb_sub['yds_att'] = a_qb_sub['Pass Yds']/a_qb_sub['Att']

a_qb_sub['yds_att'].mean()

y = 1/(a_qb_sub['yds_att'].mean()-3)

a_qb_sub['b'] = (a_qb_sub['yds_att']-3)*y

a_qb_sub['b'].mean()

b_test = a_qb_sub.loc[a_qb_sub['b']>2.375]

#%%
# c

a_qb_sub['td_att'] = a_qb_sub['TD']/a_qb_sub['Att']

a_qb_sub['td_att'].mean()

z = 1/a_qb_sub['td_att'].mean()

a_qb_sub['c'] = a_qb_sub['td_att']*z

a_qb_sub['c'].mean()

c_test = a_qb_sub.loc[a_qb_sub['c']>2.375]

#%%
# d

a_qb_sub['int_att'] = a_qb_sub['Int']/a_qb_sub['Att']

a_qb_sub['int_att'].mean()

u = 1.375/a_qb_sub['int_att'].mean()

a_qb_sub['d'] = 2.375 - (a_qb_sub['int_att'])*u

a_qb_sub['d'].mean()

d_test = a_qb_sub.loc[a_qb_sub['d']>2.375]

#%%
calc_list = ['a','b','c','d']

for i in calc_list:
    a_qb_sub[i]=np.where(a_qb_sub[i]>2.375,2.375,a_qb_sub[i])
    a_qb_sub[i]=np.where(a_qb_sub[i]<0,0,a_qb_sub[i])

q = (a_qb_sub['a'].mean()+a_qb_sub['b'].mean()+a_qb_sub['c'].mean()+a_qb_sub['d'].mean())/0.667

a_qb_sub['rating_adj'] = ((a_qb_sub['a']+a_qb_sub['b']+a_qb_sub['c']+a_qb_sub['d'])/q)*100

a_qb_sub['rating_adj'].mean()

#%%
# QB rating calculation

a_qb_df['cmp_att'] = a_qb_df['Cmp']/a_qb_df['Att']

a_qb_df['yds_att'] = a_qb_df['Pass Yds']/a_qb_df['Att']

a_qb_df['td_att'] = a_qb_df['TD']/a_qb_df['Att']

a_qb_df['int_att'] = a_qb_df['Int']/a_qb_df['Att']

# Letter calcs

a_qb_df['a'] = (a_qb_df['cmp_att']-0.3)*x

a_qb_df['b'] = (a_qb_df['yds_att']-3)*y

a_qb_df['c'] = a_qb_df['td_att']*z

a_qb_df['d'] = 2.375 - (a_qb_df['int_att'])*u

# Rating Calc

for i in calc_list:
    a_qb_df[i]=np.where(a_qb_df[i]>2.375,2.375,a_qb_df[i])
    a_qb_df[i]=np.where(a_qb_df[i]<0,0,a_qb_df[i])

a_qb_df['rating_adj'] = (((a_qb_df['a']+a_qb_df['b']+a_qb_df['c']+a_qb_df['d'])/q)*100).round(1)

a_qb_df['rating_adj'].mean()

perfect_qb = a_qb_df.loc[a_qb_df['rating_adj']==158.3]

b_qb_df = a_qb_df.loc[a_qb_df['Att']>=50].copy()

#%%
#Diagnostics

#Attempts limitation:
b_qb_df = a_qb_df.loc[a_qb_df['Att']>=50].copy()

b_qb_df['rating_adj'].mean()

#Newest decade limit:
c_qb_df = b_qb_df.loc[(b_qb_df['Year']>=2010)& (b_qb_df['Year']<=2020)].copy()

c_qb_df['rating_adj'].mean()

#%%
# Running back data

def flat_cols(cols, rev_order=False):
    if rev_order:
        cols_new = ['_'.join(col[::-1]) if col[1] else col[0] for col in cols]

    else:
        cols_new = ['_'.join(col) if col[1] else col[0] for col in cols]

    return cols_new

total_rb = []
    
for i in range(1932,2025):
    page = "https://www.pro-football-reference.com/years/" + str(i) + "/rushing.htm"
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    column_headers = pageSoup.find_all('tr')[1]
    column_headers = [j.getText() for j in column_headers.find_all('th')]
    
    rows = pageSoup.find_all('tr')[1:]
    rb_stats = []
    for j in range(len(rows)):
        rowtext = [col.get_text() for col in rows[j].find_all('td')]
        if (rowtext == [])&(j!=0):
            index = j
        if (rowtext == [])&(j==0): 
            index = len(rows)
        rb_stats.append(rowtext)
    a_rb_stats = rb_stats[0:index]
    a_df = pd.DataFrame(a_rb_stats, columns=[column_headers[1:]])
    
    a_df.columns = [str(col).strip('(').strip(')').strip("'").strip(',').strip("'") for col in a_df.columns]
    
    a_df['Year']=i
    total_rb.append(a_df)
    print(f"{i} rushing stats added.")
    time.sleep(5)

rb_df = pd.concat(total_rb,ignore_index=True)
a_rb_df = rb_df.iloc[1:].copy()

#%%

a_rb_df.columns = ['Player','Age','Tm','Pos','G','GS','Att','Yds','TD','Lng','Y/A','Y/G','A/G','Awards','Year','Fmb','1D','Succ%']

for i in a_rb_df.columns:
    a_rb_df[i] = np.where(a_rb_df[i]=='',np.nan,a_rb_df[i])

float_list_1 = ['Age','G','GS','Att','Yds','TD','Lng',
              'Y/A','Y/G','Fmb','Year','1D']

for i in float_list_1:
    a_rb_df[i] = a_rb_df[i].astype(float)


#%%
# Running back performance metric

rb_sub = a_rb_df.loc[(a_rb_df['Year']>=2000) & (a_rb_df['Year']<=2010)].copy()

rb_sub['Att'].mean()

a_rb_sub = rb_sub.loc[rb_sub['Att']>=30].copy()

#%%
# a
a_rb_sub['yds/att'] = a_rb_sub['Yds']/a_rb_sub['Att']

x=a_rb_sub['yds/att'].mean()-3

y = 1/x

a_rb_sub['a'] = (a_rb_sub['yds/att']-3)*y

a_rb_sub['a'].mean()

a_test = a_rb_sub.loc[a_rb_sub['a']>2.375]

#%%
# b

a_rb_sub['TD%'] = a_rb_sub['TD']/a_rb_sub['Att']
j = 1/a_rb_sub['TD%'].mean()

a_rb_sub['b'] = a_rb_sub['TD%']*j

a_rb_sub['b'].mean()

b_test = a_rb_sub.loc[a_rb_sub['b']>2.375]

#%%
# c

a_rb_sub['Fmb%'] = a_rb_sub['Fmb']/a_rb_sub['Att']

k = 1.375/(a_rb_sub['Fmb%'].mean())

a_rb_sub['c'] = 2.375 - a_rb_sub['Fmb%']*k

a_rb_sub['c'].mean()

c_test = a_rb_sub.loc[a_rb_sub['c']>2.375]

#%%
# Final calc

q = (a_rb_sub['a'].mean()+a_rb_sub['b'].mean()+a_rb_sub['c'].mean())/0.667

a_rb_sub['Rate'] = ((a_rb_sub['a']+a_rb_sub['b']+a_rb_sub['c'])/q)*100

a_rb_sub['Rate'].mean()

#%%
# var calcs

a_rb_df['a'] = ((a_rb_df['Yds']/a_rb_df['Att'])-2)*y

a_rb_df['b'] = (a_rb_df['TD']/a_rb_df['Att'])*j

a_rb_df['c'] = 2.375 - (a_rb_df['Fmb']/a_rb_df['Att'])*k

calc_list_1 = ['a','b','c']

for i in calc_list_1:
    a_rb_df[i]=np.where(a_rb_df[i]>2.375,2.375,a_rb_df[i])
    a_rb_df[i]=np.where(a_rb_df[i]<0,0,a_rb_df[i])

a_rb_df['rating_adj'] = (((a_rb_df['a']+a_rb_sub['b']+a_rb_df['c'])/q)*100).round(1)

rate_sub = a_rb_df.loc[a_rb_df['rating_adj']==158.3]

a_rb_df['rating_adj'].mean()

b_rb_df = a_rb_df.loc[a_rb_df['Att']>=30].copy()
b_rb_df['rating_adj'].mean()

#%%

total_wr = []
    
for i in range(1932,2025):
    page = "https://www.pro-football-reference.com/years/" + str(i) + "/receiving.htm"
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    column_headers = pageSoup.find_all('tr')[1]
    column_headers = [j.getText() for j in column_headers.find_all('th')]
    
    rows = pageSoup.find_all('tr')[1:]
    wr_stats = []
    for j in range(len(rows)):
        rowtext = [col.get_text() for col in rows[j].find_all('td')]
        if (rowtext == [])&(j!=0):
            index = j
        if (rowtext == [])&(j==0):
            index = len(rows)
        wr_stats.append(rowtext)
    a_wr_stats = wr_stats[0:index]
    df_wr = pd.DataFrame(a_wr_stats, columns=[column_headers[1:]])
    
    df_wr.columns = [str(col).strip('(').strip(')').strip("'").strip(',').strip("'") for col in df_wr.columns]
    
    df_wr = df_wr.loc[df_wr['Player']!='Player']
    df_wr['Year']=i
    total_wr.append(df_wr)
    print(f"{i} receiving stats added.")
    time.sleep(5)

wr_df = pd.concat(total_wr,ignore_index=True)

#%%

wr_df.columns = ['Player','Age','Tm','Pos','G','GS','Rec','Yds','Y/R','TD','Lng','R/G','Y/G','Awards','Year','Fmb','Tgt','Ctch%','Y/Tgt','1D','Succ%']

wr_df['Ctch%'] = wr_df['Ctch%'].astype(str).str.replace('%','')
wr_df['Ctch%'] = np.where(wr_df['Ctch%']=='None',np.nan,wr_df['Ctch%'])
a_wr_df = wr_df.iloc[1:].copy()

for i in a_wr_df.columns:
    a_wr_df[i] = np.where(a_wr_df[i]=='',np.nan,a_wr_df[i])

float_list_2 = ['Age','G','GS','Rec','Yds','Y/R','TD',
              'Lng','Y/Tgt','R/G','Y/G','Fmb','Year','Tgt','Ctch%','1D']

for i in float_list_2:
    a_wr_df[i] = a_wr_df[i].astype(float)
        
#%%
# WR stats
wr_sub = a_wr_df.loc[(a_wr_df['Year']>=2000)&(a_wr_df['Year']<=2010)].copy()

wr_sub['Rec'].mean()

a_wr_sub = wr_sub.loc[wr_sub['Rec']>=15].copy()

#%%
# a

a_wr_sub['catch_rate'] = a_wr_sub['Rec']/a_wr_sub['Tgt']

a_wr_sub['catch_rate'].mean()

t=a_wr_sub['catch_rate'].mean()-0.5

w = 1/t

a_wr_sub['a'] = (a_wr_sub['catch_rate']-0.5)*w

a_wr_sub['a'].mean()

a_test = a_wr_sub.loc[a_wr_sub['a']>2.375]

#%%
# b

a_wr_sub['yds_prec'] = a_wr_sub['Yds']/a_wr_sub['Rec']

a_wr_sub['yds_prec'].mean()

c = 1/(a_wr_sub['yds_prec'].mean()-7.2)

a_wr_sub['b'] = (a_wr_sub['yds_prec']-7.2)*c

a_wr_sub['b'].mean()

b_test = a_wr_sub.loc[a_wr_sub['b']>2.375]

#%%
# c

a_wr_sub['td_prec'] = a_wr_sub['TD']/a_wr_sub['Rec']

a_wr_sub['td_prec'].mean()

g = 1/(a_wr_sub['td_prec'].mean()+0.003)

a_wr_sub['c'] = (a_wr_sub['td_prec']+0.003)*g

a_wr_sub['c'].mean()

c_test = a_wr_sub.loc[a_wr_sub['c']>2.375]

#%%
calc_list_2 = ['a','b','c']

for i in calc_list_2:
    a_wr_sub[i]=np.where(a_wr_sub[i]>2.375,2.375,a_wr_sub[i])
    a_wr_sub[i]=np.where(a_wr_sub[i]<0,0,a_wr_sub[i])

a_q = (a_wr_sub['a'].mean()+a_wr_sub['b'].mean()+a_wr_sub['c'].mean())/0.667

a_wr_sub['Rate'] = ((a_wr_sub['a']+a_wr_sub['b']+a_wr_sub['c'])/a_q)*100

a_wr_sub['Rate'].mean()

#%%
# var calcs

a_wr_df['catch_rate'] = a_wr_df['Rec']/a_wr_df['Tgt']
a_wr_df['yds_prec'] = a_wr_df['Yds']/a_wr_df['Rec']
a_wr_df['td_prec'] = a_wr_df['TD']/a_wr_df['Rec']

a_wr_df['a'] = (a_wr_df['catch_rate']-0.5)*w

a_wr_df['b'] = (a_wr_df['yds_prec']-7.2)*c

a_wr_df['c'] = (a_wr_df['td_prec']+0.003)*g

calc_list_2 = ['a','b','c']

for i in calc_list_2:
    a_wr_df[i]=np.where(a_wr_df[i]>2.375,2.375,a_wr_df[i])
    a_wr_df[i]=np.where(a_wr_df[i]<0,0,a_wr_df[i])

a_wr_df['rating_adj'] = (((a_wr_df['a']+a_wr_df['b']+a_wr_df['c'])/a_q)*100).round(1)

wr_rate_sub = a_wr_df.loc[a_wr_df['rating_adj']==158.3]

a_wr_df['rating_adj'].mean()

b_wr_df = a_wr_df.loc[a_wr_df['Rec']>=15].copy()

b_wr_df['rating_adj'].mean()

c_wr_df = b_wr_df.loc[b_wr_df['Year']>=1992]

test_perfect = ((2.375+2.375+2.375)/a_q)*100

#%%
# Adjusting rating scale to 0 to 158.3
#QB
qb_min = b_qb_df['rating_adj'].min()
qb_range = b_qb_df['rating_adj'].max()-b_qb_df['rating_adj'].min()

b_qb_df['rating_adj_1'] = (b_qb_df['rating_adj']-qb_min)*(158.3/qb_range)

# RB
rb_min = a_rb_df['rating_adj'].min()
rb_range = a_rb_df['rating_adj'].max()-a_rb_df['rating_adj'].min()

a_rb_df['rating_adj_1'] = (a_rb_df['rating_adj']-rb_min)*(158.3/rb_range)

# WR
wr_min = b_wr_df['rating_adj'].min()
wr_range = b_wr_df['rating_adj'].max()-b_wr_df['rating_adj'].min()

b_wr_df['rating_adj_1'] = (b_wr_df['rating_adj']-wr_min)*(158.3/wr_range)

#%%
qb_rating = b_qb_df[['Player','Year','Tm','Age','Pos','G','GS','rating_adj_1']].copy()
qb_rating['df_id'] = 'Passing'

rb_rating = a_rb_df[['Player','Year','Tm','Age','Pos','G','GS','rating_adj_1']].copy()
rb_rating['df_id'] = 'Rushing'

wr_rating = b_wr_df[['Player','Year','Tm','Age','Pos','G','GS','rating_adj_1']].copy()
wr_rating['df_id'] = 'Receiving'

offense_df_list = [qb_rating,rb_rating,wr_rating]

#%%

for i in offense_df_list:
        i['pro_bowl'] = i['Player'].astype(str).apply(lambda g: 1 
                                                         if "*" in g.lower()
                                                         else 0)
        i['first_all_pro'] = i['Player'].astype(str).apply(lambda g: 1 
                                                                 if "+" in g.lower()
                                                                 else 0)
        i['Player'] = i['Player'].astype(str).str.replace('*','').str.replace('+','')

offense_final = pd.concat(offense_df_list,ignore_index=True)

perfect_offense = offense_final.loc[offense_final['rating_adj_1']==158.3]

# offense_final.to_csv(r'C:\Users\thompson.knuth\Desktop\Webscraping Practice\NFL\NFL Offensive Ratings Data Build (2000s) (TK).csv')
