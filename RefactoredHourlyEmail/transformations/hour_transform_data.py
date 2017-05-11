#!/usr/bin/env python3
import data, config
import pandas as pd
import numpy as np
from datetime import datetime
import re

month_ttl,channel,todays_data, eod_projection = data.report_data()
cif_data = data.xlsx_data()

def eod_projection_df(eod_projection):
    return pd.DataFrame(eod_projection, index=[x['Hour'] for x in eod_projection]).fillna(0)

def projected(eod_df):
    projection = eod_df.get_value(config.LAST_HOUR, 'EOD_Forecast') if config.LAST_HOUR > 6 else 0
    return {
            'eod_projected': int(projection),
            'current_actual': int(hourly_data(todays_data).Tix.sum()),
            'cif': int(cif_data['baseline']['Total_count'])
            }

def _cleanup(todays_data):
    for x in todays_data:
        x['Title'] = re.sub(u"\u2013", "-", x['Title'])
        x['Title'] = re.sub(u"(\u2018|\u2019)", "'", x['Title'])
        x['Title'] = re.sub(u"(x96)", " ", x['Title'])
        x['Title'] = re.sub(u"(\uAAB9)", " ", x['Title'])
        x['Title'] = re.sub(u"(\u2122)", " ", x['Title'])
        x['Title'] = re.sub(u"(\u00E9)", " ", x['Title'])
    return todays_data

def hourly_data(todays_data):
    return pd.DataFrame(_cleanup(todays_data))

def top_bottom_films(dataframe, hourly=None, channel=False, nbr=15):
    if hourly and not channel:
        total_tix = dataframe[dataframe.Hour == max(dataframe.Hour)].groupby('Date').\
                                            sum()['Tix'].values.tolist()[0]
        over_fifteen = dataframe[np.logical_and(( \
                                        dataframe.Hour == max(dataframe.Hour)), \
                                        (dataframe.Rank_ >= nbr))].groupby('Date').\
                                        sum()['Tix'].values.tolist()[0]
        under_fifteen_df = dataframe[np.logical_and(( \
                                        dataframe.Hour == max(dataframe.Hour)), \
                                        (dataframe.Rank_ < nbr))].drop('Date',1)
    elif hourly and channel:
        channel_hourly = dataframe[dataframe.Hour == max(dataframe.Hour)].\
                            sort_values(by='Tix', ascending=False).drop('Hour',1)\
                            .drop('Date',1)
        channel_hourly['pct'] = channel_hourly.groupby(level=0).sum().apply(lambda x: x / x.sum())
        channel_hourly['pct'] = channel_hourly['pct'].map("{:.0%}".format)
        channel_hourly['Tix'] = channel_hourly['Tix'].map("{:,}".format)
        channel_hourly = channel_hourly.values.tolist()
        return channel_hourly
    elif channel and not hourly:
        channel_hourly = dataframe.groupby(['Date', 'Title']).sum()['Tix'].\
                        reset_index().sort_values(by='Tix',ascending=False)
        channel_hourly['pct'] = channel_hourly.groupby(level=0).sum().apply(lambda x: x / x.sum())
        channel_hourly['pct'] = channel_hourly['pct'].map("{:.0%}".format)
        channel_hourly['Tix'] = channel_hourly['Tix'].map("{:,}".format)
        channel_hourly = channel_hourly.drop('Date', 1)
        return channel_hourly.values.tolist()
    else:
        total_tix = dataframe.groupby('Date').sum()['Tix'].values.tolist()[0]
        over_fifteen = (dataframe.groupby('Title').sum().sort_values(by='Tix', \
                                                ascending=0)[nbr-1:]).sum()['Tix']
        under_fifteen_df = dataframe.groupby('Title').sum().sort_values(by='Tix',\
                                                ascending=0)[:nbr]        
    over_fifteens = ['All others',
                     over_fifteen, 
                     over_fifteen/total_tix]
    under_fifteen_df['pct'] = under_fifteen_df.Tix / total_tix
    under_fifteen_df = under_fifteen_df.reset_index()
    under_fifteen_df = under_fifteen_df.drop('index', 1) if 'index' in \
                        under_fifteen_df.columns.tolist() else under_fifteen_df
    under_fifteen_lst = under_fifteen_df.drop('Hour', 1).drop('Rank_',1).values.tolist() 
    film_performance = under_fifteen_lst + [over_fifteens]
    film_performance = [[x[0],"{:,}".format(x[1]),\
                         "{:.1%}".format(x[2])] for x in film_performance]
    return film_performance

def top_six_bar(hourly_df, film=True):
    if film == True:
        top_six_lst = top_bottom_films(hourly_df, 1,False,6)
        top_films = list()
        for each in top_six_lst[:5]:
            top_films.append(each[0])
        high_end = hourly_df[hourly_df['Title'].isin(top_films)]
        filter_bottom = hourly_df[~hourly_df['Title'].isin(top_films)]
        bottom_films = filter_bottom.groupby('Hour').sum()['Tix'].tolist()
    filter_top = high_end.sort_values('Title', ascending=0)
    second_filter = filter_top.sort_values(['Title', 'Hour'], ascending=[False, True])
    merge_series = second_filter.groupby('Title').sum()['Tix'].sort_values(ascending=0)
    merged = pd.merge(second_filter, merge_series.to_frame().reset_index(), how='inner',
                      on=['Title', 'Title'])
    merged = merged.sort_values(['Tix_y','Hour'], ascending=[False, True])
    merged = merged.pivot(index='Hour', columns='Title', values='Tix_x').fillna(0).astype(int).to_dict()
    bigsix_lst = list()
    for k,v in merged.items():
        bigsix_lst.append(list(v.values()))
    bigsix_titles = list(merged.keys())
    if film == True:
        bigsix_titles.append('All Other Films')
        bigsix_lst.append(bottom_films)
#    total_for_day = hourly_df.groupby('Hour').sum()['Tix'].values.tolist()
    return (bigsix_titles, bigsix_lst)

def affiliates_chart(channels):
    channel_df = channels.drop('Date',1)
    channel_df = channel_df.fillna(0)
    channel_df = channel_df.groupby(['Hour', 'Title']).agg({'Tix':'sum'})
    channel_df = channel_df.groupby(level=0).apply(lambda x: (x / float(x.sum())) * 100)
    pivot_df = channel_df.reset_index()
    pivot_df = pivot_df.pivot(index='Hour', columns='Title', values='Tix').fillna(0)
    affiliates_dict = pivot_df.to_dict()
    order_dict = dict()
    for k,v in affiliates_dict.items():
        order_dict[k] = sum(v.values())
    full_order = [(k,order_dict[k]) for k in sorted(order_dict, key=order_dict.get, reverse=True)]
    order_list = [x[0] for x in full_order]
    affiliates_data = list()
    for each in order_list:
        affiliates_data.append(list(affiliates_dict[each].values()))
    sanitized_list = [x.replace('&', ' and ') for x in order_list]
    return sanitized_list, affiliates_data
    
    
def forecast_baseline(dow_curves):
   hourly_pct = dict()  
   for each in dow_curves:
       hourly_pct[each.get('Hour')] = each.get('Pct_Tickets')
   return pd.DataFrame(list(hourly_pct.values()))

#def eod_series(eod_projection):
#    prj = dict()
#    for each in eod_projection:
#        if each['Date'].strip() == config.TODAY.strftime('%Y-%m-%d'):
#            prj[each['Current_Hour']] = each['EOD_Forecast']
#    return pd.Series(prj).fillna(0)

def hourly_baseline(eod_df, hourly_df):
    actual_df = hourly_df.groupby('Hour').sum().drop('Rank_',1)
    hourly_baseline_df = eod_df.join(actual_df, how='outer').fillna(0)
    hourly_baseline_df['cum_tix'] = np.where(hourly_baseline_df.Tix > 0,\
                                             hourly_baseline_df.cumsum()['Tix'],0).astype(int)
    hourly_baseline_df['Tix'] = hourly_baseline_df.Tix.astype(int)                                 
    return hourly_baseline_df

def hourly_projection(hourly_baseline_df, eod_df):
    dt = datetime(config.TODAY.year, config.TODAY.month, config.TODAY.day)
    hourly_baseline_df['cif_projections_hourly'] = np.ceil((cif_data['baseline_month'][dt]['Total_count']\
                                                  * hourly_baseline_df.Pct_Tickets).\
                                                 fillna(0).astype(int)).astype(int)
    hourly_baseline_df['cif_cum'] = hourly_baseline_df.cif_projections_hourly.cumsum()
    hourly_baseline_df['overall_pace'] = (projected(eod_df)['eod_projected'] * \
                                         hourly_baseline_df.Pct_Tickets).astype(int) if \
                                         projected(eod_df)['eod_projected'] > 0 else \
                                         hourly_baseline_df['cif_projections_hourly']
    hourly_baseline_df['pacing'] = np.where(hourly_baseline_df.Tix > 0, hourly_baseline_df.Tix,
                                      hourly_baseline_df.overall_pace).astype(int)   
    return hourly_baseline_df

#nbr here is whether we want the lists in number or string format for table
def create_hourly_list(hourly_projection_df, nbr=False):
    hourly_projection_df= hourly_projection_df.reset_index()
    hourly_projection_df = hourly_projection_df[['index', 'Tix', 'cum_tix', \
                        'CumPct_Tickets', 'cif_projections_hourly', 'pacing', 'EOD_Forecast']]
    if nbr:
        hourly_projection_df['index'] = hourly_projection_df['index'].astype(int)
        hourly_projection_df['Tix'] = hourly_projection_df['Tix'].astype(int)
        hourly_projection_df['cum_tix'] = hourly_projection_df['cum_tix'].astype(int)
        hourly_projection_df['CumPct_Tickets'] = hourly_projection_df['CumPct_Tickets'].astype(float)
        hourly_projection_df['cif_projections_hourly'] = hourly_projection_df['cif_projections_hourly'].\
                                                    astype(int)
        hourly_projection_df['pacing'] = hourly_projection_df['pacing'].astype(int)
    else:
        hourly_projection_df['index'] = hourly_projection_df['index'].astype(int).map("{:,}".format)
        hourly_projection_df['Tix'] = hourly_projection_df['Tix'].astype(int).map("{:,}".format)
        hourly_projection_df['cum_tix'] = hourly_projection_df['cum_tix'].astype(int).map("{:,}".format)
        hourly_projection_df['CumPct_Tickets'] = hourly_projection_df['CumPct_Tickets'].astype(float).map("{:.0%}".format)
        hourly_projection_df['pacing'] = hourly_projection_df['pacing'].astype(int).map("{:,}".format)
        hourly_projection_df['EOD_Forecast'] = hourly_projection_df['EOD_Forecast']\
                                                .astype(int).map("{:,}".format)
        hourly_projection_df = hourly_projection_df.drop('cif_projections_hourly',1)
    return hourly_projection_df.values.tolist()

def final_list_prep(todays_data, eod_projection):
    hourly_baseline_df = hourly_baseline(eod_projection_df(eod_projection), hourly_data(todays_data))
    hourly_projection_df = hourly_projection(hourly_baseline_df, eod_projection_df(eod_projection))
    return hourly_projection_df
            
            
def chart_prep(hourly_list):
    x_axis_actual = [int(i[0]) for i in hourly_list if int(i[1]) > 0]
    actual_sales = [int(i[1]) for i in hourly_list if int(i[1]) > 0]
    x_axis_fullday = [int(i[0]) for i in hourly_list]
    cif_pace = [int(i[4]) for i in hourly_list]
    actual_pace = [i[5] for i in hourly_list]
    upper_limit = max(actual_sales) * 1.1 if max(actual_sales) >= max(cif_pace) else max(cif_pace) * 1.1
    print("hourly transformations complete")
    return [x_axis_actual, actual_sales,
            x_axis_fullday, cif_pace,
            x_axis_fullday, actual_pace], upper_limit