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
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *

class Form(QMainWindow):
    def getfile(self):
        return QFileDialog.getOpenFileName(self,"Выберите XBRL файл","")

    def inform(self,information):
        return QMessageBox.information(self, 'Info',information, QMessageBox.No)


app = QApplication(sys.argv)
explorer = Form()

getXBRL = explorer.getfile()[0]
XBRL_file = getXBRL.split("/")[-1]
'''
#XBRL_file = 'xbrl_1167746614947_test_20210430.xml'
#XBRL_file = 'XBRL_1167746614947_test2_0420417_20210430.xml'
#XBRL_file = 'XBRL_1167746614947_ep_nso_purcb_m_q_10d_reestr_0420417_20210331.xml'
XBRL_file = 'XBRL_1167746614947_ep_nso_purcb_m_10d_reestr_0420417_20210531.xml'
#XBRL_file = 'XBRL_1167746614947_ep_nso_purcb_m_10d_reestr_0420417_20200131.xml'
'''
XBRL_417 = {}
period_date = XBRL_file.split("_")[-1].replace(".xml","")
last_date = period_date[0:4]+"-"+period_date[4:6]+"-"+period_date[6:8]
OGRN = XBRL_file.split("_")[1]
#last_date = "2021-04-30"

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
direction = os.path.join(direction, 'temp')
if os.path.exists(direction):
    shutil.rmtree(direction)
os.mkdir(direction)
f_orig = open(getXBRL,'r',encoding='utf-8')
count = 0
temp_list = []
for x in f_orig:
    count +=1
    if count == 1:
        open_tag = x
    if count != 1 and len(x) > 10 and x[:11] == '<xbrli:xbrl':
        open_tag += x
close_tag = x
f_orig.close()
limit = 20000
tail_flag = 0
count_f = (count-1) // limit + 1
if count % limit == 1:
    count_f -= 1
    tail_flag = 1
for i in range(count_f):
    temp_list.append(open(direction+'\\ftemp'+str(i)+'.xml','w',encoding='utf-8'))
    if i != 0:
        temp_list[i].write(open_tag)
current = 0
f_orig = open(getXBRL,'r',encoding='utf-8')
for x in f_orig:
    current += 1
    if current == count and tail_flag == 1:
        temp_list[(current-1) // limit - 1].write(x)
    else:
        temp_list[(current-1) // limit].write(x)
f_orig.close()
for i in range(count_f):
    if i != count_f - 1:
        temp_list[i].write(close_tag)
    temp_list[i].close()

#преобразование в словарь
'''
for i in range(count_f):
    tree = etree.parse(direction+'\\ftemp'+str(i)+'.xml')
    contexts = tree.findall('xbrli:context',namespaces=NSMAP)
    for context in contexts:
        XBRL_417[context.attrib["id"]]={}
        XBRL_417[context.attrib["id"]]["identifier"] = context.find('xbrli:entity/xbrli:identifier[@scheme="http://www.cbr.ru"]',namespaces=NSMAP).text
        XBRL_417[context.attrib["id"]]["period"] = context.find('xbrli:period/xbrli:instant',namespaces=NSMAP).text
        if context.find('xbrli:scenario/xbrldi:explicitMember',namespaces=NSMAP) is not None:
            XBRL_417[context.attrib["id"]]["explict"] = context.find('xbrli:scenario/xbrldi:explicitMember[@dimension="dim-int:OKUDAxis"]',namespaces=NSMAP).text
        if context.find('xbrli:scenario/xbrldi:typedMember',namespaces=NSMAP) is not None:
            #XBRL_417[context.attrib["id"]]["idstroki"] = context.find('xbrli:scenario/xbrldi:typedMember[@dimension="dim-int:ID_strokiTaxis"]/dim_int:ID_strokiTypedname',namespaces=NSMAP).text
            #XBRL_417[context.attrib["id"]]["idsdelki"] = context.find('xbrli:scenario/xbrldi:typedMember[@dimension="dim-int:ID_vnebirg_sdelkiTaxis"]/dim_int:ID_SdelkiTypedName',namespaces=NSMAP).text
            all_typed = context.findall('xbrli:scenario/xbrldi:typedMember/',namespaces=NSMAP)
            for typed in all_typed:
                XBRL_417[context.attrib["id"]][typed.tag.split("}")[1]] = typed.text
    purcb_dic = tree.findall('.//purcb_dic:*',namespaces=NSMAP)
    for purcb in purcb_dic:
        if len(purcb) == 0:
            if purcb.text != None:
                XBRL_417[purcb.attrib["contextRef"]][purcb.tag.split("}")[1]] = purcb.text
            else:
                XBRL_417[purcb.attrib["contextRef"]][purcb.tag.split("}")[1]] = ""
    del tree
    del contexts
    gc.collect()
    del gc.garbage [:]
'''

for i in range(count_f):
    context = etree.iterparse(direction+'\\ftemp'+str(i)+'.xml')
    for event, elem in context:
        if event == "end" and elem.tag == "{"+NSMAP["xbrli"]+"}context":
        #if elem.tag == "{"+NSMAP["xbrli"]+"}context":
            XBRL_417[elem.attrib["id"]]={}
            XBRL_417[elem.attrib["id"]]["identifier"] = elem.find('xbrli:entity/xbrli:identifier[@scheme="http://www.cbr.ru"]',namespaces=NSMAP).text
            XBRL_417[elem.attrib["id"]]["period"] = elem.find('xbrli:period/xbrli:instant',namespaces=NSMAP).text
            if elem.find('xbrli:scenario/xbrldi:explicitMember',namespaces=NSMAP) is not None:
                XBRL_417[elem.attrib["id"]]["explict"] = elem.find('xbrli:scenario/xbrldi:explicitMember[@dimension="dim-int:OKUDAxis"]',namespaces=NSMAP).text
            if elem.find('xbrli:scenario/xbrldi:typedMember',namespaces=NSMAP) is not None:
                #XBRL_417[elem.attrib["id"]]["idstroki"] = elem.find('xbrli:scenario/xbrldi:typedMember[@dimension="dim-int:ID_strokiTaxis"]/dim_int:ID_strokiTypedname',namespaces=NSMAP).text
                #XBRL_417[elem.attrib["id"]]["idsdelki"] = elem.find('xbrli:scenario/xbrldi:typedMember[@dimension="dim-int:ID_vnebirg_sdelkiTaxis"]/dim_int:ID_SdelkiTypedName',namespaces=NSMAP).text
                all_typed = elem.findall('xbrli:scenario/xbrldi:typedMember/',namespaces=NSMAP)
                for typed in all_typed:
                    XBRL_417[elem.attrib["id"]][typed.tag.split("}")[1]] = typed.text
            elem.clear()
        if event == "end" and elem.tag.split("}")[0] == "{"+NSMAP["purcb_dic"]:
            if len(elem) == 0:
                if elem.text != None:
                    XBRL_417[elem.attrib["contextRef"]][elem.tag.split("}")[1]] = elem.text
                else:
                    XBRL_417[elem.attrib["contextRef"]][elem.tag.split("}")[1]] = ""
            elem.clear()
    del context
    print(str(i+1)+'/'+str(count_f)+'\tdone')
        #del elem.getparent()[0]
        #elem.clear()
        #print(elem)
#print(XBRL_417)
    
if os.path.isfile("info.txt"):
    os.remove("info.txt")
if os.path.isfile("error.txt"):
    os.remove("error.txt")

finfo = open('info.txt','w',encoding='utf-8')
ferror = open('error.txt','w',encoding='utf-8')

#подсчет новых и отмененных сделок
count_deal = 0
new_deal = 0
cancel_deal = 0
code_list = []
error_list = ""
if OGRN != '1167746614947':
    error_list += "Некорректный ОГРН в названии файла\n"
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
        '''
        if not re.fullmatch(r'Решение единственного участника ООО "Альфа-Форекс" от \d{2} \w+ \d{4} года', XBRL_417[key].get("Osnispobyaz")):
            error_list += key + ":\t" + str(XBRL_417[key].get("Osnispobyaz")) + ":\tНекорректный показатель Osnispobyaz\n"
        '''
        if XBRL_417[key].get("Osnispobyazkontr") != 'Приказ № 8 от 18.09.2018г.':
            error_list += key + ":\t" + str(XBRL_417[key].get("Osnispobyazkontr")) + ":\tНекорректный показатель Osnispobyazkontr\n"
    ferror.write(error_list)
    error_list = ""
finfo.write("Всего сделок:\t"+str(count_deal)+"\n")
finfo.write("новых:\t\t"+str(new_deal)+"\n")
finfo.write("отменных:\t"+str(cancel_deal))
info = "\nВсего сделок:\t"+str(count_deal)
info += "\nновых:\t\t"+str(new_deal)
info += "\nотменных:\t"+str(cancel_deal)
'''
print("\nВсего сделок:\t"+str(count_deal))
print("новых:\t\t"+str(new_deal))
print("отменных:\t"+str(cancel_deal))
'''
if len(code_list) != len(set(code_list)):
    finfo.write("\n\nНЕуникальные коды!!!")
    info += "\n\nНЕуникальные коды!!!"
    #print("\nНЕуникальные коды!!!")

explorer.inform(info)

finfo.close()
ferror.close()
shutil.rmtree(direction)

#проверка отсутствия других показателей

#проверка уникального кода


#print(root.tag)
#for child in root[2]: print(child.tag)
#print(root.attrib)
#print(root[1].attrib)
#print(root[3].findall('{http://www.xbrl.org/2003/instance}period'))

#entries = tree.findall('{http://www.xbrl.org/2003/instance}context')
#period_element = entries[0].find('{http://www.xbrl.org/2003/instance}period')
#print(period_element)

#all_period = tree.findall('.//{http://www.xbrl.org/2003/instance}period')
#print(all_period)
#all_idstrok = tree.findall('.//{http://www.cbr.ru/xbrl/udr/dim/dim-int}ID_strokiTypedname')
#for idstrok in all_idstrok: print(idstrok.text)

#ref = tree.findall('//{http://www.cbr.ru/xbrl/nso/purcb/dic/purcb-dic}*[@contextRef="DAB-2C4A364A-92C4-4536-81D5-7F26518A5AED"]')
#for i in ref: print(i.tag+'\t'+str(i.text))

#NS = '{http://www.xbrl.org/2003/instance}'
#print(tree.findall('//{NS}context[{NS}scenario]'.format(NS=NS)))

#print(etree.tounicode(tree, pretty_print=True))
