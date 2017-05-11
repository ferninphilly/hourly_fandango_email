#!/usr/bin/env python3
import data, config
from transformations import month_transform_data as mtd, hour_transform_data as htd

month_ttl,channel,todays_data, eod_projection= data.report_data()
cif_data = data.xlsx_data()
projected_data = htd.projected(htd.eod_projection_df(eod_projection))

def month_projections():
    month_df = mtd.join_dataframes(mtd._monthly_data(month_ttl),
                               mtd.forecast_data(cif_data))
    return mtd.monthly_projections(month_df)

def hourly_projections():
    return htd.final_list_prep(todays_data, eod_projection),\
            htd.hourly_data(todays_data)

 
def _summary(hourly_projection_df, month_projections):
    hour_var_to_budget = projected_data['eod_projected'] - projected_data['cif']
    eom_projection = month_projections['projection'].iloc[0]
    try:
        mtd_actual = month_projections['actual_cum'][config.YESTERDAY] \
                        if config.LAST_HOUR > 6 else month_projections['actual_cum'][config.TWO_DAYS_AGO]
        month_var_to_budget = month_projections['var_to_cif_actual'][config.YESTERDAY] \
                        if config.LAST_HOUR > 6 else month_projections['var_to_cif_actual'][config.TWO_DAYS_AGO]
        eom_var_to_budget = eom_projection - month_projections['cum_run'][config.END_OF_MONTH]
        pct_var_budget = (projected_data['eod_projected'] * 1.0 / month_projections['Total_count'][config.TODAY]) -1
        eom_pct_var_budget = (eom_projection * 1.0 / month_projections['cum_run'][config.END_OF_MONTH]).astype(float) -1
        month_cur_pct_var = month_projections['var_to_cif_pct'][config.YESTERDAY] if \
                        config.LAST_HOUR > 6 else month_projections['var_to_cif_pct'][config.TWO_DAYS_AGO]
    except KeyError:
        mtd_actual = 0
        month_var_to_budget = 0
        eom_var_to_budget = 0
        pct_var_budget = 0
        eom_pct_var_budget = 0
        month_cur_pct_var = 0
    return [
                [ 'Today Cumulative',
                  "{:,}".format(int(projected_data['eod_projected'])),
                  "{:,}".format(int(hour_var_to_budget)),
                  "{:.1%}".format(pct_var_budget)
                ],
                ['EOM Projection',
                   "{:,}".format(int(eom_projection)),
                   "{:,}".format(int(eom_var_to_budget)),
                   "{:.1%}".format(eom_pct_var_budget)
                ],
                ['MTD Actual',
                  "{:,}".format(int(mtd_actual)),
                  "{:,}".format(int(month_var_to_budget)),
                  "{:.1%}".format(month_cur_pct_var)
                ]
           ]

def full_transformations(month_projections, hourly_projection_df, hourly_df):
        return {
            'summary': {
                'title': config.HEADERS['summary']['title'],
                'header': config.HEADERS['summary']['header'],
                'data': _summary(hourly_projection_df, month_projections)
                },
            'hourly_projection_table': {
                'title': config.HEADERS['hourly']['title'],
                'header': config.HEADERS['hourly']['header'],
                'data': htd.create_hourly_list(hourly_projections()[0], False)
                },
            'hourly_film_summary_table': {
                'title': config.HEADERS['film_summary_hr']['title'],
                'header': config.HEADERS['film_summary_hr']['header'],
                'data': htd.top_bottom_films(hourly_df,1)
                },
            'daily_film_summary_table': {
                'title': config.HEADERS['film_perf_today']['title'],
                'header': config.HEADERS['film_perf_today']['header'],
                'data': htd.top_bottom_films(hourly_df,None)
                },
            'channel_last_hour_table': {
                'title': config.HEADERS['channel_last_hr']['title'],
                'header': config.HEADERS['channel_last_hr']['header'],
                'data': htd.top_bottom_films(htd.hourly_data(channel),1,1)
                },
            'channel_today_table': {
                'title': config.HEADERS['channel_so_far']['title'],
                'header': config.HEADERS['channel_so_far']['header'],
                'data': htd.top_bottom_films(htd.hourly_data(channel),None,1)
                },
            'chart_data': {
                'line_chart': htd.chart_prep(htd.create_hourly_list(hourly_projections()[0], True)),
                'film_bar_chart': htd.top_six_bar(hourly_df, film=True),
                'channel_bar_chart': htd.affiliates_chart(htd.hourly_data(channel)),
                'month_bar_chart': mtd.monthly_chart_data(month_projections)
                },
            'subject_line': {
                'eod_projection': projected_data['eod_projected'],
                'actual': projected_data['current_actual'],
                'cif': projected_data['cif']
            }
        }
    


