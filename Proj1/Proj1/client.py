# chat_client.py

import sys, socket, select
import utils


RECV_BUFFER = utils.MESSAGE_LENGTH

def pad_message(message):
  while len(message) < utils.MESSAGE_LENGTH:
    message += " "
  return message[:utils.MESSAGE_LENGTH]

def depad_message(message):
    i = utils.MESSAGE_LENGTH - 1
    while message[i] == " ":
        message = message[:-1]
        i = i - 1
    return message
 
def chat_client():
    Buffer = ""
    if(len(sys.argv) < 4) :
        print 'Usage : python chat_client.py hostname port'
        sys.exit()
    name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print utils.CLIENT_CANNOT_CONNECT.format(host, port)
        sys.exit()

    s.send(pad_message(name))

    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
    sys.stdout.flush()
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:            
            if sock == s:
                # incoming message from remote server, s
                data = sock.recv(RECV_BUFFER)
                # print data
                if not data :
                    print "\n" + utils.CLIENT_SERVER_DISCONNECTED.format(host, port)
                    sys.exit()
                else :
                    # print data
                    if len(data) + len(Buffer) < RECV_BUFFER:
                        Buffer = Buffer + data
                        continue
                    elif len(data) + len(Buffer) == RECV_BUFFER:
                        data = depad_message(Buffer + data)
                        Buffer = ""
                    else:
                        data = depad_message(Buffer + data)
                        Buffer = Buffer[RECV_BUFFER - len(Buffer)] 


                    sys.stdout.write(utils.CLIENT_WIPE_ME + "\r" + data)
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)

                    sys.stdout.flush()     
            
            else :
                # user entered a message
                msg = sys.stdin.readline()
                s.send(pad_message(msg[:-1]))
                sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                sys.stdout.flush() 


if __name__ == "__main__":
    sys.exit(chat_client())
