import requests
import html2text
import time
s = requests.get('https://sms-gate-rc.alfaforex.ru/_debug/messages')
d= html2text.HTML2Text().handle(s.text)
print(s.text)
print(d)
'''
check = ''
code_old = ''
i=0
while i<2:
    while (check == ''):
        time.sleep(2)
        s = requests.get('https://sms-gate-rc.alfaforex.ru/_debug/messages')
        d= html2text.HTML2Text().handle(s.text)
        check = d.split('\n')[4]
    number = d.split('|')[4].split('\n')[-1]
    code = d.split('|')[6].split('.')[0].split('— ')[-1]
    text = d.split('|')[6].split('. ')[1].replace('\n',' ')
    if code != code_old:
        print(number+'\n`'+code+'`\n'+text)
        i+=1
    code_old = code
    check = ''
'''
