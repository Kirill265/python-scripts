import requests
import html2text
import time
import telebot
from telebot import types
bot = telebot.TeleBot('1362203438:AAFNp5tXRWi6Pn5RkIgqq_7ELHdGTbY9CUs')
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Меню" or message.text == "/start":
        keyboard = types.InlineKeyboardMarkup()
        key_SMS = types.InlineKeyboardButton(text='посмотреть SMS', callback_data='code')
        keyboard.add(key_SMS)
        bot.send_message(message.from_user.id, text='Выберите действие', reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Напиши Меню")
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "code":
        s = requests.get('https://sms-gate-rc.alfaforex.ru/_debug/messages')
        msg= html2text.HTML2Text().handle(s.text)
        bot.send_message(call.message.chat.id, msg)
bot.polling(none_stop=True, interval=0)
#{ "keyboard": ["SMS CODE"]}
