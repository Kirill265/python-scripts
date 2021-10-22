import sys
import requests
import calendar
import datetime
from datetime import timedelta
import psycopg2
from psycopg2.extras import DictCursor
import time
import os
if __name__ == '__main__':
    sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from TeamWox import TW_text_file
from Telegram_report import telegram_bot
from keepass import key_pass

def Count_deals(d_from = None, d_to = None, name = ""):
    try:
        SQL_DB = 'PotgreSQL DB PROD'
        Postgre_connection = psycopg2.connect(
            host=key_pass(SQL_DB).url[:-5],
            port=int(key_pass(SQL_DB).url[-4:]),
            user=key_pass(SQL_DB).username,
            password=key_pass(SQL_DB).password,
            dbname='mt5_report'
        )
        date_from = str(d_from.date())+' 00:00:00'
        date_to = str(d_to.date())+' 23:59:59'
        with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                    SELECT COUNT(*) as deals_count FROM public.mt5_deals
                    WHERE "Action" IN (0,1)
                    AND "TimeMsc" BETWEEN '"""+date_from+"""' AND '"""+date_to+"""'
             """
            cursor.execute(query)
            deals_count = cursor.fetchone()
        Postgre_connection.close()
        rep_from = date_from.split(' ')[0].split('-')[2]+'.'+date_from.split('-')[1]+'.'+date_from.split('-')[0]
        rep_to = date_to.split(' ')[0].split('-')[2]+'.'+date_to.split('-')[1]+'.'+date_to.split('-')[0]
        Report_countdeals = str(deals_count["deals_count"])
        return Report_countdeals
    except:
        return 'Ошибка при формировании отчета.'

if __name__ == '__main__':
    Count_deals()
