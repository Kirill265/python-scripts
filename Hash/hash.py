import hashlib
import os

direction = os.path.dirname(os.path.abspath(__file__))+'\\'
f5 = open(direction+'hash5.txt', 'w')
f256 = open(direction+'hash256.txt', 'w')

f = open(direction+'original.txt', 'r')

for x in f:
    x = x.replace('\n','')
    if x == '':
        f5.write('\n')
        f256.write('\n')
    else:
        hash_object5 = hashlib.md5(x.encode())
        f5.write(hash_object5.hexdigest()+'\n')
        hash_object256 = hashlib.sha256(x.encode())
        f256.write(hash_object256.hexdigest()+'\n')

f.close()
f5.close()
f256.close()
