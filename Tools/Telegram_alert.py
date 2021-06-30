import requests
from keepass import key_pass
import telebot
from telebot import types

def telega_alert(Report: str):
    bot = telebot.TeleBot(key_pass('AF Report Bot').password)
    answer = bot.send_message(key_pass('AF Service Alert').password, Report, parse_mode= 'Markdown', disable_web_page_preview = True)
    return answer

def edit_message(msg_id,Report: str):
    bot = telebot.TeleBot(key_pass('AF Report Bot').password)
    bot.edit_message_text(chat_id=key_pass('AF Service Alert').password,message_id = msg_id,text=Report, parse_mode= 'MarkdownV2', disable_web_page_preview = True)

def reply_message(msg_id,Report: str):
    bot = telebot.TeleBot(key_pass('AF Report Bot').password)
    bot.send_message(chat_id = key_pass('AF Service Alert').password, text = Report, parse_mode= 'Markdown', disable_web_page_preview = True, reply_to_message_id = msg_id)

def pin_message(msg_id):
    bot = telebot.TeleBot(key_pass('AF Report Bot').password)
    bot.pin_chat_message(chat_id = key_pass('AF Service Alert').password, message_id = msg_id, disable_notification = True)

def unpin_message(msg_id):
    bot = telebot.TeleBot(key_pass('AF Report Bot').password)
    bot.unpin_chat_message(chat_id = key_pass('AF Service Alert').password, message_id = msg_id)
