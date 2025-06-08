import json, socket, threading
from system import RobotSystem
from log import LogType, LogMessageType, Log

class Event:
    def __init__(self,system: RobotSystem, log: Log, ip='0.0.0.0', port=7564):
        self.__ip = ip
        self.__port = port
        self.__server: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__thread: threading.Thread = threading.Thread(target=self.__run, daemon=True)
        self.__threadEvent: threading.Event = threading.Event()
        self.buff: int = 1024
        self.__clients: dict[socket.socket] = {}
        self.__system = system
        self.__log = log
    
    def __client(self, client: socket.socket, addr,id:str):
        if not self.__clients.get(id, None): self.__clients[id] = [client]
        else: self.__clients[id].append(client)
        while not self.__threadEvent.is_set():
            try:
                data = bytearray()
                while True:
                    packet = client.recv(1024)
                    if not packet: break
                    data.extend(packet)
                data: dict = json.loads(data.decode('utf8'))

                type_ = data.get('type', '')

                if type_ == 'send':
                    id_ = data.get('target', None)
                    if id_:
                        msg = json.dumps(data).encode('utf8')
                        for i in self.__clients.get(id_, []):
                            i.sendall(msg)
                elif type_ == 'log':
                    logType = LogType.getLogType(data.get('logType'))
                    if logType:
                        messageType = LogMessageType.getLogMessageType(data.get('message'))
                        if messageType:
                            message = data.get('message', '')
                            self.__log.addLog(logType, messageType, message)

            except Exception as e:
                self.__system.event.e(LogType.EVENT, f"Client Error {addr}:\t{e}")
            self.__clients[id].remove(client)
            self.__system.event.i(LogType.EVENT, f'Client Close {addr}')

    def __run(self):
        self.__server.bind((self.__ip, self.__port))
        self.__server.listen()
        while not self.__threadEvent.is_set():
            client, addr = self.__server.accept()
            id = (client.recv(1024))
            threading.Thread(target=self.__client, args=(client, addr,id,))

        

    def run(self):
        self.__thread.start()
    
    def close(self):
        self.__threadEvent.set()
        self.__thread.join()

class EventListener:
    def __init__(self, func: any, ip='0.0.0.0', port=7564):
        self.__ip = ip
        self.__port = port
        self.__client: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__thread: threading.Thread = threading.Thread(target=self.__run, daemon=True)
        self.__threadEvent: threading.Event = threading.Event()
        self.__has_connect: bool = False
        self.func = func

    def sendLog(self, logType: LogType, messageType: LogMessageType, message: str):
        msg = {
            'type': 'log',
            'logType': logType.value,
            'messageType': messageType.value,
            'message': message
        }
        self.__client.send(json.dumps(msg).encode('utf8'))

    def i(self, logType: LogType, message: str):
        self.sendLog(logType, LogMessageType.NORMAL, message)
    def e(self, logType: LogType, message: str):
        self.sendLog(logType, LogMessageType.ERROR, message)
    def w(self, logType: LogType, message: str):
        self.sendLog(logType, LogMessageType.WARNING, message)

    def __listener(self):
        while not self.__has_connect and not self.__threadEvent.is_set(): pass

        while not self.__threadEvent.is_set():
            data = bytearray()
            while True:
                packet = self.__client.recv(1024)
                if not packet: break
                data.extend(packet)
            data: dict = json.dumps(data.decode('utf8'))
            self.func(data)

    def run(self):
        self.__client.connect((self.ip, self.__port))
        self.__has_connect = True
        self.__thread = threading.Thread(self.__listener, daemon=True)
        self.__thread.start()