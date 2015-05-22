#!/usr/bin/env python3
#Simple TCP client and server that send and receive 16 octets

import argparse, socket, select, getpass, sys
import threading, string

CONNECTION_LIST = []
ACCOUNT = dict({"A":"A", "B":"B", "C":"C"})
ONLINE = []
OFFLINEMSG = dict({"A":"", "B":"", "C":""})
ARY = dict({})

def recvall(sock, length):
    data = sock.recv(4096)
    return data
"""
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (length, len(data)))
        data += more
"""  
def broadcast_data (sock, message, server_socket):
    #Do not send the message to master socket and the client who has send us the message
    for user in OFFLINEMSG.keys():
        message = '[broadcast] ' + message
        OFFLINEMSG[user] += "\n[" + user + "] " + message
    """
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                message = '[broadcast] ' + message
                socket.send(message.encode(encoding='UTF-8'))
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)
                for user in ARY.keys():
                    if ARY[user] == socks:
                        ARY[user] = ''
                        ONLINE.remove(user)
                        broadcast_data(socks, user + " is offline", sock)
                        print (user + " is offline")
                        break"""
def getNameBySock (sock):
    for user in ARY.keys():
        if ARY[user] == sock:
            return user


def server(interface, port):
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listening socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allowing to reuse address
    sock.bind((interface, port))
    sock.listen(1) #turning the socket into a passively listening socket,1:# of waiting conn.allowed
    CONNECTION_LIST.append(sock)
    ARY['server'] = sock
    print('Listening at', sock.getsockname())

    while True:
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
        for socks in read_sockets:
            #New connection
            if socks == sock:
                # Handle the case in which there is a new connection recieved through server_socket
                sc, sockname = sock.accept()
                CONNECTION_LIST.append(sc)
                print("Client (%s, %s) connected" % sockname)                 
                print('We have accepted a connection from', sockname)
                print(' Socket name:', sc.getsockname())
                print(' Socket peer:', sc.getpeername())
             
            #Some incoming message from a client
            else:
                try:
                    data = recvall(socks, 16)
                    data = data.decode('utf-8')
                    if data[0:4] == 'I am':                        
                        if ONLINE.count(data[5:])>0: #data[5:] in ARY: #
                            socks.sendall(b'Duplicate login')
                        else:
                            user = data[5:]
                            ONLINE.append(user)
                            ARY[user] = socks
                            print(user, 'login')
                            if len(OFFLINEMSG[user]) > 0:#offline msg
                                OFFLINEMSG[user] = 'Here\'s your offline message:' + OFFLINEMSG[user]
                                socks.sendall(OFFLINEMSG[user].encode(encoding='UTF-8'))
                                OFFLINEMSG[user] = ''
                            else:
                                socks.sendall(b'Welcome here.') 
                    elif data == "listuser":
                        #print(ONLINE)
                        userlist = "\n".join(ONLINE)
                        socks.sendall(userlist.encode(encoding='UTF-8'))
                    elif data[0:5] == 'talk ': # check whether the target person is online
                        if ONLINE.count(data[5:])>0:
                            socks.sendall(b'online')
                        else:
                            response = ':check:' + data[5:] + ' is offline! You can send message!'
                            socks.sendall(response.encode(encoding='UTF-8'))
                    elif data[0:5] == 'send ':
                        cmd = data.split()
                        message = " ".join(cmd[2:])
                        print('send',cmd[1],'message:', message)
                        #if cmd[1] in ARY: #online
                            #targetSock = ARY[cmd[1]]
                            #targetSock.sendall(message.encode(encoding='UTF-8'))
                        #else:
                        user = getNameBySock(socks)
                        OFFLINEMSG[cmd[1]] += "\n[" + user + "] " + message
                    elif data[0:10] == 'broadcast ':
                        print('send broadcast message:', data[10:])
                        broadcast_data(socks, data[10:], sock)
                    elif data[0:11] == 'getMessage ':
                        user = data[11:]
                        if len(OFFLINEMSG[user]) > 0:
                            socks.sendall(OFFLINEMSG[user].encode(encoding='UTF-8'))
                            OFFLINEMSG[user] = ''
                        else:
                            socks.sendall(b'nothing')
                except:
                    socks.close()
                    CONNECTION_LIST.remove(socks)
                    for user in ARY.keys():
                        if ARY[user] == socks:
                            ARY[user] = ''
                            ONLINE.remove(user)
                            broadcast_data(socks, user + " is offline", sock)
                            print (user + " is offline")
                            break
                    continue

    sock.close()
    print('Socket closed')
def receiveThread(sock):
    reply = recvall(sock, 16)
    reply = reply.decode('utf-8')
    print(reply)

def client(host, port):
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((host, port)) #perform TCP 3-way handshake
    print('Client has been assigned socket name', sock.getsockname())

    login = input('login:')
    if len(login)>0 and login in ACCOUNT:
        password = getpass.getpass()
        if password == ACCOUNT[login]:
            print('welcome back, ', login)
            data = 'I am ' + login
            sock.sendall(data.encode(encoding='UTF-8'))
            reply = recvall(sock, 16)
            if len(reply)>0 :
                    print(reply.decode('utf-8'))
            
            while True: #For user input 
                action = input('>')
                if action == 'logout': #logout. offline.
                    break
                elif action[0:8] == 'listuser':
                    sock.sendall(b'listuser')
                    msgServer = recvall(sock, 16)
                    print('User list\n', msgServer.decode('utf-8'))
                elif action[0:5] == 'send ':
                    sock.sendall(action.encode(encoding='UTF-8'))
                elif action[0:10] == 'broadcast ':
                    sock.sendall(action.encode(encoding='UTF-8'))
                elif action[0:5] == 'talk ': #talk mode
                    print('Talk to', action[5:])
                    if action[5:] == login:
                        print('You cannot talk to yourself')
                    elif action[5:] not in ACCOUNT:
                        print(action[5:], 'do not exist!')
                    else:
                        sock.sendall(action.encode(encoding='UTF-8'))
                        result = recvall(sock, 16)
                        if result.decode('utf-8') == 'online':
                            print('You are in chat mode. Key in quit to exit this mode.')
                            chater = action[5:]
                            prompt = '[' + login + '] '
                            while True: #in talk mode
                                line = input(prompt)
                                if line == 'quit':
                                    break
                                elif len(line) == 0:
                                    send = 'getMessage ' + login
                                    sock.sendall(send.encode(encoding='UTF-8'))
                                    msgServer = recvall(sock, 16)
                                    if msgServer.decode('utf-8') != 'nothing':
                                        print(msgServer.decode('utf-8'))
                                else: 
                                    data = 'send '+ chater + ' ' +line
                                    sock.sendall(data.encode(encoding='UTF-8'))
                        else:
                            print(result.decode('utf-8'))
                elif len(action) == 0:
                    send = 'getMessage ' + login
                    sock.sendall(send.encode(encoding='UTF-8'))
                    msgServer = recvall(sock, 16)
                    if msgServer.decode('utf-8') != 'nothing':
                        print(msgServer.decode('utf-8'))
                else: #invalid action
                    print('Action', action, 'is not a valid action.')                   
        else:
            print('Wrong password, you idot!')
    else:
        print('This account doesn\'t exists!')
    print('You are offline now')
    sock.close()
if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive over TCP')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('host', help='interface the server listens at:'
                        ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)
    
    
