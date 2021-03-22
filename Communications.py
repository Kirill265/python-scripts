import requests
import sys
import os
import pymysql
from pymysql.cursors import DictCursor
import xlsxwriter
import datetime
import calendar
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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
direction = 'C:/Users/Kirill_Cherkasov/Documents/Reports/Communication/'
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

driver = webdriver.Firefox()
driver.get("https://team.alfaforex.com/servicedesk/view/11462")
login_func = driver.find_element_by_id("id_login")
login_func.send_keys("Kirill Cherkasov")
pass_func = driver.find_element_by_name("password")
pass_func.send_keys("Qwerty123")
pass_func.send_keys(Keys.RETURN)
load_checked = 0
while load_checked == 0:
    try:
        iframe = driver.find_elements_by_tag_name('iframe')[0]
        load_checked = 1
    except IndexError:
        time.sleep(2)
driver.switch_to.frame(iframe)
new_comment = driver.find_element_by_link_text("Новый комментарий").click()
attach_files = driver.find_element_by_link_text("Прикрепить файл").click()
attach_file = driver.find_element_by_xpath("//input[@type='file']").send_keys("C:\\Users\\Kirill_Cherkasov\\Documents\\Reports\\Communication\\"+"customers "+str(saturday.year)+"."+sql_month_saturday+"."+sql_day_saturday+" - "+str(friday.year)+"."+sql_month_friday+"."+sql_day_friday+" with status.xlsx")
send_button = driver.find_element_by_xpath("//input[@value='Добавить']").click()
load_checked = 0
while load_checked == 0:
    try:
        find_button = driver.find_element_by_xpath("//input[@value='Добавить']")
        time.sleep(2)
    except NoSuchElementException:
        load_checked = 1
driver.quit()
