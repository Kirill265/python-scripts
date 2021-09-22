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
getCSV = explorer.getfile('Выберите файл с котировками из MT5','CSV files (*.Ticks.csv)')[0]
getTXT = explorer.gettick('Выберите файл c загруженными котировками','Text Documents (ticks_*.txt)')[0]
Load_ticks = {}
if getTXT != '':
    with open(getTXT,'r') as Load_tick_file:
        for line in Load_tick_file:
            load_tick=line.split("\t")
            Load_ticks[load_tick[2]]=load_tick[1]
print(Load_ticks)
count = 0
info = ""
name_list = []
for oneCSV in getCSV:
    CSV_file = oneCSV.split("/")[-1]
    instrument = CSV_file.split(".")[0]
    direction = oneCSV.split(CSV_file)[0]
    direction = os.path.join(direction, 'MT5toDAB_Ticks_result')
    if not os.path.exists(direction):
        os.mkdir(direction)
    cnt = 0
    tick = []
    string = '0\t0'
    file = open(oneCSV,'r')
    while len(tick) < 3 or tick[0] == 'Date' or string.split("\t")[1] <= Load_ticks.get(instrument,'0'):
        first_line = next(file)
        tick=first_line.replace('\x00', '').replace('\n', '').replace('\r', '').split(";")
        if len(tick) >= 3:
            string = "0\t"+tick[0].split(" ")[0].replace(".","")+" "+tick[0].split(" ")[-1]+"\t"+instrument+"\t"+tick[2].split(".")[0]+"."+tick[2].split(".")[-1].ljust(6,"0")+"\t"+tick[1].split(".")[0]+"."+tick[1].split(".")[-1].ljust(6,"0")+"\t0\n"
    name = tick[0].replace(".","").replace(":","").replace(" ","")
    while name in name_list:
        if name[-1] != '9':
            name = name[:-1] + str(int(name[-1])+1)
        else:
            name = name[:-1] + str(0)
    name_list.append(name)
    with open(direction+'/'+'ticks_'+str(name_list[-1])+'.txt','w') as fticks:
        fticks.write(string)
        cnt += 1
        for line in file:
            tick=line.replace('\x00', '').replace('\n', '').replace('\r', '').split(";")
            if len(tick) >= 3:
                string = "0\t"+tick[0].split(" ")[0].replace(".","")+" "+tick[0].split(" ")[-1]+"\t"+instrument+"\t"+tick[2].split(".")[0]+"."+tick[2].split(".")[-1].ljust(6,"0")+"\t"+tick[1].split(".")[0]+"."+tick[1].split(".")[-1].ljust(6,"0")+"\t0\n"
                fticks.write(string)
                cnt += 1
    info += instrument+":\t"+str(cnt)+"\n"
    count += cnt
    file.close()
info += "\nTotal:\t"+str(count)
explorer.inform('Результат',info)

