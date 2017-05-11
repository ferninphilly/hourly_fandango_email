#!/usr/bin/env python3
import visualizations.visualize as vz

#This is where we will put the values in order for the email
def create_email_html():
    html_dict= vz.html_dict()
    email_html = html_dict['summary'].getvalue()
    email_html += html_dict['cif_update'].getvalue()
    email_html += '<center>' + html_dict['line_chart'].img() + '</center>'
    email_html += html_dict['hourly_projection_table'].getvalue()
    email_html += '</br><center>' + html_dict['film_bar_chart'].img() + '</center>'
    email_html += html_dict['hourly_film_summary_table'].getvalue()
    email_html += html_dict['daily_film_summary_table'].getvalue()
    email_html += '</br><center>' + html_dict['channel_bar_chart'].img() + '</center>'
    email_html += html_dict['channel_last_hour_table'].getvalue()
    email_html += html_dict['channel_today_table'].getvalue()
    email_html += '</br><center>' + html_dict['month_bar_chart'].img() + '</center>'
    return email_html, html_dict['subject_line']

    

            
    
