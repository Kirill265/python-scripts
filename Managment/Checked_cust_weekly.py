import sys
import os
import requests
import calendar
import datetime
from datetime import timedelta
import pymysql
from pymysql.cursors import DictCursor
import time
if __name__ == '__main__':
    sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from Telegram_report import telegram_bot
from TeamWox import TW_text_file
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
                    WHERE lb.event_id = 7
                    AND lb.message LIKE '%to ??Checked??%'
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
                    WHERE lb.event_id = 7
                    AND lb.message LIKE '%to ??Checked??%'
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
        week_check = 0
        for value in manager.values():
            week_check += value
        if name == "":
            Report_checked = """[?????????? ???? ?????????????????????? ????????????????](https://team.alfaforex.com/servicedesk/view/11332)

`???? """+msg_to_day+"""."""+msg_to_month+"""."""+str(sunday.year)+"""

?????????? ???????????????? ???? ???????????????? "????????????????" ?????? "????????????", "?????????????????? ????????????????" (?? ??????????????): """+str(checked_all["count"])+"""
?????????????????????? ???? ????????????: """+str(week_check)
            
            Checked = '???? '+msg_to_day+'.'+msg_to_month+'.'+str(sunday.year)+'<br><br>?????????? ???????????????? ???? ???????????????? "????????????????" ?????? "????????????", "?????????????????? ????????????????" (?? ??????????????): '+str(checked_all["count"])+'<br>?????????????????????? ???? ????????????: '+str(week_check)
            
            if week_check != 0:
                Report_checked += """\n\n\n?????? ??????/????\n\n"""+msg_from_day+"""."""+msg_from_month+"""."""+str(monday.year)+""" - """+msg_to_day+"""."""+msg_to_month+"""."""+str(sunday.year)+"""\n"""
                Checked += '<br><br><br>?????? ??????/????<br><br>'+msg_from_day+'.'+msg_from_month+'.'+str(monday.year)+' - '+msg_to_day+'.'+msg_to_month+'.'+str(sunday.year)+'<br>'
                
                for key in manager:
                    Report_checked += """\n""" + key + """: """ + str(manager[key])
                    Checked+='<br>' + key + ': ' + str(manager[key])
            Report_checked += """`

#CheckedCustomers"""
            
            telegram_bot(Report_checked)
            #print(Report_checked)

            URL_TW = "https://team.alfaforex.com/servicedesk/view/11332"
            message_text = Checked
            attached_file = ""

            TW_text_file(URL_TW,message_text,attached_file)
        else:
            rep_from = date_from.split(' ')[0].split('-')[2]+'.'+date_from.split('-')[1]+'.'+date_from.split('-')[0]
            rep_to = date_to.split(' ')[0].split('-')[2]+'.'+date_to.split('-')[1]+'.'+date_to.split('-')[0]
            Report_checked = """???? """+rep_to+"""\n?????????? ???????????????? ???? ???????????????? "????????????????" ?????? "????????????", "?????????????????? ????????????????" (?? ??????????????): """+str(checked_all["count"])+"""\n\n?????????????????????? ???? """+rep_from +""" - """+rep_to+""": """+str(week_check)+"""\n"""
            if week_check != 0:
                for key in manager:
                    Report_checked += """\n???????????????? """ + key + """: """ + str(manager[key])
        return Report_checked
    except:
        return '???????????? ?????? ???????????????????????? ????????????.'

if __name__ == '__main__':
    Check_client()
