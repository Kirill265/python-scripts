import os
 
dir_name = "final_3_2"
test = os.listdir(dir_name)
'''
for item in test:
    if item.endswith(".xml"):
        print(item)
'''
for root, dirs, files in os.walk(dir_name):
    for file in files:
        if file.endswith('.xml'):
            #print(os.path.join(root, file))
            with open(os.path.join(root, file),'r',encoding='utf-8') as finfo:
                for line in finfo:
                    if "FORWARD_forvardnyjDogovorMember" in line:
                        print(os.path.join(root, file))
        if file.endswith('.txt'):
            #print(os.path.join(root, file))
            with open(os.path.join(root, file),'r') as finfo:
                for line in finfo:
                    if "FORWARD_forvardnyjDogovorMember" in line:
                        print(os.path.join(root, file))
