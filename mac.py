"""
Author: Abdul Kayat - c_akayat@costco.com
Mar 2023

Description:
To find a mac address on a site
"""
from Project.akMethods.AllMethods import *
import os, threading, sys, readline
#-- vars --#
MYPATH = os.path.expanduser('~')
username = MYPATH.split("/")[2]
password = getpassword()

#-- get the targeted site --#
if(len(sys.argv) > 1):
    site = int(sys.argv[1])
else:
    site = int(input("Site Number: "))

#-- get the targeted MAC address --#
mac = input("MAC Address: ").lower()[-4:]
switches = site_switches(site, username, password)
results = []
[results.append(x[0]) for x in switches if x[0] not in results]

for i, switch in enumerate(results):
    x = threading.Thread(target=find_mac_add, args=(switch, username, password, mac,))
    x.start()
    p = i+1
for i in range(p):
    x.join()