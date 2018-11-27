#!/usr/bin/env python

import os
import subprocess
from time import sleep

if os.geteuid() != 0:ser
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
                os.system("wifite -mac -e CS378-UNIFI-WPA --dict /root/Documents/demolist.txt -i %s" %mon_mode)
	else:
                os.system("wifite -mac -i %s " %mon_mode)
        return mon_mode
    except KeyboardInterrupt:
        print ("WiFite setup failed, exiting")


def network_restore(mon_name):
    os.system("airmon-ng stop %s" %mon_name)
    os.system("service network-manager restart")

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
    network_restore(mon_name)

       
    

