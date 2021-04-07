import requests
import html2text
import time
import telebot
from telebot import types
from Bot_menu_gen import actions
#import logging
'''
logger = logging.getLogger('requests')
handler = logging.FileHandler('requests')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)
'''
bot = telebot.TeleBot('1704857689:AAH0CAoHOlccZsEWeHvacUpnPR29Ob7cXAE')
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    '''
    request = {
        'name': m.chat.first_name,
        'text': m.text,
        'id': m.chat.id,
    }

    if m.chat.last_name: request['lastname'] = m.chat.last_name
    logger.warning(request)
    '''
    keyboard = types.ReplyKeyboardMarkup(True,False)
    keyboard.add('код из SMS','Генератор тест-данных')
    send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nЧем займемся?',reply_markup=keyboard)
    #bot.register_next_step_handler(send,smska)
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if "меню" in message.text.lower():
        '''
        keyboard = types.InlineKeyboardMarkup()
        key_SMS = types.InlineKeyboardButton(text='посмотреть SMS', callback_data='code')
        keyboard.add(key_SMS)
        bot.send_message(message.from_user.id, text='Выберите действие', reply_markup=keyboard)
        '''
        keyboard = types.ReplyKeyboardMarkup(True,False)
        keyboard.add('код из SMS','Генератор тест-данных')
        send = bot.send_message(message.chat.id, f'Чем займемся?',reply_markup=keyboard)
    elif message.text.lower() == "привет":
        bot.send_message(message.chat.id,'Привет!')
    elif message.text == "код из SMS":
        smska(message)
    elif (message.text == "Генератор тест-данных") or (message.text in actions):
        answer = actions[message.text]() if message.text in actions else 'Выберите значение из списка'
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(_) for _ in actions],'Назад в меню')
        if answer == "Выберите значение из списка":
            bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode= 'Markdown')
        else:
            bot.send_message(message.chat.id, '`'+answer+'`', parse_mode= 'Markdown')
    else:
        bot.send_message(message.from_user.id, "Напиши \"меню\"")
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "code":
        msg = parsing()
        bot.send_message(call.message.chat.id, msg, parse_mode= 'Markdown')
def smska(message):
    msg = parsing()
    bot.send_message(message.chat.id, msg, parse_mode= 'Markdown')
def parsing():
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
bot.polling(none_stop=True, interval=0)
