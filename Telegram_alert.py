import requests
from keepass import key_pass
import telebot
from telebot import types

def telega_alert(Report: str):
    bot = telebot.TeleBot(key_pass('AF Report Bot').password)
    answer = bot.send_message(key_pass('AF Service Alert').password, Report, parse_mode= 'Markdown')
    return answer

def edit_message(msg_id,Report: str):
    bot = telebot.TeleBot(key_pass('AF Report Bot').password)
    bot.edit_message_text(chat_id=key_pass('AF Service Alert').password,message_id = msg_id,text=Report, parse_mode= 'MarkdownV2')

