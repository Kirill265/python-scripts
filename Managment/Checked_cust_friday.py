import sys
import os
import requests
import calendar
import datetime
from datetime import timedelta
import pymysql
from pymysql.cursors import DictCursor
import time
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from TeamWox import TW_text_file
from Telegram_report import telegram_bot
from keepass import key_pass

SQL_DB = 'MySQL DB PROD'
my_connection = pymysql.connect(
    host=key_pass(SQL_DB).url[:-5],
    port=int(key_pass(SQL_DB).url[-4:]),
    user=key_pass(SQL_DB).username,
    password=key_pass(SQL_DB).password,
    db='my',
    charset='utf8mb4',
    cursorclass=DictCursor
)

now = datetime.datetime.now()
monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day))
friday = monday + timedelta(days=4)
date_from = str(monday.year)+'-'+str(monday.month)+'-'+str(monday.day)+' 00:00:00'
date_to = str(friday.year)+'-'+str(friday.month)+'-'+str(friday.day)+' 15:59:59'

with my_connection.cursor() as cursor:
    query = """
            SET @@time_zone = "+3:00";
     """
    cursor.execute(query)
    query = """
            SELECT 
            lb.manager_id AS manager
            , COUNT(lb.id) AS checked
            FROM 
            (SELECT 
            lb.customer_id, 
            MIN(lb.id) AS 'first_checked'
            FROM log_backend lb
            WHERE lb.event_id = 7
            AND lb.message LIKE '%to «Checked»%'
            GROUP BY lb.customer_id) AS fst_chk
            LEFT JOIN log_backend lb ON lb.id = fst_chk.first_checked
            WHERE lb.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            GROUP BY lb.manager_id
            ORDER BY lb.manager_id
     """
    cursor.execute(query)
    checked_for_week = cursor.fetchall()
my_connection.close()
if checked_for_week == ():
    sys.exit()

manager = {}
for manager_check in checked_for_week:
    manager[str(manager_check["manager"])] = int(manager_check["checked"])

if monday.month < 10:
    msg_from_month = '0'+str(monday.month)
else:
    msg_from_month = str(monday.month)
if monday.day < 10:
    msg_from_day = '0'+str(monday.day)
else:
    msg_from_day = str(monday.day)

if friday.month < 10:
    msg_to_month = '0'+str(friday.month)
else:
    msg_to_month = str(friday.month)
if friday.day < 10:
    msg_to_day = '0'+str(friday.day)
else:
    msg_to_day = str(friday.day)

Report_checked = """[Срез по проверенным клиентам](https://team.alfaforex.com/servicedesk/view/11332)

`Для ПОД/ФТ

"""+msg_from_day+"""."""+msg_from_month+"""."""+str(monday.year)+""" - """+msg_to_day+"""."""+msg_to_month+"""."""+str(friday.year)+""" 16:00:00
"""
Checked = 'Для ПОД/ФТ<br><br>'+msg_from_day+'.'+msg_from_month+'.'+str(monday.year)+' - '+msg_to_day+'.'+msg_to_month+'.'+str(friday.year)+' 16:00:00<br>'
for key in manager:
    Report_checked += """
""" + key + """: """ + str(manager[key])
    Checked+='<br>' + key + ': ' + str(manager[key])
Report_checked += """`"""

telegram_bot(Report_checked)
#print(Report_checked)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11332"
message_text = Checked
attached_file = ""

TW_text_file(URL_TW,message_text,attached_file)
