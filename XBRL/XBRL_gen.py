'''
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
'''
from lxml import etree
import re
import sys
import os
import shutil
import gc
import time
import csv
import uuid
import json
import datetime
from datetime import timedelta, date, time
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *

class Form(QMainWindow):
    def getfile(self,message,ftype):
        return QFileDialog.getOpenFileName(self,message,"./",ftype)

    def gettype(self):
        items = ("месячный", "квартальный", "годовой")
        item, ok = QInputDialog.getItem(self, "Параметры отчета", "тип отчета", items, 0, False)
        if ok and item:
            return(item)
    
    def direct(self,message):
        return QFileDialog.getExistingDirectory(self,message,"./")
    
    def inform(self,message,information):
        return QMessageBox.information(self, message, information)

    def getdate(self,title,message):
        return QInputDialog.getText(self, title, message, text = "ДД.ММ.ГГГГ")

def taxonomy_func(csv_key : str, default : str, deal, taxonomy_dict):
    if deal.get(csv_key) == None:
        return default
    else:
        return taxonomy_dict.get(deal[csv_key],deal[csv_key])

app = QApplication(sys.argv)
explorer = Form()
getCSV = explorer.getfile('Выберите файл со сделками','CSV files (*.csv)')[0]
if getCSV == '':
    sys.exit()
CSV_file = getCSV.split("/")[-1]
getInfSved = explorer.getfile('Выберите файл с информацией и сведением об организации','JSON files (*.json)')[0]
if getInfSved == '':
    getInfSved = os.path.dirname(os.path.abspath(__file__))+'\\inf_and_svedenia_417.json'
getTaxonomy = explorer.getfile('Выберите файл таксономии','Text files (*.txt)')[0]
if getTaxonomy == '':
    getTaxonomy = os.path.dirname(os.path.abspath(__file__))+'\\dict_417.txt'
type_dict = {"месячный":"m","квартальный":"m_q","годовой":"y"}
getType = explorer.gettype()
if getType == None:
    repType = 'm'
else:
    repType = type_dict[getType]
getRepDate = explorer.getdate("Укажите дату","отчетная дата")[0]
if not re.fullmatch(r'\d{2}.\d{2}.\d{4}', str(getRepDate)):
    report_date = str(datetime.datetime.now().date())
else:
    rep_d, rep_m, rep_y = str(getRepDate).split(".")
    report_date = rep_y+'-'+rep_m+'-'+rep_d
print(report_date)
csv_list = []
with open(getCSV) as repFile:  
    reader = csv.DictReader(repFile,delimiter=';')
    for row in reader:
        csv_list.append(row)
with open(getInfSved, encoding="utf-8") as fjson:
    inf_sved = json.load(fjson)
taxonomy_dict = {}
with open(getTaxonomy, 'r') as taxonomy_txt:
    for taxtag in taxonomy_txt:
        taxonomy_dict[taxtag.split(':')[0]] = taxtag.split(':')[1].split('\n')[0]
XBRL_417 = {}
count_str = 0
unicode_dict = {}
uid_list = []
OGRN = inf_sved["information"]["OGRN"]
for deal in csv_list:
    uid = 'DAB-'+str(uuid.uuid4())
    uid_list.append(uid)
    count_str += 1
    XBRL_417[uid]={}
    XBRL_417[uid]["identifier"] = OGRN
    XBRL_417[uid]["period"] = report_date
    XBRL_417[uid]["ID_strokiTypedname"] = deal.get("Идентификатор строки",str(count_str))
    XBRL_417[uid]["ID_SdelkiTypedName"] = deal.get("Идентификатор сделки","")
    if unicode_dict.get(deal.get("Дата заключения сделки")) == None:
        unicode_dict[deal.get("Дата заключения сделки")] = 0
    unicode_dict[deal.get("Дата заключения сделки")] += 1
    try:
        yyyy, mm, dd = str(deal.get("Дата заключения сделки")).split("-")
    except:
        yyyy, mm, dd = ['0000','00','00']
    XBRL_417[uid]["VnebirzhSdelka"] = deal.get("Уникальный номер информационного сообщения о сделке",dd+"."+mm+"."+yyyy+"-"+str(unicode_dict[deal.get("Дата заключения сделки")]).rjust(7,"0")+"-001-"+str(deal.get("Код направления сделки",""))[0]+"-001")
    #XBRL_417[uid]["VnebirzhSdelka"] = dd+"."+mm+"."+yyyy+"-"+str(unicode_dict[deal.get("Дата заключения сделки")]).rjust(7,"0")+"-001-"+str(deal.get("Код направления сделки",""))[0]+"-001"
    XBRL_417[uid]["TipVnebirzhSdelkiEnumerator"] = 'mem-int:'+taxonomy_func('Тип внебиржевой сделки','OWN_sobstvennayaMember',deal,taxonomy_dict)
    XBRL_417[uid]["Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki"] = deal.get("Дата заключения сделки","")
    XBRL_417[uid]["Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator"] = 'mem-int:'+taxonomy_func('Вид договора','FORWARD_forvardnyjDogovorMember',deal,taxonomy_dict)
    XBRL_417[uid]["Vid_PFIEnumerator"] = 'mem-int:'+taxonomy_func('Виды производных финансовых инструментов','ValyutnyjForvardMember',deal,taxonomy_dict)
    XBRL_417[uid]["Kod_naprav_sdelkiEnumerator"] = 'mem-int:'+taxonomy_func('Код направления сделки','',deal,taxonomy_dict)
    XBRL_417[uid]["Vid_Inf_SoobshhEnumerator"] = 'mem-int:'+taxonomy_func('Вид информационного сообщения о сделке','',deal,taxonomy_dict)
    XBRL_417[uid]["PlatezhUsloviyaSdelkiEnumerator"] = 'mem-int:'+taxonomy_func('Платежные условия сделки','C_raschetnyjMember',deal,taxonomy_dict)
    XBRL_417[uid]["Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki"] = deal.get("Информационная аналитическая система","MetaTrader 5")
    XBRL_417[uid]["Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd"] = deal.get("Наименование клиента","ФЛ")
    XBRL_417[uid]["Tip_identif_klienta_VnebirzhSdelkaEnumerator"] = 'mem-int:'+taxonomy_func('Тип идентификатора клиента','IDfizicheskogoLiczaMember',deal,taxonomy_dict)
    XBRL_417[uid]["Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd"] = deal.get("Идентификатор клиента","")
    XBRL_417[uid]["Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator"] = 'mem-int:'+taxonomy_func('Код страны регистрации клиента','Strana_643RusRossiyaMember',deal,taxonomy_dict)
    XBRL_417[uid]["Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd"] = deal.get("Наименование контрагента","ФЛ")
    XBRL_417[uid]["Tip_identif_kontr_VnebirzhSdelkaEnumerator"] = 'mem-int:'+taxonomy_func('Тип идентификатора контрагента','IDfizicheskogoLiczaMember',deal,taxonomy_dict)
    XBRL_417[uid]["Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd"] = deal.get("Идентификатор контрагента","")
    XBRL_417[uid]["Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator"] = 'mem-int:'+taxonomy_func('Код страны регистрации контрагента','Strana_643RusRossiyaMember',deal,taxonomy_dict)
    XBRL_417[uid]["Naim_em_Rek_em_Inf_perv_chast_sdelki"] = deal.get("Наименование эмитента по 1-й части сделки","")
    XBRL_417[uid]["ISIN_Rek_em"] = deal.get("Код финансового инструмента ISIN по 1-й части сделки","")
    XBRL_417[uid]["Kolvo_fin_instr_Rek_em"] = deal.get("Количество финансовых инструментов по 1-й части сделки","")
    XBRL_417[uid]["Tip_bazovogo_aktivaEnumerator"] = 'mem-int:'+taxonomy_func('Тип базового актива по 1-й части сделки','V1_valyutyMember',deal,taxonomy_dict)
    XBRL_417[uid]["Bazovyj_aktiv"] = deal.get("Базовый актив по 1-й части сделки","")
    XBRL_417[uid]["Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator"] = 'mem-int:'+taxonomy_func('Тип финансового инструмента по 1-й части сделки1','NekvalificzirovannyjMember',deal,taxonomy_dict)
    if deal.get("Код валюты цены по 1-й части сделки") == None:
        Kod_valyuty = ''
    else:
        if not re.fullmatch(r'\d{3}-\w{3}',deal["Код валюты цены по 1-й части сделки"]):
            Kod_valyuty = deal["Код валюты цены по 1-й части сделки"]
            for key in taxonomy_dict:
                if re.fullmatch(deal["Код валюты цены по 1-й части сделки"]+r'-\w{3}', str(key)):
                    Kod_valyuty = taxonomy_dict[key]
        else:
            Kod_valyuty = taxonomy_dict.get(deal["Код валюты цены по 1-й части сделки"],deal["Код валюты цены по 1-й части сделки"])
    XBRL_417[uid]["Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator"] = 'mem-int:'+Kod_valyuty
    XBRL_417[uid]["CZena_fin_instrumenta_Rek_em"] = deal.get("Цена финансового инструмента по 1-й части сделки","")
    XBRL_417[uid]["Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em"] = deal.get("Сумма по 1-й части сделки, в единицах валюты цены сделки","")
    XBRL_417[uid]["Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em"] = deal.get("Планируемая (фактическая) дата перерегистрации","")
    XBRL_417[uid]["Data_oplaty_fin_instrumenta_Rek_em"] = deal.get("Планируемая (фактическая) дата оплаты","")
    XBRL_417[uid]["Naim_emitenta_Inf_o_vtor_chast_sdelki"] = deal.get("Наименование эмитента по 2-й части сделки","")

del csv_list

uid = 'AF-'+str(uuid.uuid4())
uid_list.append(uid)
XBRL_417[uid]={}
XBRL_417[uid]["identifier"] = OGRN
XBRL_417[uid]["period"] = report_date
XBRL_417[uid]["Kod_Okato3"] = inf_sved["information"]["OKATO"]
XBRL_417[uid]["INN_Prof_uch"] = inf_sved["information"]["INN"]
XBRL_417[uid]["OGRN_Prof_uch"] = inf_sved["information"]["OGRN"]
XBRL_417[uid]["Poln_Naim_Prof_uch"] = inf_sved["information"]["poln_naim"]
XBRL_417[uid]["SokrNaim_Prof_uch"] = inf_sved["information"]["kratk_naim"]
XBRL_417[uid]["AdresPocht_Prof_uch"] = inf_sved["information"]["pochta"]
XBRL_417[uid]["FIOEIO"] = inf_sved["information"]["FIO_eio"]
XBRL_417[uid]["Dolzgnostlizapodpotchetnost"] = inf_sved["information"]["dolzhn_eio"]
XBRL_417[uid]["Osnispobyaz"] = inf_sved["information"]["osnov_eio"]
XBRL_417[uid]["FIOEIOkontr"] = inf_sved["information"]["FIO_kontr"]
XBRL_417[uid]["Osnispobyazkontr"] = inf_sved["information"]["osnov_kontr"]

uid = 'AF-'+str(uuid.uuid4())
uid_list.append(uid)
XBRL_417[uid]={}
XBRL_417[uid]["identifier"] = OGRN
XBRL_417[uid]["period"] = report_date
XBRL_417[uid]["explicitMember"] = 'mem-int:'+inf_sved["svedenya"]["rep_417"]["taxonomy"]
XBRL_417[uid]["LiczoOtvZaPrOblast"] = inf_sved["svedenya"]["rep_417"]["FIO_otv"]
XBRL_417[uid]["DolzhLiczaOtvZaPrOblast"] = inf_sved["svedenya"]["rep_417"]["dolzhn_otv"]
XBRL_417[uid]["KontInfLiczaOtvZaPrOblast"] = inf_sved["svedenya"]["rep_417"]["nomer_otv"]
XBRL_417[uid]["Priznak_Nulevogo_OtchetaEnumerator"] = 'mem-int:'+taxonomy_dict.get(inf_sved["svedenya"]["rep_417"].get("priznak_null","Нет"),'NetMember')
XBRL_417[uid]["NaimITrazrabotchika"] = inf_sved["svedenya"]["rep_417"]["it_razrab"]

#Проверка файлов
direction = os.path.dirname(os.path.abspath(__file__))+'\\'
direction = os.path.join(direction, 'temp_XBRL_gen')
if os.path.exists(direction):
    shutil.rmtree(direction)
os.mkdir(direction)
print('Проверка начата')
count_deal = 0
new_deal = 0
cancel_deal = 0
code_list = []
error_list = ""
count_error = 0
count_error_context = 0
count_error_deal = 0
last_date = report_date
ferror_temp = open(direction+'\\temp_errors_'+CSV_file.split(".")[0]+'.txt','w',encoding='utf-8')
if OGRN != '1167746614947':
    ferror_temp.write("Некорректный ОГРН в названии файла\n")
    count_error += 1
for key in XBRL_417:
    if XBRL_417[key].get("identifier") != OGRN:
        error_list += key + ":\t" + str(XBRL_417[key].get("identifier")) + "\tНекорректный показатель identifier\n"
    if XBRL_417[key].get("period") != last_date:
        error_list += key + ":\t" + str(XBRL_417[key].get("period")) + "\tНекорректный показатель period\n"
    if XBRL_417[key].get("VnebirzhSdelka", "wrong") != "wrong":
        count_deal += 1
        if not re.fullmatch(r'\d+', str(XBRL_417[key].get("ID_strokiTypedname"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("ID_strokiTypedname")) + "\tНекорректный показатель ID_strokiTypedname\n"
        if not re.fullmatch(r'\d+', str(XBRL_417[key].get("ID_SdelkiTypedName"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("ID_SdelkiTypedName")) + ":\tНекорректный показатель ID_SdelkiTypedName\n"
        code_list.append(XBRL_417[key].get("VnebirzhSdelka"))
        if not re.fullmatch(r'\d{2}\.\d{2}\.\d{4}-\d{7}-001-[BS]-001', str(XBRL_417[key].get("VnebirzhSdelka"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("VnebirzhSdelka")) + ":\tНекорректный показатель VnebirzhSdelka\n"
        if XBRL_417[key].get("TipVnebirzhSdelkiEnumerator") != 'mem-int:OWN_sobstvennayaMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("TipVnebirzhSdelkiEnumerator")) + ":\tНекорректный показатель TipVnebirzhSdelkiEnumerator\n"
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(XBRL_417[key].get("Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki"))) or str(XBRL_417[key].get("Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki"))[0:8] != last_date[0:8]:
                error_list += key + ":\t" + str(XBRL_417[key].get("Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki")) + ":\tНекорректный показатель Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki\n"
        except:
            error_list += key + ":\t" + str(XBRL_417[key].get("Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki")) + ":\tНекорректный показатель Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki\n"
        if XBRL_417[key].get("Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator") != 'mem-int:FORWARD_forvardnyjDogovorMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator")) + ":\tНекорректный показатель Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator\n"
        if XBRL_417[key].get("Vid_PFIEnumerator") != 'mem-int:ValyutnyjForvardMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("Vid_PFIEnumerator")) + ":\tНекорректный показатель Vid_PFIEnumerator\n"
        if not re.fullmatch(r'mem-int:[BS]_\w+member', str(XBRL_417[key].get("Kod_naprav_sdelkiEnumerator"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("Kod_naprav_sdelkiEnumerator")) + ":\tНекорректный показатель Kod_naprav_sdelkiEnumerator\n"
        if XBRL_417[key].get("Vid_Inf_SoobshhEnumerator") != 'mem-int:NEW_zaklyuchenieCdelkiMember' and XBRL_417[key].get("Vid_Inf_SoobshhEnumerator") != 'mem-int:CANCEL_OtmenaSdelkiMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("Vid_Inf_SoobshhEnumerator")) + "\tНекорректный показатель Vid_Inf_SoobshhEnumerator\n"
        else:
            if XBRL_417[key]["Vid_Inf_SoobshhEnumerator"].split("_")[0] == "mem-int:NEW": new_deal += 1
            if XBRL_417[key]["Vid_Inf_SoobshhEnumerator"].split("_")[0] == "mem-int:CANCEL": cancel_deal += 1
        if XBRL_417[key].get("PlatezhUsloviyaSdelkiEnumerator") != 'mem-int:C_raschetnyjMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("PlatezhUsloviyaSdelkiEnumerator")) + ":\tНекорректный показатель PlatezhUsloviyaSdelkiEnumerator\n"
        if XBRL_417[key].get("Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki") != 'MetaTrader 5':
            error_list += key + ":\t" + str(XBRL_417[key].get("Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki")) + ":\tНекорректный показатель Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki\n"
        if XBRL_417[key].get("Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd") != 'ФЛ':
            error_list += key + ":\t" + str(XBRL_417[key].get("Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd")) + ":\tНекорректный показатель Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd\n"
        if XBRL_417[key].get("Tip_identif_klienta_VnebirzhSdelkaEnumerator") != 'mem-int:IDfizicheskogoLiczaMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("Tip_identif_klienta_VnebirzhSdelkaEnumerator")) + ":\tНекорректный показатель Tip_identif_klienta_VnebirzhSdelkaEnumerator\n"
        if not re.fullmatch(r'\d{2}\s\d{2}\s\d{6}/1', str(XBRL_417[key].get("Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd")) + ":\tНекорректный показатель Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd\n"    
        if XBRL_417[key].get("Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator") != 'mem-int:Strana_643RusRossiyaMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator")) + ":\tНекорректный показатель Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator\n"
        if XBRL_417[key].get("Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd") != 'ФЛ':
            error_list += key + ":\t" + str(XBRL_417[key].get("Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd")) + ":\tНекорректный показатель Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd\n"
        if XBRL_417[key].get("Tip_identif_kontr_VnebirzhSdelkaEnumerator") != 'mem-int:IDfizicheskogoLiczaMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("Tip_identif_kontr_VnebirzhSdelkaEnumerator")) + ":\tНекорректный показатель Tip\n"
        if not re.fullmatch(r'\d{2}\s\d{2}\s\d{6}/1', str(XBRL_417[key].get("Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd")) + ":\tНекорректный показатель Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd\n"  
        if XBRL_417[key].get("Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator") != 'mem-int:Strana_643RusRossiyaMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator")) + ":\tНекорректный показатель Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator\n"
        if XBRL_417[key].get("Naim_em_Rek_em_Inf_perv_chast_sdelki") != "":
            error_list += key + ":\t" + str(XBRL_417[key].get("Naim_em_Rek_em_Inf_perv_chast_sdelki")) + ":\tНекорректный показатель Naim_em_Rek_em_Inf_perv_chast_sdelki\n"
        if not re.fullmatch(r'[A-Z]{3}/[A-Z]{3}', str(XBRL_417[key].get("ISIN_Rek_em"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("ISIN_Rek_em")) + ":\tНекорректный показатель ISIN_Rek_em\n"
        if XBRL_417[key].get("Kolvo_fin_instr_Rek_em") == None:
            error_list += key + ":\t" + str(XBRL_417[key].get("Kolvo_fin_instr_Rek_em")) + ":\tНекорректный показатель Kolvo_fin_instr_Rek_em\n"
        if XBRL_417[key].get("Tip_bazovogo_aktivaEnumerator") != 'mem-int:V1_valyutyMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("Tip_bazovogo_aktivaEnumerator")) + ":\tНекорректный показатель Tip_bazovogo_aktivaEnumerator\n"
        if not re.fullmatch(r'\d{3}/\d{3}', str(XBRL_417[key].get("Bazovyj_aktiv"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("Bazovyj_aktiv")) + ":\tНекорректный показатель Bazovyj_aktiv\n"
        if XBRL_417[key].get("Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator") != 'mem-int:NekvalificzirovannyjMember':
            error_list += key + ":\t" + str(XBRL_417[key].get("Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator")) + ":\tНекорректный показатель Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator\n"
        if not re.fullmatch(r'mem-int:Valyuta_\d{3}\w+Member', str(XBRL_417[key].get("Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator")) + ":\tНекорректный показатель Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator\n"
        if XBRL_417[key].get("CZena_fin_instrumenta_Rek_em") == None:
            error_list += key + ":\t" + str(XBRL_417[key].get("CZena_fin_instrumenta_Rek_em")) + ":\tНекорректный показатель CZena_fin_instrumenta_Rek_em\n"
        if XBRL_417[key].get("Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em") == None:
            error_list += key + ":\t" + str(XBRL_417[key].get("Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em")) + ":\tНекорректный показатель Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em\n"
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(XBRL_417[key].get("Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em"))) or str(XBRL_417[key].get("Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em"))[0:8] != last_date[0:8]:
                error_list += key + ":\t" + str(XBRL_417[key].get("Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em")) + ":\tНекорректный показатель Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em\n"
        except:
            error_list += key + ":\t" + str(XBRL_417[key].get("Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em")) + ":\tНекорректный показатель Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em\n"
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(XBRL_417[key].get("Data_oplaty_fin_instrumenta_Rek_em"))) or str(XBRL_417[key].get("Data_oplaty_fin_instrumenta_Rek_em"))[0:8] != last_date[0:8]:
                error_list += key + ":\t" + str(XBRL_417[key].get("Data_oplaty_fin_instrumenta_Rek_em")) + ":\tНекорректный показатель Data_oplaty_fin_instrumenta_Rek_em\n"
        except:
            error_list += key + ":\t" + str(XBRL_417[key].get("Data_oplaty_fin_instrumenta_Rek_em")) + ":\tНекорректный показатель Data_oplaty_fin_instrumenta_Rek_em\n"
        if XBRL_417[key].get("Naim_emitenta_Inf_o_vtor_chast_sdelki") != "":
            error_list += key + ":\t" + str(XBRL_417[key].get("Naim_emitenta_Inf_o_vtor_chast_sdelki")) + ":\tНекорректный показатель Naim_emitenta_Inf_o_vtor_chast_sdelki\n"
        try:
            if str(XBRL_417[key].get("VnebirzhSdelka"))[0:2] != str(XBRL_417[key].get("Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki"))[8:10] or str(XBRL_417[key].get("VnebirzhSdelka"))[3:5] != str(XBRL_417[key].get("Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki"))[5:7] or str(XBRL_417[key].get("VnebirzhSdelka"))[6:10] != str(XBRL_417[key].get("Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki"))[0:4] or str(XBRL_417[key].get("VnebirzhSdelka"))[23] != str(XBRL_417[key].get("Kod_naprav_sdelkiEnumerator"))[8]:
                error_list += key + ":\tНекорректный уникальный код\n"
        except:
            error_list += key + ":\tНекорректный уникальный код\n"
        if error_list != "":
            count_error_deal += 1
    elif XBRL_417[key].get("explicitMember", "wrong") != "wrong":
        if XBRL_417[key].get("explicitMember") != 'mem-int:OKUD0420417Member':
            error_list += key + ":\t" + str(XBRL_417[key].get("explicitMember")) + ":\tНекорректный показатель explicitMember\n"
        if XBRL_417[key].get("LiczoOtvZaPrOblast") != 'Козлова Виктория Викторовна':
            error_list += key + ":\t" + str(XBRL_417[key].get("LiczoOtvZaPrOblast")) + ":\tНекорректный показатель LiczoOtvZaPrOblast\n"
        if XBRL_417[key].get("DolzhLiczaOtvZaPrOblast") != 'Отдел внутреннего учета':
            error_list += key + ":\t" + str(XBRL_417[key].get("DolzhLiczaOtvZaPrOblast")) + ":\tНекорректный показатель DolzhLiczaOtvZaPrOblast\n"
        if not re.fullmatch(r'\d{11}', str(XBRL_417[key].get("KontInfLiczaOtvZaPrOblast"))):
            error_list += key + ":\t" + str(XBRL_417[key].get("KontInfLiczaOtvZaPrOblast")) + ":\tНекорректный показатель KontInfLiczaOtvZaPrOblast\n"
        if XBRL_417[key].get("NaimITrazrabotchika") != 'ООО "ДИБ СИСТЕМС"':
            error_list += key + ":\t" + str(XBRL_417[key].get("NaimITrazrabotchika")) + ":\tНекорректный показатель NaimITrazrabotchika\n"
    elif XBRL_417[key].get("INN_Prof_uch", "wrong") != "wrong":
        if XBRL_417[key].get("INN_Prof_uch") != '7708294216':
            error_list += key + ":\t" + str(XBRL_417[key].get("INN_Prof_uch")) + ":\tНекорректный показатель INN_Prof_uch\n"
        if XBRL_417[key].get("OGRN_Prof_uch") != OGRN:
            error_list += key + ":\t" + str(XBRL_417[key].get("OGRN_Prof_uch")) + ":\tНекорректный показатель OGRN_Prof_uch\n"
        if XBRL_417[key].get("Poln_Naim_Prof_uch") != 'Общество с ограниченной ответственностью "Альфа-Форекс"':
            error_list += key + ":\t" + str(XBRL_417[key].get("Poln_Naim_Prof_uch")) + ":\tНекорректный показатель Poln_Naim_Prof_uch\n"
        if XBRL_417[key].get("SokrNaim_Prof_uch") != 'ООО "Альфа-Форекс"':
            error_list += key + ":\t" + str(XBRL_417[key].get("SokrNaim_Prof_uch")) + ":\tНекорректный показатель SokrNaim_Prof_uch\n"
        if XBRL_417[key].get("AdresPocht_Prof_uch") != '107078, Москва г, Маши Порываевой улица, дом № 7, строение 1, этаж 1':
            error_list += key + ":\t" + str(XBRL_417[key].get("AdresPocht_Prof_uch")) + ":\tНекорректный показатель AdresPocht_Prof_uch\n"
        if XBRL_417[key].get("Kod_Okato3") != '45286565000':
            error_list += key + ":\t" + str(XBRL_417[key].get("Kod_Okato3")) + ":\tНекорректный показатель Kod_Okato3\n"
        if XBRL_417[key].get("FIOEIO") != 'Николюк Сергей Васильевич' and XBRL_417[key].get("FIOEIO") != 'Лафа Виктория Владимировна':
            error_list += key + ":\t" + str(XBRL_417[key].get("FIOEIO")) + ":\tНекорректный показатель FIOEIO\n"
        if XBRL_417[key].get("Dolzgnostlizapodpotchetnost") != 'Генеральный директор':
            error_list += key + ":\t" + str(XBRL_417[key].get("Dolzgnostlizapodpotchetnost")) + ":\tНекорректный показатель Dolzgnostlizapodpotchetnost\n"
        if XBRL_417[key].get("FIOEIOkontr") != 'Лафа Виктория Владимировна' and XBRL_417[key].get("FIOEIOkontr") != 'Козлова Виктория Викторовна':
            error_list += key + ":\t" + str(XBRL_417[key].get("FIOEIOkontr")) + ":\tНекорректный показатель FIOEIOkontr\n"
        if not re.fullmatch(r'Решение единственного участника ООО "Альфа-Форекс" от \d{2} сентября \d{4} года', XBRL_417[key].get("Osnispobyaz")):
            error_list += key + ":\t" + str(XBRL_417[key].get("Osnispobyaz")) + ":\tНекорректный показатель Osnispobyaz\n"
        if XBRL_417[key].get("Osnispobyazkontr") != 'Приказ № 8 от 18.09.2018г.':
            error_list += key + ":\t" + str(XBRL_417[key].get("Osnispobyazkontr")) + ":\tНекорректный показатель Osnispobyazkontr\n"
    if error_list != "":
        count_error_context += 1
        ferror_temp.write(error_list)
        count_error += error_list.count("\n")
    error_list = ""
print('Проверка закончена')
info = "Всего сделок:\t"+str(count_deal)
info += "\nновых:\t\t"+str(new_deal)
info += "\nотменных:\t"+str(cancel_deal)
info += "\n\nВсего ошибок:\t"+str(count_error)
info += "\nконтекстов:\t"+str(count_error_context)
info += "\nсделок:\t\t"+str(count_error_deal)
if len(code_list) != len(set(code_list)):
    info += "\n\nНЕуникальные коды!!!"
if len(uid_list) != len(set(uid_list)):
    info += "\n\nНЕуникальные UID!!!"
ferror_temp.close()
explorer.inform('Результат проверки',info)
result_dir = explorer.direct("Укажите путь для сохранения XBRL")+'/'
if result_dir != '/':
    result_dir = os.path.join(result_dir, 'result_XBRL_gen')
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    result_dir += '/'
    if os.path.isfile(result_dir+"info_"+CSV_file.split(".")[0]+".txt"):
        os.remove(result_dir+"info_"+CSV_file.split(".")[0]+".txt")
    if os.path.isfile(result_dir+"errors_"+CSV_file.split(".")[0]+".txt"):
        os.remove(result_dir+"errors_"+CSV_file.split(".")[0]+".txt")
    with open(result_dir+'info_'+CSV_file.split(".")[0]+'.txt','w',encoding='utf-8') as finfo:
        finfo.write(info)
    if count_error != 0:
        shutil.copyfile(direction+"\\temp_errors_"+CSV_file.split(".")[0]+".txt", result_dir+"errors_"+CSV_file.split(".")[0]+".txt")
    
    with open(result_dir+'XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10d_reestr_0420417_'+report_date.replace("-","")+'.xml','w',encoding='utf-8') as myXBRL:
        NSMAP = {'mem_int': 'http://www.cbr.ru/xbrl/udr/dom/mem-int',
                 'xlink': 'http://www.w3.org/1999/xlink',
                 'dim_int': 'http://www.cbr.ru/xbrl/udr/dim/dim-int',
                 'iso4217': 'http://www.xbrl.org/2003/iso4217',
                 'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                 'link': 'http://www.xbrl.org/2003/linkbase',
                 'purcb_dic': 'http://www.cbr.ru/xbrl/nso/purcb/dic/purcb-dic',
                 'xbrldi': 'http://xbrl.org/2006/xbrldi',
                 'xsi_schemaLocation': 'http://xbrl.org/2006/xbrldi http://www.xbrl.org/2006/xbrldi-2006.xsd',
                 'xbrli': 'http://www.xbrl.org/2003/instance'}
        myXBRL.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+"\n")
        myXBRL.write("<xbrli:xbrl xmlns:mem-int=\""+NSMAP["mem_int"]+"\" xmlns:xlink=\""+NSMAP["xlink"]+"\" xmlns:dim-int=\""+NSMAP["dim_int"]+"\" xmlns:iso4217=\""+NSMAP["iso4217"]+"\" xmlns:xsi=\""+NSMAP["xsi"]+"\" xmlns:link=\""+NSMAP["link"]+"\" xmlns:purcb-dic=\""+NSMAP["purcb_dic"]+"\" xmlns:xbrldi=\""+NSMAP["xbrldi"]+"\" xsi:schemaLocation=\""+NSMAP["xsi_schemaLocation"]+"\" xmlns:xbrli=\""+NSMAP["xbrli"]+"\">"+"\n")
        for context_id in XBRL_417:
            xml_str = '<xbrli:context id="{context_id}"> <xbrli:entity> <xbrli:identifier scheme="http://www.cbr.ru">{identifier}</xbrli:identifier> </xbrli:entity> <xbrli:period> <xbrli:instant>{period}</xbrli:instant> </xbrli:period>'.format(context_id=context_id, identifier=XBRL_417[context_id].get("identifier"), period=XBRL_417[context_id].get("period"))
            if XBRL_417[context_id].get("VnebirzhSdelka", "wrong") != "wrong":
                xml_str += ' <xbrli:scenario> <xbrldi:typedMember dimension="dim-int:ID_strokiTaxis"> <dim-int:ID_strokiTypedname>{ID_strokiTypedname}</dim-int:ID_strokiTypedname> </xbrldi:typedMember> <xbrldi:typedMember dimension="dim-int:ID_vnebirg_sdelkiTaxis"> <dim-int:ID_SdelkiTypedName>{ID_SdelkiTypedName}</dim-int:ID_SdelkiTypedName> </xbrldi:typedMember> </xbrli:scenario> </xbrli:context>'.format(ID_strokiTypedname=XBRL_417[context_id].get("ID_strokiTypedname"), ID_SdelkiTypedName=XBRL_417[context_id].get("ID_SdelkiTypedName"))
            elif XBRL_417[context_id].get("explicitMember", "wrong") != "wrong":
                xml_str += ' <xbrli:scenario> <xbrldi:explicitMember dimension="dim-int:OKUDAxis">{explicitMember}</xbrldi:explicitMember> </xbrli:scenario> </xbrli:context>'.format(explicitMember=XBRL_417[context_id].get("explicitMember"))
            myXBRL.write(xml_str+"\n")
        myXBRL.write("<xbrli:unit id=\"pure\"><xbrli:measure>xbrli:pure</xbrli:measure></xbrli:unit>"+"\n")
        myXBRL.write("<xbrli:unit id=\"RUB\"><xbrli:measure>iso4217:RUB</xbrli:measure></xbrli:unit>"+"\n") 
        for context_id in XBRL_417:
            xml_str = ''
            for name in XBRL_417[context_id]:
                if name not in ['identifier', 'period', 'ID_strokiTypedname', 'ID_SdelkiTypedName', 'explicitMember', 'Kolvo_fin_instr_Rek_em', 'CZena_fin_instrumenta_Rek_em', 'Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em']:
                    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=context_id, pokazatel=name, znachenie=XBRL_417[context_id][name])
                elif name in ['Kolvo_fin_instr_Rek_em', 'CZena_fin_instrumenta_Rek_em', 'Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em']:
                    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}" decimals="2" unitRef="RUB">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=context_id, pokazatel=name, znachenie=XBRL_417[context_id][name])
            myXBRL.write(xml_str+'\n') 
        myXBRL.write("</xbrli:xbrl>")

shutil.rmtree(direction)
