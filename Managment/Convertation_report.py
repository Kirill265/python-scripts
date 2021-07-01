import sys
import os
import shutil
import requests
import calendar
import datetime
from datetime import timedelta
import pymysql
import psycopg2
from psycopg2.extras import DictCursor
from pymysql.cursors import DictCursor
from TeamWox import TW_text_file
import time
from Telegram_report import telegram_bot
from keepass import key_pass
import json

def Convert_period(d_from = None, d_to = None, name = ""):
    try:
        direction = os.path.dirname(os.path.abspath(__file__))+'\\'
        path = direction+"markup.json"
        with open(path, encoding="utf-8") as fjson:
            data = json.load(fjson)
        '''
        markup_0 = data["0"][0]
        markup_1 = data["1"][0]
        #markup_4 = ''
        markup_5 = data["5"][0]
        '''
        af_staff = data["staff"][0]
        '''
        markup_0 = '234440, 234498, 234507, 227863, 200002, 230476, 226300, 213539'
        markup_1 = '227957, 229348'
        #markup_4 = ''
        markup_5 = '236371, 236372, 236357, 236377, 236362, 236369, 232842, 236365, 236369, 228105'
        af_staff = '212691, 215828, 214422, 200004, 200006, 212892, 214061, 200002'
        '''
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
        SQL_DB = 'PotgreSQL DB PROD'
        Postgre_connection = psycopg2.connect(
            host=key_pass(SQL_DB).url[:-5],
            port=int(key_pass(SQL_DB).url[-4:]),
            user=key_pass(SQL_DB).username,
            password=key_pass(SQL_DB).password,
            dbname='finance'
        )
        if name == "":
            now = datetime.datetime.now()
            monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day)) - timedelta(days=7)
            sunday = monday + timedelta(days=6)
            date_from = str(monday.year)+'-'+str(monday.month)+'-'+str(monday.day)+' 00:00:00'
            date_to = str(sunday.year)+'-'+str(sunday.month)+'-'+str(sunday.day)+' 23:59:59'
        else:
            date_from = str(d_from.date())+' 00:00:00'
            date_to = str(d_to.date())+' 23:59:59'
        with my_connection.cursor() as cursor:
            query = """
                    SELECT 
                    CONCAT("'",c.universal_id,"',") AS UID_for_Postgre 
                    FROM customer c
                    WHERE c.id IN ("""+af_staff+""")
             """
            cursor.execute(query)
            UIDS_staff = cursor.fetchall()
            customer_staff = ''
            for UID in UIDS_staff:
                customer_staff += UID["UID_for_Postgre"]
        with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                    SELECT  a.currency, date(c.created_at) AS date_conv, ROUND(c.amount_from/100.00,2) AS amount, COALESCE(mi.markup,mg.name,'default') AS markup
                    FROM convertation c
                    LEFT JOIN account a ON c.account_id_from = a.id
                    LEFT JOIN account a1 ON c.account_id_to = a1.id
                    LEFT JOIN convertation_customer_group_markup ccgm on c.customer_id = ccgm.customer_id
                    LEFT JOIN markup_group mg ON ccgm.group_id = mg.id
                    LEFT JOIN (
                    select ccm.customer_id, 
                    CASE
                    WHEN cl.markup_value=0 THEN 'individ'
                    WHEN cl.markup_value=100 THEN 'staff'
                    WHEN cl.markup_value=500 THEN 'staff_kib'
                    ELSE 'default'
                    END AS markup
                    from convertation_limit cl
                    join convertation_markup_session cms on cl.convertation_markup_session_id = cms.id
                    join convertation_markup cm on cms.convertation_markup_id = cm.id
                    join convertation_customer_markup ccm on cm.id = ccm.id
                    where cm.name like 'individual%'
                    and cm.currency_from = 'RUB' and cm.currency_to = 'USD'
                    and (cms.week_days = '1111111' or cms.week_days = '1111100')
                                ) AS mi on mi.customer_id = c.customer_id
                    WHERE c.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
                    AND c.status = 3
             """
            cursor.execute(query)
            convertation = cursor.fetchall()
            query = """
                    SELECT COUNT(c.id)
                    FROM convertation c
                    WHERE c.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
                    AND c.status = 3
             """
            cursor.execute(query)
            all_convert = cursor.fetchone()
            query = """
                    SELECT COUNT(c.id)
                    FROM convertation c
                    WHERE
                    c.customer_id NOT IN
                    (
                    """+customer_staff[:-1]+"""
                    ) 
                    AND c.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
                    AND c.status = 3
             """
            cursor.execute(query)
            customer_convert = cursor.fetchone()
        Postgre_connection.close()
        with my_connection.cursor() as cursor:
            query = """
                    SET @@time_zone = "+3:00";
             """
            cursor.execute(query)
            query = """
                    SELECT UPPER(c.name) AS Currency, crh.value, crh.date FROM currency_rate_history crh
                    LEFT JOIN currency c ON crh.from_id = c.id
                    WHERE crh.date BETWEEN date(\""""+date_from+"""\") AND date(\""""+date_to+"""\")
                    AND crh.to_id = 1
                    AND c.name IN ('eur', 'rub')
             """
            cursor.execute(query)
            currencys = cursor.fetchall()
        my_connection.close()
        currency_dict = {"RUB":{}, "EUR":{}}
        sum_usd = 0.00
        sum_usd_markup_0 = 0.00
        sum_usd_markup_1 = 0.00
        sum_usd_markup_5 = 0.00
        for currency in currencys:
            currency_dict[currency["Currency"]][currency["date"]] = currency["value"]
        for convert in convertation:
            if convert["currency"] == 'USD':
                if convert["markup"] == 'default':
                    sum_usd += round(float(convert["amount"]),2)
                elif convert["markup"] == 'staff_kib':
                    sum_usd_markup_5 += round(float(convert["amount"]),2)
                elif convert["markup"] == 'staff':
                    sum_usd_markup_1 += round(float(convert["amount"]),2)
                else:
                    sum_usd_markup_0 += round(float(convert["amount"]),2)
            else:
                if convert["markup"] == 'default':
                    sum_usd += round(float(convert["amount"])*float(currency_dict[convert["currency"]][convert["date_conv"]]),2)
                elif convert["markup"] == 'staff_kib':
                    sum_usd_markup_5 += round(float(convert["amount"])*float(currency_dict[convert["currency"]][convert["date_conv"]]),2)
                elif convert["markup"] == 'staff':
                    sum_usd_markup_1 += round(float(convert["amount"])*float(currency_dict[convert["currency"]][convert["date_conv"]]),2)
                else:
                    sum_usd_markup_0 += round(float(convert["amount"])*float(currency_dict[convert["currency"]][convert["date_conv"]]),2)
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
        if name == "":
            Report_convertations = """[Еженедельный отчет по конвертациям](https://team.alfaforex.com/servicedesk/view/11392)

`C """+msg_from_day+"""."""+msg_from_month+""" по """+msg_to_day+"""."""+msg_to_month+"""

Всего успешных конвертаций - """+str(all_convert["count"])+"""
Успешных конвертаций клиентов - """+str(customer_convert["count"])+"""
Объем $ - """+str(round(sum_usd,2))+"""
Объем с маркапом 0 $ - """+str(round(sum_usd_markup_0,2))+"""
Объем с маркапом 1 $ - """+str(round(sum_usd_markup_1,2))+"""
Объем с маркапом 5 $ - """+str(round(sum_usd_markup_5,2))+"""`

#Convertations"""

            Converts = 'C '+msg_from_day+'.'+msg_from_month+' по '+msg_to_day+'.'+msg_to_month+'<br><br>Всего успешных конвертаций - '+str(all_convert["count"])+'<br><br>Успешных конвертаций клиентов - '+str(customer_convert["count"])+'<br><br>Объем $ - '+str(round(sum_usd,2))+'<br><br>Объем с маркапом 0 $ - '+str(round(sum_usd_markup_0,2))+'<br><br>Объем с маркапом 1 $ - '+str(round(sum_usd_markup_1,2))+'<br><br>Объем с маркапом 5 $ - '+str(round(sum_usd_markup_5,2))

            telegram_bot(Report_convertations)
            #print(Report_convertations)

            URL_TW = "https://team.alfaforex.com/servicedesk/view/11392"
            message_text = Converts
            attached_file = ""

            TW_text_file(URL_TW,message_text,attached_file)
        else:
            rep_from = date_from.split(' ')[0].split('-')[2]+'.'+date_from.split('-')[1]+'.'+date_from.split('-')[0]
            rep_to = date_to.split(' ')[0].split('-')[2]+'.'+date_to.split('-')[1]+'.'+date_to.split('-')[0]
            Report_convertations = """Всего успешных конвертаций - """+str(all_convert["count"])+"""\nУспешных конвертаций клиентов - """+str(customer_convert["count"])+"""\nОбъем c маркапом 10: $"""+str(round(sum_usd,2))+"""\nОбъем с маркапом 0: $"""+str(round(sum_usd_markup_0,2))+"""\nОбъем с маркапом 1: $"""+str(round(sum_usd_markup_1,2))+"""\nОбъем с маркапом 5: $"""+str(round(sum_usd_markup_5,2))
        return Report_convertations
    except:
        return 'Ошибка при формировании отчета.'

