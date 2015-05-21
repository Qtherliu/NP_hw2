#!/usr/bin/env python3
#Simple TCP client and server that send and receive 16 octets

import argparse, socket

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
def server(interface, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listening socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allowing to reuse address
    sock.bind((interface, port))
    sock.listen(1) #turning the socket into a passively listening socket,1:# of waiting conn.allowed
    print('Listening at', sock.getsockname())
    while True:
        sc, sockname = sock.accept() #connected socket
        print('We have accepted a connection from', sockname)
        print(' Socket name:', sc.getsockname())
        print(' Socket peer:', sc.getpeername())
        message = recvall(sc, 16)
        print(' Incoming sixteen-octet message:', message.decode('utf-8'))
        sc.sendall(b'Farewell, client')
        sc.close()
        print(' Reply sent, socket closed')
def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port)) #perform TCP 3-way handshake
    print('Client has been assigned socket name', sock.getsockname())
    sock.sendall(b'Hi there, server')
    reply = recvall(sock, 16)
    print('The server said', reply.decode('utf-8'))
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
    
    
