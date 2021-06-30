import sys
import requests
import calendar
import datetime
from datetime import timedelta
import pymysql
from pymysql.cursors import DictCursor
import time
import os
from TeamWox import TW_text_file
from Telegram_report import telegram_bot
from keepass import key_pass

def Active_client(d_from = None, d_to = None, name = ""):
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
        date_from = str(d_from.date())+' 00.00.00'
        date_to = str(d_to.date())+' 23.59.59'
        with my_connection.cursor() as cursor:
            query = """
                    SET @@time_zone = "+3:00";
             """
            cursor.execute(query)
            query = """
                    SELECT COUNT(DISTINCT pmd.login) as count
                    FROM platform_mt5_deal pmd 
                    WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
             """
            cursor.execute(query)
            new_account = cursor.fetchone()
        my_connection.close()
        rep_from = date_from.split(' ')[0].split('-')[2]+'.'+date_from.split('-')[1]+'.'+date_from.split('-')[0]
        rep_to = date_to.split(' ')[0].split('-')[2]+'.'+date_to.split('-')[1]+'.'+date_to.split('-')[0]
        Report_activeaccounts = str(new_account["count"])
        return Report_activeaccounts
    except:
        return 'Ошибка при формировании отчета.'
