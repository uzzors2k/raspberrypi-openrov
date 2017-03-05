#!/usr/bin/python
#
# Receive control packets from the topside machine
# translate them into servo settings, and send over I2C
# to the servo control board
#
# Author : Eirik Taylor
# Date   : 08/12/2015
#

import socket
import signal
import sys
from thread import *

# Capture interrupt signal (Ctrl-C). Close the TCP connection
def handler(signum, frame):
	print 'Closing socket...'
	s.close()
	sys.exit(0)
	
signal.signal(signal.SIGINT, handler)

HOST = ''   
PORT = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

try:
	s.bind((HOST, PORT))
except socket.error , msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

print 'Socket bind complete'

s.listen(2)
print 'Socket now listening'

def clientthread(conn):
	#Sending message to connected client
	conn.send('Welcome to the server. Receving Data...\n')

	#infinite loop so that function do not terminate and thread do not end.
	while True:

		#Receiving from client
		data = conn.recv(1024)
		reply = 'Message Received at the server!\n'
		print data
		if not data:
			break

		conn.sendall(reply)

	conn.close()

#now keep talking with the client
while 1:
	#wait to accept a connection
	conn, addr = s.accept()
	print 'Connected with ' + addr[0] + ':' + str(addr[1])

	#start new thread
	start_new_thread(clientthread ,(conn,))

s.close()
