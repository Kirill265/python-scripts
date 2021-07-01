import sys
import os
import calendar
import datetime
from datetime import timedelta
import time
import shutil
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from TeamWox import TW_text_file
from Telegram_report import telegram_bot
from like_report_24 import report_generation

agent = "Fresh"
direction = os.path.dirname(os.path.abspath(__file__))+'\\'
utm_txt = open(direction+'utm_'+agent+'.txt', 'r')
sources_utm = utm_txt.read()
utm_txt.close()

month_number_dict = {"1":'января',"2":'февраля',"3":'марта',"4":'апреля',"5":'мая',"6":'июня',"7":'июля',"8":'августа',"9":'сентября',"10":'октября',"11":'ноября',"12":'декабря'} 
now = datetime.datetime.now()
wday = calendar.weekday(now.year, now.month, now.day)
if wday in [4,5,6]:
    report_date = now - timedelta(days=(calendar.weekday(now.year, now.month, now.day)-3))
else:
    report_date = now - timedelta(days=(calendar.weekday(now.year, now.month, now.day)+4))
month = month_number_dict[str(report_date.month)]
if report_date.month < 10:
    sql_month = '0'+str(report_date.month)
else:
    sql_month = str(report_date.month)
if report_date.day < 10:
    msg_to_day = '0'+str(report_date.day)
else:
    msg_to_day = str(report_date.day)
date_from = str(report_date.year)+'-'+sql_month+'-01 00:00:00'
date_to = str(report_date.year)+'-'+sql_month+'-'+msg_to_day+' 23:59:59'
direction = os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts"
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

send_info = {}
send_info["agent"] = agent
send_info["sources_utm"] = sources_utm
send_info["direction"] = direction
send_info["date_from"] = date_from
send_info["date_to"] = date_to
send_info["msg_to_day"] = msg_to_day
send_info["month"] = month
send_info["sql_month"] = sql_month
send_info["report_date"] = report_date
return_info = report_generation(send_info)

Report_fresh = """[Отчет по Fresh](https://team.alfaforex.com/servicedesk/view/11505)

Отчетная дата: *"""+msg_to_day+""" """+month+""" """+str(report_date.year)+"""*.

Счетов: *"""+return_info["acc_count"]+"""*
Торговых операций: *"""+return_info["oper_count"]+"""*
Конвертирующих счетов: *"""+return_info["conv_count"]+"""*

#agentFresh"""

#telegram_bot(Report_fresh)
#print(Report_fresh)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11505"
message_text = ''
attached_file = direction+agent+" 01-"+msg_to_day+" "+month+" "+str(report_date.year)+".xlsx"

#TW_text_file(URL_TW,message_text,attached_file)
