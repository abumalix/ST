"""
Author: Abdul Kayat - c_akayat@costco.com
Mar 2023

Description:
To ping site devices and get bfd sessions status
"""
from Project.akMethods.AllMethods import *
import os, threading, readline
 #-- vars --#
MYPATH = os.path.expanduser('~')
username = MYPATH.split("/")[2]
password = getpassword()
lock = threading.Lock()

#-- get the targeted site --#
if(len(sys.argv) > 1):
    site = assignSite(int(sys.argv[1]))
else:
    site = assignSite(int(input("Site Number: ")))
devices = [site+"edpr01", site+"edpr02", site+"edps01"]

#-- ping edp devices --#
for device in devices:
    os.system("ping -c 4 " + device)
    print("---------------------------------------------------------")

x = threading.Thread(target=site_check, args=(devices[1], username, password,))
x.start()
x = threading.Thread(target=site_check, args=(devices[0], username, password,))
x.start()
x.join()
x.join()