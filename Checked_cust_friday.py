import requests
import calendar
import datetime
from datetime import timedelta
import pymysql
from pymysql.cursors import DictCursor
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

my_username = 'kcherkasov'
my_password = '6ne6H7O3ikVUvmDc570AMfmIgTSXZkcOI'
my_connection = pymysql.connect(
    host='172.16.1.42',
    port=3307,
    user=my_username,
    password=my_password,
    db='my',
    charset='utf8mb4',
    cursorclass=DictCursor
)

now = datetime.datetime.now()
monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day))
friday = monday + timedelta(days=4)
date_from = str(monday.year)+'-'+str(monday.month)+'-'+str(monday.day)+' 00:00:00'
date_to = str(friday.year)+'-'+str(friday.month)+'-'+str(friday.day)+' 15:59:59'

with my_connection.cursor() as cursor:
    query = """
            SET @@time_zone = "+3:00";
     """
    cursor.execute(query)
    query = """
            SELECT 
            lb.manager_id AS manager
            , COUNT(lb.id) AS checked
            FROM 
            (SELECT 
            lb.customer_id, 
            MIN(lb.id) AS 'first_checked'
            FROM log_backend lb
            WHERE lb.manager_id IN (104,105)
            AND lb.event_id = 7
            AND lb.message LIKE '%to «Checked»%'
            GROUP BY lb.customer_id) AS fst_chk
            LEFT JOIN log_backend lb ON lb.id = fst_chk.first_checked
            WHERE lb.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            GROUP BY lb.manager_id
            ORDER BY lb.manager_id
     """
    cursor.execute(query)
    checked_for_week = cursor.fetchall()
my_connection.close()

manager = {}
for manager_check in checked_for_week:
    manager[str(manager_check["manager"])] = int(manager_check["checked"])

if monday.month < 10:
    msg_from_month = '0'+str(monday.month)
else:
    msg_from_month = str(monday.month)
if monday.day < 10:
    msg_from_day = '0'+str(monday.day)
else:
    msg_from_day = str(monday.day)

if friday.month < 10:
    msg_to_month = '0'+str(friday.month)
else:
    msg_to_month = str(friday.month)
if friday.day < 10:
    msg_to_day = '0'+str(friday.day)
else:
    msg_to_day = str(friday.day)

try:
    count_104 = manager["104"]
except KeyError:
    count_104 = 0
try:
    count_105 = manager["105"]
except KeyError:
    count_105 = 0

Report_checked = """[Срез по проверенным клиентам](https://team.alfaforex.com/servicedesk/view/11332)

`Для ПОД/ФТ

"""+msg_from_day+"""."""+msg_from_month+"""."""+str(monday.year)+""" - """+msg_to_day+"""."""+msg_to_month+"""."""+str(friday.year)+""" 16:00:00

104: """+str(count_104)+"""
105: """+str(count_105)+"""`"""

Checked = 'Для ПОД/ФТ<br><br>'+msg_from_day+'.'+msg_from_month+'.'+str(monday.year)+' - '+msg_to_day+'.'+msg_to_month+'.'+str(friday.year)+' 16:00:00<br><br>104: '+str(count_104)+'<br>105: '+str(count_105)

telegram_bot(Report_checked)
#print(Report_checked)

driver = webdriver.Firefox()
driver.get("https://team.alfaforex.com/servicedesk/view/11332")
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
SD_message.send_keys(Checked)
send_button = driver.find_element_by_xpath("//input[@value='Добавить']").click()
load_checked = 0
while load_checked == 0:
    try:
        find_button = driver.find_element_by_xpath("//input[@value='Добавить']")
        time.sleep(2)
    except NoSuchElementException:
        load_checked = 1
driver.quit()