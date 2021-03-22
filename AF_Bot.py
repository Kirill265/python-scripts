import requests
import html2text
import time
import telebot
from telebot import types
bot = telebot.TeleBot('1362203438:AAFNp5tXRWi6Pn5RkIgqq_7ELHdGTbY9CUs')
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(True,False)
    keyboard.add('посмотреть SMS')
    send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nХочешь немного SMSок?))',reply_markup=keyboard)
    bot.register_next_step_handler(send,smska)
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == "меню":
        keyboard = types.InlineKeyboardMarkup()
        key_SMS = types.InlineKeyboardButton(text='посмотреть SMS', callback_data='code')
        keyboard.add(key_SMS)
        bot.send_message(message.from_user.id, text='Выберите действие', reply_markup=keyboard)
    elif message.text.lower() == "привет":
        bot.send_message(message.chat.id,'Привет!')
    elif message.text == "посмотреть SMS":
        smska(message)
    else:
        bot.send_message(message.from_user.id, "Напиши \"меню\"")
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "code":
        s = requests.get('https://sms-gate-rc.alfaforex.ru/_debug/messages')
        msg= html2text.HTML2Text().handle(s.text)
        bot.send_message(call.message.chat.id, msg)
def smska(message):
    s = requests.get('https://sms-gate-rc.alfaforex.ru/_debug/messages')
    msg= html2text.HTML2Text().handle(s.text)
    bot.send_message(message.chat.id, msg)
bot.polling(none_stop=True, interval=0)
#{ "keyboard": ["SMS CODE"]}
