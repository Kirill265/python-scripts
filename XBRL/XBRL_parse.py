import xml.etree.ElementTree as ET
import re
'''
root = ET.parse('XBRL_1167746614977_ep_nso_purcb_m_10d_reestr_0420417_20210430.xml').getroot()
n=0
for type_tag in root.findall('contextRef'):
    n+=1
    #value = type_tag.get('contextRef')
    print(type_tag)
print(n)
'''

XML_FILE='XBRL_1167746614977_ep_nso_purcb_m_10d_reestr_0420417_20210430.xml'
n=0
try:
    tree = ET.ElementTree(file=XML_FILE)
    root = tree.getroot()
    '''
    for item in root.iterfind('.//'):
        print('Find: %sn' % item.tag)
    '''
    for child_of_root in root.iter():
        n+=1
        #print('Tag: %snKeys: %snItems: %snText: %sn' % (child_of_root.tag, child_of_root.keys(), child_of_root.items(), child_of_root.text))
    print(n)
except:
    pass

