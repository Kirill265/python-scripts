import sys
import os
import datetime
import calendar
from datetime import timedelta
import time
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from TeamWox import TW_text_file
from Telegram_report import telegram_bot
from Volume_USD import volume_USD

now = datetime.datetime.now()
wday = calendar.weekday(now.year, now.month, now.day)
if wday in [1,2,3,4,5]:
    report_date = now - timedelta(days=1)
else:
    sys.exit()

if report_date.month < 10:
    msg_month = '0'+str(report_date.month)
else:
    msg_month = str(report_date.month)
if report_date.day < 10:
    msg_day = '0'+str(report_date.day)
else:
    msg_day = str(report_date.day)

date_from = str(report_date.year)+'-'+str(report_date.month)+'-'+str(report_date.day)+' 00.00.00'
date_to = str(report_date.year)+'-'+str(report_date.month)+'-'+str(report_date.day)+' 23.59.59'

direction = os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts"
direction = os.path.join(direction, 'Reports')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, 'Volume USD')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction += '\\'

send_info = {}
send_info["date_from"] = date_from
send_info["date_to"] = date_to
send_info["direction"] = direction
send_info["msg_from_day"] = ''
send_info["msg_to_day"] = msg_day
send_info["msg_from_month"] = ''
send_info["msg_to_month"] = msg_month
return_info = volume_USD(send_info)

Report_USD = """[Оборот в USD](https://team.alfaforex.com/servicedesk/view/11459)

За день: """+msg_day+"""."""+msg_month+""".
по """+return_info["count_symbol"]+""" инструментам"""

telegram_bot(Report_USD)
#print(Report_USD)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11459"
message_text = ''
attached_file = direction+"Оборот USD "+msg_day+"."+msg_month+".xlsx"

TW_text_file(URL_TW,message_text,attached_file)
