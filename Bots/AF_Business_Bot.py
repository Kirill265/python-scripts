import sys
import os
import shutil
import json
import requests
import time
import calendar
import datetime
from datetime import timedelta
import telebot
from telebot import types
import report_calendar
from report_calendar import CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Monitoring")
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Managment")
from Business_menu_gen import actions_check, actions_report
from keepass import key_pass
from check_service import check_site, site_for_check

from New_client_report import New_client
from Checked_cust_report import Check_client
from Convertation_report import Convert_period
from Volume_USD_report import Volume_period

path_staff = os.path.dirname(os.path.abspath(__file__))+'\\'+"bot_staff_id.json"
path_guest = os.path.dirname(os.path.abspath(__file__))+'\\'+"bot_guest_id.json"
'''
with open(path_staff, encoding="utf-8") as jFile:
    data = json.load(jFile)
available_list = []
if len(data["staff"]) != 0:
    for i in data["staff"]:
        available_list.append(i["id"])
'''
period = {}
text_from = {}
date_from = {}
date_to = {}
calendar_to_del = {}
report = {}
bot = telebot.TeleBot(key_pass('AF help').password)
calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")
def gen_report(call: CallbackQuery):
    global date_from
    global date_to
    global report
    try:
        if date_from[call.message.chat.id] > date_to[call.message.chat.id]:
            bot.send_message(call.message.chat.id, 'Некорректно задан период', parse_mode= 'Markdown',disable_web_page_preview = True)
        else:
            answer = actions_report[report[call.message.chat.id]](date_from[call.message.chat.id],date_to[call.message.chat.id],'name') if report[call.message.chat.id] in actions_report else 'Выбери отчет из списка'
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(_) for _ in actions_report],'Назад в меню')
            if answer != "Выбери отчет из списка":
                bot.send_message(call.message.chat.id, answer, parse_mode= 'Markdown',disable_web_page_preview = True)
    except:
        pass
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    #global data
    global path_staff
    global path_guest
    #global available_list
    with open(path_staff, encoding="utf-8") as jFile:
        data_staff = json.load(jFile)
    superuser_list = []
    if len(data_staff["superuser"]) != 0:
        for i in data_staff["superuser"]:
            superuser_list.append(i["id"])
    checkonly_list = []
    if len(data_staff["checkonly"]) != 0:
        for i in data_staff["checkonly"]:
            checkonly_list.append(i["id"])
    #For SUPERUSER
    if message.chat.id in superuser_list:
        keyboard = types.ReplyKeyboardMarkup(True,False)
        keyboard.add('Выгрузить отчет','Проверить сервис')
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nВыбери действие.',reply_markup=keyboard)
    #For CHECKONLY
    elif message.chat.id in checkonly_list:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(_) for _ in actions_check],'Один ресурс')
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nВыбери значение из списка.',reply_markup=keyboard)
    #For GUEST
    else:
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nТвой id: `{message.from_user.id}`', parse_mode= 'Markdown')
        with open(path_guest, encoding="utf-8") as jFile:
            data_guest = json.load(jFile)
        guest_list = []
        if len(data_guest["guest"]) != 0:
            for i in data_guest["guest"]:
                guest_list.append(i["id"])
        if message.chat.id not in guest_list:
            data_guest["guest"].append({"id":message.from_user.id,"username":message.from_user.username,"firstname":message.from_user.first_name,"lastname":message.from_user.last_name,"isbot":message.from_user.is_bot})
            jFile = open(path_guest, "w")
            jFile.write(json.dumps(data_guest))
            jFile.close()
@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_inline(call: CallbackQuery):
    global period
    global text_from
    global calendar_to_del
    global date_from
    global date_to
    period.setdefault(call.message.chat.id, False)
    name, action, year, month, day = call.data.split(calendar_1.sep)
    date = report_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day, period=period[call.message.chat.id]
    )
    if action == "DAY" and period[call.message.chat.id] == False:
        period[call.message.chat.id] = True
        text_from[call.message.chat.id]="С "+str(date.strftime('%d.%m.%Y'))
        date_from[call.message.chat.id] = date
    elif action == "DAY" and period[call.message.chat.id] == True:
        period[call.message.chat.id] = False
        bot.send_message(
            chat_id=call.from_user.id,
            text=text_from[call.message.chat.id]+" по "+str(date.strftime('%d.%m.%Y')),
        )
        date_to[call.message.chat.id] = date
        text_from[call.message.chat.id] = ""
        gen_report(call)
        report[call.message.chat.id] = ""
        try:
            calendar_to_del[call.message.chat.id].remove(call.message.message_id)
        except:
            pass
    elif action == "CANCEL":
        period[call.message.chat.id] = False
        text_from[call.message.chat.id] = ""
        bot.send_message(
            chat_id=call.from_user.id,
            text="Выбери отчет",
        )
        try:
            calendar_to_del[call.message.chat.id].remove(call.message.message_id)
        except:
            pass
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    #global data
    global path_staff
    global path_guest
    global period
    global text_from
    global calendar_to_del
    global report
    #global available_list
    with open(path_staff, encoding="utf-8") as jFile:
        data_staff = json.load(jFile)
    superuser_list = []
    if len(data_staff["superuser"]) != 0:
        for i in data_staff["superuser"]:
            superuser_list.append(i["id"])
    checkonly_list = []
    if len(data_staff["checkonly"]) != 0:
        for i in data_staff["checkonly"]:
            checkonly_list.append(i["id"])
    #For SUPERUSER
    if message.chat.id in superuser_list:
        if "меню" in message.text.lower():
            keyboard = types.ReplyKeyboardMarkup(True,False)
            keyboard.add('Выгрузить отчет','Проверить сервис')
            send = bot.send_message(message.chat.id, f'Выбери действие',reply_markup=keyboard)
        elif message.text.lower() == "привет":
            bot.send_message(message.chat.id,'Привет!')
        elif "отчет" in message.text.lower() or message.text == 'За прошлую неделю':
            answer = 'Выбери отчет из списка'
            if message.text == 'За прошлую неделю':
                period[message.chat.id] = False
                text_from[message.chat.id] = ""
                report[message.chat.id] = message.text
                if message.chat.id in calendar_to_del.keys():
                    if len(calendar_to_del[message.chat.id]) != 0:
                        for msg_id in calendar_to_del[message.chat.id]:
                            bot.delete_message(chat_id=message.chat.id, message_id=msg_id,)
                            calendar_to_del[message.chat.id].remove(msg_id)
                now = datetime.datetime.now()
                monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day)) - timedelta(days=7)
                sunday = monday + timedelta(days=6)
                answer = 'С '+str(monday.strftime('%d.%m.%Y'))+' по '+str(sunday.strftime('%d.%m.%Y'))
                answer += '\n\n\n*Новые активные клиенты*\n\n' + New_client(monday,sunday,'name')
                answer += '\n\n\n*Проверенные клиенты*\n\n' + Check_client(monday,sunday,'name')
                answer += '\n\n\n*Конвертации*\n\n' + Convert_period(monday,sunday,'name')
                answer += '\n\n\n*Оборот в USD*\n\n' + Volume_period(monday,sunday,'name')
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(_) for _ in actions_report],'За прошлую неделю','Назад в меню')
            if answer == "Выбери отчет из списка":
                bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode= 'Markdown',disable_web_page_preview = True)
            else:
                bot.send_message(message.chat.id, answer, parse_mode= 'Markdown',disable_web_page_preview = True)
        elif message.text in actions_report:
            period[message.chat.id] = False
            text_from[message.chat.id] = ""
            report[message.chat.id] = message.text
            if message.chat.id in calendar_to_del.keys():
                if len(calendar_to_del[message.chat.id]) != 0:
                    for msg_id in calendar_to_del[message.chat.id]:
                        bot.delete_message(chat_id=message.chat.id, message_id=msg_id,)
                        calendar_to_del[message.chat.id].remove(msg_id)
            now = datetime.datetime.now()
            sended = bot.send_message(
                chat_id=message.chat.id,
                text="Выбери период",
                reply_markup=report_calendar.create_calendar(
                    name=calendar_1.prefix,
                    year=now.year,
                    month=now.month,
                ),
            )
            if message.chat.id not in calendar_to_del.keys():
                calendar_to_del[message.chat.id] = []
            calendar_to_del[message.chat.id].append(sended.message_id)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('За прошлую неделю',*[types.KeyboardButton(_) for _ in actions_report],'Назад в меню')
        elif ("сервис" in message.text.lower()) or (message.text in actions_check):
            answer = actions_check[message.text]('name') if message.text in actions_check else 'Выбери значение из списка'
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(_) for _ in actions_check],'Один ресурс','Назад в меню')
            if answer == "Выбери значение из списка":
                bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode= 'Markdown',disable_web_page_preview = True)
            else:
                bot.send_message(message.chat.id, answer, parse_mode= 'Markdown',disable_web_page_preview = True)
        elif (message.text == "Один ресурс") or (message.text in site_for_check):
            answer = check_site(message.text,'name') if message.text in site_for_check else 'Выбери значение из списка'
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*site_for_check,'К сервисам','Назад в меню')
            if answer == "Выбери значение из списка":
                bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode= 'Markdown',disable_web_page_preview = True)
            else:
                bot.send_message(message.chat.id, answer, parse_mode= 'Markdown',disable_web_page_preview = True)
        else:
            bot.send_message(message.from_user.id, "Напиши \"меню\"")
    #For CHECKONLY
    elif message.chat.id in checkonly_list:
        if message.text.lower() == "привет":
            bot.send_message(message.chat.id,'Привет!')
        elif ("меню" in message.text.lower()) or ("сервис" in message.text.lower()) or (message.text in actions_check):
            answer = actions_check[message.text]('name') if message.text in actions_check else 'Выбери значение из списка'
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(_) for _ in actions_check],'Один ресурс')
            if answer == "Выбери значение из списка":
                bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode= 'Markdown',disable_web_page_preview = True)
            else:
                bot.send_message(message.chat.id, answer, parse_mode= 'Markdown',disable_web_page_preview = True)
        elif (message.text == "Один ресурс") or (message.text in site_for_check):
            answer = check_site(message.text,'name') if message.text in site_for_check else 'Выбери значение из списка'
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*site_for_check,'Назад в меню')
            if answer == "Выбери значение из списка":
                bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode= 'Markdown',disable_web_page_preview = True)
            else:
                bot.send_message(message.chat.id, answer, parse_mode= 'Markdown',disable_web_page_preview = True)
        else:
            bot.send_message(message.from_user.id, "Напиши \"меню\"")
    #For GUEST
    else:
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nТвой id: `{message.from_user.id}`', parse_mode= 'Markdown')
        with open(path_guest, encoding="utf-8") as jFile:
            data_guest = json.load(jFile)
        guest_list = []
        if len(data_guest["guest"]) != 0:
            for i in data_guest["guest"]:
                guest_list.append(i["id"])
        if message.chat.id not in guest_list:
            data_guest["guest"].append({"id":message.from_user.id,"username":message.from_user.username,"firstname":message.from_user.first_name,"lastname":message.from_user.last_name,"isbot":message.from_user.is_bot})
            jFile = open(path_guest, "w")
            jFile.write(json.dumps(data_guest))
            jFile.close()
bot.polling(none_stop=True, interval=0)
