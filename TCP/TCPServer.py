import socket
import threading

bind_ip = "127.0.0.1"
bind_port = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(3) #nb connections max in queue

print "[*] Listening on %s:%d" % (bind_ip,bind_port)

def handle_connection(client_socket):

    request = client_socket.recv(1024)
    print "[*] Received: %s" % request
    client_socket.send("ACK")

    client_socket.close()

while True:

    client, addr = server.accept()

    print "[*] Accepted connection from: %s:%d" % (addr[0], addr[1])

    client_handler = threading.Thread(target=handle_connection,args=(client,))
    client_handler.start()