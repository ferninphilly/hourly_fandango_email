#!/usr/bin/env python3
__author__ = 'fpombeiro'
#Standard Lib
from datetime import datetime
import os
import sys

#Pip installed
import memcache

from config import MEMCACHE_CONNECTION_DATA
today_date_str=lambda: datetime.today().strftime('%Y%m%d') + "refactor"

def kill_cached_data():
    key = today_date_str()
    return memcache.Client(MEMCACHE_CONNECTION_DATA).delete(key)

if __name__ == '__main__':
    kill_cached_data()
    print("Okay- I've deleted memcache")

