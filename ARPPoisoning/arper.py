import sys

from scapy.config import conf
from scapy.layers.l2 import Ether, ARP
from scapy.sendrecv import srp

interface = "en0"
target_ip = sys.argv[1]
gateway_ip = "192.168.1.254"
packet_count = "1000"

#Configure Scapy
#Set interface
conf.iface = interface
#Disable Verbose Mode
conf.verb = 0

def get_mac(ip_address):
    #srp sends and receives
    #srp returns packets and associated answer in the first arg
    #srp returns unanswered packets
    response, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address), timeout=2, retry=100)

    for s,r in response:
        return r[Ether].src

    return None # in case of argument IP address is not found

print "Setting up %s" % interface

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print "<!> Failed to get gateway MAC Address"
    sys.exit(0)
else:
    print "Gateway MAC Address is %s" % gateway_mac



