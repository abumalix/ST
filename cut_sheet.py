"""
Author: Abdul Kayat - c_akayat@costco.com
Mar 2023

Description:
To prepare cut sheets for a specific site
"""
from Project.akMethods.AllMethods import *
import os, threading, readline
#-- vars --#
MYPATH = os.path.expanduser('~')
username = MYPATH.split("/")[2]
password = getpassword()

#-- get the targeted site --#
if(len(sys.argv) > 1):
    site = int(sys.argv[1])
else:
    site = int(input("Site Number: "))
switches = site_switches(site, username, password)
results = []
[results.append(x[0]) for x in switches if x[0] not in results]

for i, switch in enumerate(results):
    x = threading.Thread(target=ios_itr_int_status, args=(switch, username, password,))
    x.start()
    p = i+1
for i in range(p):
    x.join()