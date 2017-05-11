
import data, config
import pandas as pd
import numpy as np
from datetime import datetime
import re

def _monthly_data(month_ttl):
    month_base_df= pd.DataFrame(month_ttl).set_index('PSTDate').sort_index(ascending=True)
    return month_base_df

def forecast_data(forecast_baseline):
    forecast = forecast_baseline['baseline_month']
    forecast_df = pd.DataFrame([[x['Day_of_week'], x['Total_count']] for x in \
                                    forecast.values()],
        index=forecast.keys(), columns=['Day_of_week', 'Total_count'])
    forecast_df = forecast_df.sort_index(ascending=True)
    forecast_df['cum_run'] = forecast_df.Total_count.cumsum()
    forecast_df['pct_month'] = forecast_df.Total_count/forecast_df.Total_count.sum()
    forecast_df['pct_run'] = forecast_df.pct_month.cumsum()
    return forecast_df

def join_dataframes(month_base_df, forecast_df):
    begin_of_month = config.TODAY.strftime('%Y-%m-01')
    month_df = forecast_df.join(month_base_df[begin_of_month:], how='outer').fillna(0)
    return month_df.sort_index(ascending=True)

def monthly_projections(month_df):
    month_df['proj_delta'] = np.where(month_df.Tickets > 0, \
                                      month_df.Tickets/month_df.Total_count -1, 0)
    month_df['actual_cum'] = np.where(month_df.Tickets > 0, \
                                      month_df.Tickets.cumsum(),0)
    month_df['cum_delta'] = np.where(month_df.Tickets > 0, \
                                     month_df.actual_cum/month_df.cum_run -1,0)
    monthly_projection = (month_df[config.TODAY:]['Total_count'].sum() + \
                              max(month_df.actual_cum)).astype(int)
    month_df['proj_pct'] = month_df.pct_month.cumsum().map("{:.0%}".format)
    month_df['projection'] = monthly_projection
    month_df['proj_sofar'] = (monthly_projection * month_df.pct_run).astype(int)
    month_df['var_to_cif_actual'] = month_df.actual_cum - month_df.proj_sofar
    month_df['var_to_cif_pct'] = (month_df.actual_cum / month_df.proj_sofar) -1
    month_df['pct_month'] = month_df['pct_month'].map("{:.0%}".format)
    month_df['proj_delta'] = month_df['proj_delta'].map("{:.0%}".format)
    month_df['cum_delta'] = month_df['cum_delta'].map("{:.0%}".format)
    print("monthly projections complete")
    return month_df

def monthly_chart_data(monthly_projection_df):
    cif_lst = monthly_projection_df.Total_count.values.tolist()
    actual_lst = monthly_projection_df.Tickets.values.tolist()
    days_in_month = [int(x) for x in range(1,len(cif_lst) +1)]
    upper_limit = max(cif_lst) if max(cif_lst) > max(actual_lst) else max(actual_lst)
    return cif_lst, actual_lst, days_in_month, upper_limit
    



    