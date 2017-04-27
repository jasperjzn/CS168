import socket
import sys

class BasicClient(object):

    def __init__(self, address, port):
        self.address = address
        self.port = int(port)
        self.socket = socket.socket()

    def connect(self):
    	self.socket.connect((self.address, self.port))

    def send(self, message):
        self.socket.send(message)

args = sys.argv
if len(args) != 3:
    print "Please supply a server address and port."
    sys.exit()
client = BasicClient(args[1], args[2])
client.connect()
while True:
	msg = raw_input()
	client.send(msg)