import requests
from keepass import key_pass
import telebot
from telebot import types

def telega_alert(Report: str):
    bot = telebot.TeleBot(key_pass('AF Report Bot').password)
    answer = bot.send_message(key_pass('AF Net Total').password, Report, parse_mode= 'Markdown', disable_web_page_preview = True)
    return answer
