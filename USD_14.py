import requests
import sys
import os
import pymysql
from pymysql.cursors import DictCursor
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
date_from = str(report_date.year)+'-'+str(report_date.month)+'-'+str(report_date.day)+' 00.00.00'
date_to = str(report_date.year)+'-'+str(report_date.month)+'-'+str(report_date.day)+' 23.59.59'
with connection.cursor() as cursor:
    query = """
            SET @@time_zone = \"+3:00\";
    """
    cursor.execute(query)
    query = """
            SELECT c.name
            , SUM(pmd.profit) AS profit_sum
            FROM platform_mt5_deal pmd
            LEFT JOIN account a ON pmd.login = a.login
            LEFT JOIN currency c ON a.currency_id = c.id
            WHERE pmd.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND pmd.symbol IN ('AUDNZDrfd', 'AUDJPYrfd', 'GBPNZDrfd', 'AUDCHFrfd',
                               'CHFJPYrfd', 'EURCHFrfd', 'EURNZDrfd', 'EURCADrfd',
                               'EURNOKrfd', 'GBPCADrfd', 'GBPCHFrfd', 'USDNOKrfd',
                               'USDZARrfd', 'USDMXNrfd')
            GROUP BY a.currency_id;
    """
    cursor.execute(query)
    profit_by = cursor.fetchall()
    sum_profit = 0
    message = ''
    for profit in profit_by:
        if str(profit["name"]) == 'usd':
            sum_profit += round(float(profit["profit_sum"]),2)
        elif str(profit["name"]) == 'eur':
            sum_profit += round(float(profit["profit_sum"]) * 89 / 74.5, 2)
        elif str(profit["name"]) == 'rub':
            sum_profit += round(float(profit["profit_sum"]) / 74.5, 2)
        else:
            Report = """*Оборот в USD по 14 инструментам*

Error: БОЛЬШЕ 3-Х ВАЛЮТ СЧЕТА!!!"""
            telegram_bot(Report)
            sys.exit()
connection.close()

if report_date.month < 10:
    msg_month = '0'+str(report_date.month)
else:
    msg_month = str(report_date.month)
if report_date.day < 10:
    msg_day = '0'+str(report_date.day)
else:
    msg_day = str(report_date.day)


Report_PL = """[PL в USD по 14 инструментам](https://team.alfaforex.com/servicedesk/view/11550)

`За """+msg_day+"""."""+msg_month+"""."""+str(report_date.year)+""":"""
PL = 'За '+msg_day+'.'+msg_month+'.'+str(report_date.year)+':'
if sum_profit > 0:
    Report_PL += """
Клиенты заработали """+str(round(sum_profit,2))+"""`"""
    PL += '<br>Клиенты заработали '+str(round(sum_profit,2))
elif sum_profit < 0:
    Report_PL += """
Клиенты потеряли """+str(round(sum_profit,2))+"""`"""
    PL += '<br>Клиенты потеряли '+str(round(sum_profit,2))
else:
    Report_PL += str(round(sum_profit,2))+"""`"""
    PL += '<br>'+str(round(sum_profit,2))

telegram_bot(Report_PL)
#print(Report_PL)

driver = webdriver.Firefox()
driver.get("https://team.alfaforex.com/servicedesk/view/11550")
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
SD_message = driver.find_element_by_name("content")
SD_message.send_keys(PL)
send_button = driver.find_element_by_xpath("//input[@value='Добавить']").click()
load_checked = 0
while load_checked == 0:
    try:
        find_button = driver.find_element_by_xpath("//input[@value='Добавить']")
        time.sleep(2)
    except NoSuchElementException:
        load_checked = 1
driver.quit()
