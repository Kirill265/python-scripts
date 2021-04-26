import os
import shutil
from pykeepass import PyKeePass
def key_pass(sys_title: str):
    direction = os.path.dirname(os.path.abspath(__file__))+'\\'
    DB = direction+'Database.kdbx'
    my_pass = direction+'not_password.txt'
    # load database
    kp = PyKeePass(DB, keyfile=my_pass)
    # find any entry by its title
    entry = kp.find_entries(title=sys_title, first=True)
    # retrieve the associated entries
    return entry

