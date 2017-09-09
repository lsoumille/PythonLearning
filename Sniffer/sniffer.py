import socket
import os

#Network interface
host = "192.168.1.12"

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

print sniffer.recvfrom(65565)

#Action to put network card in normal mode in windows
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)