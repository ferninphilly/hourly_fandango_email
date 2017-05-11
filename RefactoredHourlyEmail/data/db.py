  
__author__ = 'fpombeiro'
#Standard Lib
from datetime import datetime
import os
import sys

#Pip installed
import memcache
import pymssql

#Local
from config import MSSQL_CONNECTION_DATA, MEMCACHE_CONNECTION_DATA, _yaml
today_date_str=lambda: datetime.today().strftime('%Y%m%d') + "refactor"

CURSOR=pymssql.connect(as_dict=True,**MSSQL_CONNECTION_DATA).cursor()
yamld = _yaml('hourly.yaml')['hourly_report']['file_locations']

def report_data_db():
#    dow_curves=_cached_data_if_exists(today_date_str())
#    if dow_curves is None:
#        CURSOR.callproc(yamld['acct_proc'])
#        dow_curves = _data_from_query_file(yamld['dow_curve'])
#        memcache.Client(MEMCACHE_CONNECTION_DATA).set(today_date_str(), dow_curves, 86400)
#    CURSOR.callproc(yamld['acct_proc'])
#    dow_curves = _data_from_query_file(yamld['dow_curve'])
    channel = _data_from_query_file(yamld['channel'])
    today_data = _data_from_query_file(yamld['today_data'])
    eod_projection = _data_from_query_file(yamld['hourly_projection'])
    month_ttl = _data_from_query_file(yamld['month_ttl'])
    print("Connected to database successfully")
    return month_ttl, channel, today_data, eod_projection


def _data_from_query_file(sourcefile):
    with open(sourcefile) as cnx:
        query = cnx.read()
    try:
        CURSOR.execute(query)
        return CURSOR.fetchall()
    except Exception as e:
        print("Cursor Exception {}".format(e))
    
def _cached_data_if_exists(key):
    return memcache.Client(MEMCACHE_CONNECTION_DATA).get(key)

def kill_cached_data():
    key = today_date_str()
    return memcache.Client(MEMCACHE_CONNECTION_DATA).delete(key)








