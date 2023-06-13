"""
Author: Abdul Kayat - c_akayat@costco.com
Mar 2023

Description:
To get a list of all switches on site
"""
from Project.akMethods.AllMethods import *
import os, readline
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
[results.append(x) for x in switches if x not in results]
print(tabulate(results))