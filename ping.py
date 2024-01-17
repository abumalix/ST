"""
Author: Abdul Kayat - a.alkhayyat@saudiatechnic.com
Jan 2024

Description:
To ping devices connected to switches ports

To Do:
- Clear locked ports
"""
from Project.akMethods.AllMethods import *
from tabulate import tabulate
import os, sys, readline
#-- vars --#
MYPATH = os.path.expanduser('~')
username = MYPATH.split("/")[2]
password = getpassword()

Banner = [["Switch", "Type"],["EDP", "edp"], ["Receiving", "rec"], ["Membership", "mem"], ["Floor", "fl1 or flr"], ["Shipping", "shp"], ["Gashut", "ght"], ["Tire Shop", "tir"], ["Liquor", "liq"]]
print(tabulate(Banner,headers="firstrow"))
print("\n---------------------------------------------------------\n")

#-- get the targeted site --#
if(len(sys.argv) > 1):
    site = assignSite(int(sys.argv[1]))
else:
    site = assignSite(int(input("Site Number: ")))

print("\nEnter switch type + Port (e.g. mem 1/0/13) \nEnter \"go\" to start ping")

Ports, IP, IP_Mask = ([] for i in range(3))
entry = str(input("switch type + Port : "))
while(entry != "go"):
    interface = "Gi"+ entry.split()[1]
    switch = site + entry.split()[0] + "s01"
    print(switch,interface)
    Ports.append([switch,interface])
    entry = str(input("switch type + Port : "))
print("\n---------------------------------------------------------\n")

#-- get mac addresses and port info from switches --#
records = []
records_headers = ["Switch", "Port", "MAC", "Rmac", "VLAN", "VLAN Description", "IP Address", "Subnet", "VPN"]
for p in Ports:
    mac_address = ios_mac_add(p[0], username, password)
    for item in Global_Error:
        if(item[1] == p[1]):
            print(switch, item[1], "error-disabled")
    clean_Global_Error()
    temp = ""
    for m in mac_address:
        if(str(m[3]) == p[1]):
            #Switch, Port, MAC, Rmac, VLAN
            records.append([str(m[4]), str(m[3]), str(m[0]), str(StoR_mac(m[0])), int(m[2])])

#-- get ARP info from router1 --#
arp = xr_arp(site+"edpr01-sd", username, password)
arp_headers = ["VPN", "IF NAME", "IP", "MAC", "STATE", "IDLE TIMER", "UPTIME"]
for a in arp:
    for r in records:
        if(len(r)==5):
            r.append("No IP")
            r.append("N/A")
        if(r[3] == a[3]):
            IP.append(a[2])
            r[5] = a[2]     # add IP
            r[6] = a[0]     # add VPN

#-- add vlan description and mask --#
for v in VLANS():
    for r in records:
        if(r[4] == v[1]):
            r.insert(5,v[3])    #-- add vlan description --#
            r.insert(7,v[2])    #-- add subnet mask --#
            r[8] = v[0]         #-- add VPN --#

#-- associate IPs to a subnet mask --#
for r in records:
    if("No IP" not in r[6]):
        IP_Mask.append([r[6],r[7]])

#-- records table --#
records.insert(0,records_headers)
print(tabulate(records,headers="firstrow"))

#-- ping IPs --#
for ip in set(IP):
    for set in IP_Mask:
        if(set[0] == ip):
            mask = set[1]
            os.system("fping -gqc 2 " + ip + "/" + str(mask) + " > /dev/null 2>&1")
            os.system("ping -c 4 " + ip)
            print("---------------------------------------------------------")
            break
