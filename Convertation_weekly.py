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
now = datetime.datetime.now()
monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day)) - timedelta(days=7)
sunday = monday + timedelta(days=6)
date_from = str(monday.year)+'-'+str(monday.month)+'-'+str(monday.day)+' 00:00:00'
date_to = str(sunday.year)+'-'+str(sunday.month)+'-'+str(sunday.day)+' 23:59:59'
with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
    query = """
            SELECT  a.currency, date(c.created_at) AS date_conv, ROUND(c.amount_from/100.00,2) AS amount
            FROM convertation c
            LEFT JOIN account a ON c.account_id_from = a.id
            LEFT JOIN account a1 ON c.account_id_to = a1.id
            WHERE 
            c.customer_id NOT IN
            ( 'f1f6abc0-95ad-4b18-91f0-ba9bf38a8c06', -- 200002 0
              '62e245f0-0a7f-4f61-9bfd-08e08fdc72a2', -- 227863 0
              '821d6a05-0915-4fcb-a5b6-9b499d836272', -- 234440 0
              '8b0e3d93-7d29-47ae-a329-a9c0af126b1b', -- 234498 0
              '4f8ef984-41a7-4bad-8d57-275815276051', -- 234507 0
              '93641a11-da6f-45d1-8537-2c5ee6a8e7bb', -- 227957 4
              
              '13c4d52d-74a2-4b29-ae0c-9efac8b50b88', -- 226300 0
              '2a0cad23-3e53-4bdd-8ff7-e7e4c245e24b', -- 230476 0
              'd3cde87b-fa99-482e-aa0a-2d300dc9b20c'  -- 213539 0
            ) 
            AND  c.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND c.status = 3
     """
    cursor.execute(query)
    convertation = cursor.fetchall()
    query = """
            SELECT  a.currency, date(c.created_at) AS date_conv, ROUND(c.amount_from/100.00,2) AS amount
            FROM convertation c
            LEFT JOIN account a ON c.account_id_from = a.id
            LEFT JOIN account a1 ON c.account_id_to = a1.id
            WHERE 
            c.customer_id IN
            ( 'f1f6abc0-95ad-4b18-91f0-ba9bf38a8c06', -- 200002 0
              '62e245f0-0a7f-4f61-9bfd-08e08fdc72a2', -- 227863 0
              '821d6a05-0915-4fcb-a5b6-9b499d836272', -- 234440 0
              '8b0e3d93-7d29-47ae-a329-a9c0af126b1b', -- 234498 0
              '4f8ef984-41a7-4bad-8d57-275815276051', -- 234507 0

              '13c4d52d-74a2-4b29-ae0c-9efac8b50b88', -- 226300 0
              '2a0cad23-3e53-4bdd-8ff7-e7e4c245e24b', -- 230476 0
              'd3cde87b-fa99-482e-aa0a-2d300dc9b20c'  -- 213539 0
            ) 
            AND  c.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND c.status = 3
     """
    cursor.execute(query)
    convertation_markup_0 = cursor.fetchall()
    query = """
            SELECT  a.currency, date(c.created_at) AS date_conv, ROUND(c.amount_from/100.00,2) AS amount
            FROM convertation c
            LEFT JOIN account a ON c.account_id_from = a.id
            LEFT JOIN account a1 ON c.account_id_to = a1.id
            WHERE 
            c.customer_id IN
            ( '93641a11-da6f-45d1-8537-2c5ee6a8e7bb'  -- 227957 4
            ) 
            AND  c.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND c.status = 3
     """
    cursor.execute(query)
    convertation_markup_4 = cursor.fetchall()
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
	    ('49db6685-e38a-4af5-a519-732bbfe5ff28', -- Kirill Cherkasov
	    'f1c3a714-5f01-4bed-9f31-f10cee8a4aee', -- Denis Savostyanov
	    'c54c75bc-33dc-4fb8-966c-693089c6887d', -- Tanya Grineva
	    '775fa215-9a9a-4166-83aa-d47494d3fcf7', -- Ivan Muravev
	    '11fd9048-f703-4b1d-96de-70ee45fc5f84', -- Aleksandr Sazonov
	    'da9285d4-e3c8-487d-af22-957b59791ac5', -- Irina Okhotina
	    '416651f0-414b-4ec9-92cc-d158d0b72475', -- Dima Belyakov
	    '4c0cb0ae-a5fa-44a3-a959-cfe6a3c88414', -- Olga Popova
	    'f1f6abc0-95ad-4b18-91f0-ba9bf38a8c06'  -- Anton Krasov
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
sum_usd_markup_4 = 0.00
for currency in currencys:
    currency_dict[currency["Currency"]][currency["date"]] = currency["value"]
for convert in convertation:
    if convert["currency"] == 'USD':
        sum_usd += round(float(convert["amount"]),2)
    else:
        sum_usd += round(float(convert["amount"])*float(currency_dict[convert["currency"]][convert["date_conv"]]),2)
for convert in convertation_markup_0:
    if convert["currency"] == 'USD':
        sum_usd_markup_0 += round(float(convert["amount"]),2)
    else:
        sum_usd_markup_0 += round(float(convert["amount"])*float(currency_dict[convert["currency"]][convert["date_conv"]]),2)
for convert in convertation_markup_4:
    if convert["currency"] == 'USD':
        sum_usd_markup_4 += round(float(convert["amount"]),2)
    else:
        sum_usd_markup_4 += round(float(convert["amount"])*float(currency_dict[convert["currency"]][convert["date_conv"]]),2)

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

Report_convertations = """[Еженедельный отчет по конвертациям](https://team.alfaforex.com/servicedesk/view/11392)

`C """+msg_from_day+"""."""+msg_from_month+""" по """+msg_to_day+"""."""+msg_to_month+"""

Всего успешных конвертаций - """+str(all_convert["count"])+"""
Успешных конвертаций клиентов - """+str(customer_convert["count"])+"""
Объем $ - """+str(round(sum_usd,2))+"""
Объем с маркапом 0 $ - """+str(round(sum_usd_markup_0,2))+"""
Объем с маркапом 4 $ - """+str(round(sum_usd_markup_4,2))+"""`"""

Converts = 'C '+msg_from_day+'.'+msg_from_month+' по '+msg_to_day+'.'+msg_to_month+'<br><br>Всего успешных конвертаций - '+str(all_convert["count"])+'<br><br>Успешных конвертаций клиентов - '+str(customer_convert["count"])+'<br><br>Объем $ - '+str(round(sum_usd,2))+'<br><br>Объем с маркапом 0 $ - '+str(round(sum_usd_markup_0,2))+'<br><br>Объем с маркапом 4 $ - '+str(round(sum_usd_markup_4,2))

telegram_bot(Report_convertations)
#print(Report_convertations)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11392"
message_text = Converts
attached_file = ""

TW_text_file(URL_TW,message_text,attached_file)
