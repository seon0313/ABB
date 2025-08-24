import json, socket, threading
from system import RobotSystem
from log import LogType, LogMessageType, Log
import struct
import traceback

class Event:
    def __init__(self,system: RobotSystem, log: Log, ip='0.0.0.0', port=7564):
        self.__ip = ip
        self.__port = port
        self.__server: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__thread: threading.Thread = threading.Thread(target=self.__run, daemon=True)
        self.__threadEvent: threading.Event = threading.Event()
        self.buff: int = 1024
        self.__clients: dict[socket.socket] = {}
        self.__system = system
        self.__log = log
        self.isOpend: bool = False
        self.__send_lock = threading.Lock()

        self.__oldversion: bool = False
    
    def sendEvent(self, name: str, value: any):
        msg = {
            'type': 'send',
            'target': name,
            'value': value
        }
        id_ = name
        if id_:
            msg = json.dumps(msg).encode('utf8')
            for i in tuple(self.__clients.get(id_, [])):
                self.__send(msg,c=i)
    
    def __send(self, data, c:socket.socket=None):
        with self.__send_lock:
            s = self.__server if not c else c
            s.sendall(struct.pack('>Q', len(data)))
            s.sendall(data)
    
    def __recv_all(self, c: socket.socket, n: int) -> bytearray | None:
        data = bytearray()
        while len(data) < n:
            try:
                l = n - len(data)
                packet = c.recv(l if l <= 1024 else 1024)
                if not packet:
                    return None
                data.extend(packet)
            except socket.error:
                return None
        return data

    def __read(self, c=socket.socket) -> str:
        (length,) = struct.unpack('>Q', self.__recv_all(c, 8))
        data = self.__recv_all(c,length)
        
        data = data.decode('utf8')
        #print('read:\t', data.split('value')[0], flush=True)
        return data

    def __client(self, client: socket.socket, addr):
        id = client.recv(1024).decode('utf8')
        client.sendall('end'.encode('utf8'))
        self.__log.i(LogType.EVENT, f'connected id:{id} | {addr}')
        if not self.__clients.get(id, None): self.__clients[id] = [client]
        else: self.__clients[id].append(client)

        overflow: str = ''

        #client.settimeout(10)

        while not self.__threadEvent.is_set():
            try:
                data: dict = json.loads(self.__read(client))

                type_ = data.get('type', '')

                if type_ == 'send':
                    id_ = data.get('target', None)
                    if id_:
                        msg = json.dumps(data.get('value', '')).encode('utf8')
                        for i in tuple(self.__clients.get(id_, [])):
                            self.__send(msg,c=i)
                if type_ == 'log':
                    logType = LogType.getLogType(data.get('logType'))
                    if logType:
                        messageType = LogMessageType.getLogMessageType(data.get('messageType'))
                        if messageType:
                            message = data.get('message', '')
                            self.__log.addLog(logType, messageType, message)
                            if self.__clients.get('server'):
                                self.__send(json.dumps({'type':'log','data':Log.logToStr(logType, messageType, message)}).encode('utf8'), c=self.__clients.get('server')[0])

            except Exception as e:
                self.__log.e(LogType.EVENT, f"Client Error id={id} {addr}:\t{traceback.format_exc()}")
        client.close()
        self.__clients[id].remove(client)
        self.__log.i(LogType.EVENT, f'Client Close {addr}')

    def __run(self):
        self.__server.bind((self.__ip, self.__port))
        self.__server.listen()
        self.__log.i(LogType.EVENT, "Event Server Open")
        self.isOpend = True
        while not self.__threadEvent.is_set():
            client, addr = self.__server.accept()
            threading.Thread(target=self.__client, args=(client, addr,)).start()

    def run(self):
        self.__thread.start()
    
    def close(self):
        self.__threadEvent.set()
        self.isOpend = False
        self.__server.close()

class EventListener:
    def __init__(self, name: str, func: any, ip='127.0.0.1', port=7564):
        self.__ip = ip
        self.name = name
        self.__port = port
        self.__client: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #self.__client.settimeout(10)
        self.__thread: threading.Thread = None
        self.__threadEvent: threading.Event = threading.Event()
        self.__has_connect: bool = False
        self.func = func
        self.__send_lock = threading.Lock()
    
    def ifcloseRestart(self) -> bool:
        if self.__client._closed:
            self.run()
            return True
        return False
    
    def __send(self, data, c:socket.socket=None):
        with self.__send_lock:
            s = self.__client if not c else c
            s.sendall(struct.pack('>Q', len(data)))
            s.sendall(data)
    def __recv_all(self, c: socket.socket, n: int) -> bytearray | None:
        data = bytearray()
        while len(data) < n:
            try:
                packet = c.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            except socket.error:
                return None
        return data

    def __read(self, c=socket.socket) -> str:
        (length,) = struct.unpack('>Q', self.__recv_all(c, 8))
        data = self.__recv_all(c,length)
        
        data = data.decode('utf8')
        #print('read:\t', data.split('value')[0], flush=True)
        return data

    def sendEvent(self, name: str, value: any):
        msg = {
            'type': 'send',
            'target': name,
            'value': value
        }
        self.__send(str(json.dumps(msg)).encode('utf8'))

    def sendLog(self, logType: LogType, messageType: LogMessageType, message: str):
        msg = {
            'type': 'log',
            'logType': logType.value,
            'messageType': messageType.value,
            'message': message
        }
        self.__send(str(json.dumps(msg)).encode('utf8'))

    def i(self, logType: LogType, message: str):
        self.sendLog(logType, LogMessageType.NORMAL, message)
    def e(self, logType: LogType, message: str):
        self.sendLog(logType, LogMessageType.ERROR, message)
    def w(self, logType: LogType, message: str):
        self.sendLog(logType, LogMessageType.WARNING, message)

    def __listener(self):
        while not self.__has_connect and not self.__threadEvent.is_set(): pass

        while not self.__threadEvent.is_set():
            try:
                #data = self.__read(self.__client)
                data: dict = json.loads(self.__read(self.__client))
                self.func(data)
            except Exception as e: self.sendLog(LogType.EVENT, LogMessageType.ERROR, f'L:\t{e}')

    def run(self):
        self.__client.connect((self.__ip, self.__port))
        self.__client.sendall(self.name.encode('utf8'))
        r = self.__client.recv(1024).decode('utf8')
        self.__has_connect = True
        self.__thread = threading.Thread(target=self.__listener, daemon=True)
        self.__thread.start()
    
    def close(self):
        self.__threadEvent.is_set()
        self.__client.close()