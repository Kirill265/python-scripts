import requests
import calendar
import datetime
from datetime import timedelta
import pymysql
from pymysql.cursors import DictCursor
from TeamWox import TW_text_file
import time
from Telegram_report import telegram_bot
from keepass import key_pass

def Check_client(d_from = None, d_to = None, name = ""):
    try:
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
        now = datetime.datetime.now()
        if name == "":
            monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day))- timedelta(days=7)
            sunday = monday + timedelta(days=6)
            friday = monday + timedelta(days=4)
            date_from = str(monday.year)+'-'+str(monday.month)+'-'+str(monday.day)+' 00:00:00'
            date_to = str(sunday.year)+'-'+str(sunday.month)+'-'+str(sunday.day)+' 23:59:59'
            monday_next = monday + timedelta(days=7)
            sunday_next = monday_next + timedelta(days=6)
            date_from_next = str(monday_next.year)+'-'+str(monday_next.month)+'-'+str(monday_next.day)+' 00:00:00'
            date_to_next = str(sunday_next.year)+'-'+str(sunday_next.month)+'-'+str(sunday_next.day)+' 23:59:59'
        else:
            date_from = str(d_from.date())+' 00.00.00'
            date_to = str(d_to.date())+' 23.59.59'
            date_from_next = date_to
            if d_to < now:
                date_to_next = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' 23:59:59'
            else:
                date_to_next = date_to
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
            query = """
                    SELECT
                    (SELECT COUNT(c.id) FROM customer c  WHERE c.status_id = 12) 
                    +
                    (SELECT 
                    COUNT(DISTINCT a.customer_id)
                    FROM account a
                    WHERE a.customer_id IN (
                    SELECT c.id FROM customer c
                    WHERE c.status_id IN (13,18)
                    )
                    AND a.customer_id IN (
                    SELECT cc.customer_id FROM customer_contract cc
                    ))
                    -
                    (SELECT 
                    COUNT(lb.id)
                    FROM (SELECT 
                    lb.customer_id, 
                    MIN(lb.id) AS 'first_checked'
                    FROM log_backend lb
                    WHERE lb.manager_id IN (104,105)
                    AND lb.event_id = 7
                    AND lb.message LIKE '%to «Checked»%'
                    GROUP BY lb.customer_id) AS fst_chk
                    LEFT JOIN log_backend lb ON lb.id = fst_chk.first_checked
                    WHERE lb.created_at BETWEEN \""""+date_from_next+"""\" AND \""""+date_to_next+"""\"
                    ) AS count
             """
            cursor.execute(query)
            checked_all = cursor.fetchone()
        my_connection.close()
        
        manager = {}
        for manager_check in checked_for_week:
            manager[str(manager_check["manager"])] = int(manager_check["checked"])
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
                
        try:
            count_104 = manager["104"]
        except KeyError:
            count_104 = 0
        try:
            count_105 = manager["105"]
        except KeyError:
            count_105 = 0
        if name == "":
            Report_checked = """[Отчет по проверенным клиентам](https://team.alfaforex.com/servicedesk/view/11332)

`На """+msg_to_day+"""."""+msg_to_month+"""."""+str(sunday.year)+"""

Всего клиентов со статусом "проверен" или "ошибка", "повторная проверка" (с рамками): """+str(checked_all["count"])+"""
Проверенных за неделю: """+str(count_104+count_105)+"""


Для ПОД/ФТ

"""+msg_from_day+"""."""+msg_from_month+"""."""+str(monday.year)+""" - """+msg_to_day+"""."""+msg_to_month+"""."""+str(sunday.year)+"""

104: """+str(count_104)+"""
105: """+str(count_105)+"""`"""

            Checked = 'На '+msg_to_day+'.'+msg_to_month+'.'+str(sunday.year)+'<br><br>Всего клиентов со статусом "проверен" или "ошибка", "повторная проверка" (с рамками): '+str(checked_all["count"])+'<br>Проверенных за неделю: '+str(count_104+count_105)+'<br><br><br>Для ПОД/ФТ<br><br>'+msg_from_day+'.'+msg_from_month+'.'+str(monday.year)+' - '+msg_to_day+'.'+msg_to_month+'.'+str(sunday.year)+'<br><br>104: '+str(count_104)+'<br>105: '+str(count_105)

            telegram_bot(Report_checked)
            #print(Report_checked)

            URL_TW = "https://team.alfaforex.com/servicedesk/view/11332"
            message_text = Checked
            attached_file = ""

            TW_text_file(URL_TW,message_text,attached_file)
        else:
            rep_from = date_from.split(' ')[0].split('-')[2]+'.'+date_from.split('-')[1]+'.'+date_from.split('-')[0]
            rep_to = date_to.split(' ')[0].split('-')[2]+'.'+date_to.split('-')[1]+'.'+date_to.split('-')[0]
            Report_checked = """На """+rep_to+"""\nВсего клиентов со статусом "проверен" или "ошибка", "повторная проверка" (с рамками): """+str(checked_all["count"])+"""\n\nПроверенных за """+rep_from +""" - """+rep_to+""": """+str(count_104+count_105)+"""\n\nменеджер 104: """+str(count_104)+"""\nменеджер 105: """+str(count_105)
        return Report_checked
    except:
        return 'Ошибка при формировании отчета.'
