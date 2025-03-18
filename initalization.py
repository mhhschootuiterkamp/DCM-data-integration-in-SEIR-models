"""
Calculate intializations and reproduction numbers based on COVID RADAR and CoronaMelder data prepared in data_loader.py.

- Start and end dates are set to cover the maximal range of dates for which data is possible, but reducing the time range is possible by adjusting these dates.
"""

import pandas as pd
import datetime as dt
import math

from data_loader import *



'''
Create results for COVID RADAR data
'''
S_est_contacts = []
E_est_contacts = []
I_est_contacts = []
R_est_contacts = []

radar_contacts = []
radar_risk_contact_list = []

I_est_date_contacts = []

HELP_exp_I = 0
HELP_I_cum = 0

Recovered_0 = 0
'''
Calculate initialization for each day
'''
start_date_nr = dt.datetime.strptime('16apr2020', date_format)
end_date_nr = dt.datetime.strptime('28feb2022', date_format)
for t in range(0, (end_date_nr - start_date_nr).days - 14):
    day_difference = dt.timedelta(days=t)
    current_date_nr = start_date_nr + day_difference
    current_date = current_date_nr.strftime(date_format).lower()
    current_date_str = current_date_nr.strftime('%d-%m-%Y')
    print('Current date:', current_date)
    I_est_date_contacts.append(current_date_nr)
    
    I_value =  radar_indexed.at[current_date_nr,'risk contact rate'] / radar_indexed.at[current_date_nr, 'numberpersons150cm'] * Inhabitants
    I_est_contacts.append(I_value)
    HELP_I_cum += I_value
    
    R_value = Recovered_0
    if t > 0:
        R_value = math.exp(-(t-1) / immunity_period) * (Recovered_0 + HELP_exp_I / infectious_period)
    R_est_contacts.append(R_value)
    
    E_value = 0
    if t > 0:
        E_value = (I_est_contacts[t] - I_est_contacts[t-1] + I_est_contacts[t-1] / infectious_period) * latent_period
    E_est_contacts.append(E_value)
    
    S_est_contacts.append(Inhabitants - E_value - I_value - R_value)
    
    HELP_exp_I += math.exp(t / immunity_period) * I_est_contacts[t]

    radar_contacts.append(radar_indexed.at[current_date_nr, 'numberpersons150cm'] )
    radar_risk_contact_list.append(radar_indexed.at[current_date_nr,'risk contact rate'] )

''' Organize in dataframe:'''
HELP_dict = {'Date': I_est_date_contacts,
             'S': S_est_contacts,
             'E': E_est_contacts,
             'I': I_est_contacts,
             'R': R_est_contacts,
             'contact rate': radar_contacts,
             'risk contact rate': radar_risk_contact_list}
df_SEIR = pd.DataFrame(HELP_dict)
df_SEIR['incidence'] = df_SEIR['S'] * df_SEIR['I'] * df_SEIR['contact rate'] / Inhabitants


'''Reproduction number'''
R_contact_est = []
R_contact_est_only_contacts = []
for t in range(14, (end_date_nr - start_date_nr).days - 14):
    day_difference = dt.timedelta(days=t)
    current_date_nr = start_date_nr + day_difference
    current_date = current_date_nr.strftime(date_format).lower()
    current_date_str = current_date_nr.strftime('%d-%m-%Y')
    print('Computing R. Current date:', current_date)

    # For the original version:
    denominator = 0
    for tt in range(0, 14):
        denominator += df_SEIR['incidence'][t - tt - 1] * gamma_list[tt]
    R_contact_est.append(df_SEIR['incidence'][t] / denominator)

    # For the version without S:
    denominator = 0
    for tt in range(0, 14):
        denominator += df_SEIR['risk contact rate'][t - tt - 1] * gamma_list[tt]
    R_contact_est_only_contacts.append(df_SEIR['risk contact rate'][t] / denominator)

# RIVM estimates of reproduction number
df_SEIR['Rep_rivm'] = math.nan
df_SEIR['Rep_rivm'][14:] = df_R['Rt_avg'][start_date_nr + dt.timedelta(days = 14):end_date_nr - dt.timedelta(days = 15)]
df_SEIR['Rep_rivm_upper'] = math.nan
df_SEIR['Rep_rivm_upper'][14:] = df_R['Rt_up'][start_date_nr + dt.timedelta(days = 14):end_date_nr - dt.timedelta(days = 15)]
df_SEIR['Rep_rivm_lower'] = math.nan
df_SEIR['Rep_rivm_lower'][14:] = df_R['Rt_low'][start_date_nr + dt.timedelta(days = 14):end_date_nr - dt.timedelta(days = 15)]

# RIVM estimates of # of infectious people
df_SEIR['prev'] = math.nan
df_SEIR.loc[df_SEIR['Date'] <= df_infectious.index[-1],'prev'] = df_infectious.loc[start_date_nr : df_infectious.index[-1],'prev_avg'].values
df_SEIR['prev_up'] = math.nan
df_SEIR.loc[df_SEIR['Date'] <= df_infectious.index[-1],'prev_up'] = df_infectious.loc[start_date_nr : df_infectious.index[-1],'prev_up'].values
df_SEIR['prev_low'] = math.nan
df_SEIR.loc[df_SEIR['Date'] <= df_infectious.index[-1],'prev_low'] = df_infectious.loc[start_date_nr : df_infectious.index[-1],'prev_low'].values

# Include reproduction number estimates
df_SEIR['Rep'] = math.nan
df_SEIR['Rep'][14:] = R_contact_est
df_SEIR['Rep only contacts'] = math.nan
df_SEIR['Rep only contacts'][14:] = R_contact_est_only_contacts




'''
Create results for CoronaMelder data:
'''
S_est_contacts = []
E_est_contacts = []
I_est_contacts = []
R_est_contacts = []

radar_contacts = []
radar_risk_contact_list = []

I_est_date_contacts = []

HELP_exp_I = 0
HELP_I_cum = 0

# Rough initialization based on outcome of COVID RADAR model:
Recovered_0 = 10000

'''Calculate initialization for each time'''
start_date_nr = dt.datetime.strptime('10oct2020', date_format)
end_date_nr = dt.datetime.strptime('28feb2022', date_format)
for t in range(0, (end_date_nr - start_date_nr).days - 14):
    day_difference = dt.timedelta(days=t)
    current_date_nr = start_date_nr + day_difference
    current_date = current_date_nr.strftime(date_format).lower()
    current_date_str = current_date_nr.strftime('%d-%m-%Y')
    I_est_date_contacts.append(current_date_nr)
 
    I_value = df_melder.at[current_date_nr,'risk contact rate'] / radar_indexed.at[current_date_nr, 'numberpersons150cm'] * Inhabitants    
    I_est_contacts.append(I_value)
    
    HELP_I_cum += I_value
    
    R_value = Recovered_0
    if t > 0:
        R_value = math.exp(-(t-1) / immunity_period) * (Recovered_0 + HELP_exp_I / infectious_period)
    R_est_contacts.append(R_value)
    
    E_value = 0
    if t > 0:
        E_value = (I_est_contacts[t] - I_est_contacts[t-1] + I_est_contacts[t-1] / infectious_period) * latent_period      
    E_est_contacts.append(E_value)
    
    S_est_contacts.append(Inhabitants - E_value - I_value - R_value)
    
    HELP_exp_I += math.exp(t / immunity_period) * I_est_contacts[t]

    radar_contacts.append(radar_indexed.at[current_date_nr, 'numberpersons150cm'] )
    radar_risk_contact_list.append(df_melder.at[current_date_nr,'risk contact rate'])
    

'''Organize in dataframe'''
HELP_dict = {'Date': I_est_date_contacts,
             'S': S_est_contacts,
             'E': E_est_contacts,
             'I': I_est_contacts,
             'R': R_est_contacts,
             'contact rate': radar_contacts,
             'risk contact rate': radar_risk_contact_list}
df_SEIR_m = pd.DataFrame(HELP_dict)
df_SEIR_m['incidence'] = df_SEIR_m['S'] * df_SEIR_m['I'] * df_SEIR_m['contact rate'] / Inhabitants



'''Reproduction number'''
R_contact_est = []
R_contact_est_only_contacts = []
for t in range(14, (end_date_nr - start_date_nr).days - 14):
    day_difference = dt.timedelta(days=t)
    current_date_nr = start_date_nr + day_difference
    current_date = current_date_nr.strftime(date_format).lower()
    current_date_str = current_date_nr.strftime('%d-%m-%Y')

    # For the original version:
    denominator = 0
    for tt in range(0, 14):
        denominator += df_SEIR_m['incidence'][t - tt - 1] * gamma_list[tt]
    R_contact_est.append(df_SEIR_m['incidence'][t] / denominator)

    # For the version without S:
    denominator = 0
    for tt in range(0, 14):
        denominator += df_SEIR_m['risk contact rate'][t - tt - 1] * gamma_list[tt]
    R_contact_est_only_contacts.append(df_SEIR_m['risk contact rate'][t] / denominator)

# RIVM estiamtes of reprouction number
df_SEIR_m['Rep_rivm'] = math.nan
df_SEIR_m['Rep_rivm'][14:] = df_R['Rt_avg'][start_date_nr + dt.timedelta(days = 14):end_date_nr - dt.timedelta(days = 15)]
df_SEIR_m['Rep_rivm_upper'] = math.nan
df_SEIR_m['Rep_rivm_upper'][14:] = df_R['Rt_up'][start_date_nr + dt.timedelta(days = 14):end_date_nr - dt.timedelta(days = 15)]
df_SEIR_m['Rep_rivm_lower'] = math.nan
df_SEIR_m['Rep_rivm_lower'][14:] = df_R['Rt_low'][start_date_nr + dt.timedelta(days = 14):end_date_nr - dt.timedelta(days = 15)]

# RIVM estimates of number of infectious people:
df_SEIR_m['prev'] = math.nan
df_SEIR_m.loc[df_SEIR_m['Date'] <= df_infectious.index[-1],'prev'] = df_infectious.loc[start_date_nr : df_infectious.index[-1],'prev_avg'].values
df_SEIR_m['prev_up'] = math.nan
df_SEIR_m.loc[df_SEIR_m['Date'] <= df_infectious.index[-1],'prev_up'] = df_infectious.loc[start_date_nr : df_infectious.index[-1],'prev_up'].values
df_SEIR_m['prev_low'] = math.nan
df_SEIR_m.loc[df_SEIR_m['Date'] <= df_infectious.index[-1],'prev_low'] = df_infectious.loc[start_date_nr : df_infectious.index[-1],'prev_low'].values

# Include reproduction number estimates
df_SEIR_m['Rep'] = math.nan
df_SEIR_m['Rep'][14:] = R_contact_est
df_SEIR_m['Rep only contacts'] = math.nan
df_SEIR_m['Rep only contacts'][14:] = R_contact_est_only_contacts