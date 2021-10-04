import sys
import os
import shutil
import re
from datetime import datetime, timedelta
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from keepass import key_pass

class Form(QMainWindow):
    def getfile(self,message,ftype):
        return QFileDialog.getOpenFileNames(self,message,"./",ftype)
    def direct(self,message):
        return QFileDialog.getExistingDirectory(self,message,"./")
    def inform(self,message,information):
        return QMessageBox.information(self, message, information)
    def getid(self,title,message):
        deal_id = QInputDialog.getText(self, title, message)[0]
        while not re.fullmatch(r'\d{10}', deal_id):
            deal_id = QInputDialog.getText(self, title, message)[0]
        return deal_id

app = QApplication(sys.argv)
explorer = Form()
getHistory = explorer.getfile('Выберите файлы со сделками','Excel (*.xlsx)')[0]

j = 0
period_start = []
period_end = []
currencies = []
for History_file in getHistory:
    j += 1
    history = pd.read_excel(History_file)
    fio = history["Unnamed: 3"][0]
    login = history["Unnamed: 3"][1].split(" ")[0]
    currency = history["Unnamed: 3"][1].split("(")[1][:3]
    currencies.append(currency)
    period_start.append(history["Unnamed: 3"][2].split("-")[0].replace(".","-"))
    period_end.append(history["Unnamed: 3"][2].split("-")[1].replace(".","-"))
    i = 0
    for deal in history["Trade History Report"]:
        i += 1
        if deal == "Deals":
            start = i
        elif deal == "Balance:" or deal == "Open Positions":
            end = i-2
            break
    history_deal = history[start:end]
    login_list = ["Торговый счет"]
    currency_list = ["Валюта"]
    for deal in range(len(history_deal)-1):
        login_list.append(login)
        currency_list.append(currency)
    history_deal.drop(["Unnamed: 13"], axis=1, inplace=True)
    history_deal.loc[:, "login"] = login_list
    history_deal.loc[:, "currency"] = currency_list
    if j != 1:
        Deals = pd.concat([Deals, history_deal[1:]], ignore_index=True)
    else:
        Deals = history_deal

if 'USD' in currencies or 'EUR' in currencies:
    getCBR = explorer.getfile('Выберите файлы с котировками ЦБ','Excel (*.xlsx)')[0]
    getOPRDS = explorer.getfile('Выберите файл с операциями прихода / расхода ДС','Excel (*.xls)')[0]
else:
    getCBR = []
    getOPRDS = []
result_dir = explorer.direct("Укажите путь для сохранения")+'/'
result_dir = os.path.join(result_dir, 'TaxDetail_result')
if not os.path.exists(result_dir):
    os.mkdir(result_dir)

Deals.columns = Deals.iloc[0]

for (idx, deal) in Deals.iterrows():
    if 'Withdrawal' in str(deal.loc['Comment']):
        old_time = datetime.strptime(str(deal.loc['Time']), '%Y.%m.%d %H:%M:%S')
        new_time = old_time + timedelta(days=1)
        deal.loc['Time'] = str(new_time).split(" ")[0].replace("-",".")+' 00:00:00'
    elif 'Rollover commission' in str(deal.loc['Comment']):
        deal.loc['Time'] = str(deal.loc['Comment']).split(".")[2]+'.'+str(deal.loc['Comment']).split(".")[1]+'.'+str(deal.loc['Comment']).split(".")[0].split(" ")[-1]+' 23:59:59'

Deals = Deals.iloc[1:].sort_values('Time')

rates_list = []
profit_RUB_list = []
NOD_current_list = []
tax_holding_list = []
tax13_list = []
tax13_current_list = []
tax13_holding_list = []
tax15_list = []
tax15_current_list = []
tax15_holding_list = []
tax_current_list = []

for k in range(len(Deals)):
    if 'EUR' in currencies and 'USD' in currencies and 'RUB' in currencies:
        rates_list.append("""=IF(AND(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2)+""")),O"""+str(k+2) \
                          +"""="EUR"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'курс ЦБ EUR'!A:B,2,0),IF(AND(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2) \
                          +""")),O"""+str(k+2)+"""="USD"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'курс ЦБ USD'!A:B,2,0),IF(AND(OR(D"""+str(k+2) \
                          +"""="balance",K"""+str(k+2)+"""=0),O"""+str(k+2)+"""<>"RUB"),0,IF(AND(D"""+str(k+2) \
                          +"""="commission",O"""+str(k+2)+"""="USD"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'курс свопов USD'!A:B,2,0),IF(AND(D"""+str(k+2)+"""="commission",O"""+str(k+2) \
                          +"""="EUR"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'курс свопов EUR'!A:B,2,0),IF(O"""+str(k+2) \
                          +"""="EUR",VLOOKUP(VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'дата исполнения финреза'!A:B,2,0),'курс ЦБ EUR'!A:B,2,0),IF(O"""+str(k+2) \
                          +"""="USD",VLOOKUP(VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'дата исполнения финреза'!A:B,2,0),'курс ЦБ USD'!A:B,2,0),1)))))))""")
    elif 'EUR' in currencies and 'USD' in currencies:
        rates_list.append("""=IF(AND(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2)+""")),O"""+str(k+2) \
                          +"""="EUR"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'курс ЦБ EUR'!A:B,2,0),IF(AND(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2) \
                          +""")),O"""+str(k+2)+"""="USD"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'курс ЦБ USD'!A:B,2,0),IF(OR(D"""+str(k+2) \
                          +"""="balance",K"""+str(k+2)+"""=0),0,IF(AND(D"""+str(k+2) \
                          +"""="commission",O"""+str(k+2)+"""="USD"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'курс свопов USD'!A:B,2,0),IF(AND(D"""+str(k+2)+"""="commission",O"""+str(k+2) \
                          +"""="EUR"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'курс свопов EUR'!A:B,2,0),IF(O"""+str(k+2) \
                          +"""="EUR",VLOOKUP(VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'дата исполнения финреза'!A:B,2,0),'курс ЦБ EUR'!A:B,2,0),IF(O"""+str(k+2) \
                          +"""="USD",VLOOKUP(VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'дата исполнения финреза'!A:B,2,0),'курс ЦБ USD'!A:B,2,0),1)))))))""")
    elif 'EUR' in currencies and 'RUB' in currencies:
        rates_list.append("""=IF(AND(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2)+""")),O"""+str(k+2) \
                          +"""="EUR"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'курс ЦБ EUR'!A:B,2,0),IF(AND(OR(D"""+str(k+2) \
                          +"""="balance",K"""+str(k+2)+"""=0),O"""+str(k+2)+"""<>"RUB"),0,IF(AND(D"""+str(k+2) \
                          +"""="commission",O"""+str(k+2)+"""="EUR"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'курс свопов EUR'!A:B,2,0),IF(O"""+str(k+2)+"""="EUR",VLOOKUP(VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'дата исполнения финреза'!A:B,2,0),'курс ЦБ EUR'!A:B,2,0),1))))""")
    elif 'USD' in currencies and 'RUB' in currencies:
        rates_list.append("""=IF(AND(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2)+""")),O"""+str(k+2) \
                          +"""="USD"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2)+""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2) \
                          +""",7),2)&"."&LEFT(A"""+str(k+2)+""",4),'курс ЦБ USD'!A:B,2,0),IF(AND(OR(D"""+str(k+2) \
                          +"""="balance",K"""+str(k+2)+"""=0),O"""+str(k+2)+"""<>"RUB"),0,IF(AND(D"""+str(k+2) \
                          +"""="commission",O"""+str(k+2)+"""="USD"),VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'курс свопов USD'!A:B,2,0),IF(O"""+str(k+2)+"""="USD",VLOOKUP(VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'дата исполнения финреза'!A:B,2,0),'курс ЦБ USD'!A:B,2,0),1))))""")
    elif 'EUR' in currencies:
        rates_list.append("""=IF(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2)+""")),VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'курс ЦБ EUR'!A:B,2,0),IF(OR(D"""+str(k+2)+"""="balance",K"""+str(k+2) \
                          +"""=0),0,IF(D"""+str(k+2)+"""="commission",VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'курс свопов EUR'!A:B,2,0),VLOOKUP(VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'дата исполнения финреза'!A:B,2,0),'курс ЦБ EUR'!A:B,2,0))))""")
    elif 'USD' in currencies:
        rates_list.append("""=IF(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2)+""")),VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'курс ЦБ USD'!A:B,2,0),IF(OR(D"""+str(k+2)+"""="balance",K"""+str(k+2) \
                          +"""=0),0,IF(D"""+str(k+2)+"""="commission",VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'курс свопов USD'!A:B,2,0),VLOOKUP(VLOOKUP(RIGHT(LEFT(A"""+str(k+2) \
                          +""",10),2)&"."&RIGHT(LEFT(A"""+str(k+2)+""",7),2)&"."&LEFT(A"""+str(k+2) \
                          +""",4),'дата исполнения финреза'!A:B,2,0),'курс ЦБ USD'!A:B,2,0))))""")
    else:
        rates_list.append("""=1""")
    profit_RUB_list.append("""=IF(D"""+str(k+2)+"""<>"balance",ROUND(P"""+str(k+2)+"""*K"""+str(k+2)+""",2),0)""")
    NOD_current_list.append("""=SUM($Q$1:Q"""+str(k+2)+""")""")
    tax_holding_list.append("""=SUM($V$1:V"""+str(k+1)+""")+SUM($Y$1:Y"""+str(k+1)+""")""")
    tax13_list.append("""=IF(A"""+str(k+2)+"""<"2020.12.31 00:00:00",Q"""+str(k+2)+"""*0.13,IF(AND(K"""+str(k+2)+""">=0,SUM($Q$2:Q"""+str(k+2)+""")<=5000000),Q"""+str(k+2) \
                      +"""*0.13,IF(AND(K"""+str(k+2)+""">=0,SUM($Q$2:Q"""+str(k+2)+""")>5000000,SUM($T$1:T"""+str(k+1) \
                      +""")<650000),650000-SUM($T$1:T"""+str(k+1)+"""),IF(AND(K"""+str(k+2)+"""<0,SUM($Q$2:Q"""+str(k+2) \
                      +""")<5000000,SUM($T$1:T"""+str(k+1)+""")<650000),Q"""+str(k+2)+"""*0.13,IF(AND(K"""+str(k+2) \
                      +"""<0,SUM($Q$2:Q"""+str(k+2)+""")<5000000,SUM($T$1:T"""+str(k+1)+""")>=650000),(SUM($Q$2:Q"""+str(k+2) \
                      +""")-5000000)*0.13,0)))))""")
    tax13_current_list.append("""=ROUND(SUM($T$2:T"""+str(k+2)+""")-SUM($V$1:V"""+str(k+1)+"""),0)""")
    tax13_holding_list.append("""=ROUND(IF(AND(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2)+""")),U"""+str(k+2) \
                              +""">0),IF(A"""+str(k+2)+"""<"2021.04.09 00:00:00",MIN(-0.13*K"""+str(k+2) \
                              +"""*P"""+str(k+2)+""",U"""+str(k+2)+"""+X"""+str(k+2)+"""*13/15),IF((-1)*K"""+str(k+2) \
                              +"""*P"""+str(k+2)+""">=Z"""+str(k+2)+""",U"""+str(k+2)+""",MIN(-0.13*K"""+str(k+2) \
                              +"""*P"""+str(k+2)+""",U"""+str(k+2)+"""))),0),0)""")
    tax15_list.append("""=IF(A"""+str(k+2)+"""<"2020.12.31 00:00:00",0,IF(AND(K"""+str(k+2)+""">=0,SUM($Q$2:Q"""+str(k+2)+""")>5000000,SUM($T$1:T"""+str(k+1) \
                      +""")>=650000),Q"""+str(k+2)+"""*0.15,IF(AND(K"""+str(k+2)+""">=0,SUM($Q$2:Q"""+str(k+2) \
                      +""")>5000000,SUM($T$1:T"""+str(k+1)+""")<650000),(SUM($Q$2:Q"""+str(k+2) \
                      +""")-5000000)*0.15,IF(AND(K"""+str(k+2)+"""<0,SUM($Q$2:Q"""+str(k+2)+""")>5000000),Q"""+str(k+2) \
                      +"""*0.15,IF(AND(K"""+str(k+2)+"""<0,SUM($Q$2:Q"""+str(k+2)+""")<5000000,SUM($T$1:T"""+str(k+1) \
                      +""")>=650000),-SUM($W$1:W"""+str(k+1)+"""),0)))))""")
    tax15_current_list.append("""=ROUND(SUM($W$2:W"""+str(k+2)+""")-SUM($Y$1:Y"""+str(k+1)+"""),0)""")
    tax15_holding_list.append("""=ROUND(IF(AND(ISNUMBER(SEARCH("Withdrawal",M"""+str(k+2)+""")),X"""+str(k+2) \
                              +""">0),IF(A"""+str(k+2)+"""<"2021.04.09 00:00:00",0,IF((-1)*K"""+str(k+2) \
                              +"""*P"""+str(k+2)+""">Z"""+str(k+2)+""",X"""+str(k+2)+""",IF(0.13*K"""+str(k+2) \
                              +"""*P"""+str(k+2)+"""+U"""+str(k+2)+""">0,0,0.15*((-1)*K"""+str(k+2) \
                              +"""*P"""+str(k+2)+"""-U"""+str(k+2)+"""/0.13)))),0),0)""")
    tax_current_list.append("""=U"""+str(k+2)+"""+X"""+str(k+2)+"""""")

Deals.loc[:, "Курс"] = rates_list
Deals.loc[:, "Прибыль в рублях"] = profit_RUB_list
Deals.loc[:, "Налогооблагаемый доход (на момент сделки)"] = NOD_current_list
Deals.loc[:, "Уже удержанный налог (на момент сделки)"] = tax_holding_list
Deals.loc[:, "Налог 13% за сделку"] = tax13_list
Deals.loc[:, "Накопленный налог 13%"] = tax13_current_list
Deals.loc[:, "Удержано 13% при выводе"] = tax13_holding_list
Deals.loc[:, "Налог 15% за сделку"] = tax15_list
Deals.loc[:, "Накопленный налог 15%"] = tax15_current_list
Deals.loc[:, "Удержано 15% при выводе"] = tax15_holding_list
Deals.loc[:, "Налог с учетом всех сделок и удержаний"] = tax_current_list

now = datetime.now()
if max(period_end).split("-")[0] == str(now.year):
    daterange = pd.date_range(str(now.year)+'-01-01',str(now.year)+'-'+str(now.month)+'-'+str(now.day))
else:
    daterange = pd.date_range(max(period_end).split("-")[0]+'-01-01',max(period_end).split("-")[0]+'-12-31')
#daterange = pd.date_range('2021-01-01','2021-12-31')
cbr_EUR = pd.DataFrame(columns=['Дата начала', 'Значение'])
cbr_USD = pd.DataFrame(columns=['Дата начала', 'Значение'])
for CBR_file in getCBR:
    cbr = pd.read_excel(CBR_file)
    cbr.sort_values(by='data')
    cbr_all = pd.DataFrame(columns=['Дата начала', 'Значение'])
    last_curs = '1'
    for date in daterange:
        date_rus = str(date).split(" ")[0].split("-")[2]+'.'+str(date).split(" ")[0].split("-")[1]+'.'+str(date).split(" ")[0].split("-")[0]
        curs = cbr[cbr['data']==str(date).split(" ")[0]]['curs']
        if not curs.empty:
            last_curs = curs.item()
        cbr_all.loc[len(cbr_all)] = [date_rus, last_curs]
    if cbr['cdx'][0] == 'Евро':
        cbr_EUR = cbr_all.copy()
    elif cbr['cdx'][0] == 'Доллар США':
        cbr_USD = cbr_all.copy()

swap_rates_USD = pd.DataFrame(columns=['Дата свопа','курс'])
swap_rates_EUR = pd.DataFrame(columns=['Дата свопа','курс'])
cliring_date = pd.DataFrame(columns=['Дата операции','Дата исполнения'])
for OPRDS_file in getOPRDS:
    oprds = pd.read_excel(OPRDS_file)
    swap_rates_USD = oprds.loc[(oprds['Вид сделки/операции'] == 'Комиссия за своп в валюте')&(oprds['Валюта'] == 'USD')&(oprds['%'] == '100 %'), ['Примечание']]
    if not swap_rates_USD.empty:
        swap_rates_USD = swap_rates_USD['Примечание'].str.split('\n',expand=True)
        swap_rates_USD_date = swap_rates_USD[0].str.split(' ',expand=True)
        swap_rates_USD_tick = swap_rates_USD[1].str.split(' ',expand=True)
        swap_rates_USD = pd.concat([swap_rates_USD_date[2],swap_rates_USD_tick[2]],axis=1)
        swap_rates_USD.columns=['Дата свопа','курс']
        swap_rates_USD.sort_values(by='Дата свопа')
    
    swap_rates_EUR = oprds.loc[(oprds['Вид сделки/операции'] == 'Комиссия за своп в валюте')&(oprds['Валюта'] == 'EUR')&(oprds['%'] == '100 %'), ['Примечание']]
    if not swap_rates_EUR.empty:
        swap_rates_EUR = swap_rates_EUR['Примечание'].str.split('\n',expand=True)
        swap_rates_EUR_date = swap_rates_EUR[0].str.split(' ',expand=True)
        swap_rates_EUR_tick = swap_rates_EUR[1].str.split(' ',expand=True)
        swap_rates_EUR = pd.concat([swap_rates_EUR_date[2],swap_rates_EUR_tick[2]],axis=1)
        swap_rates_EUR.columns=['Дата свопа','курс']
        swap_rates_EUR.sort_values(by='Дата свопа')
    
    cliring_date = oprds.loc[(oprds['Тип плана исполнения'] == 'Финансовый результат')&(oprds['Валюта'] != 'RUB')&(oprds['%'] == '100 %'), ['Дата операции','Дата исполнения']]
    if not cliring_date.empty:
        cliring_date = cliring_date.drop_duplicates(['Дата операции','Дата исполнения'], keep='first')
        cliring_date.sort_values(by='Дата операции')

with pd.ExcelWriter(result_dir+'/Налог '+fio.split(" ")[0]+' '+max(period_end).split("-")[0]+' .xlsx') as writer:
    Deals.to_excel(writer,index=False,header=True, sheet_name = 'Налог')
    if 'USD' in currencies:
        cbr_USD.to_excel(writer,index=False,header=True, sheet_name = 'курс ЦБ USD')
        swap_rates_USD.to_excel(writer,index=False,header=True, sheet_name = 'курс свопов USD')
    if 'EUR' in currencies:
        cbr_EUR.to_excel(writer,index=False,header=True, sheet_name = 'курс ЦБ EUR')
        swap_rates_EUR.to_excel(writer,index=False,header=True, sheet_name = 'курс свопов EUR')
    if 'USD' in currencies or 'EUR' in currencies:
        cliring_date.to_excel(writer,index=False,header=True, sheet_name = 'дата исполнения финреза')

