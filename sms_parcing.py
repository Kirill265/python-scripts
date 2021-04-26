import requests
import html2text
import time

#s = requests.get('https://sms-gate.trunk.alfaforex.dom/_debug/messages')
s = requests.get('https://sms-gate-rc.alfaforex.ru/_debug/messages')
d= html2text.HTML2Text().handle(s.text)
print(s.text)
print(d)
clear_text = d.replace('#  Latest sent messages\n\nPhone number| Date| Message text  \n---|---|---','')
clear_text = clear_text.replace('\n\n','').replace('. ','|').replace('.\n','|').replace('\n',' ').replace('   ','').replace('  ','')
print(clear_text)
sms_parse = clear_text.split('|')
print(sms_parse)
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
print(sms[2:])
