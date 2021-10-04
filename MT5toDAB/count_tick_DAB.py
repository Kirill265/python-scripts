import sys
import os
import shutil
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *

class Form(QMainWindow):
    def getfile(self,message,ftype):
        return QFileDialog.getOpenFileNames(self,message,"./",ftype)
    def inform(self,message,information):
        return QMessageBox.information(self, message, information)

app = QApplication(sys.argv)
explorer = Form()
getCSV = explorer.getfile('Выберите файл с котировками из ДИБ','CSV files (*.csv)')[0]
info = ""
tick_dict = {}
bidask_dict = {}
tick = []
#file = open(oneCSV,'r',encoding='utf-8')
for oneCSV in getCSV:
    CSV_file = oneCSV.split("/")[-1]
    file = open(oneCSV,'r')
    first_line = next(file)
    for line in file:
        tick=line.replace('\x00', '').replace('\n', '').replace('\r', '').split(";")
        instrument = tick[1]
        if not instrument in tick_dict:
            tick_dict[instrument] = [tick[0]]
            bidask_dict[instrument] = [tick[2]+tick[3]]
        else:
            tick_dict[instrument].append(tick[0])
            if bidask_dict[instrument][-1] != tick[2]+tick[3]:
                bidask_dict[instrument].append(tick[2]+tick[3])
    file.close()
info += 'Инструмент\tдубли по времени\tдубли по цене\t\tвсего\n'
for instrument in tick_dict:
    cnt = len(tick_dict[instrument])
    cnt_time = cnt-len(set(tick_dict[instrument]))
    cnt_bidask = cnt-len(bidask_dict[instrument])
    info += instrument+":\t\t"+str(cnt_time)+"\t\t"+str(cnt_bidask)+"\t\t\t"+str(cnt)+"\n"
explorer.inform('Результат',info)

