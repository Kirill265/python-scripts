import requests
import sys
import os
import pymysql
from pymysql.cursors import DictCursor
import datetime
import calendar
from datetime import timedelta
from TeamWox import TW_text_file
import time
from Telegram_report import telegram_bot
from keepass import key_pass

SQL_DB = 'MySQL DB PROD'
connection = pymysql.connect(
    host=key_pass(SQL_DB).url[:-5],
    port=int(key_pass(SQL_DB).url[-4:]),
    user=key_pass(SQL_DB).username,
    password=key_pass(SQL_DB).password,
    db='my',
    charset='utf8mb4',
    cursorclass=DictCursor
)
now = datetime.datetime.now()
wday = calendar.weekday(now.year, now.month, now.day)
if wday in [1,2,3,4,5]:
    report_date = now - timedelta(days=1)
else:
    sys.exit()
date_from = str(report_date.year)+'-'+str(report_date.month)+'-'+str(report_date.day)+' 00.00.00'
date_to = str(report_date.year)+'-'+str(report_date.month)+'-'+str(report_date.day)+' 23.59.59'
with connection.cursor() as cursor:
    query = """
            SET @@time_zone = \"+3:00\";
    """
    cursor.execute(query)
    query = """
            SELECT c.name
            , SUM(pmd.profit) AS profit_sum
            FROM platform_mt5_deal pmd
            LEFT JOIN account a ON pmd.login = a.login
            LEFT JOIN currency c ON a.currency_id = c.id
            WHERE pmd.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND pmd.symbol IN ('AUDNZDrfd', 'AUDJPYrfd', 'GBPNZDrfd', 'AUDCHFrfd',
                               'CHFJPYrfd', 'EURCHFrfd', 'EURNZDrfd', 'EURCADrfd',
                               'EURNOKrfd', 'GBPCADrfd', 'GBPCHFrfd', 'USDNOKrfd',
                               'USDZARrfd', 'USDMXNrfd')
            GROUP BY a.currency_id;
    """
    cursor.execute(query)
    profit_by = cursor.fetchall()
    sum_profit = 0
    message = ''
    for profit in profit_by:
        if str(profit["name"]) == 'usd':
            sum_profit += round(float(profit["profit_sum"]),2)
        elif str(profit["name"]) == 'eur':
            sum_profit += round(float(profit["profit_sum"]) * 89 / 74.5, 2)
        elif str(profit["name"]) == 'rub':
            sum_profit += round(float(profit["profit_sum"]) / 74.5, 2)
        else:
            Report = """*Оборот в USD по 14 инструментам*

Error: БОЛЬШЕ 3-Х ВАЛЮТ СЧЕТА!!!"""
            telegram_bot(Report)
            sys.exit()
connection.close()

if report_date.month < 10:
    msg_month = '0'+str(report_date.month)
else:
    msg_month = str(report_date.month)
if report_date.day < 10:
    msg_day = '0'+str(report_date.day)
else:
    msg_day = str(report_date.day)


Report_PL = """[PL в USD по 14 инструментам](https://team.alfaforex.com/servicedesk/view/11550)

`За """+msg_day+"""."""+msg_month+"""."""+str(report_date.year)+""":"""
PL = 'За '+msg_day+'.'+msg_month+'.'+str(report_date.year)+':'
if sum_profit > 0:
    Report_PL += """
Клиенты заработали """+str(round(sum_profit,2))+"""`"""
    PL += '<br>Клиенты заработали '+str(round(sum_profit,2))
elif sum_profit < 0:
    Report_PL += """
Клиенты потеряли """+str(round(sum_profit,2))+"""`"""
    PL += '<br>Клиенты потеряли '+str(round(sum_profit,2))
else:
    Report_PL += str(round(sum_profit,2))+"""`"""
    PL += '<br>'+str(round(sum_profit,2))

telegram_bot(Report_PL)
#print(Report_PL)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11550"
message_text = PL
attached_file = ""

TW_text_file(URL_TW,message_text,attached_file)
