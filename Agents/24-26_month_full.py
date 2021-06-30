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
from like_report_new_24 import report_generation
#from like_report_24_temp import report_generation

agent = "24"
direction = os.path.dirname(os.path.abspath(__file__))+'\\'
utm_txt = open(direction+'utm_'+agent+'.txt', 'r')
sources_utm = utm_txt.read()
utm_txt.close()
dir_utm = direction

month_number_dict = {"1":'января',"2":'февраля',"3":'марта',"4":'апреля',"5":'мая',"6":'июня',"7":'июля',"8":'августа',"9":'сентября',"10":'октября',"11":'ноября',"12":'декабря'} 
now = datetime.datetime.now()
report_date = now - timedelta(days=now.day)
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
direction = os.path.join(direction, 'month')
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

Report_24_26 = """[Расчет вознаграждения агента 24](https://team.alfaforex.com/servicedesk/view/11160)

Отчетный месяц: *"""+month+""" """+str(report_date.year)+"""*.

24 агент: *"""+return_info24["acc_count"]+"""* счетов
26 агент: *"""+return_info26["acc_count"]+"""* счетов
Конвертирующих счетов: *"""+str(int(return_info24["conv_count"])+int(return_info26["conv_count"]))+"""*"""

telegram_bot(Report_24_26)
#print(Report_24_26)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11160"
message_text = ''
attached_file = direction+agent24+" 01-"+msg_to_day+" "+month+" "+str(report_date.year)+".xlsx"+"\n"+direction+agent26+" 01-"+msg_to_day+" "+month+" "+str(report_date.year)+".xlsx"

TW_text_file(URL_TW,message_text,attached_file)
