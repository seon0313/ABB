import json, socket, threading
from system import RobotSystem
from log import LogType, LogMessageType, Log

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
    def sendEvent(self, name: str, value: any):
        msg = {
            'type': 'send',
            'target': name,
            'value': value
        }
        id_ = name
        if id_:
            msg = json.dumps(msg).encode('utf8')
            for i in self.__clients.get(id_, []):
                i.sendall(msg)
    
    def __client(self, client: socket.socket, addr):
        id = client.recv(1024).decode('utf8')
        client.sendall('end'.encode('utf8'))
        self.__log.i(LogType.EVENT, f'connected id:{id} | {addr}')
        if not self.__clients.get(id, None): self.__clients[id] = [client]
        else: self.__clients[id].append(client)

        overflow: str = ''

        while not self.__threadEvent.is_set():
            try:
                if overflow != '' and overflow[-1] == '\0': 
                    data = overflow.split('\0')
                    overflow = ''
                else:
                    data = str(overflow+(client.recv(4096).decode('utf8'))).split('\0')
                    if len(data)>1:
                        overflow = data[1]
                        if len(data) >= 3: overflow += '\0'
                    else: overflow = ''

                data: dict = json.loads(data[0])

                type_ = data.get('type', '')

                if type_ == 'send':
                    id_ = data.get('target', None)
                    if id_:
                        msg = json.dumps(data.get('value', '')).encode('utf8')
                        for i in self.__clients.get(id_, []):
                            i.sendall(msg)
                if type_ == 'log':
                    logType = LogType.getLogType(data.get('logType'))
                    if logType:
                        messageType = LogMessageType.getLogMessageType(data.get('messageType'))
                        if messageType:
                            message = data.get('message', '')
                            self.__log.addLog(logType, messageType, message)

            except Exception as e:
                self.__log.e(LogType.EVENT, f"Client Error {addr}:\t{e}")
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
        self.__thread.join()

class EventListener:
    def __init__(self, name: str, func: any, ip='127.0.0.1', port=7564):
        self.__ip = ip
        self.name = name
        self.__port = port
        self.__client: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__thread: threading.Thread = None
        self.__threadEvent: threading.Event = threading.Event()
        self.__has_connect: bool = False
        self.func = func

    def sendEvent(self, name: str, value: any):
        msg = {
            'type': 'send',
            'target': name,
            'value': value
        }
        self.__client.sendall(str(json.dumps(msg)+'\0').encode('utf8'))

    def sendLog(self, logType: LogType, messageType: LogMessageType, message: str):
        msg = {
            'type': 'log',
            'logType': logType.value,
            'messageType': messageType.value,
            'message': message
        }
        self.__client.send(str(json.dumps(msg)+'\0').encode('utf8'))

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
                data = self.__client.recv(4096)
                data: dict = json.loads(data.decode('utf8'))
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
        self.__client.close()