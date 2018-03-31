'Author: Jeh Lokhande'
'Georgia Institute of Technology'

import os
os.chdir('C:\\Users\\Jeh\\Desktop\\Google Data\\takeout-20180329T030349Z-001\\Takeout\\Chrome')

import pandas as pd
import numpy as np
import json

import datetime
import tldextract


with open("BrowserHistory.json", encoding = 'UTF-8') as f:
    data = json.loads(f.read())
    df = pd.DataFrame(data["Browser History"])
# A possible param if differentiation is needed b/w different clients
df.drop('client_id', axis=1, inplace=True)
df.drop('favicon_url', axis=1, inplace=True)
df.sample(1)

dfcopy=df.copy()
df= df[(df['page_transition'] == "LINK") | (df['page_transition'] == "TYPED")]

#Some datetime operations
df['date_time'] = df['time_usec'].apply(lambda x: datetime.datetime.fromtimestamp(x/1000000))
df['date'] = df['date_time'].apply(lambda x: x.date())
df['day_of_week'] = df['date_time'].apply(lambda x: x.weekday())
df['month'] = df['date_time'].apply(lambda x: x.month)
df['month'] = df['month'].apply(lambda x: '%02d' % x)
df['year'] = df['date_time'].apply(lambda x: x.year)
df['year_month'] = df.apply(lambda x: int(str(x['year'])+x['month']),axis=1)
df['month'] = df['month'].apply(lambda x: int(x))
df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if ((x==5) | (x==6)) else 0)
df['hour'] = df['date_time'].apply(lambda x: x.hour)

#Get values for URL security
df['secure'] = df['url'].apply(lambda x: x[0:6])
df['is_secure'] = 0
df['is_secure'] = df['secure'].apply(lambda x: 1 if x !='http:/' else 0)
df['value']=1

#Function to get values domain and sub-domain names
def get_domain(x):
    domain = tldextract.extract(x)[1]
    sub_domain = tldextract.extract(x)[0]
    if sub_domain == "mail":
        return sub_domain + "." + domain
    if domain == "google" and sub_domain=="www":
        return "google_search" 
    return domain

df['domain'] = df['url'].apply(get_domain)

##Write data to a csv, categorize domains into Learning, Entertainment, Communication, News, General, Job Search and Uncategorized
#Read data and merge
dcat = pd.read_csv('domaincategory.csv')
dfcat=df.merge(dcat, on =['domain'], how ='left')

##Visualization

#Browsing patterns
#1. Over time
import seaborn as sns
sns.countplot(x='year_month', data=dfcat)

#Over hours
df_hour = pd.DataFrame(pd.DataFrame(dfcat[dfcat['year_month']>201708].groupby(by = ['date','hour'], as_index=False)['value'].sum()).groupby(by=['hour'], as_index=False).mean())
sns.barplot(x='hour',y='value', data=df_hour)
#
##Over hours - only for Learning
#df_hour_learning = pd.DataFrame(pd.DataFrame(dfcat[(dfcat['year_month']>201708) & (dfcat['category']>'Learning')].groupby(by = ['date','hour'], as_index=False)['value'].sum()).groupby(by=['hour'], as_index=False).mean())
#sns.barplot(x='hour',y='value', data=df_hour_learning)
#
#
#sns.countplot(x='hour', data=dfcat[(dfcat['category']=='Learning') & (dfcat['year_month']>=201707)])
#
#sns.countplot(x='hour', data=dfcat[(dfcat['category']=='Entertainment') & (dfcat['year_month']>=201707)])

##Browsing pattern (Secure vs Unsecure)
c1 = sns.countplot(x="year_month", hue="is_secure", data=dfcat)
c1.set(xlabel='Year - Month', ylabel='Count of websites visited')

##Heatmap of categories over year_month
df_bycat = pd.DataFrame(dfcat[dfcat['year_month']!=201803].groupby(by = ['year_month', 'category'], as_index=False)['value'].sum())
result = df_bycat.pivot(index='year_month', columns='category', values='value')
a1 = sns.heatmap(result)
a1.set(xlabel='Category', ylabel='Year - Month')

##Heatmap of categories over weekday
df_bycat_weekday = pd.DataFrame(dfcat[(dfcat['year_month']!=201803) & (dfcat['year_month']>=201708)].groupby(by = ['day_of_week', 'category'], as_index=False)['value'].sum())
result = df_bycat_weekday.pivot(index='day_of_week', columns='category', values='value')
a2 = sns.heatmap(result)
a2.set(xlabel='Category', ylabel='Day of the Week (0 - Mon, 6 - Sun)')

##Heatmap of categories over Hour
df_bycat_hour = pd.DataFrame(dfcat[(dfcat['year_month']!=201803) & (dfcat['year_month']>201708)].groupby(by = ['hour', 'category'], as_index=False)['value'].sum())
result = df_bycat_hour.pivot(index='hour', columns='category', values='value')
a3 = sns.heatmap(result)
a3.set(xlabel='Category', ylabel='Hour')

##Heatmap of browsing pattern over Hour in March 2018
df_bydate_hour_march = pd.DataFrame(dfcat[(dfcat['year_month']==201803)].groupby(by = ['hour', 'date'], as_index=False)['value'].sum())
result = df_bydate_hour_march.pivot(index='hour', columns='date', values='value')
a4 = sns.heatmap(result,cmap="PuBuGn")
a4.set(xlabel='Date', ylabel='Hour')

##Heatmap of browsing pattern over Hour by day of the week
df_byday_hour = pd.DataFrame(dfcat[(dfcat['year_month']!=201803) & (dfcat['year_month']>201708)].groupby(by = ['hour', 'day_of_week'], as_index=False)['value'].sum())
result = df_byday_hour.pivot(index='hour', columns='day_of_week', values='value')
a5 = sns.heatmap(result,cmap="Blues")
a5.set(xlabel='Day', ylabel='Hour')

##Aggregating data and writing it to a csv file, to pivot
dffinal = dfcat.groupby(by=['date','hour','category'], as_index=False)['value'].sum()
dffinal.to_csv('df.csv')

##Calculate correlation matrix
catbyhour = pd.read_csv('category_by_hour.csv')
catbyhour[['Entertainment', 'Learning', 'Job Search', 'Communication']].corr()

##Correlation matrix between the 4 categories
a6 = sns.heatmap(catbyhour[['Entertainment', 'Learning', 'Job Search', 'Communication']].corr(),cmap = sns.diverging_palette(220, 10, as_cmap=True))



