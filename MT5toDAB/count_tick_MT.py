import sys
import os
import shutil
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *

class Form(QMainWindow):
    def gettick(self,message,ftype):
        return QFileDialog.getOpenFileName(self,message,"./",ftype)
    def getfile(self,message,ftype):
        return QFileDialog.getOpenFileNames(self,message,"./",ftype)
    def inform(self,message,information):
        return QMessageBox.information(self, message, information)

app = QApplication(sys.argv)
explorer = Form()
getCSV = explorer.getfile('Выберите файл с котировками из MT5','CSV files (*.Ticks*.csv)')[0]
count = 0
ms1 = 0
info = ""
name_list = []
for oneCSV in getCSV:
    list_tick = []
    CSV_file = oneCSV.split("/")[-1]
    instrument = CSV_file.split(".")[0]
    cnt = 0
    tick = []
    string = '0\t0'
    file = open(oneCSV,'r')
    while len(tick) < 2 or tick[0] == 'Date':
        first_line = next(file)
        tick=first_line.replace('\x00', '').replace('\n', '').replace('\r', '').split(";")
        if len(tick) >= 2:
            list_tick.append(tick[0])
    cnt += 1
    for line in file:
        tick=line.replace('\x00', '').replace('\n', '').replace('\r', '').split(";")
        if len(tick) >= 2:
            list_tick.append(tick[0])
            cnt += 1
    info += instrument+":\t"+str(cnt-len(set(list_tick)))+"\tиз\t"+str(cnt)+"\t\t"+str(round((cnt-len(set(list_tick)))/cnt*100,3))+"%\n"
    ms1 += cnt-len(set(list_tick))
    count += cnt
    file.close()
info += "\nTotal:\t"+str(ms1)+"\tиз\t"+str(count)+"\t\t"+str(round(ms1/count*100,3))+"%"
explorer.inform('Результат',info)

