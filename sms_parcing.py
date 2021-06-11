import requests
import html2text
import time
import psycopg2
from psycopg2.extras import DictCursor
from keepass import key_pass
import datetime
from datetime import timedelta

def parsing_rc():
    s = requests.get('https://sms-gate-rc.alfaforex.ru/_debug/messages')
    d= html2text.HTML2Text().handle(s.text)
    clear_text = d.replace('#  Latest sent messages\n\nPhone number| Date| Message text  \n---|---|---','')
    clear_text = clear_text.replace('\n\n','').replace('. ','|').replace('.\n','|').replace('\n',' ').replace('   ','').replace('  ','')
    sms_parse = clear_text.split('|')
    sms = ''
    for i in sms_parse:
        if (sms_parse.index(i)+1) % 4 == 0:
            sms += '\n' + i
        elif (sms_parse.index(i)+2) % 4 == 0:
            if i.lower().find('код') != -1:
                sms += '\nCode: `' + i.replace(' Код — ','') + '`'
            elif i.lower().find('логин') != -1:
                sms += '\nLogin: `' + i.replace(' Ваш логин: ','') + '`'
            else:
                sms += '\n' + i
        elif (sms_parse.index(i)+3) % 4 == 0:
            sms += '\nDate:' + i
        elif i != '':
            sms += '\n\nPhone: ' + i
        else:
            sms += '\n\nНовых SMS нет.'
    return sms[2:]

def parsing_trunk():
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
                SELECT phone_number, content, state, sended_at
                FROM message
                WHERE created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
                ;
         """
        cursor.execute(query)
        sms_gate = cursor.fetchall()
    Postgre_connection.close()
    if len(sms_gate) == 0:
        text = 'Новых SMS нет.\n\n'
    else:
        text = ''
        for sms in sms_gate:
            text += '*Phone*: ' + str(sms["phone_number"]) + '\n*Sended*: ' + str(sms["sended_at"]) + '\n*Message*:'
            if 'Код — ' in str(sms["content"]):
                sms_parse = str(sms["content"]).split('. ')
                text += '\nКод — `'+sms_parse[0].replace('Код — ','')+'`. '+sms_parse[1]+'\n\n'
            elif 'Ваш логин:' in str(sms["content"]):
                sms_parse = str(sms["content"]).split('. ')
                text += '\nВаш логин: `'+sms_parse[0].replace('Ваш логин: ','')+'`. '+sms_parse[1]+'\n\n'
            else:
                text += '\n'+str(sms["content"])+'\n\n'
    return text[:-2]
