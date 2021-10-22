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

def Neto_balance(d_from = None, d_to = None, name = ""):
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
                    SELECT mg."Currency" as currency, ROUND(SUM(md."Profit")::numeric,2) as neto FROM public.mt5_deals md
                    LEFT JOIN public.mt5_users mu USING("Login")
                    LEFT JOIN public.mt5_groups mg USING("Group")
                    WHERE md."Action" = 2
                    AND md."TimeMsc" BETWEEN '"""+date_from+"""' AND '"""+date_to+"""'
                    GROUP BY mg."Currency"
             """
            cursor.execute(query)
            neto = cursor.fetchall()
            print(neto)
        Postgre_connection.close()
        rep_from = date_from.split(' ')[0].split('-')[2]+'.'+date_from.split('-')[1]+'.'+date_from.split('-')[0]
        rep_to = date_to.split(' ')[0].split('-')[2]+'.'+date_to.split('-')[1]+'.'+date_to.split('-')[0]
        Report_netobalance = ''
        for currency in neto:
            Report_netobalance += '\n'+currency["currency"]+': \t\t'+str(currency["neto"])
        print(Report_netobalance)
        return Report_netobalance
    except:
        return 'Ошибка при формировании отчета.'

if __name__ == '__main__':
    Neto_balance()
