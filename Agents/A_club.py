import sys
import requests
import calendar
import datetime
from datetime import timedelta
import xlsxwriter
import pymysql
import psycopg2
from psycopg2.extras import DictCursor
from pymysql.cursors import DictCursor
import time
import os
import shutil
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
SQL_DB = 'PotgreSQL DB PROD'
Postgre_connection = psycopg2.connect(
    host=key_pass(SQL_DB).url[:-5],
    port=int(key_pass(SQL_DB).url[-4:]),
    user=key_pass(SQL_DB).username,
    password=key_pass(SQL_DB).password,
    dbname='finance'
)
month_number_dict = {"1":'январь',"2":'февраль',"3":'март',"4":'апрель',"5":'май',"6":'июнь',"7":'июль',"8":'август',"9":'сентябрь',"10":'октябрь',"11":'ноябрь',"12":'декабрь'} 
now = datetime.datetime.now()
report_date = now - timedelta(days=now.day)
month = month_number_dict[str(report_date.month)]
if report_date.month < 10:
    sql_month = '0'+str(report_date.month)
else:
    sql_month = str(report_date.month)
date_from = str(report_date.year)+'-'+sql_month+'-01 00:00:00'
date_to = str(report_date.year)+'-'+sql_month+'-'+str(report_date.day)+' 23:59:59'
direction = os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts"
direction = os.path.join(direction, 'Reports')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, 'A-club')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction += '\\'
workbook = xlsxwriter.Workbook(direction+'А-Клуб 01'+'.'+sql_month+'.'+str(report_date.year)+'-'+str(report_date.day)+'.'+sql_month+'.'+str(report_date.year)+'.xlsx')
workbook.formats[0].set_font_size(8.5)
workbook.formats[0].set_font_name('Tahoma')
wrap_format = workbook.add_format({'border': 1})
wrap_format.set_text_wrap()
wrap_format.set_font_size(8.5)
wrap_format.set_font_name('Tahoma')
bold_blue = workbook.add_format({'border': 1, 'bold': True, 'fg_color': '#DDEBF7', 'align': 'center','valign': 'vcenter'})
bold_blue.set_font_size(8.5)
bold_blue.set_font_name('Tahoma')
wrap_format_bold_blue = workbook.add_format({'border': 1, 'bold': True, 'fg_color': '#DDEBF7', 'align': 'center','valign': 'vcenter'})
wrap_format_bold_blue.set_text_wrap()
wrap_format_bold_blue.set_font_size(8.5)
wrap_format_bold_blue.set_font_name('Tahoma')
number_format = workbook.add_format({'border': 1, 'num_format': '0.00','align': 'right'})
number_format.set_font_size(8.5)
number_format.set_font_name('Tahoma')
border_format = workbook.add_format({'border': 1})
border_format.set_font_size(8.5)
border_format.set_font_name('Tahoma')
worksheet_oper = workbook.add_worksheet('Торговые операции')
worksheet_oper.set_default_row(22)
worksheet_oper.set_row(0, 20)
worksheet_oper.write('A1', 'Дата', bold_blue)
worksheet_oper.set_column(0, 0, 15)
worksheet_oper.write('B1', 'ЛК', bold_blue)
worksheet_oper.set_column(1, 1, 16)
worksheet_oper.write('C1', 'ФИО', bold_blue)
worksheet_oper.set_column(2, 2, 25)
worksheet_oper.write('D1', 'Торговый счет', bold_blue)
worksheet_oper.set_column(3, 3, 15)
worksheet_oper.write('E1', 'Баланс\n в валюте счета', wrap_format_bold_blue)
worksheet_oper.set_column(4, 4, 20)
worksheet_oper.write('F1', 'Валюта счета', bold_blue)
worksheet_oper.write('G1', 'Оборот в USD', bold_blue)
worksheet_oper.set_column(5, 6, 15)
worksheet_oper.write('H1', 'Доход в USD', bold_blue)
worksheet_oper.set_column(7, 7, 26)
worksheet_oper.write('I1', 'А-клуб', bold_blue)
worksheet_oper.set_column(8, 8, 24)
worksheet_conv = workbook.add_worksheet('Конвертации')
worksheet_conv.set_default_row(22)
worksheet_conv.set_row(0, 30)
worksheet_conv.write('A1', 'ЛК', bold_blue)
worksheet_conv.set_column(0, 0, 16)
worksheet_conv.write('B1', 'ФИО', bold_blue)
worksheet_conv.set_column(1, 1, 25)
worksheet_conv.write('C1', 'Счет списания', bold_blue)
worksheet_conv.write('D1', 'Счет зачисления', bold_blue)
worksheet_conv.set_column(2, 3, 20)
worksheet_conv.write('E1', 'Сумма списания / Оборот\n в валюте счета\n списания',wrap_format_bold_blue)
worksheet_conv.set_column(4, 4, 25)
worksheet_conv.write('F1', 'Валюта списания', bold_blue)
worksheet_conv.set_column(5, 5, 19)
worksheet_conv.write('G1', 'Сумма зачисления\n в валюте счета\n зачисления',wrap_format_bold_blue)
worksheet_conv.set_column(6, 6, 25)
worksheet_conv.write('H1', 'Валюта зачсления', bold_blue)
worksheet_conv.set_column(7, 7, 19)
worksheet_conv.write('I1', 'Доход со сделки\n в валюте счета\n зачисления',wrap_format_bold_blue)
worksheet_conv.write('J1', 'Доход со сделки\n в USD',wrap_format_bold_blue)
worksheet_conv.set_column(8, 9, 22)
worksheet_conv.write('K1', 'Дата операции', bold_blue)
worksheet_conv.set_column(10, 10, 20)
worksheet_balance = workbook.add_worksheet('Баллансы')
worksheet_balance.set_default_row(22)
worksheet_balance.set_row(0, 20)
worksheet_balance.write('A1', 'Дата', bold_blue)
worksheet_balance.set_column(0, 0, 15)
worksheet_balance.write('B1', 'ЛК', bold_blue)
worksheet_balance.set_column(1, 1, 16)
worksheet_balance.write('C1', 'ФИО', bold_blue)
worksheet_balance.set_column(2, 2, 25)
worksheet_balance.write('D1', 'Торговый счет', bold_blue)
worksheet_balance.write('E1', 'Баланс\n в валюте счета', wrap_format_bold_blue)
worksheet_balance.write('F1', 'Валюта счета', bold_blue)
worksheet_balance.set_column(3, 5, 20)
worksheet_balance.write('G1', 'А-клуб', bold_blue)
worksheet_balance.set_column(6, 6, 24)
with my_connection.cursor() as cursor:
    query = """
            SET @@time_zone = "+3:00";
     """
    cursor.execute(query)
    query = """
            SELECT
            date(NOW()) Date_report
            , a.customer_id
            , concat(ci.last_name_ru," ",ci.first_name_ru," ",middle_name_ru) AS FIO
            , a.login
            , a.amount AS balance
            , UPPER(c.name) AS currency
            , SUM(pmd.volume_usd) AS volume_in_usd
            , SUM(pmd.profit) AS Profit_without_swap
            , ad.name AS AClub
            FROM platform_mt5_deal pmd
            LEFT JOIN account a ON pmd.login = a.login
            LEFT JOIN aclub_manager_client amc ON a.customer_id = amc.customer_id
            LEFT JOIN aclub_manager am ON amc.manager_id = am.id
            LEFT JOIN aclub_division ad ON am.id_division_aclub = ad.id
            LEFT JOIN customer_individual ci ON a.customer_id = ci.customer_id
            LEFT JOIN currency c ON a.currency_id = c.id
            WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            AND amc.id IS NOT NULL
            AND amc.is_not_pay = 0
            GROUP BY a.login
     """
    cursor.execute(query)
    opers = cursor.fetchall()
    i = 1
    for oper in opers:
        i += 1
        worksheet_oper.write(f'A{i}', str(oper["Date_report"]), border_format)
        worksheet_oper.write(f'B{i}', oper["customer_id"], border_format)
        worksheet_oper.write(f'C{i}', oper["FIO"],wrap_format)
        worksheet_oper.write(f'D{i}', oper["login"], border_format)
        worksheet_oper.write(f'E{i}', oper["balance"], number_format)
        worksheet_oper.write(f'F{i}', oper["currency"], border_format)
        worksheet_oper.write(f'G{i}', oper["volume_in_usd"], number_format)
        worksheet_oper.write(f'H{i}', oper["Profit_without_swap"], number_format)
        worksheet_oper.write(f'I{i}', oper["AClub"],wrap_format)
    query = """
            SELECT 
            date(NOW()) AS Date_report
            , c.universal_id
            , a.customer_id
            , CONCAT(ci.last_name_ru," ",ci.first_name_ru," ",middle_name_ru) AS FIO
            , a.login
            , a.amount
            , UPPER(c1.name) AS currency
            , ad.name AS AClub
            , CONCAT("'",c.universal_id,"',") AS UID_for_Postgre
            FROM
            account a
            LEFT JOIN customer c ON a.customer_id = c.id
            LEFT JOIN customer_individual ci ON c.id = ci.customer_id
            LEFT JOIN aclub_manager_client amc ON c.id = amc.customer_id
            LEFT JOIN aclub_manager am ON amc.manager_id = am.id
            LEFT JOIN aclub_division ad ON am.id_division_aclub = ad.id
            LEFT JOIN currency c1 ON a.currency_id = c1.id
            WHERE amc.is_not_pay = 0
    """
    cursor.execute(query)
    balances = cursor.fetchall()
    customer_id = ''
    customer_dict = {}
    j = 1
    for balance in balances:
        j += 1
        customer_id += balance["UID_for_Postgre"]
        customer_dict[balance["universal_id"]] = {"LK":balance["customer_id"], "FIO":balance["FIO"]}
        worksheet_balance.write(f'A{j}', str(balance["Date_report"]), border_format)
        worksheet_balance.write(f'B{j}', balance["customer_id"], border_format)
        worksheet_balance.write(f'C{j}', balance["FIO"], wrap_format)
        worksheet_balance.write(f'D{j}', balance["login"], border_format)
        worksheet_balance.write(f'E{j}', balance["amount"], number_format)
        worksheet_balance.write(f'F{j}', balance["currency"], border_format)
        worksheet_balance.write(f'G{j}', balance["AClub"], wrap_format)
    query = """
            SELECT UPPER(c.name) AS Currency, crh.value, crh.date FROM currency_rate_history crh
            LEFT JOIN currency c ON crh.from_id = c.id
            WHERE crh.date BETWEEN date(\""""+date_from+"""\") AND date(\""""+date_to+"""\")
            AND crh.to_id = 1
            AND c.name IN ('eur', 'rub')
    """
    cursor.execute(query)
    currencys = cursor.fetchall()
    currency_dict = {"RUB":{}, "EUR":{}}
    sum_usd = 0.00
    for currency in currencys:
        currency_dict[currency["Currency"]][currency["date"]] = currency["value"]

with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
    query = """
            SELECT
            a_from.customer_id
            , a_from.login AS login_from
            , a_to.login AS login_to
            , ROUND(c.amount_from / 100.0, 2) AS amount_from
            , a_from.currency AS currency_from
            , ROUND(c.amount_to / 100.0, 2) AS amount_to
            , a_to.currency AS currency_to
            ,CASE
            WHEN c.operation_type = 'BUY' THEN ROUND(c.amount_from / c.market_rate / 100.0, 2) - ROUND(c.amount_to / 100.0, 2)
            WHEN c.operation_type = 'SELL' THEN ROUND(c.amount_from * c.market_rate / 100.0, 2) - ROUND(c.amount_to / 100.0, 2) 
            END AS "Profit"
            , DATE(c.updated_at) AS date_oper
            FROM convertation c
            LEFT JOIN account a_from ON c.account_id_from = a_from.id
            LEFT JOIN account a_to ON c.account_id_to = a_to.id
            WHERE c.customer_id IN (
            """+customer_id[:-1]+"""
            )
            AND c.updated_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND c.status = 3
            ORDER BY c.updated_at
    """
    cursor.execute(query)
    convertations = cursor.fetchall()
    k = 1
    for convertation in convertations:
        k += 1
        worksheet_conv.write(f'A{k}', customer_dict[convertation["customer_id"]]["LK"], border_format)
        worksheet_conv.write(f'B{k}', customer_dict[convertation["customer_id"]]["FIO"],wrap_format)
        worksheet_conv.write(f'C{k}', convertation["login_from"], border_format)
        worksheet_conv.write(f'D{k}', convertation["login_to"], border_format)
        worksheet_conv.write(f'E{k}', convertation["amount_from"], number_format)
        worksheet_conv.write(f'F{k}', convertation["currency_from"], border_format)
        worksheet_conv.write(f'G{k}', convertation["amount_to"], number_format)
        worksheet_conv.write(f'H{k}', convertation["currency_to"], border_format)
        worksheet_conv.write(f'I{k}', convertation["Profit"], number_format)
        if convertation["currency_to"] == 'USD':
            worksheet_conv.write(f'J{k}', float(convertation["Profit"]), number_format)
        else:
            worksheet_conv.write(f'J{k}', round(float(convertation["Profit"])*float(currency_dict[convertation["currency_to"]][convertation["date_oper"]]),2), number_format)
        worksheet_conv.write(f'K{k}', str(convertation["date_oper"]), border_format)
    query = """
            SELECT
            COUNT(DISTINCT c.customer_id) AS count_cnv
            FROM convertation c
            WHERE c.customer_id IN (
            """+customer_id[:-1]+"""
            )
            AND c.updated_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND c.status = 3
    """
    cursor.execute(query)
    count_conv = cursor.fetchone()
Postgre_connection.close()
my_connection.close()
workbook.close()

Report_AClub = """[Расчет вознаграждения А-клуб](https://team.alfaforex.com/servicedesk/view/11347)

Отчетный месяц: *"""+month+""" """+str(report_date.year)+"""*.

Торговые операции у *"""+str(len(opers))+""" / """+ str(len(balances))+"""* клиентов.
Конвертаций *"""+str(len(convertations))+"""* у *"""+str(count_conv["count_cnv"])+""" / """+ str(len(balances))+"""* клиентов."""

telegram_bot(Report_AClub)
#print(Report_AClub)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11347"
message_text = ''
attached_file = direction+"А-Клуб 01"+"."+sql_month+"."+str(report_date.year)+"-"+str(report_date.day)+"."+sql_month+"."+str(report_date.year)+".xlsx"

TW_text_file(URL_TW,message_text,attached_file)
