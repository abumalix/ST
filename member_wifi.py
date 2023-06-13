"""
Author: Abdul Kayat - c_akayat@costco.com
Mar 2023

Description:
To ensure readiness of sites for member wifi rollout
"""
from Project.akMethods.AllMethods import *
import os, threading, sys, readline
#-- vars --#
MYPATH = os.path.expanduser('~')
username = MYPATH.split("/")[2]
password = getpassword()
Testing_Sites = [2,6,13,38,54,55,101,103,152,158,163,205,241,243,254,255,305,321,326,335,337,343,363,364,365,377,383,420,441,466,468,471,480,482,488,503,505,516,521,524,528,529,531,533,535,536,537,542,545,546,547,549,564,578,591,592,651,659,661,740,761,769,801,1007,1009,1014,1020,1021,1049,1058,1069,1110,1186,1225,1248,1265,1274,1342,1359,1367,1372,1436,1447,1448,1619,1620,1621,1629,1900]

#-- get list of targeted sites --#
if(len(sys.argv) > 1):
    Testing_Sites = [int(i) for i in sys.argv[1].split(",")]
else:
    option = int(input("1 - Checking one or multiple Sites\n2 - Checking Pre-defined Sites\n:"))
    while(option!=2):
        if(option == 1):
            x = input("Sites (separate by commas): ")
            Testing_Sites = [int(i) for i in x.split(",")]
            break
        option = int(input("1 - Checking one or multiple Sites\n2 - Checking Pre-defined Sites\n:"))

for site in Testing_Sites:
    #-- get list of all switches in site --#
    switches = site_switches(site, username, password)
    clean_Global_Switches()
    results = []
    try:
        [results.append(x[0]) for x in switches if x[0] not in results]
    except:
        print(f"Error while getting site swithces")
        continue
    #-- only EDP,MEM,REC,FLR switches are to be checked --#
    wifi_switches = []
    for sw in results:
        if("edps" in sw or "mems" in sw or "flrs" in sw or "recs" in sw or "fl1s" in sw):
            wifi_switches.append(sw)
    #-- check for VLAN 666 in switches --#
    for i, switch in enumerate(wifi_switches):
        x = threading.Thread(target=ios_member_wifi, args=(switch, username, password,))
        x.start()
        p = i+1
    #-- check interfaces status in R2 vpn 0 --#
    x = threading.Thread(target=sec_circuit_check, args=(site, username, password,))
    x.start()
    #-- get bfd sessions --#
    x = threading.Thread(target=itr_bfd_sessions, args=(assignSite(site) + "edpr02", username, password,))
    x.start()
    for i in range(p+2):
        x.join()