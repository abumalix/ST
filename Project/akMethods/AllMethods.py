"""
Author: Abdul Kayat - c_akayat@costco.com
Mar 2023

To Do:
- Error handling as logs
- Logging in text
"""
import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')
warnings.filterwarnings(action='ignore',message='Python 3.6 is no longer supported')
from cryptography.fernet import Fernet
from netmiko import ConnectHandler
from tabulate import tabulate
from operator import itemgetter
from getpass import getpass
import os, sys, textfsm, requests, json, threading, math, readline

#-- vars --#
lock = threading.Lock()
MYPATH = os.path.expanduser('~/NOC3')
Global_Records, Global_Switches, Global_MAC, Global_Error = ([] for i in range(4))

def clean_Global_Records():
    global Global_Records
    Global_Records = []

def clean_Global_Switches():
    global Global_Switches
    Global_Switches = []

def clean_Global_MAC():
    global Global_MAC
    Global_MAC = []

def clean_Global_Error():
    global Global_Error
    Global_Error = []

def StoR_mac(mac_address):
    mac = mac_address.split(".")
    rMac = ""
    for i in mac:
        rMac += i[:2] + ":" + i[2:] + ":"
    return rMac[:-1]

def printTitle(title):
    print("- "*10 + title + " -"*10)

def VLANS():
    #VPN, VLAN, Mask, Description
    WH_VLANs_10 = [[10,10,22,"PC's,Printers,HVAC,Time Clocks"],[10,20,26,"ESX-SRVMGT"],[10,21,28,"VLAN 21 ESX Host Management"],[10,22,28,"VLAN 22 ESX OOB Management"],[10,23,28,"VLAN 23 ESX Provisioning"],[10,24,28,"VLAN 24 ESX General Services"],[10,51,25,"Cisco Voice Network"],[10,90,25,"Thin Clients"],[10,100,28,"Vlan 100 Environmental"],[10,120,29,"VLAN 120 Alarm"],[10,140,26,"BreakRoom VLAN"],[10,150,27,"Warehouse Scale VLAN"],[10,160,29,"VLAN 160 CARWASH"],[10,200,26,"AP Management vlan"],[10,202,25,"Trusted User Untrusted Device VLAN 202"],[10,203,25,"Wireless Devices WPA/ASCII"],[10,204,26,"WLAN/WPA Mobile Printer Cart"],[10,209,26,"PRESCAN"],[10,210,27,"CREDIT-SIGNUP"],[10,211,27,"ECOMM-TABLET"],[10,218,25,"Wireless Internet Device"],[10,277,26,"Apple Sales"],[10,360,26,"VENDOR-ACCESS"],[10,428,28,"VLAN 428 Alarm NVR"],[10,877,28,"UPS Management"]]
    WH_VLANs_60 = [[60,60,24,"POS"],[60,65,29,"MIMO"],[60,110,27,"Liquor Pod"],[60,130,26,"VLAN 130 LEGACY-Gas POS"],[60,131,26,"VLAN 131 Gas HUT"],[60,136,25,"VLAN 136 GASPOS Dispensers"],[60,137,28,"VLAN 137 GASPOS site servers"]]
    WH_VLANs_70 = [[70,40,26,"Hearing Aid"],[70,70,26,"PHARMACY VLAN"],[70,71,29,"Pharmacy Provincial Firewall"],[70,268,29,"Rx-Bot"],[70,678,27,"Vlan 678 OPTICAL"]]
    WH_VLANs_300 = [[300,62,28,"cash recycler"],[300,235,29,"cell repeater"],[300,298,29,"Car Wash Vendor"],[300,302,29,"car toys"],[300,303,29,"online photo"],[300,306,29,"ink refill vendor"],[300,309,29,"energyrecommerce"],[300,310,28,"photo-kiosk"],[300,311,29,"CN_HD"],[300,312,28,"photo-printer"],[300,313,29,"PedAlign"],[300,314,28,"costco.com"],[300,315,29,"tms_propane network"],[300,327,29,"TOMRA Recycling"],[300,397,29,"tempalert"],[300,398,29,"ada phones"],[300,399,29,"vendor network"],[300,637,28,"optical dr internet"],[300,1309,28,"energyrecommerce"]]
    WH_VLANs_648 = [[648,648,26,"Infrastructure Management"],[999,666,21,"Member Wifi"]]
    WH_VLANs = WH_VLANs_10 + WH_VLANs_60 + WH_VLANs_70 + WH_VLANs_300 + WH_VLANs_648
    return WH_VLANs

DEPOT = [76,171,175,179,196,210,260,262,267,280,289,572,574,584,725,731,908,910,960,1034,1052,1179,1203,1239,1354,1376,1386,1453,1454,1494,4096,4138]
REGIONAL = [20,30,50,60,200,350,400,495,499,500,700,701,880,696,1067,1608,5400,5500]
#[5500 spain rg]
#[500 has extra router rg0500edpr03 (missing 0) and connected to both 500 and 550 edp switches + rg00500mgts01]
#[350 has extra router rg00350edpr03,rg00350edcs01-03]
CENTER_FILL = [562,581,1145,1240,1241,1347]
DCS = [4015,4016,4020,4040,4060,4075,4076,4120,4140,4157,4176,4200]
CALL_CENTER = [1417,4073]
OPTICAL = [190,566]
def assignSite(sdwan_site):
    if sdwan_site in DEPOT:
        sdwan_site = "dp" + (str(sdwan_site).zfill(5))
    elif sdwan_site in REGIONAL:
        sdwan_site = "rg" + (str(sdwan_site).zfill(5))
    elif sdwan_site in CENTER_FILL:
        sdwan_site = "cf" + (str(sdwan_site).zfill(5))
    elif sdwan_site in DCS:
        sdwan_site = "dc" + (str(sdwan_site).zfill(5))
    elif sdwan_site in CALL_CENTER:
        sdwan_site = "cc" + (str(sdwan_site).zfill(5))
    elif sdwan_site == 4220:
        sdwan_site = "dc04015"
    elif sdwan_site == 792:
        sdwan_site = "dp00076"
    elif sdwan_site == 1204:
        sdwan_site = "dp01203"
    elif sdwan_site == 265:
        sdwan_site = "dp00175"
    elif sdwan_site == 936:
        sdwan_site = "dp00260"
    elif sdwan_site == 268:
        sdwan_site = "dp00267"
    elif sdwan_site == 174:
        sdwan_site = "dp00280"#-sd
    elif sdwan_site == 288:
        sdwan_site = "dp00289"
    elif sdwan_site == 559:
        sdwan_site = "dp00572"
    elif sdwan_site == 1053:
        sdwan_site = "dp01052"
    elif sdwan_site == 1437:
        sdwan_site = "dp01386"
    elif sdwan_site == 1618:
        sdwan_site = "wh01442"
    elif sdwan_site == 570:
        sdwan_site = "cf00562"
    elif sdwan_site == 1032:
        sdwan_site = "cf00562"
    elif sdwan_site == 550:
        sdwan_site = "rg00500"
    elif sdwan_site == 565:
        sdwan_site = "op00190"
    elif sdwan_site == 587:
        sdwan_site = "op00190"
    elif sdwan_site == 588:
        sdwan_site = "op00190"
    elif sdwan_site == 828:
        sdwan_site = "op00190"
    elif sdwan_site == 835:
        sdwan_site = "op00190"
    elif sdwan_site < 10:
        sdwan_site = "wh0000" + str(sdwan_site)
    elif sdwan_site < 100:
        sdwan_site = "wh000" + str(sdwan_site)
    elif sdwan_site < 1000:
        sdwan_site = "wh00" + str(sdwan_site)
    elif sdwan_site < 4000:
        sdwan_site = "wh0" + str(sdwan_site)
    elif sdwan_site < 10000:
        sdwan_site = "dc0" + str(sdwan_site)
    else:
        sys.exit("invalid warehouse number: " + str(sdwan_site))
    return sdwan_site

def getpassword():
    try:
        with open('.env', 'r') as file:
            line = file.readline().split("'")
            encMessage = line[1]
            key = line[3]
            fernet = Fernet(key)
        password = fernet.decrypt(encMessage).decode()
    except:
        password = getpass()
    return password

def connectIOS(ios_device, username, password):
    cisco_ios = {
        'device_type': 'cisco_ios',
        'host': ios_device,
        'username': username,
        'password': password,
        'verbose': False
    }
    try:
        net_connect = ConnectHandler(**cisco_ios)
        return net_connect
    except:
        print(f"Error while connecting to {ios_device}")

def connectXE(xe_device, username, password):
    cisco_xe = {
        'device_type': 'cisco_xe',
        'host': xe_device,
        'username': username,
        'password': password,
    }
    try:
        net_connect = ConnectHandler(**cisco_xe)
        net_connect.send_command("paginate false")
        return net_connect
    except:
        print(f"Error while connecting to {xe_device}")

def connectXR(xr_device, username, password):
    cisco_xr = {
        'device_type': 'cisco_xr',
        'host': xr_device,
        'username': username,
        'password': password,
    }
    try:
        net_connect = ConnectHandler(**cisco_xr)
        net_connect.send_command("paginate false")
        return net_connect
    except:
        print(f"Error while connecting to: {xr_device}")

def connectWLC(wlc_device, username, password):
    cisco_wlc = {
        'device_type': 'cisco_xe',
        'host': wlc_device,
        'username': username,
        'password': password,
        "fast_cli": False,
    }
    try:
        net_connect = ConnectHandler(**cisco_wlc)
        net_connect.send_command("terminal length 0")
        return net_connect
    except:
        print(f"Error while connecting to: {wlc_device}")

def connectWLC_old(wlc_device, username, password):
    cisco_wlc = {
        'device_type': 'cisco_wlc_ssh',
        'host': wlc_device,
        'username': username,
        'password': password,
        "fast_cli": False,
    }
    try:
        net_connect = ConnectHandler(**cisco_wlc)
        return net_connect
    except:
        print(f"Error while connecting to: {wlc_device}")

def cisco_asa_connect(asa_device , username, password):
    cisco_asa = {
        'device_type': 'cisco_asa',
        'host': asa_device,
        'username': username,
        'password': password,
        'secret': password,
        'verbose': False
    }
    try:
        net_connect = ConnectHandler(**cisco_asa)
        return net_connect
    except:
        print(f"Error while connecting to {asa_device}")

def table_it(listOfLists):
    # for python2 only
    table_lengths = []
    for item in listOfLists[0]:
        table_lengths.append(len(item))
    for line in listOfLists:
        for i, item in enumerate(line):
            if(len(item) > table_lengths[i]):
                table_lengths[i] = len(item)
    for line in listOfLists:
        for i, item in enumerate(line):
            if(len(item) < table_lengths[i] and table_lengths[i] > 7):
                tabs = int(math.ceil(table_lengths[i]/7))
                n = int(math.ceil(len(item)/8))
                line[i] += "\t"*(tabs-n)
        print('\t'.join(map(str, line)))

def ios_int_status(switch, net_connect):
    header = ["Port", "Name", "Status", "VLAN", "Duplex", "Speed", "Type", ""]
    try:
        int_status = net_connect.send_command("show interface status")
        int_status_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/IOS/cisco_ios_show_interfaces_status.textfsm"))
        int_status_results = int_status_table.ParseText(int_status)
        return int_status_results
    except:
        print(f"Not able to get interface status from {switch}")

def ios_itr_int_status(switch, username, password):
    header = ["Port", "Name", "Status", "VLAN", "Duplex", "Speed", "Type", ""]
    try:
        net_connect = connectIOS(switch, username, password)
        int_status = net_connect.send_command("show interface status")
        int_status_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/IOS/cisco_ios_show_interfaces_status.textfsm"))
        int_status_results = int_status_table.ParseText(int_status)
    except:
        print(f"Not able to get interface status from {switch}")
        return
    lock.acquire()
    printTitle(switch)
    if(len(int_status_results) != 0):
        int_status_results.insert(0,header)
        print(tabulate(int_status_results,headers="firstrow"))
    lock.release()
    return int_status_results

def check_AP_vlan666(net_connect, switch, port):
    run_port = net_connect.send_command("show running interface " + port)
    lines = run_port.splitlines()
    v = True
    for line in lines:
        if("666" in line):
            v = False
            break
            if(v):
                print(f"{switch} {port} Needs vlan 666")
                
def ios_member_wifi(switch, username, password):
    header = ["Port", "Name", "Status", "VLAN", "Duplex", "Speed", "Type", ""]
    try:
        net_connect = connectIOS(switch, username, password)
        vlans = ios_vlan(switch, net_connect)
        v = True
        for vlan in vlans:
            if("666" in str(vlan[0])):
                v = False
        if (v):
            print(f"{switch} No vlan 666")
        if(not v):
            int_status = net_connect.send_command("show interface status")
            int_status_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/IOS/cisco_ios_show_interfaces_status.textfsm"))
            int_status_results = int_status_table.ParseText(int_status)
            AP_Ports =[]
            for port in int_status_results:
                if("AP" in str(port[1])):
                    AP_Ports.append(str(port[0]))
            for port in AP_Ports:
                run_port = net_connect.send_command("show running interface " + port)
                lines = run_port.splitlines()
                v = True
                for line in lines:
                    if("666" in line):
                        v = False
                        break
                if(v):
                    print(f"{switch} {port} Needs vlan 666")
    except:
        print(f"Not able to check member wifi vlan on {switch}")

def ios_mac_add(switch, username, password):
    #[Mac Address, Type, VLAN, Port, Switch]
    global Global_MAC, Global_Error
    try:
        net_connect = connectIOS(switch, username, password)
        mac_address = net_connect.send_command("show mac address")
        mac_address_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/IOS/cisco_ios_show_mac-address-table.textfsm"))
        mac_address_results = mac_address_table.ParseText(mac_address)
        switch = net_connect.find_prompt()[:-1]
        for mac in mac_address_results:
            mac.append(switch)
        Global_MAC.append(mac_address_results)
        error_ports = net_connect.send_command("show int status | i err-dis")
        for i in error_ports.split():
            if("Gi" in i):
                Global_Error.append([switch,i])
        return mac_address_results
    except:
        print(f"Not able to get mac addresses from {switch}")

def find_mac_add(switch, username, password, mac_address):
    header = ["VLAN", "Mac Address", "Type", "Port", "Switch"]
    global Global_MAC
    try:
        net_connect = connectIOS(switch, username, password)
        mac_found = net_connect.send_command("show mac address | include " + mac_address).split()
        mac_found.append(switch)
        Port = mac_found[3]
        results = [header,mac_found]
        #-- ignoring uplinks ports --#
        if("Po" not in Port and "1" not in Port.split("/")[1]):
            print(tabulate(results,headers="firstrow"))
        return mac_found
    except:
        print(f"{mac_address} is not in {switch}")

class xe_interface:
    def __init__(self, interface, vpn, ip, admin_status, operation_status, description):
        self.interface = interface
        self.vpn = vpn
        self.ip = ip
        self.admin_status = admin_status
        self.operation_status = operation_status
        self.description = description
    
    def reset(self):
        self.interface = ""
        self.vpn = ""
        self.ip = ""
        self.admin_status = ""
        self.operation_status = ""
        self.description = ""

    def __str__(self):
        return "vpn {} {} {} admin {} {} {}".format(self.vpn, self.interface, self.ip, self.admin_status, self.operation_status, self.description)
        # return f"vpn {self.vpn} {self.interface} {self.ip} admin {self.admin_status} {self.operation_status} {self.description}"

def sdwan_int_desc(router, username, password):
    #[VPN, INTERFACE, TYPE, IP ADDRESS, STATUS, STATUS, STATUS, DESC]
    try:
        net_connect = connectXR(router, username, password)
        int_desc = net_connect.send_command("show interface description")
    except:
        print(f"Not able to get interface description from {router}")
        return
    if("-sd" in net_connect.find_prompt()[:-1]):
        new_obj = False
        new = True
        interfaceObj = xe_interface("","","No IP","","","")
        interface_list = []
        for line in int_desc.splitlines():
            if("interface vpn " in line):
                if(not new):
                    interface_list.append(interfaceObj)
                    del interfaceObj
                    interfaceObj = xe_interface("","","No IP","","","")
                new = False
                interfaceObj.vpn = line.split()[2]
                interfaceObj.interface = line.split()[4]
                new_obj = True
                new = False
            elif("ip-address" in line):
                interfaceObj.ip = line.split()[1]
            elif("if-admin-status" in line):
                interfaceObj.admin_status = line.split()[1]
            elif("if-oper-status" in line):
                interfaceObj.operation_status = line.split()[1]
            elif("desc" in line):
                interfaceObj.description = line.split("desc              ")[1]
        interface_list.append(interfaceObj)
        lock.acquire()
        printTitle(router)
        for int in interface_list:
            print(int)
        lock.release()
    else:
        lock.acquire()
        printTitle(router)
        print(int_desc)
        lock.release()
        return int_desc

def xr_int_desc(router, username, password):
    #[VPN, INTERFACE, TYPE, IP ADDRESS, STATUS, STATUS, STATUS, DESC]
    net_connect = connectXR(router, username, password)
    try:
        int_desc = net_connect.send_command("show interface description | tab")
    except:
        print(f"Not able to get interface description from {router}")
        return
    lock.acquire()
    print(int_desc)
    lock.release()
    return int_desc

def xr_vpn0_interfaces(xr_router, username, password):
    try:
        net_connect = connectXR(xr_router, username, password)
        int_description = net_connect.send_command("show interface vpn 0 | tab")
    except:
        print(f"Not able to check vpn 0 interfaces on {xr_router}")
        return
    lock.acquire()
    printTitle(xr_router)
    print(int_description)
    print("---------------------------------------------------------")
    lock.release()

def xr_arp(router, username, password):
    headers = ["VPN", "IF NAME", "IP", "MAC", "STATE", "IDLE TIMER", "UPTIME"]
    net_connect = connectXR(router, username, password)
    # net_connect = connectXR(router, username, password)
    arp = net_connect.send_command("show arp | tab")
    # arp_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/XR/cisco_xr_show_arp3.textfsm"))
    # arp_results = arp_table.ParseText(arp)
    arp_table = (line.split() for line in arp.splitlines() if len(line.split()) == 7)
    return arp_table

def ios_vlan(switch, net_connect):
    #[VLAN ID, VLAN Name, Status, Ports]
    try:
        sh_vlan = net_connect.send_command("show vlan")
        sh_vlan_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/IOS/cisco_ios_show_vlan.textfsm"))
        sh_vlan_results = sh_vlan_table.ParseText(sh_vlan)
        return sh_vlan_results
    except:
        print(f"Not able to get vlans from {switch}")

def ios_cdp(switch, username, password):
    global Global_Switches
    try:
        neighbors = []
        net_connect = connectIOS(switch, username, password)
        cdp = net_connect.send_command("show cdp neighbors")
        cdp_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/IOS/cisco_ios_show_cdp_neighbors.textfsm"))
        cdp_results = cdp_table.ParseText(cdp)
        for c in cdp_results:
            if((switch[:7] in c[0] and c[0].split(".")[0][10] == "s")):
                neighbors.append(c[0].split(".")[0])
                Global_Switches.append(c[0].split(".")[0])
        return set(neighbors)
    except:
        print(f"Not able to get cdp neighbors from {switch}")

def ios_cdp_details(switch, username, password):
    #[switch,IP]
    global Global_Switches
    try:
        neighbors = []
        net_connect = connectIOS(switch, username, password)
        cdp = net_connect.send_command("show cdp neighbors detail")
        cdp_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/IOS/cisco_ios_show_cdp_neighbors_detail.textfsm"))
        cdp_results = cdp_table.ParseText(cdp)
        for c in cdp_results:
            if((switch[:7] in c[0] and c[0].split(".")[0][10] == "s")):
                neighbors.append([str(c[0].split(".")[0]), str(c[1])])
                Global_Switches.append([c[0].split(".")[0], str(c[1])])
        results = []
        [results.append(x) for x in neighbors if x not in results]
        edp_ip = net_connect.send_command("sh ip int br | ex unass|IP")
        edp_ip = edp_ip.split()[1]
        results.append([switch,edp_ip])
        return results
    except:
        print(f"Not able to get cdp neighbors from {switch}")

def site_switches(site, username, password):
    global Global_Switches
    site = assignSite(site)
    edp_switch = site + "edps01"
    neighbors = ios_cdp_details(edp_switch, username, password)
    switches = []
    try:
        [switches.append(x[0]) for x in neighbors if x not in switches]
        for i, switch in enumerate(switches):
            x = threading.Thread(target=ios_cdp_details, args=(switch, username, password,))
            x.start()
            p = i+1
        for i in range(p):
            x.join()
        return Global_Switches
    except:
        print(f"Not able to get site switches from {edp_switch}")

def wlc_ap_summary(controller, username, password, site):
    #-- vars --#
    header = ["AP Name", "Ethernet MAC", "Country", "IP Address", "State", "Switch", "Port", "WLC"]
    global Global_MAC
    site = assignSite(site)
    #-- get list of APs from WLC --#
    try:
        net_connect = connectWLC(controller, username, password)
        ap_summary = net_connect.send_command("show ap summary | i "+site[2:])
        ap_summary_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/WLC/cisco_wlc_ssh_show_ap_summary2.textfsm"))
        ap_summary_results = ap_summary_table.ParseText(ap_summary)
        wlc = net_connect.find_prompt()[:-1]
        #-- sort by AP number --#
        ap_summary_results = sorted(ap_summary_results, key=lambda x: itemgetter(1,2)(x[0][10:]))
        if(ap_summary_results):
            mac = []
            #-- keep macs from VLAN 200 only --#
            for record in Global_MAC:
                for r in record:
                    if("200" in r[2] and "/0/" in r[3]):
                        mac.append(r)
            #-- remove unnecesary info from each AP record --#
            for a in ap_summary_results:
                a.pop(1)
                a.pop(1)
                a.pop(2)
                a.pop(2)
                #-- append switch and interface to AP record --#
                for macset in mac:
                    if(a[1] == macset[0]):
                        a.append(macset[4])
                        a.append(macset[3])
                #-- append WLC to AP record --#
                a.append(str(wlc))
            ap_summary_results.insert(0,header)
            print(tabulate(ap_summary_results,headers="firstrow"))
            print(f"AP count on {str(wlc)} : {str(len(ap_summary_results)-1)}")
        a = False
        return ap_summary_results
    except:
        print(f"Not able to get AP summary from {controller}")

def wlc_ap_summary_old(controller, username, password, site):
    # header = ["AP Name", "Slots", "AP Model", "Ethernet MAC", "Location", "Country", "IP Address", "Clients", "DSE Location", "WLC"]
    header = ["AP Name", "Ethernet MAC", "Country" , "IP Address", "Switch", "Port", "WLC"]
    global Global_MAC
    site = assignSite(site)
    try:
        net_connect = connectWLC_old(controller, username, password)
        ap_summary = net_connect.send_command("show ap summary "+site[2:])
        ap_summary_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/WLC/cisco_wlc_ssh_show_ap_summary.textfsm"))
        ap_summary_results = ap_summary_table.ParseText(ap_summary)
        ap_summary_results.sort()
        systemINFO = net_connect.send_command("show sysinfo")
        systemINFO_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/WLC/cisco_wlc_ssh_show_sysinfo.textfsm"))
        systemINFO_results = systemINFO_table.ParseText(systemINFO)
        wlc = systemINFO_results[0][5]
        if(ap_summary_results):
            mac = []
            for record in Global_MAC:
                for r in record:
                    if("200" in r[2] and "/0/" in r[3]):
                        mac.append(r)
            for a in ap_summary_results:
                a.pop(1)
                a.pop(1)
                a.pop(2)
                a.pop(4)
                a.pop(4)
                for macset in mac:
                        if(a[1] == StoR_mac(macset[0])):
                            a.append(macset[4])
                            a.append(macset[3])
                a.append(str(wlc))
            ap_summary_results.insert(0,header)
            print(tabulate(ap_summary_results,headers="firstrow"))
            print(f"AP count on {str(wlc)} : {str(len(ap_summary_results)-1)}")
        return ap_summary_results
    except:
        print(f"Not able to get AP summary from {controller}")

def ATT_VLAN_Check(site, vlan, username, password):
    device = assignSite(site) + "edpr01-sd"
    try:
        net_connect = connectXR(device, username, password)
    except:
        try:
            device = assignSite(site) + "edpr01"
            net_connect = connectXR(device, username, password)
        except:
            print(f"Error while connecting to: {device} on connectXR()")
    int_description = net_connect.send_command("show interface description | i ge0/5").splitlines()
    int_description2 = net_connect.send_command("show interface description | i ge0/1").splitlines()
    #-- Removes empty item at the beginning --#
    if (not str(int_description[0])):
        int_description.pop(0)
    if (not str(int_description2[0])):
        int_description2.pop(0)
    try:
        #-- Get the vlan from output for int ge0/5 --#
        interface_vlan = int(str(int_description[1]).split()[1].split(".")[1])
        if(interface_vlan != vlan):
            print(f"Site {site}\t VLAN {interface_vlan}\t Incorrect\t ATT sheet has {vlan}")
    except:
        try:
            #-- Get the vlan from output for int ge0/1 --#
            interface_vlan = int(str(int_description2[1]).split()[1].split(".")[1])
            if(interface_vlan != vlan):
                print(f"Site {site}\t VLAN {interface_vlan}\t Incorrect\t ATT sheet has {vlan}")
        except:
            print(f"Error for site {site}")

def sec_circuit_check(site, username, password):
    device = assignSite(site) + "edpr02"
    try:
        net_connect = connectXR(device, username, password)
        int_description = net_connect.send_command("show interface vpn 0 | tab")
    except:
        print(f"Not able to check secondary circuit on {device}")
        return
    lock.acquire()
    printTitle(device)
    print(int_description)
    print("---------------------------------------------------------")
    lock.release()

def site_check(xr_device, username, password):
    try:
        net_connect = connectXR(xr_device, username, password)
        bfd_sessions = net_connect.send_command("show bfd sessions")
        uptime = net_connect.send_command("show uptime")
        int_desc = net_connect.send_command("show interface description vpn 0 | tab")
    except:
        print(f"Not able to get bfd sessions from {xr_device}")
        return
    lock.acquire()
    printTitle(xr_device)
    print(int_desc)
    print(bfd_sessions)
    print(uptime)
    print("---------------------------------------------------------")
    lock.release()

def itr_bfd_sessions(xr_device, username, password):
    try:
        net_connect = connectXR(xr_device, username, password)
        bfd_sessions = net_connect.send_command("show bfd sessions")
    except:
        print(f"Not able to get bfd sessions from {xr_device}")
        return
    lock.acquire()
    printTitle(xr_device)
    print(bfd_sessions)
    print("---------------------------------------------------------")
    lock.release()

def xr_bfd_sessions(xr_device, username, password):
    net_connect = connectXR(xr_device, username, password)
    # header = ["SYSTEM IP", "SITE ID", "SOURCE TLOC COLOR", "REMOTE TLOC COLOR", "SOURCE IP", "DST PUBLIC IP", "DST PUBLIC PORT", "ENCAP", "DETECT MULTIPLIER", "TX INTERVAL(msec)", "UPTIME", "TRANSITIONS"]
    try:
        bfd_sessions = net_connect.send_command("show bfd sessions")
        bfd_sessions_table = textfsm.TextFSM(open(MYPATH + "/Project/akMethods/textfsm_Templates/XR/cisco_xr_show_bfd_sessions.textfsm"))
        bfd_sessions_results = bfd_sessions_table.ParseText(bfd_sessions)
        return bfd_sessions_results
    except:
        print(f"Not able to get bfd sessions from {xr_device}")

def sdwan_devices(username, password):
    headers = ['bfdSessions', 'bfdSessionsUp', 'device-model', 'host-name', 'system-ip', 'ompPeers', 'reachability', 'state', 'uptime-date', 'uuid', 'validity']
    login_url= 'https://costco-vmanage.viptela.net/j_security_check'
    login_credentials = {'j_username' : username, 'j_password' : password}
    session = requests.session()
    response_login = session.post(url=login_url, data=login_credentials, verify=False)
    get_url = 'https://costco-vmanage.viptela.net/dataservice/device'
    response_get = session.get(url=get_url, verify=False)
    response_get = json.loads((response_get.content))
    # print(json.dumps(response_get, indent=4, sort_keys=True))
    return response_get['data']

def sdwan_call(sdwan_site, username, password):
    headers = ['bfdSessions', 'bfdSessionsUp', 'device-model', 'host-name', 'system-ip', 'ompPeers', 'reachability', 'state', 'uptime-date', 'uuid', 'validity']
    sdwan_site = assignSite(sdwan_site)
    login_url= 'https://costco-vmanage.viptela.net/j_security_check'
    login_credentials = {'j_username' : username, 'j_password' : password}
    session = requests.session()
    response_login = session.post(url=login_url, data=login_credentials, verify=False)
    get_url = 'https://costco-vmanage.viptela.net/dataservice/device'
    response_get = session.get(url=get_url, verify=False)
    response_get = json.loads((response_get.content))
    # print(json.dumps(response_get, indent=4, sort_keys=True))
    sdwan_list = []
    for device in response_get['data']:
        if(sdwan_site in device[headers[3]]):
            sdwan_list.append(device)
    return sdwan_list

def sdwan_bfdSummary(sdwan_site, IP, username, password):
    headers = ['bfd-sessions-flap', 'bfd-sessions-max', 'bfd-sessions-total', 'bfd-sessions-up', 'lastupdated', 'vdevice-host-name', 'vdevice-name']
    sdwan_site = assignSite(sdwan_site)
    login_url= 'https://costco-vmanage.viptela.net/j_security_check'
    login_credentials = {'j_username' : username, 'j_password' : password}
    session = requests.session()
    response_login = session.post(url=login_url, data=login_credentials, verify=False)
    get_url = 'https://costco-vmanage.viptela.net/dataservice/device/bfd/summary?deviceId=' +  IP
    response_get = session.get(url=get_url, verify=False)
    response_get = json.loads((response_get.content))
    # print(json.dumps(response_get, indent=4, sort_keys=True))
    return response_get['data']

def sdwan_bfdSessions(sdwan_site, IP, username, password):
    headers = ['system-ip', 'color', 'dst-ip', 'local-color', 'src-ip', 'state', 'uptime', 'vdevice-host-name', 'vdevice-name', 'transitions']
    sdwan_site = assignSite(sdwan_site)
    login_url= 'https://costco-vmanage.viptela.net/j_security_check'
    login_credentials = {'j_username' : username, 'j_password' : password}
    session = requests.session()
    response_login = session.post(url=login_url, data=login_credentials, verify=False)
    get_url = 'https://costco-vmanage.viptela.net/dataservice/device/bfd/sessions?deviceId=' +  IP
    response_get = session.get(url=get_url, verify=False)
    response_get = json.loads((response_get.content))
    # print(json.dumps(response_get, indent=4, sort_keys=True))
    return response_get['data']

def sdwan_interface(sdwan_site, IP, username, password):
    headers = ['vdevice-host-name', 'vdevice-name', 'vpn-id', 'ifname', 'ip-address', 'if-admin-status', 'if-oper-status', 'desc']
    sdwan_site = assignSite(sdwan_site)
    login_url= 'https://costco-vmanage.viptela.net/j_security_check'
    login_credentials = {'j_username' : username, 'j_password' : password}
    session = requests.session()
    response_login = session.post(url=login_url, data=login_credentials, verify=False)
    get_url = 'https://costco-vmanage.viptela.net/dataservice/device/interface?deviceId=' + IP
    response_get = session.get(url=get_url, verify=False)
    response_get = json.loads((response_get.content))
    # print(json.dumps(response_get, indent=4, sort_keys=True))
    return response_get['data']

def sdwan_ipRoute(sdwan_site, IP, username, password):
    headers = ['system-ip', 'color', 'dst-ip', 'local-color', 'src-ip', 'state', 'uptime', 'vdevice-host-name', 'vdevice-name', 'transitions']
    sdwan_site = assignSite(sdwan_site)
    login_url= 'https://costco-vmanage.viptela.net/j_security_check'
    login_credentials = {'j_username' : username, 'j_password' : password}
    session = requests.session()
    response_login = session.post(url=login_url, data=login_credentials, verify=False)
    get_url = 'https://costco-vmanage.viptela.net/dataservice/device/ip/fib?deviceId=' +  IP
    response_get = session.get(url=get_url, verify=False)
    response_get = json.loads((response_get.content))
    # print(json.dumps(response_get, indent=4, sort_keys=True))
    return response_get['data']

# devices = json.loads(response.content)
# for i in range(0, len(devices["data"])):
#     if "vedge" in devices["data"][i]["device-type"]:
#     print("Backing up config for device " + devices["data"][i]["host-name"])
#     deviceUUId = devices["data"][i]["uuid"]
#     url = 'https://costco-vmanage.viptela.net/dataservice/template/config/running/' + deviceUUID
#     response = sess.get(url=url, verify=False)
#     if response.status_code != 200:
#         print ('Get Device Running Config Failed. Code: ' + str(response.status_code))
#         sys.exit(0)
#     config = json.loads(response.content)
#     with open ('./config/' + devices["data"][i]["host-name"] + '.txt', 'w') as f:
#         f.write(config["config"])

'''

device
system/device/controllers
system/device/vedges
device/arp?deviceId=10.81.159.254
device/interface?deviceId=10.81.159.254
device/interface/stats?deviceId=10.81.159.254
https://costco-vmanage.viptela.net/dataservice/
device/omp/peers?deviceId=10.81.159.254
device/omp/routes/advertised?deviceId=10.81.159.254
device/omp/routes/received?deviceId=10.81.159.254
device/omp/tlocs/received?deviceId=10.81.159.254
device/omp/tlocs/advertised?deviceId=10.81.159.254
device/app-route/sla-class?deviceId=10.81.159.254
device/app-route/statistics?deviceId=10.81.159.254
device/software?deviceId=10.81.159.254
device/control/localproperties?deviceId=10.81.159.254

'''
