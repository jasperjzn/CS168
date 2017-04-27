# chat_server.py
 
import sys, socket, select
import utils

HOST = '' 
SOCKET_LIST = []
all_users = []
username_dict = {}
chatrooms = ["\r"]
RECV_BUFFER = utils.MESSAGE_LENGTH
PORT = 0

def pad_message(message):
  while len(message) < RECV_BUFFER:
    message += " "
  return message[:RECV_BUFFER]

def depad_message(message):
    i = utils.MESSAGE_LENGTH - 1
    while message[i] == " ":
        message = message[:-1]
        i = i - 1
    return message

def helper(String):
    i = 0
    while String[i] != " ":
        i = i + 1
        if i == len(String):
            return String
    return String[:i]

def chat_server():

    if(len(sys.argv) < 2) :
        print 'Usage : python chat_server.py port'
        sys.exit()
    PORT = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
      
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                 
                # broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room\n" % addr)
             
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        if sock not in all_users:
                            all_users.append(sock)
                            username_dict[sock] = ["default", "lobby", ""]

                        if len(data) + len(username_dict[sock][2]) < RECV_BUFFER:
                            username_dict[sock][2] = username_dict[sock][2] + data
                            continue
                        elif len(data) + len(username_dict[sock][2]) == RECV_BUFFER:
                            data = depad_message(username_dict[sock][2] + data)
                            username_dict[sock][2] = ""
                        else:
                            data = depad_message(username_dict[sock][2] + data)
                            username_dict[sock][2] = username_dict[sock][2][RECV_BUFFER - len(username_dict[sock[2]])] 

                        if username_dict[sock][0] == "default":
                            username_dict[sock][0] = data
                            continue

                        if data[0] == "/" and (helper(data) != "/list") and (helper(data) != "/join") and (helper(data) != "/create"):
                            sock.send(pad_message(utils.SERVER_INVALID_CONTROL_MESSAGE.format(helper(data)) + "\n"))

                        elif data == "/list":
                            for item in chatrooms:
                                sock.send(pad_message(item))

                        elif data[:7] == "/create":
                            if len(data) == 7:
                                sock.send(pad_message(utils.SERVER_CREATE_REQUIRES_ARGUMENT + "\n"))
                            else:
                                newRoom = "\r" + data[8:] + "\n"
                                if newRoom in chatrooms:
                                    sock.send(pad_message(utils.SERVER_CHANNEL_EXISTS.format(data[8:]) + "\n"))
                                else:
                                    chatrooms.append(newRoom)
                                    if username_dict[sock][1] != "lobby":
                                        newBroadcast(server_socket, sock, username_dict[sock][1], utils.SERVER_CLIENT_LEFT_CHANNEL.format(username_dict[sock][0]) + "\n")
                                    username_dict[sock][1] = newRoom

                        elif data[:5] == "/join":
                            if len(data) == 5:
                                sock.send(pad_message(utils.SERVER_JOIN_REQUIRES_ARGUMENT + "\n"))
                            else:
                                specificRoom = "\r" + data[6:] + "\n"
                                if specificRoom not in chatrooms:
                                    sock.send(pad_message(utils.SERVER_NO_CHANNEL_EXISTS.format(specificRoom[1:-1]) + "\n"))
                                else:
                                    if username_dict[sock][1] != "lobby":
                                        newBroadcast(server_socket, sock, username_dict[sock][1], utils.SERVER_CLIENT_LEFT_CHANNEL.format(username_dict[sock][0]) + "\n")
                                    username_dict[sock][1] = specificRoom
                                    newBroadcast(server_socket, sock, specificRoom, utils.SERVER_CLIENT_JOINED_CHANNEL.format(username_dict[sock][0]) + "\n")
                        
                        elif username_dict[sock][1] == "lobby":
                            sock.send(pad_message(utils.SERVER_CLIENT_NOT_IN_CHANNEL + "\n"))
                        else:
                            newBroadcast(server_socket, sock, username_dict[sock][1], "\r" + '[' + username_dict[sock][0] + '] ' + data + "\n")  
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        newBroadcast(server_socket, sock, username_dict[sock][1], utils.SERVER_CLIENT_LEFT_CHANNEL.format(username_dict[sock][0]) + "\n")

                # exception 
                except:
                    if username_dict[sock][1] != "lobby":
                        newBroadcast(server_socket, sock, username_dict[sock][1], utils.SERVER_CLIENT_LEFT_CHANNEL.format(username_dict[sock][0]) + "\n")
                    continue

    server_socket.close()
    

def newBroadcast (server_socket, sock, room, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock and username_dict[socket][1] == room:
            try :
                socket.send(pad_message(message))
                # socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

if __name__ == "__main__":
    sys.exit(chat_server())


