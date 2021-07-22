import sys
import os
import requests
import calendar
import datetime
from datetime import timedelta
import pymysql
from pymysql.cursors import DictCursor
import time
if __name__ == '__main__':
    sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from Telegram_report import telegram_bot
from TeamWox import TW_text_file
from keepass import key_pass

def New_client(d_from = None, d_to = None, name = ""):
    try:
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
        if name == "":
            now = datetime.datetime.now()
            monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day)) - timedelta(days=7)
            sunday = monday + timedelta(days=6)
            friday = monday + timedelta(days=4)
            date_from = str(monday.year)+'-'+str(monday.month)+'-'+str(monday.day)+' 00:00:00'
            date_to = str(sunday.year)+'-'+str(sunday.month)+'-'+str(sunday.day)+' 23:59:59'
        else:
            date_from = str(d_from.date())+' 00.00.00'
            date_to = str(d_to.date())+' 23.59.59'
        
        with my_connection.cursor() as cursor:
            query = """
                    SET @@time_zone = "+3:00";
             """
            cursor.execute(query)
            query = """
                    SELECT COUNT(new_ac.login) AS count FROM
                    (
                    SELECT pmd.login, MIN(pmd.created_at) AS date
                    FROM platform_mt5_deal pmd 
                    GROUP BY pmd.login
                    HAVING date BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
                    ) AS new_ac
             """
            cursor.execute(query)
            new_account = cursor.fetchone()
        my_connection.close()
        if name == "":
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

            Report_newaccounts = """[Кол-во новых активных клиентов](https://team.alfaforex.com/servicedesk/view/10999)

`C """+msg_from_day+"""."""+msg_from_month+""" по """+msg_to_day+"""."""+msg_to_month+""" - """+str(new_account["count"])+"""`

#NewClients"""

            new_accounts = 'C '+msg_from_day+'.'+msg_from_month+' по '+msg_to_day+'.'+msg_to_month+' - '+str(new_account["count"])

            telegram_bot(Report_newaccounts)
            #print(Report_newaccounts)

            URL_TW = "https://team.alfaforex.com/servicedesk/view/10999"
            message_text = new_accounts
            attached_file = ""

            TW_text_file(URL_TW,message_text,attached_file)
        else:
            rep_from = date_from.split(' ')[0].split('-')[2]+'.'+date_from.split('-')[1]+'.'+date_from.split('-')[0]
            rep_to = date_to.split(' ')[0].split('-')[2]+'.'+date_to.split('-')[1]+'.'+date_to.split('-')[0]
            Report_newaccounts = str(new_account["count"])
        return Report_newaccounts
    except:
        return 'Ошибка при формировании отчета.'

if __name__ == '__main__':
    New_client()
