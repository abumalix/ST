# ST
Network Support Automation

Link to this repo: https://gheprod.corp.costco.com/akayat/ST.git

To clone it to your jumpbox, while at your jumpbox home directory:
- cd        (to be in home directory)
- git clone https://gheprod.corp.costco.com/akayat/ST.git
- cd ST
- pip3 install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

To run any script (ping.py for example):
- cd ST
- python3 ping.py

Make sure you allways have the latest updates by:
- cd ST
- git pull origin main

Current working scripts:
- ping.py: To ping switch ports, given the switch name and port
- switches.py: List all existing switches in site
- ap_summary.py: List all APs connected to controllers for a site
- cut_sheet.py: Get the cut sheet for a site
- member_wifi.py: Check if a site is ready for memberwifi deployment and has vlan 666
- site_check.py: Check basics connectivity for a site (ping R1/2 and edps, get bfd sessions, get int status)
- savepass.py: To save your password encrypted and hidden, so you do not need to enter it everytime.
- mac.py: To find a mac address on a site

Facing Issues or need help?
- If running a script generates errors or fails, email me a screenshot to address it. (c_akayat@costco.com)

News:
2022
- October 19: I will be updating all scripts to work with Python3. Check here for updates.
- November 18: Scripts are working on Python3!
2023
- Feb 8: All scripts can take the site number as an argument like: python ping 110.
- Feb 10: Fixed special characters appearing when hitting keyboard arrow keys or bacspace when getting input.
- March 10: All scripts are updated to work with saved password. Check "savepass.py" description.
- March 10: You can use aliases: alias p='python3'   to run scripts like this: p ping.py
