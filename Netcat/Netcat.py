import sys
import socket
import getopt
import threading
import subprocess

#GLOBAL
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print "Netcat Replacement Tool\n"
    print "Usage: Netcat.py -t target -p host"
    print "-l --listen              - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run - execute the given file upon receiving a connection"
    print "-c --command             - initialize a command shell"
    print "-u --upload=destination  - upon receiving connection upload a file and write to [destination]\n\n"
    print "Examples: "
    print "Netcat.py -t 192.168.1.1 -p 8000 -l -c"
    print "Netcat.py -t 192.168.1.1 -p 8000 -l -u=c:\\target.exe"
    print "Netcat.py -t 192.168.1.1 -p 8000 -l -e=\"cat /etc/passwd\""
    print "echo 'ABC' | Netcat.py -t 192.168.1.1 -p 800"
    sys.exit(0)

def main():
    print "WIP"

main()