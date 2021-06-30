import sys
import os
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from Checked_cust_report import Check_client

Check_client()
