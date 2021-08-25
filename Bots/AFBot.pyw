import sys
import os
import shutil
import json
import requests
import html2text
import time
import telebot
from telebot import types
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Monitoring")
from Bot_menu_gen import actions, actions_check, actions_net
from keepass import key_pass
from sms_parcing import parsing_trunk, parsing_rc
from create_trunk import customer_trunk
from check_service import check_site, site_for_check

path_staff = os.path.dirname(os.path.abspath(__file__))+'\\'+"bot_afr_staff_id.json"
path_guest = os.path.dirname(os.path.abspath(__file__))+'\\'+"bot_afr_guest_id.json"
bot_name = 'AF Report Bot'
bot = telebot.TeleBot(key_pass(bot_name).password)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    global path_staff
    global path_guest
    with open(path_staff, encoding="utf-8") as jFile:
        data_staff = json.load(jFile)
    superuser_list = []
    if len(data_staff["superuser"]) != 0:
        for i in data_staff["superuser"]:
            superuser_list.append(i["id"])
    selectonly_list = []
    if len(data_staff["selectonly"]) != 0:
        for i in data_staff["selectonly"]:
            selectonly_list.append(i["id"])
    #For SUPERUSER
    if message.chat.id in superuser_list:
        keyboard = types.ReplyKeyboardMarkup(True,False)
        #keyboard.add('Получить код из SMS (тест)','Генератор тест-данных','Проверка сервисов (бой)','Проверка лимитов (бой)')
        keyboard.add('Получить код из SMS','Генератор тест-данных','Создать клиента')
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nВыбери действие.',reply_markup=keyboard)
    #For SELECTONLY
    elif message.chat.id in selectonly_list:
        keyboard = types.ReplyKeyboardMarkup(True,False)
        keyboard.add('Получить код из SMS','Генератор тест-данных')
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nВыбери действие.',reply_markup=keyboard)
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
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global path_staff
    global path_guest
    with open(path_staff, encoding="utf-8") as jFile:
        data_staff = json.load(jFile)
    superuser_list = []
    if len(data_staff["superuser"]) != 0:
        for i in data_staff["superuser"]:
            superuser_list.append(i["id"])
    selectonly_list = []
    if len(data_staff["selectonly"]) != 0:
        for i in data_staff["selectonly"]:
            selectonly_list.append(i["id"])
    #For SUPERUSER
    if message.chat.id in superuser_list:
        if "меню" in message.text.lower():
            '''
            keyboard = types.InlineKeyboardMarkup()
            key_SMS = types.InlineKeyboardButton(text='посмотреть SMS', callback_data='code')
            keyboard.add(key_SMS)
            bot.send_message(message.from_user.id, text='Выбери действие', reply_markup=keyboard)
            '''
            keyboard = types.ReplyKeyboardMarkup(True,False)
            #keyboard.add('Получить код из SMS (тест)','Генератор тест-данных','Проверка сервисов (бой)','Проверка лимитов (бой)')
            keyboard.add('Получить код из SMS','Генератор тест-данных','Создать клиента')
            send = bot.send_message(message.chat.id, f'Выбери действие',reply_markup=keyboard)
        elif message.text.lower() == "привет":
            bot.send_message(message.chat.id,'Привет!')
        elif "код из sms" in message.text.lower():
            smska(message)
        elif (message.text == "Генератор тест-данных") or (message.text in actions):
            answer = actions[message.text]() if message.text in actions else 'Выбери значение из списка'
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(_) for _ in actions],'Назад в меню')
            if answer == "Выбери значение из списка":
                bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode= 'Markdown')
            else:
                bot.send_message(message.chat.id, '`'+answer+'`', parse_mode= 'MarkdownV2')
        elif "создать клиента" in message.text.lower():
            customer(message)
        else:
            bot.send_message(message.from_user.id, "Напиши \"меню\"")
        '''
        elif ("лимит" in message.text.lower()) or (message.text in actions_net):
            answer = actions_net[message.text]('name') if message.text in actions_net else 'Выбери значение из списка'
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(_) for _ in actions_net],'Назад в меню')
            if answer == "Выбери значение из списка":
                bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode= 'Markdown',disable_web_page_preview = True)
            else:
                bot.send_message(message.chat.id, answer, parse_mode= 'Markdown',disable_web_page_preview = True)
        elif ("сервис" in message.text.lower()) or (message.text in actions_check) or ("Один ресурс" in message.text.lower()):
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
        '''
    #For SELECTONLY
    elif message.chat.id in selectonly_list:
        if "меню" in message.text.lower():
            '''
            keyboard = types.InlineKeyboardMarkup()
            key_SMS = types.InlineKeyboardButton(text='посмотреть SMS', callback_data='code')
            keyboard.add(key_SMS)
            bot.send_message(message.from_user.id, text='Выбери действие', reply_markup=keyboard)
            '''
            keyboard = types.ReplyKeyboardMarkup(True,False)
            keyboard.add('Получить код из SMS','Генератор тест-данных')
            send = bot.send_message(message.chat.id, f'Выбери действие',reply_markup=keyboard)
        elif message.text.lower() == "привет":
            bot.send_message(message.chat.id,'Привет!')
        elif "код из sms" in message.text.lower():
            smska(message)
        elif (message.text == "Генератор тест-данных") or (message.text in actions):
            answer = actions[message.text]() if message.text in actions else 'Выбери значение из списка'
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(_) for _ in actions],'Назад в меню')
            if answer == "Выбери значение из списка":
                bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode= 'Markdown')
            else:
                bot.send_message(message.chat.id, '`'+answer+'`', parse_mode= 'MarkdownV2')
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
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "code":
        msg = parsing_trunk()
        bot.send_message(call.message.chat.id, msg, parse_mode= 'Markdown')
def smska(message):
    msg = parsing_trunk()
    bot.send_message(message.chat.id, msg, parse_mode= 'Markdown')
def customer(message):
    try:
        result = customer_trunk(key_pass(bot_name).username,message.from_user.username,message.from_user.id)
        if result["error"]!='':
            msg = 'Что-то пошло не так.\n\n'
            msg += result["error"]+'\n'
            msg += result["error_msg"]
        else:
            msg = 'Новый клиент:\n\n'
            msg += 'CRM:\t['+result["lk"]+'](https://office.trunk.alfaforex.dom/customer/'+result["lk"]+')\n'
            msg += 'ФИО:\t'+result["fio"]+'\n'
            msg += 'ID:\t`'+result["id"]+'`'
        bot.send_message(message.chat.id, msg, parse_mode= 'Markdown',disable_web_page_preview = True)
    except:
        msg = 'Что-то пошло не так.\n\n'
        msg += 'Ошибка в функции *customer*\n'
        msg += '[Сообщи об ошибке.](https://t.me/Kirill_Cherkasov)'
        bot.send_message(message.chat.id, msg, parse_mode= 'Markdown',disable_web_page_preview = True)
bot.polling(none_stop=True, interval=0)
