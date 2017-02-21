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
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
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

        # send buffer
        if len(buffer):
            client.send(buffer)

        while True:

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
            client.send(buffer)
    except:
        print "[*] Exiting."
        client.close()

def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0" #listen on all interfaces with an IPv4 address

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(3)

    while True:
        client_socket, addr = server.accept()
        #Launch the client in a new thread
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(cmd):
    #Trim
    cmd = cmd.rstrip()
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    #Need to perform an upload
    if len(upload_destination):
        file_buffer = ""
        #Fulfill the buffer with the cleint data
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        #Write the buffer in the file
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    #Need to execute a command
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    #Need to emulate a shell
    if command:
        while True:
            client_socket.send("$> ")
            cmd_buffer = ""
            #get the cmd
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            output = run_command(cmd_buffer)
            client_socket.send(output)
main()