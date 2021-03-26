import requests
import sys
import os
import pymysql
from pymysql.cursors import DictCursor
import xlsxwriter
import datetime
import calendar
from datetime import timedelta
from TeamWox import TW_text_file
import time

def telegram_bot(Report: str):
    api_token = '1362203438:AAFNp5tXRWi6Pn5RkIgqq_7ELHdGTbY9CUs'
    requests.get('https://api.telegram.org/bot{}/sendMessage'.format(api_token), params=dict(
        chat_id='-1001156138635',
        parse_mode= 'Markdown',
        text=Report 
))

hostname='172.16.1.42'
portnum = 3307        
username = 'kcherkasov'
password = '6ne6H7O3ikVUvmDc570AMfmIgTSXZkcOI'
connection = pymysql.connect(
    host=hostname,
    port=portnum,
    user=username,
    password=password,
    db='my',
    charset='utf8mb4',
    cursorclass=DictCursor
)
now = datetime.datetime.now()
monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day)) - timedelta(days=7)
sunday = monday + timedelta(days=6)
friday = monday + timedelta(days=4)
if monday.month < 10:
    msg_from_month = '0'+str(monday.month)
else:
    msg_from_month = str(monday.month)
if monday.day < 10:
    msg_from_day = '0'+str(monday.day)
else:
    msg_from_day = str(monday.day)

if sunday.month < 10:
    msg_to_month = '0'+str(sunday.month)
else:
    msg_to_month = str(sunday.month)
if sunday.day < 10:
    msg_to_day = '0'+str(sunday.day)
else:
    msg_to_day = str(sunday.day)
date_from = str(monday.year)+'-'+str(monday.month)+'-'+str(monday.day)+' 00:00:00'
date_to = str(sunday.year)+'-'+str(sunday.month)+'-'+str(sunday.day)+' 23:59:59'
direction = 'C:/Users/Kirill_Cherkasov/Documents/Reports/Volume USD/'
workbook = xlsxwriter.Workbook(direction+'Оборот USD '+msg_from_day+'.'+msg_from_month+' - '+msg_to_day+'.'+msg_to_month+'.xlsx')
workbook.formats[0].set_font_size(8.5)
workbook.formats[0].set_font_name('Tahoma')
worksheet = workbook.add_worksheet()
worksheet.set_default_row(15)
worksheet.set_row(0, 17)
worksheet.write('A1', 'Symbol')
worksheet.set_column(0, 0, 10)
worksheet.write('B1', 'Volume USD')
worksheet.set_column(1, 1, 15)
with connection.cursor() as cursor:
    query = """
            SET @@time_zone = \"+3:00\";
    """
    cursor.execute(query)
    query = """
            SELECT COUNT(DISTINCT pmd.symbol) AS symbols
            FROM platform_mt5_deal pmd
            WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\";
    """
    cursor.execute(query)
    count_symbol = cursor.fetchone()
    query = """
            SELECT SUBSTRING(pmd.symbol,1,6) AS symbol
            , ROUND(SUM(pmd.volume_usd),0) AS volume_usd 
            FROM platform_mt5_deal pmd
            WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            GROUP BY pmd.symbol
            ORDER BY symbol;
    """
    cursor.execute(query)
    Volumes_USD = cursor.fetchall()
    j = 1
    for Volume_USD in Volumes_USD:
        j += 1
        worksheet.write(f'A{j}', Volume_USD["symbol"])
        worksheet.write(f'B{j}', Volume_USD["volume_usd"])
    workbook.close()
connection.close()

Report_USD = """[Оборот в USD](https://team.alfaforex.com/servicedesk/view/11459)

За период: """+msg_from_day+"""."""+msg_from_month+""" - """+msg_to_day+"""."""+msg_to_month+""".
по """+str(count_symbol["symbols"])+""" инструментам"""

telegram_bot(Report_USD)
#print(Report_USD)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11459"
message_text = ''
attached_file = "C:\\Users\\Kirill_Cherkasov\\Documents\\Reports\\Volume USD\\"+"Оборот USD "+msg_from_day+"."+msg_from_month+" - "+msg_to_day+"."+msg_to_month+".xlsx"

TW_text_file(URL_TW,message_text,attached_file)
