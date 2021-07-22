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
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
import PySimpleGUI as sg
import time

class Form(QMainWindow):
    def getfile(self):
        return QFileDialog.getOpenFileName(self,"Выберите XBRL файл","./","XBRL files (*.xml)")
    
    def direct(self):
        return QFileDialog.getExistingDirectory(self,"Укажите путь для сохранения результатов","./")
    
    def inform(self,message,information):
        return QMessageBox.information(self, message,information)


app = QApplication(sys.argv)
explorer = Form()
getXBRL = explorer.getfile()[0]
if getXBRL == '':
    sys.exit()
XBRL_file = getXBRL.split("/")[-1]
XBRL_417 = {}

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

direction = os.path.dirname(os.path.abspath(__file__))+'\\'
direction = os.path.join(direction, 'temp_XBRL_check')
if os.path.exists(direction):
    shutil.rmtree(direction)
os.mkdir(direction)

count_str = 0
with open(getXBRL,'r',encoding='utf-8') as f_orig:
    for line in f_orig:
        count_str += 1

count_deal = 0
new_deal = 0
cancel_deal = 0
code_list = []
count_error = 0
if count_str >= 100:
    shag = int(count_str/100)
else:
    shag = 1
progress = 0

sg.one_line_progress_meter('', progress, 100, 'Проверка файла:\n'+XBRL_file ,orientation='h',size = (40,20), no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'),key = 'progresspar')

period_date = XBRL_file.split("_")[-1].replace(".xml","")
last_date = period_date[0:4]+"-"+period_date[4:6]+"-"+period_date[6:8]
OGRN = XBRL_file.split("_")[1]
ferror_temp = open(direction+'\\temp_errors_'+XBRL_file.split(".")[0]+'.txt','w',encoding='utf-8')
try:
    if XBRL_file.split("_")[6] == '10d':
        repType = XBRL_file.split("_")[5]
    elif XBRL_file.split("_")[7] == '10d':
        repType = XBRL_file.split("_")[5]+'_'+XBRL_file.split("_")[6]
    else:
        ferror_temp.write("Некорректное название файла\n")
        count_error += 1
except:
    repType = ''
    ferror_temp.write("Некорректное название файла\n")
    count_error += 1
error_list = ""

if OGRN != '1167746614947':
    ferror_temp.write("Некорректный ОГРН в названии файла\n")
    count_error += 1
if period_date[4:6] in ['01','02','04','05','07','08','10','11']:
    if repType != 'm':
        ferror_temp.write("Некорректно указана точка входа в названии файла\n")
        count_error += 1
elif period_date[4:6] in ['03','06','09']:
    if repType != 'm_q':
        ferror_temp.write("Некорректно указана точка входа в названии файла\n")
        count_error += 1
elif period_date[4:6] in ['12']:
    if repType != 'y':
        ferror_temp.write("Некорректно указана точка входа в названии файла\n")
        count_error += 1
else:
    ferror_temp.write("Некорректно указан месяц в названии файла\n")
######################################################################### рабочий вариант чтения по-строчно ######################################################################

count_str = 0
with open(getXBRL,'r',encoding='utf-8') as f_orig:
    context_id = ''
    context_ref = ''
    print('Проверка начата')
    for line in f_orig:
        count_str += 1
        if 'ep_nso_purcb_' in line:
            for_check = 'ep_nso_purcb_' + line.split("ep_nso_purcb_")[1].split(".xsd")[0]
            typeTaxonomy = line.split("ep_nso_purcb_")[1].split("_10d")[0]
            if period_date[4:6] in ['01','02','04','05','07','08','10','11']:
                if typeTaxonomy != 'm':
                    error_list += for_check + "\tНекорректная точка входа в шапке\n"
                    count_error += 1
            elif period_date[4:6] in ['03','06','09']:
                if typeTaxonomy != 'm_q':
                    error_list += for_check + "\tНекорректная точка входа в шапке\n"
                    count_error += 1
            elif period_date[4:6] in ['12']:
                if typeTaxonomy != 'y':
                    error_list += for_check + "\tНекорректная точка входа в шапке\n"
                    count_error += 1
        if '<xbrli:context' in line:
            if 'id="' in line:
                context_id = line.split("id=\"")[1].split("\"")[0]
        if 'xbrli:identifier' in line:
            for_check = line.split("</xbrli:identifier>")[0].split(">")[-1]
            if for_check != OGRN:
                error_list += context_id + ":\t" + for_check + "\tНекорректный показатель identifier\n"
        if 'xbrli:instant' in line:
            for_check = line.split("</xbrli:instant>")[0].split(">")[-1]
            if for_check != last_date:
                error_list += context_id + ":\t" + for_check + "\tНекорректный показатель period\n"
        if 'dim-int:ID_strokiTypedname' in line:
            for_check = line.split("</dim-int:ID_strokiTypedname>")[0].split(">")[-1]
            if not re.fullmatch(r'\d+', for_check):
                error_list += context_id + ":\t" + for_check + "\tНекорректный показатель ID_strokiTypedname\n"
        if 'dim-int:ID_SdelkiTypedName' in line:
            count_deal += 1
            XBRL_417[context_id]={}
            for_check = line.split("</dim-int:ID_SdelkiTypedName>")[0].split(">")[-1]
            if not re.fullmatch(r'\d+', for_check):
                error_list += context_id + ":\t" + for_check + ":\tНекорректный показатель ID_SdelkiTypedName\n"
        if 'xbrldi:explicitMember' in line:
            for_check = line.split("</xbrldi:explicitMember>")[0].split(">")[-1]
            if for_check != 'mem-int:OKUD0420417Member':
                error_list += context_id + ":\t" + for_check + ":\tНекорректный показатель explicitMember\n"
        if '<purcb-dic:' in line:
            pokazateli = line.split("<")
            for i in range(len(pokazateli)):
                if i % 2 == 1:
                    tag, znach = pokazateli[i].split(">")
                    name = tag.split("purcb-dic:")[-1].split(" ")[0]
                    if 'contextRef="' in line:
                        context_ref = tag.split("contextRef=\"")[-1].split("\"")[0]
                    if name == 'VnebirzhSdelka':
                        code_list.append(znach)
                        try:
                            XBRL_417[context_ref]["Code"] = znach.split("-")[0]+"-"+znach.split("-")[3]
                        except:
                            XBRL_417[context_ref]["Code"] = ''
                        if not re.fullmatch(r'\d{2}\.\d{2}\.\d{4}-\d{7}-001-[BS]-001', znach):
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель VnebirzhSdelka\n"
                    if name == 'TipVnebirzhSdelkiEnumerator':
                        if znach != 'mem-int:OWN_sobstvennayaMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель TipVnebirzhSdelkiEnumerator\n"
                    if name == 'Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki':
                        XBRL_417[context_ref]["Date"] = znach
                        try:
                            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', znach) or znach[0:8] != last_date[0:8]:
                                error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki\n"
                        except:
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki\n"
                    if name == 'Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator':
                        if znach != 'mem-int:FORWARD_forvardnyjDogovorMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator\n"
                    if name == 'Vid_PFIEnumerator':
                        if znach != 'mem-int:ValyutnyjForvardMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Vid_PFIEnumerator\n"
                    if name == 'Kod_naprav_sdelkiEnumerator':
                        try:
                            XBRL_417[context_ref]["Napr"] = znach[8]
                        except:
                            XBRL_417[context_ref]["Napr"] = ''
                        if not re.fullmatch(r'mem-int:[BS]_\w+member', znach):
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Kod_naprav_sdelkiEnumerator\n"
                    if name == 'Vid_Inf_SoobshhEnumerator':
                        if znach != 'mem-int:NEW_zaklyuchenieCdelkiMember' and znach != 'mem-int:CANCEL_OtmenaSdelkiMember':
                            error_list += context_ref + ":\t" + znach + "\tНекорректный показатель Vid_Inf_SoobshhEnumerator\n"
                        else:
                            if znach.split("_")[0] == "mem-int:NEW": new_deal += 1
                            if znach.split("_")[0] == "mem-int:CANCEL": cancel_deal += 1
                    if name == 'PlatezhUsloviyaSdelkiEnumerator':
                        if znach != 'mem-int:C_raschetnyjMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель PlatezhUsloviyaSdelkiEnumerator\n"
                    if name == 'Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki':
                        if znach != 'MetaTrader 5':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki\n"
                    if name == 'Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd':
                        if znach != 'ФЛ':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd\n"
                    if name == 'Tip_identif_klienta_VnebirzhSdelkaEnumerator':
                        if znach != 'mem-int:IDfizicheskogoLiczaMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Tip_identif_klienta_VnebirzhSdelkaEnumerator\n"
                    if name == 'Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd':
                        if not re.fullmatch(r'\d{2}\s\d{2}\s\d{6}/1', znach):
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd\n"    
                    if name == 'Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator':
                        if znach != 'mem-int:Strana_643RusRossiyaMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator\n"
                    if name == 'Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd':
                        if znach != 'ФЛ':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd\n"
                    if name == 'Tip_identif_kontr_VnebirzhSdelkaEnumerator':
                        if znach != 'mem-int:IDfizicheskogoLiczaMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Tip\n"
                    if name == 'Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd':
                        if not re.fullmatch(r'\d{2}\s\d{2}\s\d{6}/1', znach):
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd\n"  
                    if name == 'Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator':
                        if znach != 'mem-int:Strana_643RusRossiyaMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator\n"
                    if name == 'Naim_em_Rek_em_Inf_perv_chast_sdelki':
                        if znach != "":
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Naim_em_Rek_em_Inf_perv_chast_sdelki\n"
                    if name == 'ISIN_Rek_em':
                        if not re.fullmatch(r'[A-Z]{3}/[A-Z]{3}', znach):
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель ISIN_Rek_em\n"
                    if name == 'Kolvo_fin_instr_Rek_em':
                        if znach == None:
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Kolvo_fin_instr_Rek_em\n"
                    if name == 'Tip_bazovogo_aktivaEnumerator':
                        if znach != 'mem-int:V1_valyutyMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Tip_bazovogo_aktivaEnumerator\n"
                    if name == 'Bazovyj_aktiv':
                        if not re.fullmatch(r'\d{3}/\d{3}', znach):
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Bazovyj_aktiv\n"
                    if name == 'Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator':
                        if znach != 'mem-int:NekvalificzirovannyjMember':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator\n"
                    if name == 'Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator':
                        if not re.fullmatch(r'mem-int:Valyuta_\d{3}\w+Member', znach):
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator\n"
                    if name == 'CZena_fin_instrumenta_Rek_em':
                        if znach == None:
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель CZena_fin_instrumenta_Rek_em\n"
                    if name == 'Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em':
                        if znach == None:
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em\n"
                    if name == 'Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em':
                        try:
                            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', znach) or znach[0:8] != last_date[0:8]:
                                error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em\n"
                        except:
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em\n"
                    if name == 'Data_oplaty_fin_instrumenta_Rek_em':
                        try:
                            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', znach) or znach[0:8] != last_date[0:8]:
                                error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Data_oplaty_fin_instrumenta_Rek_em\n"
                        except:
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Data_oplaty_fin_instrumenta_Rek_em\n"
                    if name == 'Naim_emitenta_Inf_o_vtor_chast_sdelki':
                        if znach != "":
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Naim_emitenta_Inf_o_vtor_chast_sdelki\n"
                    if name == 'LiczoOtvZaPrOblast':
                        if znach != 'Козлова Виктория Викторовна':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель LiczoOtvZaPrOblast\n"
                    if name == 'DolzhLiczaOtvZaPrOblast':
                        if znach != 'Отдел внутреннего учета':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель DolzhLiczaOtvZaPrOblast\n"
                    if name == 'KontInfLiczaOtvZaPrOblast':
                        if not re.fullmatch(r'\d{11}', znach):
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель KontInfLiczaOtvZaPrOblast\n"
                    if name == 'NaimITrazrabotchika':
                        if znach != 'ООО "ДИБ СИСТЕМС"':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель NaimITrazrabotchika\n"
                    if name == 'INN_Prof_uch':
                        if znach != '7708294216':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель INN_Prof_uch\n"
                    if name == 'OGRN_Prof_uch':
                        if znach != OGRN:
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель OGRN_Prof_uch\n"
                    if name == 'Poln_Naim_Prof_uch':
                        if znach != 'Общество с ограниченной ответственностью "Альфа-Форекс"':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Poln_Naim_Prof_uch\n"
                    if name == 'SokrNaim_Prof_uch':
                        if znach != 'ООО "Альфа-Форекс"':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель SokrNaim_Prof_uch\n"
                    if name == 'AdresPocht_Prof_uch':
                        if znach != '107078, Москва г, Маши Порываевой улица, дом № 7, строение 1, этаж 1':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель AdresPocht_Prof_uch\n"
                    if name == 'Kod_Okato3':
                        if znach != '45286565000':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Kod_Okato3\n"
                    if name == 'FIOEIO':
                        if znach != 'Николюк Сергей Васильевич' and znach != 'Лафа Виктория Владимировна':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель FIOEIO\n"
                    if name == 'Dolzgnostlizapodpotchetnost':
                        if znach != 'Генеральный директор':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Dolzgnostlizapodpotchetnost\n"
                    if name == 'FIOEIOkontr':
                        if znach != 'Лафа Виктория Владимировна' and znach != 'Козлова Виктория Викторовна':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель FIOEIOkontr\n"
                    if name == 'Osnispobyaz':
                        if not re.fullmatch(r'Решение единственного участника ООО "Альфа-Форекс" от \d{2} сентября \d{4} года', znach):
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Osnispobyaz\n"
                    if name == 'Osnispobyazkontr':
                        if znach != 'Приказ № 8 от 18.09.2018г.':
                            error_list += context_ref + ":\t" + znach + ":\tНекорректный показатель Osnispobyazkontr\n"
        if count_str % shag == 0:
            progress += 1
            sg.one_line_progress_meter('', progress, 100, 'Проверка файла:\n'+XBRL_file ,orientation='h',size = (40,20), no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'),key = 'progresspar')
        if error_list != "":
            ferror_temp.write(error_list)
            count_error += error_list.count("\n")
        error_list = ""
        del line
for context_id in XBRL_417: 
    try:
        if XBRL_417[context_id]["Code"][0:2] != XBRL_417[context_id]["Date"][8:10] or XBRL_417[context_id]["Code"][3:5] != XBRL_417[context_id]["Date"][5:7] or XBRL_417[context_id]["Code"][6:10] != XBRL_417[context_id]["Date"][0:4] or XBRL_417[context_id]["Code"][11] != XBRL_417[context_id]["Napr"]:
            error_list += context_id + ":\tНекорректный уникальный код\n"
    except:
        error_list += context_id + ":\tНекорректный уникальный код\n"
    if error_list != "":
        ferror_temp.write(error_list)
        count_error += error_list.count("\n")
    error_list = ""

check = False

ferror_temp.close()
################################################################################# конец блока проверки ########################################################################

with open(direction+'\\temp_errors_'+XBRL_file.split(".")[0]+'.txt','r',encoding='utf-8') as ferror_temp:
    temp_list = []
    try:
        for line in ferror_temp:
            temp_list.append(line.split(":")[0])
    except:
        pass
    count_error_context = len(set(temp_list))
print('Проверка закончена')
progress = 100
sg.one_line_progress_meter('', progress, 100, 'Проверка файла:\n'+XBRL_file ,orientation='h',size = (40,20), no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'),key = 'progresspar')

info = "Всего сделок:\t"+str(count_deal)
info += "\nновых:\t\t"+str(new_deal)
info += "\nотменных:\t"+str(cancel_deal)
info += "\n\nОшибок:\t"+str(count_error)
info += "\nв "+str(count_error_context)+" контекстах."

if len(code_list) != len(set(code_list)):
    info += "\n\nНЕуникальные коды!!!"
explorer.inform('Результат проверки',info)
result_dir = explorer.direct()+'/'
if result_dir != '/':
    result_dir = os.path.join(result_dir, 'result_XBRL_check')
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    result_dir += '/'
    if os.path.isfile(result_dir+"info_"+XBRL_file.split(".")[0]+".txt"):
        os.remove(result_dir+"info_"+XBRL_file.split(".")[0]+".txt")
    if os.path.isfile(result_dir+"errors_"+XBRL_file.split(".")[0]+".txt"):
        os.remove(result_dir+"errors_"+XBRL_file.split(".")[0]+".txt")
    with open(result_dir+'info_'+XBRL_file.split(".")[0]+'.txt','w',encoding='utf-8') as finfo:
        finfo.write(info)
    if count_error != 0:
        shutil.copyfile(direction+"\\temp_errors_"+XBRL_file.split(".")[0]+".txt", result_dir+"errors_"+XBRL_file.split(".")[0]+".txt")
    '''
    if all_error_list != "":
        with open(result_dir+'errors_'+XBRL_file.split(".")[0]+'.txt','w',encoding='utf-8') as ferror:
            ferror.write(all_error_list)
    '''

shutil.rmtree(direction)

explorer.inform('0420417_check','Выполнено!')
