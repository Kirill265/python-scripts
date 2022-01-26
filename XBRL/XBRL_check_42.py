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
    if XBRL_file.split("_")[6] == '10rd':
        repType = XBRL_file.split("_")[5]
    elif XBRL_file.split("_")[7] == '10rd':
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
    context_num = 0
    identifier_num = 0
    instant_num = 0
    ID_NomeraInformSoobshheniyaOSdelkeTypedName_num = 0
    explicitMember_num = 0
    VnebirzhSdelka_num = 0
    TipVnebirzhSdelkiEnumerator_num = 0
    Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki_num = 0
    Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator_num = 0
    Vid_PFIEnumerator_num = 0
    Kod_naprav_sdelkiEnumerator_num = 0
    Vid_Inf_SoobshhEnumerator_num = 0
    PlatezhUsloviyaSdelkiEnumerator_num = 0
    Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki_num = 0
    Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd_num = 0
    Tip_identif_klienta_VnebirzhSdelkaEnumerator_num = 0
    Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd_num = 0
    Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator_num = 0
    Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd_num = 0
    Tip_identif_kontr_VnebirzhSdelkaEnumerator_num = 0
    Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd_num = 0
    Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator_num = 0
    Naim_em_Rek_em_Inf_perv_chast_sdelki_num = 0
    ISIN_Rek_em_num = 0
    Kolvo_fin_instr_Rek_em_num = 0
    Tip_bazovogo_aktivaEnumerator_num = 0
    Bazovyj_aktiv_num = 0
    Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator_num = 0
    Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator_num = 0
    CZena_fin_instrumenta_Rek_em_num = 0
    Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em_num = 0
    Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em_num = 0
    Data_oplaty_fin_instrumenta_Rek_em_num = 0
    Naim_emitenta_Inf_o_vtor_chast_sdelki_num = 0
    LiczoOtvZaPrOblast_num = 0
    DolzhLiczaOtvZaPrOblast_num = 0
    KontInfLiczaOtvZaPrOblast_num = 0
    Priznak_Nulevogo_OtchetaEnumerator_num = 0
    NaimITrazrabotchika_num = 0
    INN_Prof_uch_num = 0
    OGRN_Prof_uch_num = 0
    Poln_Naim_Prof_uch_num = 0
    SokrNaim_Prof_uch_num = 0
    AdresPocht_Prof_uch_num = 0
    Kod_Okato3_num = 0
    FIOEIO_num = 0
    Dolzgnostlizapodpotchetnost_num = 0
    FIOEIOkontr_num = 0
    Osnispobyaz_num = 0
    Osnispobyazkontr_num = 0
    uknown_index = 0
    unequal_index = 0
    for line in f_orig:
        count_str += 1
        if 'ep_nso_purcb_' in line:
            for_check = 'ep_nso_purcb_' + line.split("ep_nso_purcb_")[1].split(".xsd")[0]
            typeTaxonomy = line.split("ep_nso_purcb_")[1].split("_10rd")[0]
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
            context_num += 1
            if 'id="' in line:
                context_id = line.split("id=\"")[1].split("\"")[0]
        if 'xbrli:identifier' in line:
            identifier_num += 1
            for_check = line.split("</xbrli:identifier>")[0].split(">")[-1]
            if for_check != OGRN:
                error_list += context_id + ":\t" + for_check + "\tНекорректный показатель identifier\n"
        if 'xbrli:instant' in line:
            instant_num += 1
            for_check = line.split("</xbrli:instant>")[0].split(">")[-1]
            if for_check != last_date:
                error_list += context_id + ":\t" + for_check + "\tНекорректный показатель period\n"
        if 'dim-int:ID_NomeraInformSoobshheniyaOSdelkeTypedName' in line:
            ID_NomeraInformSoobshheniyaOSdelkeTypedName_num += 1
            count_deal += 1
            XBRL_417[context_id]={}
            for_check = line.split("</dim-int:ID_NomeraInformSoobshheniyaOSdelkeTypedName>")[0].split(">")[-1]
            if not re.fullmatch(r'\d+', for_check):
                error_list += context_id + ":\t" + for_check + ":\tНекорректный показатель ID_NomeraInformSoobshheniyaOSdelkeTypedName\n"
        if 'xbrldi:explicitMember' in line:
            explicitMember_num += 1
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
                        VnebirzhSdelka_num += 1
                        code_list.append(znach)
                        try:
                            XBRL_417[context_ref]["Code"] = znach.split("-")[0]+"-"+znach.split("-")[3]
                        except:
                            XBRL_417[context_ref]["Code"] = ''
                        if not re.fullmatch(r'\d{2}\.\d{2}\.\d{4}-\d{7}-001-[BS]-001', znach):
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'TipVnebirzhSdelkiEnumerator':
                        TipVnebirzhSdelkiEnumerator_num += 1
                        if znach != 'mem-int:OWN_sobstvennayaMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki':
                        Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki_num += 1
                        XBRL_417[context_ref]["Date"] = znach
                        try:
                            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', znach) or znach[0:8] != last_date[0:8]:
                                error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                        except:
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator':
                        Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator_num += 1
                        if znach != 'mem-int:FORWARD_forvardnyjDogovorMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Vid_PFIEnumerator':
                        Vid_PFIEnumerator_num += 1
                        if znach != 'mem-int:ValyutnyjForvardMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Kod_naprav_sdelkiEnumerator':
                        Kod_naprav_sdelkiEnumerator_num += 1
                        try:
                            XBRL_417[context_ref]["Napr"] = znach[8]
                        except:
                            XBRL_417[context_ref]["Napr"] = ''
                        if not re.fullmatch(r'mem-int:[BS]_\w+member', znach):
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Vid_Inf_SoobshhEnumerator':
                        Vid_Inf_SoobshhEnumerator_num += 1
                        if znach != 'mem-int:NEW_zaklyuchenieCdelkiMember' and znach != 'mem-int:CANCEL_OtmenaSdelkiMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                        else:
                            if znach.split("_")[0] == "mem-int:NEW": new_deal += 1
                            if znach.split("_")[0] == "mem-int:CANCEL": cancel_deal += 1
                    elif name == 'PlatezhUsloviyaSdelkiEnumerator':
                        PlatezhUsloviyaSdelkiEnumerator_num += 1
                        if znach != 'mem-int:C_raschetnyjMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki':
                        Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki_num += 1
                        if znach != 'MetaTrader 5':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd':
                        Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd_num += 1
                        if znach != 'ФЛ':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Tip_identif_klienta_VnebirzhSdelkaEnumerator':
                        Tip_identif_klienta_VnebirzhSdelkaEnumerator_num += 1
                        if znach != 'mem-int:UnikalnyjKodKlientaVoVnutrennemUcheteOtchityvayushhejsyaOrganizacziiMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd':
                        Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd_num += 1
                        if not re.fullmatch(r'AF\d{7}', znach):
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"    
                    elif name == 'Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator':
                        Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator_num += 1
                        if znach != 'mem-int:Strana_643RusRossiyaMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd':
                        Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd_num += 1
                        if znach != 'ФЛ':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Tip_identif_kontr_VnebirzhSdelkaEnumerator':
                        Tip_identif_kontr_VnebirzhSdelkaEnumerator_num += 1
                        if znach != 'mem-int:UnikalnyjKodKlientaVoVnutrennemUcheteOtchityvayushhejsyaOrganizacziiMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd':
                        Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd_num += 1
                        if not re.fullmatch(r'AF\d{7}', znach):
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"  
                    elif name == 'Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator':
                        Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator_num += 1
                        if znach != 'mem-int:Strana_643RusRossiyaMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Naim_em_Rek_em_Inf_perv_chast_sdelki':
                        Naim_em_Rek_em_Inf_perv_chast_sdelki_num += 1
                        if znach != "":
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'ISIN_Rek_em':
                        ISIN_Rek_em_num += 1
                        if not re.fullmatch(r'[A-Z]{3}/[A-Z]{3}', znach):
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Kolvo_fin_instr_Rek_em':
                        Kolvo_fin_instr_Rek_em_num += 1
                        if znach == None:
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Tip_bazovogo_aktivaEnumerator':
                        Tip_bazovogo_aktivaEnumerator_num += 1
                        if znach != 'mem-int:V1_valyutyMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Bazovyj_aktiv':
                        Bazovyj_aktiv_num += 1
                        if not re.fullmatch(r'\d{3}/\d{3}', znach):
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator':
                        Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator_num += 1
                        if znach != 'mem-int:NekvalificzirovannyjMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator':
                        Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator_num += 1
                        if not re.fullmatch(r'mem-int:Valyuta_\d{3}\w+Member', znach):
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'CZena_fin_instrumenta_Rek_em':
                        CZena_fin_instrumenta_Rek_em_num += 1
                        if znach == None:
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em':
                        Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em_num += 1
                        if znach == None:
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em':
                        Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em_num += 1
                        try:
                            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', znach) or znach[0:8] != last_date[0:8]:
                                error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                        except:
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Data_oplaty_fin_instrumenta_Rek_em':
                        Data_oplaty_fin_instrumenta_Rek_em_num += 1
                        try:
                            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', znach) or znach[0:8] != last_date[0:8]:
                                error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                        except:
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Naim_emitenta_Inf_o_vtor_chast_sdelki':
                        Naim_emitenta_Inf_o_vtor_chast_sdelki_num += 1
                        if znach != "":
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'LiczoOtvZaPrOblast':
                        LiczoOtvZaPrOblast_num += 1
                        if znach != 'Козлова Виктория Викторовна':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'DolzhLiczaOtvZaPrOblast':
                        DolzhLiczaOtvZaPrOblast_num += 1
                        if znach != 'Отдел внутреннего учета':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'KontInfLiczaOtvZaPrOblast':
                        KontInfLiczaOtvZaPrOblast_num += 1
                        if not re.fullmatch(r'\d{11}', znach):
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Priznak_Nulevogo_OtchetaEnumerator':
                        Priznak_Nulevogo_OtchetaEnumerator_num += 1
                        if znach != 'mem-int:NetMember':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'NaimITrazrabotchika':
                        NaimITrazrabotchika_num += 1
                        if znach != 'ООО "ДИБ СИСТЕМС"':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'INN_Prof_uch':
                        INN_Prof_uch_num += 1
                        if znach != '7708294216':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'OGRN_Prof_uch':
                        OGRN_Prof_uch_num += 1
                        if znach != OGRN:
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Poln_Naim_Prof_uch':
                        Poln_Naim_Prof_uch_num += 1
                        if znach != 'Общество с ограниченной ответственностью "Альфа-Форекс"':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'SokrNaim_Prof_uch':
                        SokrNaim_Prof_uch_num += 1
                        if znach != 'ООО "Альфа-Форекс"':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'AdresPocht_Prof_uch':
                        AdresPocht_Prof_uch_num += 1
                        if znach != '107078, Москва г, Маши Порываевой улица, дом № 7, строение 1, этаж 1':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Kod_Okato3':
                        Kod_Okato3_num += 1
                        if znach != '45286565000':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'FIOEIO':
                        FIOEIO_num += 1
                        if znach != 'Николюк Сергей Васильевич' and znach != 'Лафа Виктория Владимировна':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Dolzgnostlizapodpotchetnost':
                        Dolzgnostlizapodpotchetnost_num += 1
                        if znach != 'Генеральный директор':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'FIOEIOkontr':
                        FIOEIOkontr_num += 1
                        if znach != 'Лафа Виктория Владимировна' and znach != 'Козлова Виктория Викторовна':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Osnispobyaz':
                        Osnispobyaz_num += 1
                        if not re.fullmatch(r'Решение единственного участника ООО "Альфа-Форекс" от \d{1,2} (?:августа|сентября) \d{4} года', znach):
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    elif name == 'Osnispobyazkontr':
                        Osnispobyazkontr_num += 1
                        if znach != 'Приказ № 8 от 18.09.2018г.':
                            error_list += context_ref + ":\tНекорректный показатель " + name + ":\t" + znach + "\n"
                    else:
                        error_list += context_ref + ":\tНеизвестный показатель " + name + ":\t" + znach + "\n"
                        uknown_index += 1
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

if context_num != count_deal + 2:
    error_list += "Количество показателей context != количеству сделок + 2:\t" + str(context_num) +"\n"
if identifier_num != count_deal + 2:
    error_list += "Количество показателей identifier != количеству сделок + 2:\t" + str(identifier_num) +"\n"
if instant_num != count_deal + 2:
    error_list += "Количество показателей instant != количеству сделок + 2:\t" + str(instant_num) +"\n"

if ID_NomeraInformSoobshheniyaOSdelkeTypedName_num != count_deal:
    error_list += "Количество показателей ID_NomeraInformSoobshheniyaOSdelkeTypedName и сделок расходится:\t" + str(ID_NomeraInformSoobshheniyaOSdelkeTypedName_num) +"\n"

if explicitMember_num == 0:
    error_list += "Нет показателя explicitMember\n"
elif explicitMember_num != 1:
    error_list += "Показатель explicitMember встречается более одного раза:\t" + str(explicitMember_num) +"\n"

if VnebirzhSdelka_num != count_deal:
    error_list += "Количество показателей VnebirzhSdelka и сделок расходится:\t" + str(VnebirzhSdelka_num) +"\n"
if TipVnebirzhSdelkiEnumerator_num != count_deal:
    error_list += "Количество показателей TipVnebirzhSdelkiEnumerator и сделок расходится:\t" + str(TipVnebirzhSdelkiEnumerator_num) +"\n"
if Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki_num != count_deal:
    error_list += "Количество показателей Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki и сделок расходится:\t" + str(Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki_num) +"\n"
if Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator_num != count_deal:
    error_list += "Количество показателей Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator и сделок расходится:\t" + str(Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator_num) +"\n"
if Vid_PFIEnumerator_num != count_deal:
    error_list += "Количество показателей Vid_PFIEnumerator и сделок расходится:\t" + str(Vid_PFIEnumerator_num) +"\n"
if Kod_naprav_sdelkiEnumerator_num != count_deal:
    error_list += "Количество показателей Kod_naprav_sdelkiEnumerator и сделок расходится:\t" + str(Kod_naprav_sdelkiEnumerator_num) +"\n"
if Vid_Inf_SoobshhEnumerator_num != count_deal:
    error_list += "Количество показателей Vid_Inf_SoobshhEnumerator и сделок расходится:\t" + str(Vid_Inf_SoobshhEnumerator_num) +"\n"
if PlatezhUsloviyaSdelkiEnumerator_num != count_deal:
    error_list += "Количество показателей PlatezhUsloviyaSdelkiEnumerator и сделок расходится:\t" + str(PlatezhUsloviyaSdelkiEnumerator_num) +"\n"
if Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki_num != count_deal:
    error_list += "Количество показателей Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki и сделок расходится:\t" + str(Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki_num) +"\n"
if Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd_num != count_deal:
    error_list += "Количество показателей Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd и сделок расходится:\t" + str(Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd_num) +"\n"
if Tip_identif_klienta_VnebirzhSdelkaEnumerator_num != count_deal:
    error_list += "Количество показателей Tip_identif_klienta_VnebirzhSdelkaEnumerator и сделок расходится:\t" + str(Tip_identif_klienta_VnebirzhSdelkaEnumerator_num) +"\n"
if Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd_num != count_deal:
    error_list += "Количество показателей Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd и сделок расходится:\t" + str(Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd_num) +"\n"
if Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator_num != count_deal:
    error_list += "Количество показателей Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator и сделок расходится:\t" + str(Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator_num) +"\n"
if Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd_num != count_deal:
    error_list += "Количество показателей Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd и сделок расходится:\t" + str(Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd_num) +"\n"
if Tip_identif_kontr_VnebirzhSdelkaEnumerator_num != count_deal:
    error_list += "Количество показателей Tip_identif_kontr_VnebirzhSdelkaEnumerator и сделок расходится:\t" + str(Tip_identif_kontr_VnebirzhSdelkaEnumerator_num) +"\n"
if Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd_num != count_deal:
    error_list += "Количество показателей Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd и сделок расходится:\t" + str(Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd_num) +"\n"
if Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator_num != count_deal:
    error_list += "Количество показателей Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator и сделок расходится:\t" + str(Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator_num) +"\n"
if Naim_em_Rek_em_Inf_perv_chast_sdelki_num != count_deal:
    error_list += "Количество показателей Naim_em_Rek_em_Inf_perv_chast_sdelki и сделок расходится:\t" + str(Naim_em_Rek_em_Inf_perv_chast_sdelki_num) +"\n"
if ISIN_Rek_em_num != count_deal:
    error_list += "Количество показателей ISIN_Rek_em и сделок расходится:\t" + str(ISIN_Rek_em_num) +"\n"
if Kolvo_fin_instr_Rek_em_num != count_deal:
    error_list += "Количество показателей Kolvo_fin_instr_Rek_em и сделок расходится:\t" + str(Kolvo_fin_instr_Rek_em_num) +"\n"
if Tip_bazovogo_aktivaEnumerator_num != count_deal:
    error_list += "Количество показателей Tip_bazovogo_aktivaEnumerator и сделок расходится:\t" + str(Tip_bazovogo_aktivaEnumerator_num) +"\n"
if Bazovyj_aktiv_num != count_deal:
    error_list += "Количество показателей Bazovyj_aktiv и сделок расходится:\t" + str(Bazovyj_aktiv_num) +"\n"
if Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator_num != count_deal:
    error_list += "Количество показателей Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator и сделок расходится:\t" + str(Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator_num) +"\n"
if Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator_num != count_deal:
    error_list += "Количество показателей Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator и сделок расходится:\t" + str(Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator_num) +"\n"
if CZena_fin_instrumenta_Rek_em_num != count_deal:
    error_list += "Количество показателей CZena_fin_instrumenta_Rek_em и сделок расходится:\t" + str(CZena_fin_instrumenta_Rek_em_num) +"\n"
if Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em_num != count_deal:
    error_list += "Количество показателей Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em и сделок расходится:\t" + str(Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em_num) +"\n"
if Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em_num != count_deal:
    error_list += "Количество показателей Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em и сделок расходится:\t" + str(Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em_num) +"\n"
if Data_oplaty_fin_instrumenta_Rek_em_num != count_deal:
    error_list += "Количество показателей Data_oplaty_fin_instrumenta_Rek_em и сделок расходится:\t" + str(Data_oplaty_fin_instrumenta_Rek_em_num) +"\n"
if Naim_emitenta_Inf_o_vtor_chast_sdelki_num != count_deal:
    error_list += "Количество показателей Naim_emitenta_Inf_o_vtor_chast_sdelki и сделок расходится:\t" + str(Naim_emitenta_Inf_o_vtor_chast_sdelki_num) +"\n"

if LiczoOtvZaPrOblast_num == 0:
    error_list += "Нет показателя LiczoOtvZaPrOblast\n"
elif LiczoOtvZaPrOblast_num != 1:
    error_list += "Показатель LiczoOtvZaPrOblast встречается более одного раза:\t" + str(LiczoOtvZaPrOblast_num) +"\n"
if DolzhLiczaOtvZaPrOblast_num == 0:
    error_list += "Нет показателя DolzhLiczaOtvZaPrOblast\n"
elif DolzhLiczaOtvZaPrOblast_num != 1:
    error_list += "Показатель DolzhLiczaOtvZaPrOblast встречается более одного раза:\t" + str(DolzhLiczaOtvZaPrOblast_num) +"\n"
if KontInfLiczaOtvZaPrOblast_num == 0:
    error_list += "Нет показателя KontInfLiczaOtvZaPrOblast\n"
elif KontInfLiczaOtvZaPrOblast_num != 1:
    error_list += "Показатель KontInfLiczaOtvZaPrOblast встречается более одного раза:\t" + str(KontInfLiczaOtvZaPrOblast_num) +"\n"
if Priznak_Nulevogo_OtchetaEnumerator_num > 1:
    error_list += "Показатель Priznak_Nulevogo_OtchetaEnumerator встречается более одного раза:\t" + str(Priznak_Nulevogo_OtchetaEnumerator_num) +"\n"
if NaimITrazrabotchika_num == 0:
    error_list += "Нет показателя NaimITrazrabotchika\n"
elif NaimITrazrabotchika_num != 1:
    error_list += "Показатель NaimITrazrabotchika встречается более одного раза:\t" + str(NaimITrazrabotchika_num) +"\n"

if INN_Prof_uch_num == 0:
    error_list += "Нет показателя INN_Prof_uch\n"
elif INN_Prof_uch_num != 1:
    error_list += "Показатель INN_Prof_uch встречается более одного раза:\t" + str(INN_Prof_uch_num) +"\n"
if OGRN_Prof_uch_num == 0:
    error_list += "Нет показателя OGRN_Prof_uch\n"
elif OGRN_Prof_uch_num != 1:
    error_list += "Показатель OGRN_Prof_uch встречается более одного раза:\t" + str(OGRN_Prof_uch_num) +"\n"
if Poln_Naim_Prof_uch_num == 0:
    error_list += "Нет показателя Poln_Naim_Prof_uch\n"
elif Poln_Naim_Prof_uch_num != 1:
    error_list += "Показатель Poln_Naim_Prof_uch встречается более одного раза:\t" + str(Poln_Naim_Prof_uch_num) +"\n"
if SokrNaim_Prof_uch_num == 0:
    error_list += "Нет показателя SokrNaim_Prof_uch\n"
elif SokrNaim_Prof_uch_num != 1:
    error_list += "Показатель SokrNaim_Prof_uch встречается более одного раза:\t" + str(SokrNaim_Prof_uch_num) +"\n"
if AdresPocht_Prof_uch_num == 0:
    error_list += "Нет показателя AdresPocht_Prof_uch\n"
elif AdresPocht_Prof_uch_num != 1:
    error_list += "Показатель AdresPocht_Prof_uch встречается более одного раза:\t" + str(AdresPocht_Prof_uch_num) +"\n"
if Kod_Okato3_num == 0:
    error_list += "Нет показателя Kod_Okato3\n"
elif Kod_Okato3_num != 1:
    error_list += "Показатель Kod_Okato3 встречается более одного раза:\t" + str(Kod_Okato3_num) +"\n"
if FIOEIO_num == 0:
    error_list += "Нет показателя FIOEIO\n"
elif FIOEIO_num != 1:
    error_list += "Показатель FIOEIO встречается более одного раза:\t" + str(FIOEIO_num) +"\n"
if Dolzgnostlizapodpotchetnost_num == 0:
    error_list += "Нет показателя Dolzgnostlizapodpotchetnost\n"
elif Dolzgnostlizapodpotchetnost_num != 1:
    error_list += "Показатель Dolzgnostlizapodpotchetnost встречается более одного раза:\t" + str(Dolzgnostlizapodpotchetnost_num) +"\n"
if FIOEIOkontr_num == 0:
    error_list += "Нет показателя FIOEIOkontr\n"
elif FIOEIOkontr_num != 1:
    error_list += "Показатель FIOEIOkontr встречается более одного раза:\t" + str(FIOEIOkontr_num) +"\n"
if Osnispobyaz_num == 0:
    error_list += "Нет показателя Osnispobyaz\n"
elif Osnispobyaz_num != 1:
    error_list += "Показатель Osnispobyaz встречается более одного раза:\t" + str(Osnispobyaz_num) +"\n"
if Osnispobyazkontr_num == 0:
    error_list += "Нет показателя Osnispobyazkontr\n"
elif Osnispobyazkontr_num != 1:
    error_list += "Показатель Osnispobyazkontr встречается более одного раза:\t" + str(Osnispobyazkontr_num) +"\n"
    
if error_list != "":
    unequal_index = error_list.count("\n")
    ferror_temp.write(error_list)
    count_error += unequal_index
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
if uknown_index != 0:
    info += "\n\nНеизвестные показатели!"
if unequal_index != 0:
    info += "\n\nКоличество показателей и сделок расходится!"
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
