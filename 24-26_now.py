import sys
import os
import calendar
import datetime
from datetime import timedelta
import shutil
from like_report_24 import report_generation
   
agent = "24"
direction = os.path.dirname(os.path.abspath(__file__))+'\\'
utm_txt = open(direction+'utm_'+agent+'.txt', 'r')
sources_utm = utm_txt.read()
utm_txt.close()
dir_utm = direction

month_number_dict = {"1":'январь',"2":'февраль',"3":'март',"4":'апрель',"5":'май',"6":'июнь',"7":'июль',"8":'август',"9":'сентябрь',"10":'октябрь',"11":'ноябрь',"12":'декабрь'} 
now = datetime.datetime.now()
report_date = now - timedelta(days=1)
msg_to_day = str(report_date.day)
month = month_number_dict[str(report_date.month)]
if report_date.month < 10:
    sql_month = '0'+str(report_date.month)
else:
    sql_month = str(report_date.month)
date_from = str(report_date.year)+'-'+sql_month+'-01 00:00:00'
date_to = str(report_date.year)+'-'+sql_month+'-'+msg_to_day+' 23:59:59'

direction = os.path.dirname(os.path.abspath(__file__))
direction = os.path.join(direction, 'Reports')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, agent)
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, 'weekly')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction += '\\'

agent24 = "24, 24a, 24b"
send_info = {}
send_info["agent"] = agent24
send_info["sources_utm"] = sources_utm
send_info["direction"] = direction
send_info["date_from"] = date_from
send_info["date_to"] = date_to
send_info["msg_to_day"] = msg_to_day
send_info["month"] = month
send_info["sql_month"] = sql_month
send_info["report_date"] = report_date
return_info24 = report_generation(send_info)

agent = "26"
utm_txt = open(dir_utm+'utm_'+agent+'.txt', 'r')
sources_utm = utm_txt.read()
utm_txt.close()
agent26 = "26a"
send_info["agent"] = agent26
send_info["sources_utm"] = sources_utm
return_info26 = report_generation(send_info)
