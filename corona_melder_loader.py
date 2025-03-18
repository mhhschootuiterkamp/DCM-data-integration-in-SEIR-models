"""
Reformat data from CoronaMelder into simpler format
"""

import pandas as pd
import datetime as dt
import json


with open('NL.json') as f:
    d = json.load(f)
    
df_melder = pd.DataFrame(columns = {'date','value'})
list_date = []
list_vlaues = []


list_values = []
for i in range(0,len(d['corona_melder_app_warning_archived_20220421']['values'])):
    list_values.append(d['corona_melder_app_warning_archived_20220421']['values'][i]['count'])
    
list_dates = []
for i in range(0,len(d['corona_melder_app_warning_archived_20220421']['values'])):
    list_dates.append(d['corona_melder_app_warning_archived_20220421']['values'][i]['date_unix'])

list_values_total = []
for i in range(0,len(d['corona_melder_app_download_archived_20220421']['values'])):
    list_values_total.append(d['corona_melder_app_download_archived_20220421']['values'][i]['count'])
    
list_dates_total = []
for i in range(0,len(d['corona_melder_app_download_archived_20220421']['values'])):
    list_dates_total.append(d['corona_melder_app_download_archived_20220421']['values'][i]['date_unix'])


list_dates_string = []
for i in range(0,len(list_dates)):
    list_dates_string.append(dt.datetime.fromtimestamp(
        int(list_dates[i])
    ).strftime('%Y-%m-%d'))

list_dates_total_string = []
for i in range(0,len(list_dates_total)):
    list_dates_total_string.append(dt.datetime.fromtimestamp(
        int(list_dates_total[i])
    ).strftime('%Y-%m-%d'))


'''# of warning count entries is longer than # of download count entries'''
list_dates_string = list_dates_string[7:]
list_values = list_values[7:]

list_rate = []
for i in range(0,len(list_dates_total)):
    list_rate.append(list_values[i] / list_values_total[i])

data = {'Date':list_dates_string, 'Counts':list_values, 'Users':list_values_total, 'Rate':list_rate}
pd.DataFrame(data)
df_new = pd.DataFrame(data)
df_new = df_new.iloc[::-1]
df_new.to_excel('Corona_melder.xlsx', index = False)