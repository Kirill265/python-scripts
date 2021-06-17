import sys
import os
import datetime
import calendar
from datetime import timedelta
from TeamWox import TW_text_file
from Telegram_report import telegram_bot
from Volume_USD import volume_USD
import time

def Volume_period(d_from = None, d_to = None, name = ""):
    if True:
        if name == "":
            now = datetime.datetime.now()
            monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day)) - timedelta(days=7)
            sunday = monday + timedelta(days=6)
            friday = monday + timedelta(days=4)
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
            date_from = str(monday.year)+'-'+str(monday.month)+'-'+str(monday.day)+' 00:00:00'
            date_to = str(sunday.year)+'-'+str(sunday.month)+'-'+str(sunday.day)+' 23:59:59'
            
            direction = os.path.dirname(os.path.abspath(__file__))
            direction = os.path.join(direction, 'Reports')
            if not(os.path.exists(direction)):
                os.mkdir(direction)
            direction = os.path.join(direction, 'Volume USD')
            if not(os.path.exists(direction)):
                os.mkdir(direction)
            direction += '\\'
        else:
            date_from = str(d_from.date())+' 00.00.00'
            date_to = str(d_to.date())+' 23.59.59'
        
        send_info = {}
        send_info["date_from"] = date_from
        send_info["date_to"] = date_to
        if name == "":
            send_info["direction"] = direction
            send_info["msg_from_day"] = msg_from_day
            send_info["msg_to_day"] = msg_to_day
            send_info["msg_from_month"] = msg_from_month
            send_info["msg_to_month"] = msg_to_month
        return_info = volume_USD(send_info, name)
        if name == "":
            Report_USD = """[Оборот в USD](https://team.alfaforex.com/servicedesk/view/11459)

За период: """+msg_from_day+"""."""+msg_from_month+""" - """+msg_to_day+"""."""+msg_to_month+""".
по """+return_info["count_symbol"]+""" инструментам"""

            telegram_bot(Report_USD)
            #print(Report_USD)

            URL_TW = "https://team.alfaforex.com/servicedesk/view/11459"
            message_text = ''
            attached_file = direction+"Оборот USD "+msg_from_day+"."+msg_from_month+" - "+msg_to_day+"."+msg_to_month+".xlsx"

            TW_text_file(URL_TW,message_text,attached_file)
        else:
            rep_from = date_from.split(' ')[0].split('-')[2]+'.'+date_from.split('-')[1]+'.'+date_from.split('-')[0]
            rep_to = date_to.split(' ')[0].split('-')[2]+'.'+date_to.split('-')[1]+'.'+date_to.split('-')[0]
            Report_USD = return_info["report"][1:]
        return Report_USD
    '''
    except:
        return 'Ошибка при формировании отчета.'

'''
