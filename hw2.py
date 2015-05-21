#!/usr/bin/env python3
#Simple TCP client and server that send and receive 16 octets

import argparse, socket, select, getpass

CONNECTION_LIST = []
ACCOUNT = dict({"A":"A", "B":"B", "C":"C"})
ONLINE = []

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (length, len(data)))
        data += more
    return data
def broadcast_data (sock, message, server_socket):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)
def server(interface, port):
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listening socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allowing to reuse address
    sock.bind((interface, port))
    sock.listen(1) #turning the socket into a passively listening socket,1:# of waiting conn.allowed
    CONNECTION_LIST.append(sock)
    print('Listening at', sock.getsockname())    
    while True:
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
        for socks in read_sockets:
            #New connection
            if socks == sock:
                # Handle the case in which there is a new connection recieved through server_socket
                sc, sockname = sock.accept()
                CONNECTION_LIST.append(sc)
                print ("Client (%s, %s) connected" % sockname)
                 
                print('We have accepted a connection from', sockname)
                print(' Socket name:', sc.getsockname())
                print(' Socket peer:', sc.getpeername())
             
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = recvall(socks, 16)
                    """if data[0:4] == 'I am':                        
                        if ONLINE.count(data[5:])>0:
                            socks.sendall(b'Duplicate login')
                        else:
                            ONLINE.append(data[5:])
                            socks.sendall(b'very good!')
                    #if data == 'listuser':"""
                        
                    if data:
                        
                        print(data)
                        #broadcast_data(socks, "\r" + '<' + str(socks.getpeername()) + '> ' + data)
                        #print(' Incoming sixteen-octet message:', data.decode('utf-8'))
                        #socks.sendall(b'What is your name?')             
                except:
                    broadcast_data(socks, "Client (%s, %s) is offline" % sockname, sock)
                    print ("Client (%s, %s) is offline" % sockname)
                    socks.close()
                    CONNECTION_LIST.remove(socks)
                    continue
    sc.close()
    print('Socket closed')
def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port)) #perform TCP 3-way handshake
    print('Client has been assigned socket name', sock.getsockname())
    sock.sendall(b'hey!!!')
    """reply = recvall(sock, 16)
    print('The server said', reply.decode('utf-8'))

    login = input('login:')
    if len(login)>0 and login in ACCOUNT:
        password = getpass.getpass()
        if password == ACCOUNT[login]:
            print('welcome back, ', login)
            data = 'I am ' + login
            sock.sendall(b'hey!!!')#data.encode(encoding='UTF-8')
            reply = recvall(sock, 16)
            print( reply.decode('utf-8') )
            if len(reply)>0 :
                print(reply)
            while True: #For user input
                msgServer = recvall(sock, 16)
                if msgServer:
                    print(msgServer.decode('utf-8'))
                action = input('>')
                if action == 'logout': #logout. offline.
                    break
                elif action[0:8] == 'listuser':
                    sock.sendall(b'listuser')
                    msgServer = recvall(sock, 16)
                    print(msgServer.decode('utf-8'))
                elif action[0:4] == 'send':
                    data = b'' + action[5:]
                    sock.sendall(data)
                elif action[0:9] == 'broadcast':
                    data = b'' + action[10:] 
                    sock.sendall(data)
                elif action[0:4] == 'talk' or action[0:4] == 'Talk': #talk mode
                    print('Talk to', action[5:])
                    if action[5:] == login:
                        print('You cannot talk to yourself')
                    elif action[5:] not in ACCOUNT:
                        print(action[5:], 'do not exist!')
                    else:
                        print('You are in chat mode. Key in quit to exit this mode.')
                        while True: #in talk mode
                            data = b''
                            line = input('[',login,']')
                            if line == 'quit':
                                break
                            data += line                    
                else: #invalid action
                    print('Action', action, 'is not a valid action.')
        else:
            print('Wrong password, you idot!')
    else:
        print('This account doesn\'t exists!')
    print('You are offline now')"""
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
    
    
