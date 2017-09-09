import socket
import os
from ctypes import *
import struct
#Network interface
host = "192.168.1.12"

class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sul", c_ushort),
        ("src", c_uint),
        ("dst", c_uint)
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)
    def __init__(self, socket_buffer=None):
        #Constant map to retrieve packets protocol
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        #Format IP addresses to be more friendly
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        #Update protocol with the previous map, in case of failed let the default value
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

class ICMP(Structure):
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("nothing", c_ushort),
        ("next_hop_mtu", c_ushort)
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass

#SNIFFER CODE
#Create socket
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    #On linux you must specify the protocol that you want to sniff
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))

#Tell to get IP headers
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

#Action to put network car in promiscuous mode in Windows
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    while True:
        #Read packet (Index 0 is for retrieving only the packet content)
        raw_buffer = sniffer.recvfrom(65565)[0]
        #Get packet header
        ip_header = IP(raw_buffer[0:20])
        #Display data
        print "Protocol : %s | Src : %s -> Dst : %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address)

        if ip_header.protocol == "ICMP":
            #multiplied ihl by 4 to obtain header length
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]
            icmp_header = ICMP(buf)
            print "ICMP -> Type: %d | Code: %d" % (icmp_header.type, icmp_header.code)
except KeyboardInterrupt:
    # Action to put network card in normal mode in windows
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
