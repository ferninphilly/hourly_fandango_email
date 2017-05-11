#!/usr/bin/env python3
import transformations as tn
from yattag import Doc
from data.db import yamld
import GChartWrapper as gc
from config import DATE_LAST_HOUR


tables = tn.full_transformations(tn.month_projections(), tn.hourly_projections()[0],
                                 tn.hourly_projections()[1])

def cif_update():
    doc = None
    doc, tag, text = Doc().tagtext()
    with tag('center'):
        with tag('H4'):
            text('C.I.F updated as of {}'.format(yamld['last_cif_update']))
    return doc

def table_maker(title, header,data):
    doc = None
    doc, tag, text = Doc().tagtext()
    with tag('br'):
        with tag('center'):
            with tag('h2'):
                text(title)
    with tag('center'):
        with tag('table border=4'):
            with tag('tr'):
                for x in header:
                    with tag('th'):
                        text(x)
            for row in data:
                with tag('tr'):
                    with tag('center'):
                        for val in row:
                            with tag('td'):
                                text(val)
    return doc

def line_chart(chartdata):
    uplimit = int(chartdata[1])
    lc = gc.LineXY(chartdata[0])
    lc.color('red', 'blue', 'green')
    lc.scale(0,23,0,uplimit,0,23,0,uplimit,0,23,0,uplimit)
    lc.axes('xy')
    lc.axes.label(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23)
    lc.axes.label(1,0, "{:,}".format((int(uplimit * .25))), \
                  "{:,}".format((int(uplimit * 0.5))), \
                  "{:,}".format((int(uplimit * .75))), \
                  "{:,}".format(uplimit))
    lc.marker('N**','black',0,-1,9)
    lc.size(640,320)
    lc.legend('Today', 'C.I.F', 'Projected Curve')
    lc.line(5,4,1)
    lc.line(1)
    lc.line(4,3,1)
    lc.title('Hourly Today vs. Projected')
    return lc

def bar_chart(barchart_data, upper, films=True):
    bc = gc.VerticalBarStack(barchart_data[1])
    bc.color('blue', 'red', 'green', 'pink', 'purple', 'gray', 'orange',
             'silver', 'gold', 'black', 'yellow')
    bc.size(640,320)
    bc.legend("|".join(barchart_data[0]))
    bc.axes('xy')
    bc.axes.label(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23)
    bc.title('Percent tickets purchased by Channel')
    bc.legend_pos('b')
    if films == True:
        bc.scale(0,int(upper))
        bc.marker('N**', 'black', -1, -1, 9)
        bc.axes.label(1,0, "{:,}".format((int(upper * .25))), "{:,}".format((int(upper * 0.5))), \
                  "{:,}".format((int(upper * .75))), "{:,}".format(upper))
        bc.title('Historical Performace of Top Films')
    return bc

def month_sum_bar_chart(cif, actual, days, upper):
    vb = gc.VerticalBarGroup([cif, actual])
    vb.color('c6d9fd', '848482')
    vb.size(900,310)
    vb.scale(0, int(upper * 1.12))
    vb.axes("xy")
    vb.legend("Budgeted", "Actual")
    vb.legend_pos('b')
    vb.marker('N**', 'black', 1, -1, 9)
    vb.bar(10,0)
    vb.axes.label(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31)
    vb.axes.label(1,0, "{:,}".format(int(upper * .25)),"{:,}".format(int(upper * .5)), "{:,}".format(int(upper * .75)), "{:,}".format(int(upper)))
    vb.title('Month to date performance for {monthname}'.format(monthname=DATE_LAST_HOUR.strftime('%B')))
    return vb
    
def html_dict():
    html_tables = dict()
    cif, actual, days, upper = tables['chart_data']['month_bar_chart']
    for key, value in tables.items():
        if key not in ('chart_data','subject_line'):
            
            html_tables[key]= table_maker(value['title'],
                                             value['header'],
                                             value['data'])
    html_tables['cif_update'] = cif_update()
    html_tables['line_chart'] = line_chart(tables['chart_data']['line_chart'])
    html_tables['film_bar_chart'] = bar_chart(tables['chart_data']['film_bar_chart'],
                                              tables['chart_data']['line_chart'][1])
    html_tables['channel_bar_chart'] = bar_chart(tables['chart_data']['channel_bar_chart'],
                                                 tables['chart_data']['line_chart'][1],
                                                 films=False)
    html_tables['subject_line'] = tables['subject_line']
    html_tables['month_bar_chart'] = month_sum_bar_chart(cif, actual, days, upper)
    print("html tables ready")
    return html_tables

