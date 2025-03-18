import pandas as pd
import numpy as np
import datetime as dt
import math
from scipy import interpolate
from scipy.stats import gamma
import copy
from scipy import signal

dtype=np.float64


'''
This module loads, cleans, and prepares all the relevant data:
    - Prevalence data from RIVM
    - Effective rerpoduction number data from RIVM
    - COVID RADAR data
    - CoronaMelder data
'''

date_format = '%d%b%Y'

'''Load prevalence data'''
df_infectious = pd.read_json('COVID-19_prevalentie.json').set_index('Date')

'''Load data on effective reproduction number'''
df_R = pd.read_json('COVID-19_reproductiegetal_tm_03102021.json')
df_R = df_R.append(pd.read_json('COVID-19_reproductiegetal.json')).set_index('Date')


'''
For CoronaMelder data:
    - Load data
    - Fix outliers
    - Estimate number of active users via external report data
'''

#Load contact tracing data from coronamelder
df_melder = (pd.read_csv('ggd_positive_test_authorisations.csv')).rename(columns = {'Date (yyyy-mm-dd)':'Date','Reported positive tests through app authorised by GGD (daily)': 'Counts'})
df_melder['Date'] =  pd.to_datetime(df_melder['Date'])
df_melder['Active users'] = np.nan
df_melder = df_melder.set_index('Date')

#Fix outliers / measurement error in coronamelder data from 29-4-2021 to 1-5-2021:
df_melder.loc[dt.datetime.strptime('29apr2021',date_format):dt.datetime.strptime('01may2021',date_format),'Counts'] = np.nan
df_melder['Counts'] = df_melder['Counts'].interpolate()

#Additional data points for coronamelder data:
df_melder.at[dt.datetime.strptime('10oct2020', date_format),'Active users'] = 2260489
df_melder.at[dt.datetime.strptime('30apr2021', date_format),'Active users'] = 3049347
df_melder.at[dt.datetime.strptime('31may2021', date_format),'Active users'] = 3327002
df_melder.at[dt.datetime.strptime('30jun2021', date_format),'Active users'] = 2883373
df_melder.at[dt.datetime.strptime('31jul2021', date_format),'Active users'] = 2727479
df_melder.at[dt.datetime.strptime('31aug2021', date_format),'Active users'] = 2600700
df_melder.at[dt.datetime.strptime('30sep2021', date_format),'Active users'] = 2531497
df_melder.at[dt.datetime.strptime('31oct2021', date_format),'Active users'] = 2449499
df_melder.at[dt.datetime.strptime('30nov2021', date_format),'Active users'] = 2236463
df_melder.at[dt.datetime.strptime('31dec2021', date_format),'Active users'] = 1945557
df_melder.at[dt.datetime.strptime('31jan2022', date_format),'Active users'] = 2429568
df_melder.at[dt.datetime.strptime('28feb2022', date_format),'Active users'] = 2443277

#Interpolate number of active users in coronamelder and compute rate of counts per user
df_melder['Active users'] = df_melder['Active users'].interpolate()
df_melder['Rate'] = df_melder['Counts'] / df_melder['Active users'] 
df_melder = df_melder.dropna()

'''
For COVID RADAR data:
    - Load data
    - Create variable on whether the given day is last mentioning of a risk-contact
    - Filter out users with few responses or healthcare professions
    - Create aggregated rates weighted by age group
'''

#Read COVID-radar data
radar = (pd.read_csv('CRdataShared.csv', delimiter=',')).rename(columns = {'date':'Date'})
radar['Date'] = pd.to_datetime(radar['Date'])
 
#For the last time if difference with next entry is more than Days_ago days OR if next entry is from another ID
#-- Based on assumption dat dataframe is sorted on ID, then date.
Days_ago = 30
radar['lasttcontact'] = 0
radar_1 = radar.loc[(radar['contact'] == 1)]
radar_2 = radar_1.loc[(( radar_1['Date'].shift(-1) - radar_1['Date'] > dt.timedelta(days=Days_ago)) | (radar_1['ID'] != radar_1['ID'].shift(-1)))]
radar.loc[radar_2.index, 'lasttcontact'] = 1
    
# Age categories:
radar['age'] = radar['age'].replace(
        {'0-5':'0-29','06-11': '0-29', '12-18': '0-29', '19-29': '0-29'})

#Filter out users with low nr of responses
ID_counts = radar.ID.value_counts()
ID_more_than = ID_counts.loc[ID_counts >= 5]
radar = radar.loc[radar['ID'].isin(ID_more_than.index)]

#Filter out healthcare workers
radar = radar.loc[radar['profession'] != 'hcpro']


'''
Create lists of gamma distributions for generation time and for reporting time in CoronaMelder
'''

#Gamma-list for generation time
gamma_mean = 4
gamma_sd = 2

gamma_alpha = math.pow(gamma_mean / gamma_sd,2)
gamma_beta = gamma_mean / math.pow(gamma_sd,2)
# Create gamma_values list until 14:
gamma_list = []
for t in range(0, 14):
    gamma_list.append(gamma.cdf(t+1, gamma_alpha, scale=gamma_beta) -
                      gamma.cdf(t, gamma_alpha, scale=gamma_beta))

#Gamma-list for coronamelder
gamma_mean_melder = 3.1
gamma_sd_melder = 3.6

gamma_alpha_melder = math.pow(gamma_mean_melder / gamma_sd_melder,2)
gamma_beta_melder = gamma_mean_melder / math.pow(gamma_sd_melder,2)
# Create gamma_values list until 14:
gamma_list_melder = []
for t in range(0, 14):
    gamma_list_melder.append(gamma.cdf(t+1, gamma_alpha_melder, scale=1/gamma_beta_melder) -
                      gamma.cdf(t, gamma_alpha_melder, scale=1/gamma_beta_melder))


# Age distribution
Age_distribution = {'0-29': 5878384.0,
                    '30-39': 2211241.5,
                    '40-49': 2129321.5,
                    '50-59': 2551752.0,
                    '60-69': 2186358.0,
                    '70-79': 1675611.0,
                    '80+': 933055.0}
Inhabitants = sum(Age_distribution[i] for i in Age_distribution)

# Parameters of SEIR model
latent_period = 5.5
infectious_period = 9.5
immunity_period = 90
infected_infectious_factor = infectious_period / (latent_period + infectious_period)


'''To get age-weighted daily number of responses in radar_indexed:'''

def age_adder(age):
    return Age_distribution[age]

radar['age_size'] = radar['age'].apply(age_adder) / Inhabitants
radar_indexed_age = copy.copy(radar.groupby(['Date', 'age']).agg(np.mean))
radar_indexed_age = (radar_indexed_age.drop('age_size',axis = 1).multiply(radar_indexed_age['age_size'],axis = 'index')).assign(age_size = radar_indexed_age['age_size'])
radar_indexed = radar_indexed_age.reset_index().groupby('Date').sum()
# Include risk contact rates
radar_risk_contacts = radar_indexed.shift(-14)['lasttcontact'] * infected_infectious_factor
radar_indexed['risk contact rate'] = radar_risk_contacts

radar_twoweeks = radar_indexed.rolling(14).sum()


'''
To get daily number of risk contacts in coronamelder:
'''

df_melder['requests'] = df_melder['Rate'] * radar_twoweeks.loc[df_melder.index[0]:df_melder.index[-1]]['numberpersons150cm']
df_melder['risk contact rate'] = np.nan
# Using deconvolution:
melder_risk_contacts, remainder = signal.deconvolve(df_melder['requests'],gamma_list_melder)
df_melder.loc[df_melder.index[0]:df_melder.index[len(melder_risk_contacts) -1],'risk contact rate'] = melder_risk_contacts * infected_infectious_factor
df_melder.loc[df_melder['risk contact rate'] < 0] = 0
melder_risk_contacts = df_melder['risk contact rate']

'''
Smoothing of both contact data sources:
'''
tck_c = interpolate.make_smoothing_spline(range(0,len(radar_indexed)-14),radar_indexed.iloc[0:-14]['risk contact rate'])
radar_indexed['risk contact rate'][0:-14] = tck_c(range(0,len(radar_indexed)-14))

tck_150 = interpolate.make_smoothing_spline(range(0,len(radar_indexed)),radar_indexed['numberpersons150cm'])
radar_indexed['numberpersons150cm'] = tck_150(range(0,len(radar_indexed)))

df_melder = df_melder[df_melder['risk contact rate'].notnull()]
tck_m = interpolate.make_smoothing_spline(range(0,len(df_melder)),df_melder['risk contact rate'])
df_melder['risk contact rate'] = tck_m(range(0,len(df_melder)))