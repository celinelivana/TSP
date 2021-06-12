import socket, os
from socket import*
from threading import *
import main
import client
import struct
import math

PORT = 20000
MSG_SIZE = 2048
BLOCK_SIZE = 1024

class server_client:
    def __init__(self,CLIENT_IP):

        #handle connections
        self.CONNECTIONS = []
        self.CONNECTED_CLIENTS = []
        self.CIP = CLIENT_IP
        self.CONNECTED = []
        self.CLIENTS = []

        #create server
        self.SERVERS = socket(AF_INET, SOCK_STREAM)
        self.SERVERS.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        #bind and listen
        self.IP = '0.0.0.0'
        self.SERVERS.bind((self.IP, PORT))
        self.SERVERS.listen()

        #start threading
        SERVER = Thread(target=self.server)
        CLIENT = Thread(target=self.client)
        SERVER.start()
        CLIENT.start()

    #waiting to connect with client
    def server(self):
        while True:
            conn, addr = self.SERVERS.accept()
            self.CONNECTED.append(addr[0])
            self.CIP.append(addr[0])
            self.CONNECTIONS.append([conn, addr[0]])
            print(f'CONNECTED TO =======> {self. CONNECTED}')
            SMSG= Thread(target=self.s_msg, args=(conn, addr))
            SMSG.start()

    #check client IP and connect with client
    def client(self):
        CHECK = Thread(target=self.check)
        CHECK.start()
        while True:
            for IP in self.CIP:
                if IP in self.CLIENTS:
                    self.CIP.remove(IP)
                else:
                    IPS = client.client(IP)
                    self.CONNECTED_CLIENTS.append(IPS)
                    self.CLIENTS.append(IP)
                    print(f'CONNECTED TO =======> {IP}')

    #checking file inside share folder
    def check(self):
        print('CHECKING FILES=======>')
        while True:
            for root, sub_dirs, files in os.walk("./share", topdown=True):
                for FILE in files:
                    FILENAME = os.path.join(root, FILE)
                    if FILENAME not in main.owned:
                        print(f'NEW FILE DETECTED =======>{FILENAME}')
                        main.owned.append(FILENAME)
                        header = b'\x00' + struct.pack('!Q', len(FILENAME.encode())) + FILENAME.encode()
                        if main.sign:
                            pass
                        else:
                            main.sign = True
                            for connection in self.CONNECTIONS:
                                connection[0].send(header)

    #recieve and respond client messages
    def s_msg(self, conn, addr):
        while True:
            MSG = conn.recv(MSG_SIZE)
            if MSG[0:1] == b'\x01':
                DATA = struct.unpack('!Q', MSG[1:9])
                FILENAME = MSG[9:9 + DATA[0]].decode()
                SIZE = os.path.getsize(FILENAME)
                TOTAL_BLOCKS = math.ceil(SIZE / BLOCK_SIZE)
                header = b'\x02' +struct.pack('!QQ', len(MSG[9:9 + DATA[0]]), TOTAL_BLOCKS) + MSG[ 9:9 + DATA[0]]
                print('FILE REQUESTED BY OTHER IPs =======>')
                conn.send(header)
            elif MSG[0:1] == b'\x03':
                DATA = struct.unpack('!QQ', MSG[1:17])
                FILENAME = MSG[17:17 + DATA[0]].decode()
                self.upload(FILENAME, DATA[1], conn)
            elif MSG == b'1':
                print('SEND TO OTHER IP =======>')
                OWNED = ""
                for file in main.owned:
                    OWNED += file + ","
                header = b'\x05' + struct.pack('!Q', len(OWNED.encode())) + OWNED.encode()
                conn.send(header)
            elif MSG == b'2':
                print('==========UPLOAD COMPLETE==========')
                main.sign = False
                conn.send(b'3')

    #upload file in chunks
    def upload(self, FILENAME, blocks, conn):
        f = open(FILENAME, 'rb')
        f.seek(blocks * BLOCK_SIZE)
        CHUNK = f.read(BLOCK_SIZE)
        f.close()
        header = b'\x04' +struct.pack('!QQQ', len(FILENAME.encode()), len(CHUNK), blocks) + FILENAME.encode()+ CHUNK
        conn.send(header)

