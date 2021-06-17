import requests
import html2text
import time
import telebot
from telebot import types
from test_Bot_menu_gen import actions, actions_check
from keepass import key_pass
from sms_parcing import parsing_trunk, parsing_rc
from test import check_site, site_for_check

bot = telebot.TeleBot(key_pass('AF test Bot').password)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(True,False)
    keyboard.add('Получить код из SMS (тест)','Генератор тест-данных','Проверка сервисов (бой)')
    send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nВыбери действие.',reply_markup=keyboard)
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if "меню" in message.text.lower():
        '''
        keyboard = types.InlineKeyboardMarkup()
        key_SMS = types.InlineKeyboardButton(text='посмотреть SMS', callback_data='code')
        keyboard.add(key_SMS)
        bot.send_message(message.from_user.id, text='Выбери действие', reply_markup=keyboard)
        '''
        keyboard = types.ReplyKeyboardMarkup(True,False)
        keyboard.add('Получить код из SMS (тест)','Генератор тест-данных','Проверка сервисов (бой)')
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
            bot.send_message(message.chat.id, '`'+answer+'`', parse_mode= 'Markdown')
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
    else:
        bot.send_message(message.from_user.id, "Напиши \"меню\"")
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "code":
        msg = parsing_trunk()
        bot.send_message(call.message.chat.id, msg, parse_mode= 'Markdown')
def smska(message):
    msg = parsing_trunk()
    bot.send_message(message.chat.id, msg, parse_mode= 'Markdown')
bot.polling(none_stop=True, interval=0)
