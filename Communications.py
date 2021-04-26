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
import shutil
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
monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day))
friday = monday - timedelta(days=3)
saturday = monday - timedelta(days=9)
if friday.month < 10:
    sql_month_friday = '0'+str(friday.month)
else:
    sql_month_friday = str(friday.month)
if saturday.month < 10:
    sql_month_saturday = '0'+str(saturday.month)
else:
    sql_month_saturday = str(saturday.month)
if friday.day < 10:
    sql_day_friday = '0'+str(friday.day)
else:
    sql_day_friday = str(friday.day)
if saturday.day < 10:
    sql_day_saturday = '0'+str(saturday.day)
else:
    sql_day_saturday = str(saturday.day) 
date_from = str(saturday.year)+'-'+sql_month_saturday+'-'+sql_day_saturday+' 00.00.00'
date_to = str(friday.year)+'-'+sql_month_friday+'-'+sql_day_friday+' 23.59.59'
direction = os.path.dirname(os.path.abspath(__file__))
direction = os.path.join(direction, 'Reports')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, 'Communication')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction += '\\'
workbook = xlsxwriter.Workbook(direction+'customers '+str(saturday.year)+'.'+sql_month_saturday+'.'+sql_day_saturday+' - '+str(friday.year)+'.'+sql_month_friday+'.'+sql_day_friday+' with status.xlsx')
workbook.formats[0].set_font_size(11)
workbook.formats[0].set_font_name('Calibri')
bold_blue = workbook.add_format({'border': 1, 'bold': True, 'fg_color': '#DDEBF7', 'align': 'center','valign': 'vcenter'})
bold_blue.set_font_size(11)
bold_blue.set_font_name('Calibri')
wrap_format_bold_blue = workbook.add_format({'border': 1, 'bold': True, 'fg_color': '#DDEBF7', 'align': 'center','valign': 'vcenter'})
wrap_format_bold_blue.set_text_wrap()
wrap_format_bold_blue.set_font_size(11)
wrap_format_bold_blue.set_font_name('Calibri')
border_format = workbook.add_format({'border': 1})
border_format.set_font_size(11)
border_format.set_font_name('Calibri')
worksheet = workbook.add_worksheet()
worksheet.set_default_row(15)
worksheet.set_row(0, 32)
worksheet.write('A1', 'ЛК', bold_blue)
worksheet.set_column(0, 0, 15)
worksheet.write('B1', 'Дата регистрации', bold_blue)
worksheet.set_column(1, 1, 23)
worksheet.write('C1', 'Менеджер', bold_blue)
worksheet.set_column(2, 2, 20)
worksheet.write('D1', 'Текущий статус\n('+str(now)[:16]+')', wrap_format_bold_blue)
worksheet.set_column(3, 3, 25)
worksheet.write('E1', 'Дата последней исходящей коммуникации', wrap_format_bold_blue)
worksheet.set_column(4, 4, 32)
worksheet.write('F1', 'Тип коммуникации', bold_blue)
worksheet.set_column(5, 5, 24)
with connection.cursor() as cursor:
    query = """
            SET @@time_zone = \"+3:00\";
    """
    cursor.execute(query)
    query = """
            SELECT COUNT(c.id) AS checked
            FROM customer c
            LEFT JOIN customer_status cs ON c.status_id = cs.id
            LEFT JOIN (
            SELECT * FROM communication c1
            WHERE c1.id IN (
            SELECT MAX(c2.id) FROM communication c2
            -- WHERE c2.direction_id = 2
            GROUP BY c2.customer_id)
            ) AS lastcom ON lastcom.customer_id = c.id
            LEFT JOIN communication_type ct ON lastcom.type_id = ct.id
            WHERE c.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            AND cs.name = 'checked';
    """
    cursor.execute(query)
    Customers_checked = cursor.fetchone()
    query = """
            SELECT COUNT(c.id) AS without
            FROM customer c
            LEFT JOIN customer_status cs ON c.status_id = cs.id
            LEFT JOIN (
            SELECT * FROM communication c1
            WHERE c1.id IN (
            SELECT MAX(c2.id) FROM communication c2
            -- WHERE c2.direction_id = 2
            GROUP BY c2.customer_id)
            ) AS lastcom ON lastcom.customer_id = c.id
            LEFT JOIN communication_type ct ON lastcom.type_id = ct.id
            WHERE c.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            AND cs.name != 'checked'
            AND lastcom.created_at IS NULL;
    """
    cursor.execute(query)
    Customers_without = cursor.fetchone()
    query = """
            SELECT c.id, c.created_at, m.login , cs.name,
            IFNULL(lastcom.created_at,'не было') AS last_com
            , IFNULL(ct.name,'') AS type_com
            FROM customer c
            LEFT JOIN customer_status cs ON c.status_id = cs.id
            LEFT JOIN (
            SELECT * FROM communication c1
            WHERE c1.id IN (
            SELECT MAX(c2.id) FROM communication c2
            -- WHERE c2.direction_id = 2
            GROUP BY c2.customer_id)
            ) AS lastcom ON lastcom.customer_id = c.id
            LEFT JOIN communication_type ct ON lastcom.type_id = ct.id
            LEFT JOIN manager m ON c.manager_id = m.id
			WHERE c.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\";
    """
    cursor.execute(query)
    Com_customers = cursor.fetchall()
    j = 1
    for Com_customer in Com_customers:
        j += 1
        worksheet.write(f'A{j}', Com_customer["id"], border_format)
        worksheet.write(f'B{j}', str(Com_customer["created_at"]), border_format)
        worksheet.write(f'C{j}', Com_customer["login"], border_format)
        worksheet.write(f'D{j}', Com_customer["name"], border_format)
        worksheet.write(f'E{j}', str(Com_customer["last_com"]), border_format)
        worksheet.write(f'F{j}', Com_customer["type_com"], border_format)
    workbook.close()
connection.close()

Report_Communicate = """[Недельный отчет по коммуникациям](https://team.alfaforex.com/servicedesk/view/11462)

За период: """+sql_day_saturday+"""."""+sql_month_saturday+"""."""+str(saturday.year)+""" - """+sql_day_friday+"""."""+sql_month_friday+"""."""+str(friday.year)+""".

Новых клиентов: *"""+str(len(Com_customers))+"""*
Проверено: *"""+str(Customers_checked["checked"])+"""*
Без коммуникаций, не проверено: *"""+str(Customers_without["without"])+"""*."""

telegram_bot(Report_Communicate)
#print(Report_Communicate)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11462"
message_text = ''
attached_file = direction+"customers "+str(saturday.year)+"."+sql_month_saturday+"."+sql_day_saturday+" - "+str(friday.year)+"."+sql_month_friday+"."+sql_day_friday+" with status.xlsx"

TW_text_file(URL_TW,message_text,attached_file)
