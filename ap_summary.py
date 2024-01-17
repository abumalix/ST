"""
Author: Abdul Kayat - a.alkhayyat@saudiatechnic.com
Jan 2024

Description:
Find and list all APs for a specific site
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
local_controller = assignSite(site)+"wlcw01"
old_controllers = ["ln01094cwcw01","ln01094cwcw02","ln01094cwcw03","ln01094cwcw04"]
controllers = ["ln01094cwcw05","ln01094cwcw06","ln01094cwcw07","ln01094cwcw08", "ln01094cwcw09", "ln01094cwcw10", "ln01094cdpw01"]

#-- get list of all switches in site --#
switches = site_switches(site, username, password)
results = []
[results.append(x[0]) for x in switches if x[0] not in results]

#-- getting all mac address tables --#
for i, switch in enumerate(results):
    x = threading.Thread(target=ios_mac_add, args=(switch, username, password,))
    x.start()
    p = i+1
for i in range(p):
    x.join()

#-- search depo WLC for site APs --#
if(assignSite(site)[:2] == "dp"):
    wlc_ap_summary(local_controller, username, password, site)
else:
    #-- search old WLC for site APs --#
    for i, cont in enumerate(old_controllers):
        x = threading.Thread(target=wlc_ap_summary_old, args=(cont, username, password, site,))
        x.start()
        p = i+1
    #-- search new WLC for site APs --#
    for cont in controllers:
        x = threading.Thread(target=wlc_ap_summary, args=(cont, username, password, site,))
        x.start()
        p += 1
    for i in range(p):
        x.join()
