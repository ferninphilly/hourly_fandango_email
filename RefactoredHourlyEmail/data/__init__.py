__author__ = 'fpombeiro'

from data.db import report_data_db
from data.xlsx import get_excel_reports 

def report_data():
    return report_data_db()

def xlsx_data():
    return get_excel_reports()