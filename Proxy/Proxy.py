import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		server.bind((local_host, local_port))
	except:
		print "Failed to listen on %s:%d" % (local_host, local_port)
		sys.exit(0)

	print "[*] Listening on %s:%d" % (local_host, local_port)

	server.listen(5)

	while True:
		client_socket, addr = server.accept()
		print "[*] Received connection from %s:%d" % (addr[0], addr[1])

		#Start a thread to handle proxy request
		proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
		proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
	#connect to target
	remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	remote_socket.connect((remote_host, remote_port))

	if receive_first:
		remote_buffer = receive_from(remote_socket)
		hexdump(remote_buffer)

		remote_buffer = response_handler(remote_buffer)

		if len(remote_buffer):
			print "[<==] Sending %d bytes to local host." % len(remote_buffer)
			client_socket.send(remote_buffer)

	#do normal proxy things
	while True:
		#send our data to target
		local_buffer = receive_from(client_socket)

		if len(local_buffer):
			print "[==>] Sending %d bytes to remote host." % len(local_buffer)
			hexdump(local_buffer)

			local_buffer = request_handler(local_buffer)

			remote_socket.send(local_buffer)
			print "[==>] Sent to remote host."

		remote_buffer = receive_from(remote_socket)

		if len(remote_buffer):
			print "[<==] Sending %d bytes to local host." % len(remote_buffer)
			hexdump(remote_buffer)

			remote_buffer = response_handler(remote_buffer)

			client_socket.send(remote_buffer)
			print "[<==] Send to local host."

		if not len(local_buffer) or not len(remote_buffer):
			client_socket.close()
			remote_socket.close()
			print "[*] Closing connection"
			break

def receive_from(socket):
	buffer = ""
	#We need to set a timer because of the network latency
	socket.settimeout(2)
	try:
		while True:
			data = socket.recv(4096)
			if not data:
				break
			buffer += data
	except:
		pass
	return buffer

#https://gist.github.com/7h3rAm/5603718
def hexdump(src, length=16, sep='.'):
	FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or sep for x in range(256)])
	lines = []
	for c in xrange(0, len(src), length):
		chars = src[c:c+length]
		hex = ' '.join(["%02x" % ord(x) for x in chars])
		if len(hex) > 24:
			hex = "%s %s" % (hex[:24], hex[24:])
		printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or sep) for x in chars])
		lines.append("%08x:  %-*s  |%s|\n" % (c, length*3, hex, printable))
	print ''.join(lines)


def response_handler(buffer):
	#Process data destinated to the localhost if you want
	return buffer

def request_handler(buffer):
 	#Process data destinated to the remotehost if you want
 	return buffer

def main():
	if len(sys.argv[1:]) != 5:
		print "Usage ./Proxy.py localhost localport remotehost remoteport receivefirst"
		print "Example: ./Proxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
		sys.exit(0)

	local_host = sys.argv[1]
	local_port = int(sys.argv[2])
	remote_host = sys.argv[3]
	remote_port = int(sys.argv[4])

	#true -> proxy connect and receive data first before sending to remote host
	receive_first = sys.argv[5]

	if "True" in receive_first:
		receive_first = True
	else:
		receive_first = False

	#Launch Proxy server
	server_loop(local_host, local_port, remote_host, remote_port, receive_first)

main()