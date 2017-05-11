#!/usr/bin/env python3

import yaml
import os
from datetime import datetime, timedelta
import calendar
import csv
import sys


YAML_LOCATION = os.environ['HOURLY_ENV']
#YAML_LOCATION = '/home/fernbi/refactored_hourly/RefactoredHourlyEmail/data/yaml/'
SENDER = 'hourly_tix_report@fandango.com'
TESTING = True #TRUE if testing, FALSE if ready for broad release

def _yaml(yaml_file):
    with open(YAML_LOCATION + yaml_file, 'rU') as ym:
        return yaml.load(ym)
                                                   
MSSQL_CONNECTION_DATA=_yaml('hourly.yaml')['hourly_report']['connection_data']
MEMCACHE_CONNECTION_DATA= ['127.0.0.1:11211']
TODAY = datetime.date(datetime.today())
YESTERDAY = TODAY - timedelta(days=1)
TWO_DAYS_AGO = TODAY - timedelta(days=2)
LAST_HOUR = datetime.now().hour -1
THIS_HOUR = datetime.now().hour
DATE_LAST_HOUR = datetime.now() - timedelta(hours=1)
END_OF_MONTH = datetime.date(datetime(YESTERDAY.year, YESTERDAY.month,\
                    calendar.monthrange(YESTERDAY.year, YESTERDAY.month)[1]))

def subject(eod_projection):
    if LAST_HOUR > 6:
        SUBJECT = "CUR: {sofar} | EOD PROJ: {projected} | CIF: {cif}".format(
                        sofar = "{:,}".format(eod_projection['actual']),
                        projected = "{:,}".format(eod_projection['eod_projection']),
                        cif = "{:,}".format(eod_projection['cif'])
                        #datentime=DATE_LAST_HOUR.strftime('%I%p %m/%d')
                                                                    )
    else:
        SUBJECT = "CUR: {sofar} | EOD (PROJ): After 7am | CIF: {cif}".format(
                                    sofar = "{:,}".format(eod_projection['actual']),
                                    cif = "{:,}".format(eod_projection['cif']),
                                    datentime=DATE_LAST_HOUR.strftime('%I%p %m/%d')
                                                                    )
    return SUBJECT

HEADERS = {'summary':
                {'title': 'Summary Table',
                 'header': ['Title',
                           'Current Projection',
                           'Var to Budget',
                           '% var to Budget']
                },
            'hourly':
                {'title': 'Hourly Projections Table',
                 'header': ['Hour',
                              'Hourly_Actual',
                              'Today Cumulative(actual)',
                              '% of Tix sold so far',
                              'Hourly Projection',
                              'End of Day Projection']
                },
            'film_summary_hr':
                {'title': 'Hourly Film Summary',
                  'header': ['Title',
                            'Tix Sold Last Hour',
                            '% Last Hr']
                },
            'film_perf_today':
                {'title': 'Film Performance Today Summary',
                 'header': ['Title',
                            'Tix Sold so far Today',
                            '% Total Day']
                },
            'channel_last_hr':
                {'title': 'Channel Last Hour',
                 'header': ['Channel', 'Tickets', 'Percentage'],
                },
            'channel_so_far':
                {'title': 'Channel So Far Today',
                 'header': ['Channel', 'Tickets', 'Percentage']
                }
            }


