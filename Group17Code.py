#!/usr/bin/env python

import os
import subprocess
from time import sleep

#Varaible Hard-Coded Values
number_deauth_packets = 20

if os.geteuid() != 0:
    print("\nThis script requires you to run it with root privileges.\n")
    exit(0)

def run_wifite(mon_name):
    try:
        os.system("airmon-ng check kill")
        os.system("ifconfig %s down" %mon_name)
        os.system("airmon-ng start %s" %mon_name)
        cmd = "ifconfig | grep mon | awk -F ':' '{print $1}' | awk '{print $1}'"
        int_name = str(os.popen(cmd).read()).strip('\n')
        os.system("wifite -mac -i %s" %mon_name)
    except KeyboardInterrupt:
        print ("WiFite setup failed, exiting")




if __name__ == "__main__":
    #Print out wireless interfaces
    os.system("iwconfig")
    print ("Do you have at least 2 wireless interfaces before proceeding?")

    monitor_name = raw_input ("What is the name of your wireless interface that supports monitor mode?")
    ap_name = raw_input("What is the name of your AP wireless interface? ")

    print ("\nStarting WiFite with monitor interface")
    mon_name = run_wifite(monitor_name)

