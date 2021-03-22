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
wday = calendar.weekday(now.year, now.month, now.day)
if wday in [1,2,3,4,5]:
    report_date = now - timedelta(days=1)
else:
    sys.exit()

if report_date.month < 10:
    msg_month = '0'+str(report_date.month)
else:
    msg_month = str(report_date.month)
if report_date.day < 10:
    msg_day = '0'+str(report_date.day)
else:
    msg_day = str(report_date.day)

date_from = str(report_date.year)+'-'+str(report_date.month)+'-'+str(report_date.day)+' 00.00.00'
date_to = str(report_date.year)+'-'+str(report_date.month)+'-'+str(report_date.day)+' 23.59.59'

direction = 'C:/Users/Kirill_Cherkasov/Documents/Reports/Volume USD/'
workbook = xlsxwriter.Workbook(direction+'Оборот USD '+msg_day+'.'+msg_month+'.xlsx')
workbook.formats[0].set_font_size(8.5)
workbook.formats[0].set_font_name('Tahoma')
worksheet = workbook.add_worksheet()
worksheet.set_default_row(15)
worksheet.set_row(0, 17)
worksheet.write('A1', 'Symbol')
worksheet.set_column(0, 0, 10)
worksheet.write('B1', 'Volume USD')
worksheet.set_column(1, 1, 15)
with connection.cursor() as cursor:
    query = """
            SET @@time_zone = \"+3:00\";
    """
    cursor.execute(query)
    query = """
            SELECT COUNT(DISTINCT pmd.symbol) AS symbols
            FROM platform_mt5_deal pmd
            WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\";
    """
    cursor.execute(query)
    count_symbol = cursor.fetchone()
    query = """
            SELECT SUBSTRING(pmd.symbol,1,6) AS symbol
            , ROUND(SUM(pmd.volume_usd),0) AS volume_usd 
            FROM platform_mt5_deal pmd
            WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            GROUP BY pmd.symbol
            ORDER BY symbol;
    """
    cursor.execute(query)
    Volumes_USD = cursor.fetchall()
    j = 1
    for Volume_USD in Volumes_USD:
        j += 1
        worksheet.write(f'A{j}', Volume_USD["symbol"])
        worksheet.write(f'B{j}', Volume_USD["volume_usd"])
    workbook.close()
connection.close()

Report_BRB = """[Оборот в USD](https://team.alfaforex.com/servicedesk/view/11459)

За день: """+msg_day+"""."""+msg_month+""".
по """+str(count_symbol["symbols"])+""" инструментам"""

telegram_bot(Report_BRB)
#print(Report_BRB)

driver = webdriver.Firefox()
driver.get("https://team.alfaforex.com/servicedesk/view/11459")
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
attach_file = driver.find_element_by_xpath("//input[@type='file']").send_keys("C:\\Users\\Kirill_Cherkasov\\Documents\\Reports\\Volume USD\\"+"Оборот USD "+msg_day+"."+msg_month+".xlsx")
send_button = driver.find_element_by_xpath("//input[@value='Добавить']").click()
load_checked = 0
while load_checked == 0:
    try:
        find_button = driver.find_element_by_xpath("//input[@value='Добавить']")
        time.sleep(2)
    except NoSuchElementException:
        load_checked = 1
driver.quit()
