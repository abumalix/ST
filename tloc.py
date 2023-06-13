"""
Author: Abdul Kayat - c_akayat@costco.com
Mar 2023

Description:
To get TLOC settings for SDWAN sites
"""
import os, sys, readline, urllib3, warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings(action='ignore',module='.*paramiko.*')
from Project.akMethods.AllMethods import *
#-- vars --#
MYPATH = os.path.expanduser('~')
username = MYPATH.split("/")[2]
password = getpassword()

def sdwan_devices(sites, username, password):
    headers = ['bfdSessions', 'bfdSessionsUp', 'device-model', 'host-name', 'system-ip', 'ompPeers', 'reachability', 'state', 'uptime-date', 'uuid', 'validity']
    login_url= 'https://costco-vmanage.viptela.net/j_security_check'
    login_credentials = {'j_username' : username, 'j_password' : password}
    session = requests.session()
    response_login = session.post(url=login_url, data=login_credentials, verify=False)
    get_url = 'https://costco-vmanage.viptela.net/dataservice/device'
    response_get = session.get(url=get_url, verify=False)
    response_get = json.loads((response_get.content))
    # print(json.dumps(response_get, indent=4, sort_keys=True))
    ipList = []
    for site in sites:
        for device in response_get['data']:
            if(assignSite(site)+"edpr01" in device[headers[3]]):
                router_ip = device["system-ip"]
                print(device["host-name"], router_ip)
                ipList.append(router_ip)
            if(assignSite(site)+"edpr02" in device[headers[3]]):
                router_ip = device["system-ip"]
                print(device["host-name"], router_ip)
                ipList.append(router_ip)

    int_table = [["Router", "ifindex", "Interface", "admin-status", "oper-status", "shaping-rate", "downstream", "upstream", "desc", "ip-address"]]
    for ip in ipList:
        try:
            get_url = 'https://costco-vmanage.viptela.net/dataservice/device/interface?deviceId=' + ip
            response_get = session.get(url=get_url, verify=False)
            response_get = json.loads((response_get.content))
            flip = True
            for i in response_get['data']: # iterate interfaces records
                if("edpr01" in i["vdevice-host-name"] and "ge0/5" in i["ifname"]):
                    router = i["vdevice-host-name"]
                    if(flip): #-- vManage has 2 records for each interface, skipping redundant info --#
                        if("ge0/5" == i["ifname"]):
                            try:
                                int_table.append([i["vdevice-host-name"], i["ifindex"], i["ifname"], i["if-admin-status"], i["if-oper-status"], i["shaping-rate"], i["bandwidth-downstream"], i["bandwidth-upstream"], i["desc"], i["ip-address"]])
                            except:
                                print(f"Not able to get ge0/5 info from {router}")    
                        else:
                            int_table.append([i["vdevice-host-name"], i["ifindex"], i["ifname"], i["if-admin-status"], i["if-oper-status"], i["shaping-rate"], "-", "-", i["desc"], i["ip-address"]])
                    flip = not flip
                elif("edpr02" in i["vdevice-host-name"] and "ge0/4" in i["ifname"]):
                    router = i["vdevice-host-name"]
                    if(flip): #-- vManage has 2 records for each interface, skipping redundant info --#
                        try:
                            int_table.append([i["vdevice-host-name"], i["ifindex"], i["ifname"], i["if-admin-status"], i["if-oper-status"], i["shaping-rate"], i["bandwidth-downstream"], i["bandwidth-upstream"], i["desc"], i["ip-address"]])
                        except:
                            print(f"Not able to get ge0/4 info from {router}")    
                    flip = not flip
        except:
            print(f"Not able to get API info from {ip}")
    print(tabulate(int_table,headers="firstrow"))
    return response_get['data']
    
sites0 = [1372,741,41,781,128,1363,69,10,691,328,1124,648,1487,334,9,637,1620,314,4096,1167,1031,766,1121,141,315,120,61,343,485,63,107,4200,1073,1390,664,827,431,640,1614,1038,687,119,4076,325,474,760,441,1441,1415,140,1243,683,4140,4020,4138,1615,243,374]
sites1 = [13,29,64,91,93,103,106,110,111,112,113,116,121,125,127,145,180,181,183,187,188,189,202,204,205,206,213,222,227,230]
sites2 = [233,237,239,240,241,246,249,302,304,305,306,307,312,316,318,320,321,324,326,329,332,333,336,338,339,340,342,345,346,347,348]
sites3 = [351,352,353,354,357,360,361,362,363,366,367,368,370,371,372,373,377,378,380,382,382,387,390,403,407,410,422,424,436,437,440]
sites4 = [447,466,468,473,475,479,480,481,486,487,489,490,491,563,579,580,621,622,623,624,628,632,633,635,636,639,641,642,643,643,646]
sites5 = [647,649,651,652,654,655,657,662,667,668,669,671,675,680,681,684,686,689,692,693,694,729,733,734,738,740,742,745,746,749,761]
sites6 = [764,768,768,771,773,774,779,788,893,943,947,1000,1002,1003,1004,1005,1006,1008,1010,1011,1013,1014,1017,1018,1020,1023,1026]
sites7 = [1039,1040,1042,1049,1050,1060,1061,1062,1067,1070,1074,1078,1079,1080,1081,1083,1084,1085,1086,1087,1088,1091,1093,1097]
sites8 = [1101,1102,1103,1106,1108,1110,1111,1116,1118,1119,1122,1123,1126,1147,1152,1153,1156,1160,1161,1162,1163,1172,1173,1175,1178]
sites9 = [1183,1184,1185,1191,1192,1194,1198,1200,1207,1208,1226,1227,1235,1295,1297,1317,1319,1320,1321,1322,1325,1330,1331,1333]
sites10 = [1334,1342,1344,1353,1360,1361,1364,1372,1379,1384,1388,1389,1420,1422,1442,1443,1444,1448,1450,1485,1486,1492,1577,1581]
sites11 = [4075,4157,1,1197,1199,1201,1202,1205,1206,1209,1211,1212,1214,1215,1216,1221,1222,1228,1229,1232,1236,1238,1244,1262,1266]
sites12 = [1268,1275,1277,1279,1284,1294,1318,1366,2,25,31,38,8,88,1347,1203,1354,175,210,260,267,280,289,725,731,908,910,495,200,60,696]
sites13 = [1195,670,96,1120,1376,1022,330,848,99,95,465,1033,244,1115,245,1237,737,1016,1052,682,319,322,146,453,778,401,118,644,1383]
sites14 = [782,301,484,114,327,379,659,218,21,650,777,117,126,455,1343,743,685,785,747,660,203,1012,67,1029,638,960,190,412,142,488]
sites15 = [133,1009,1363,581,69,1127,1090,519,1186,1069,533]

allSites = [sites0]

#-- get targeted sites --#
if(len(sys.argv) > 1):
    allSites = [[int(i) for i in sys.argv[1].split(",")]]
else:
    option = int(input("1 - Checking one or multiple Sites\n2 - Checking Pre-defined Sites\n:"))
    while(option!=2):
        if(option == 1):
            x = input("Sites (separate by commas): ")
            allSites = [[int(i) for i in x.split(",")]]
            break
        option = int(input("1 - Checking one or multiple Sites\n2 - Checking Pre-defined Sites\n:"))
        
for sites in allSites:
    print(".. Check PingID for approval ..")
    sdwan_devices(sites, username, password)