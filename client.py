import socket, os, time
from socket import *
from threading import *
import main
import struct
from tqdm import tqdm

PORT = 20000
MSG_SIZE = 2048
BLOCK_SIZE = 1024

class client:
    def __init__(self, ip):
        #create client
        self.CLIENTS = socket(AF_INET,SOCK_STREAM)
        self.CLIENTS.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)

        #try to connect with server
        while True:
            try:
                self.CLIENTS.connect((ip, PORT))
                print(f'CONNECTED TO>>>>>>>>{ip} ')
                break
            except Exception as e:
                time.sleep(2)

        #start thread
        CMSG = Thread(target=self.c_msg)
        CMSG.start()

    #recieve and respond server messages
    def c_msg(self):
        self.CLIENTS.send(b'1')
        while True:
            MSG = self.CLIENTS.recv(MSG_SIZE)
            if MSG[0:1] == b'\x00':
                UNPACK = struct.unpack('!Q', MSG[1:9])
                FILENAME = MSG[9:9 + UNPACK[0]].decode()
                if FILENAME not in main.owned:
                    main.sign = True
                    print('REQUESTING FILE>>>>>>>>')
                    header = b'\x01' +struct.pack('!Q', len(FILENAME.encode())) + FILENAME.encode()
                    main.owned.append(FILENAME)
                    self.CLIENTS.send(header)
                else:
                    pass
            elif MSG[0:1] == b'\x02':
                UNPACK = struct.unpack('!QQ', MSG[1:17])
                FILENAME = MSG[17:17 + UNPACK[0]].decode()
                BLOCKS = UNPACK[1]
                self.download(FILENAME, BLOCKS)
                main.sign = False
                self.CLIENTS.send(b'2')
                while True:
                    MSGG = self.CLIENTS.recv(MSG_SIZE)
                    if not MSGG:
                        pass
                    elif MSGG == b'3':
                        print('>>>>>>>>>>>>DOWNLOAD COMPLETE<<<<<<<<<<<<')
                        break
                    else:
                        self.CLIENTS.send(b'2')
                self.CLIENTS.send(b'1')
            elif MSG[0:1] == b'\x05':
                UNPACK = struct.unpack('!Q', MSG[1:9])
                FILENAME_LIST = MSG[9:9 + UNPACK[0]].decode().split(",")[:-1]
                for FILE in FILENAME_LIST:
                    if FILE not in main.owned:
                        print('REQUESTING FILE>>>>>>>>')
                        main.send_state = True
                        header = b'\x01' +struct.pack('!Q', len(FILE.encode())) + FILE.encode()
                        main.owned.append(FILE)
                        self.CLIENTS.send(header)
                        break

    #download file in chunks
    def download(self, FILENAME, blocks):
        os.makedirs(os.path.dirname(FILENAME),exist_ok=True)
        f = open(FILENAME, 'wb')
        for COUNT in tqdm(range(blocks+1)):
            header = b'\x03' + struct.pack('!QQ', len(FILENAME.encode()),COUNT) + FILENAME.encode()
            self.CLIENTS.send(header)
            while True:
                MSG = self.CLIENTS.recv(MSG_SIZE)
                if MSG[0:1] == b'\x04':
                    UNPACK = struct.unpack('!QQQ', MSG[1:25])
                    CHUNK = MSG[25+UNPACK[0] : 25+UNPACK[0]+UNPACK[1]]
                    f.write(CHUNK)
                    break
        f.close()


