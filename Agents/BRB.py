import requests
import sys
import os
import pymysql
from pymysql.cursors import DictCursor
import xlsxwriter
import datetime
#import calendar
from datetime import timedelta
import time
import shutil
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from TeamWox import TW_text_file
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
month_number_dict = {"1":'январь',"2":'февраль',"3":'март',"4":'апрель',"5":'май',"6":'июнь',"7":'июль',"8":'август',"9":'сентябрь',"10":'октябрь',"11":'ноябрь',"12":'декабрь'} 
now = datetime.datetime.now()
report_date = now - timedelta(days=now.day)
month = month_number_dict[str(report_date.month)]
if report_date.month < 10:
    sql_month = '0'+str(report_date.month)
else:
    sql_month = str(report_date.month)
date_from = str(report_date.year)+'-'+sql_month+'-01 00.00.00'
date_to = str(report_date.year)+'-'+sql_month+'-'+str(report_date.day)+' 23.59.59'
direction = os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts"
direction = os.path.join(direction, 'Reports')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, 'BRB')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction += '\\'
workbook = xlsxwriter.Workbook(direction+'01-'+str(report_date.day)+'.'+sql_month+'.'+str(report_date.year)+'.xlsx')
workbook.formats[0].set_font_size(8.5)
workbook.formats[0].set_font_name('Tahoma')
wrap_format = workbook.add_format()
wrap_format.set_text_wrap()
wrap_format.set_font_size(8.5)
wrap_format.set_font_name('Tahoma')
worksheet = workbook.add_worksheet()
worksheet.set_default_row(22)
worksheet.set_row(0, 20)
worksheet.write('A1', 'Личный кабинет')
worksheet.set_column(0, 0, 15)
worksheet.write('B1', 'Дата регистрации')
worksheet.set_column(1, 1, 20)
worksheet.write('C1', 'ФИО клиента')
worksheet.set_column(2, 2, 30)
worksheet.write('D1', 'Номер рамочного договора')
worksheet.set_column(3, 3, 24)
worksheet.write('E1', 'Логин торгового счета')
worksheet.set_column(4, 4, 21)
worksheet.write('F1', 'Дата первого пополнения')
worksheet.set_column(5, 5, 24)
worksheet.write('G1', 'Дата совершения первой сделки')
worksheet.set_column(6, 6, 24)
with connection.cursor() as cursor:
    query = """
            SET @@time_zone = \"+3:00\";
    """
    cursor.execute(query)
    query = """
            SELECT
            c.id AS LK,  c.created_at AS registration_date,  
            CONCAT(ci.last_name_ru, ' ', ci.first_name_ru, ' ',ifnull(ci.middle_name_ru,"")) AS FIO,
            cc.contract_code, pmd.login,
            IFNULL(depo.depo_executed_at,'null') AS first_deposit, pmd.created_at AS first_deal
            FROM customer c 
            LEFT JOIN customer_individual ci ON c.id = ci.customer_id
            -- дата первой активности клиента по любому счету
            LEFT JOIN 
            (
            SELECT a.customer_id, MIN(pmd.id) AS 'id_first_action'
            FROM platform_mt5_deal pmd 
            LEFT JOIN account a ON pmd.login = a.login
            GROUP BY a.customer_id
            ) AS first_action ON c.id = first_action.customer_id    
            LEFT JOIN platform_mt5_deal pmd ON first_action.id_first_action = pmd.id
            LEFT JOIN account a ON pmd.login = a.login
            -- дата первого депозита на любой из счетов
            LEFT JOIN
            (
            SELECT dr.account_id, MIN(dr.executed_at) AS 'depo_executed_at'
            FROM deposit_request dr 
            WHERE dr.status_id = 10 -- done
            GROUP BY dr.account_id
            ) AS depo ON a.id = depo.account_id
            LEFT JOIN customer_contract cc ON a.customer_contract_id = cc.id
            WHERE c.source_id = 14 --     acr привлеченных через Альфа-Клик
            HAVING pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\";
    """
    cursor.execute(query)
    BRB_customers = cursor.fetchall()
    j = 1
    for BRB_customer in BRB_customers:
        j += 1
        worksheet.write(f'A{j}', BRB_customer["LK"])
        worksheet.write(f'B{j}', str(BRB_customer["registration_date"]))
        worksheet.write(f'C{j}', BRB_customer["FIO"], wrap_format)
        worksheet.write(f'D{j}', BRB_customer["contract_code"])
        worksheet.write(f'E{j}', BRB_customer["login"])
        worksheet.write(f'F{j}', str(BRB_customer["first_deposit"]))
        worksheet.write(f'G{j}', str(BRB_customer["first_deal"]))
    workbook.close()
connection.close()

Report_BRB = """[Расчет вознаграждения БРБ](https://team.alfaforex.com/servicedesk/view/10945)

Отчетный месяц: *"""+month+""" """+str(report_date.year)+"""*.

Выплата за *"""+str(len(BRB_customers))+"""* клиентов."""

telegram_bot(Report_BRB)
#print(Report_BRB)

URL_TW = "https://team.alfaforex.com/servicedesk/view/10945"
message_text = ''
attached_file = direction+"01-"+str(report_date.day)+"."+sql_month+"."+str(report_date.year)+".xlsx"

TW_text_file(URL_TW,message_text,attached_file)
