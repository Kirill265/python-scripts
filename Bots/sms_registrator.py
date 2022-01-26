import sys
import os
import time
from time import sleep
import datetime
from datetime import timedelta, date, time
import psycopg2
from psycopg2.extras import DictCursor
if __name__ == '__main__':
    sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from keepass import key_pass

def check_sms(phone):
    try:
        SQL_DB = 'PostgreSQL DB TRUNK'
        Postgre_connection = psycopg2.connect(
            host=key_pass(SQL_DB).url[:-5],
            port=int(key_pass(SQL_DB).url[-4:]),
            user=key_pass(SQL_DB).username,
            password=key_pass(SQL_DB).password,
            dbname='sms_gate'
        )
        now = datetime.datetime.now()
        prev = now - timedelta(minutes=3)
        date_from = str(prev.year)+'-'+str(prev.month)+'-'+str(prev.day)+' '+str(prev.hour)+':'+str(prev.minute)+':'+str(prev.second)
        date_to = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second)
        with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                    SELECT content, state
                    FROM message
                    WHERE content LIKE 'Ваш логин: %'
                    AND phone_number LIKE '%"""+phone+"""'
                    ;
             """
            cursor.execute(query)
            sms_gate = cursor.fetchall()
        Postgre_connection.close()
        if len(sms_gate) == 0:
            text = ''
        else:
            text = ''
            for sms in sms_gate:
                text += str(sms["content"]) + '\n'
        return text
    except:
        return ''

def sms_for_login(phone):
    try:
        for i in range(5):
            now = datetime.datetime.now()
            print('начали\t'+str(now))
            sms = check_sms(phone)
            if sms != '':
                result = {}
                result["error"] = ""
                result["text"] = sms
                now = datetime.datetime.now()
                print('ответ\t'+str(now))
                return result
            now = datetime.datetime.now()
            print('перерыв\t'+str(now))
            sleep((i+1)*15)
            now = datetime.datetime.now()
            print('закончили\t'+str(now))
        result = {}
        result["error"] = "SMS не приходила."
        return result
    except:
        result = {"error":"Ошибка в функции *sms_for_login*","error_msg":"[Сообщи об ошибке.](https://t.me/Kirill_Cherkasov)"}
        return result



if __name__ == '__main__':
    customer_trunk()
