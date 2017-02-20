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
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    #If the script is called without parameters
    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as e:
        print str(e)
        usage()

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    #Receiving data from stdin
    if not listen and len(target) and port > 0:
        #read the the buffer
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))

        while True:
            # send buffer
            if len(buffer):
                client.send("buffer")

            recv_len = 1
            response = ""
            #Process response
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break

            print response
            #fulfill the buffer with the new data from the client
            buffer = raw_input("")
            buffer += "\n"
    except:
        print "[*] Exiting."
        client.close()

def server_loop():
    print "ToDO"
main()