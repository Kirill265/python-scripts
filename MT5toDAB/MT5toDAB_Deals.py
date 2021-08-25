import sys
import os
import shutil
import re
#import pandas as pd
from pandas import read_excel
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *

class Form(QMainWindow):
    def getfile(self,message,ftype):
        return QFileDialog.getOpenFileNames(self,message,"./",ftype)
    def getlogin(self,message,ftype):
        return QFileDialog.getOpenFileName(self,message,"./",ftype)
    def inform(self,message,information):
        return QMessageBox.information(self, message, information)
    def getcurrency(self,title,message):
        currency = QInputDialog.getText(self, title, message)[0]
        currency = currency.replace(",",".")
        while not re.fullmatch(r'\d+\.\d+', currency):
            currency = QInputDialog.getText(self, title, message)[0]
            currency = currency.replace(",",".")
        return currency

app = QApplication(sys.argv)
explorer = Form()
getTXT = explorer.getfile('Выберите файл со сделками','Text Documents (*.txt)')[0]
getLogin = explorer.getlogin('Выберите файл Segregated за период утраченных сделок','Excel Workbook (*.xlsx)')[0]
data_segregated = read_excel(getLogin,usecols = ['Login','Currency'], skiprows=2,skipfooter=3)
login_currency = {}
for index, data in data_segregated.iterrows():
    login_currency[str(data["Login"])] = data["Currency"]
USDRUB = explorer.getcurrency("Введите курс","USD/RUB")
EURRUB = explorer.getcurrency("Введите курс","EUR/RUB")
count_deal = 0
count_swap = 0
info = ""
for oneTXT in getTXT:
    TXT_file = oneTXT.split("/")[-1]
    direction = oneTXT.split(TXT_file)[0]
    direction = os.path.join(direction, 'MT5toDAB_Deals_result')
    if not os.path.exists(direction):
        os.mkdir(direction)
    file = open(oneTXT,'r')
    with open(direction+'/'+TXT_file,'w') as fdeals: 
        for line in file:
            line_split=line.split("\t")
            if line_split[23][:19] == 'Rollover commission' and line_split[1] == '1':
                line_split[1] = '2'
                line_split[-3] = '1'
                if True:
                    if login_currency[line_split[4]].lower() == 'usd':
                        line_split[-1] = USDRUB+'\n'
                    elif login_currency[line_split[4]].lower() == 'eur':
                        line_split[-1] = EURRUB+'\n'
                    elif login_currency[line_split[4]].lower() == 'rub':
                        line_split[-1] = '1\n'
                    else:
                        explorer.inform('Ошибка','Неизвестная валюта у счета '+line_split[4]+'!')
                        continue
                '''
                except:
                    explorer.inform('Ошибка','Неизвестная валюта у счета '+line_split[4]+'!')
                    continue
                '''
                new_line = '\t'.join(line_split)
                fdeals.write(new_line)
                count_swap += 1
            elif line_split[23][:19] == 'Rollover commission' and line_split[1] == '4':
                continue
            else:
                fdeals.write(line)
                count_deal += 1
    file.close()
info += "сделок:\t"+str(int(count_deal/2))+"\n"
info += "свопов:\t"+str(count_swap)+"\n"
info += "\nкурс USDRUB:\t"+str(USDRUB)+"\n"
info += "курс EURRUB:\t"+str(EURRUB)
explorer.inform('Результат',info)

