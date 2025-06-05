import json, socket, threading
from system import RobotSystem

class Event:
    def __init__(self,system: RobotSystem, ip='0.0.0.0', port=7564):
        self.__ip = ip
        self.__port = port
        self.__server: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__thread: threading.Thread = threading.Thread(target=self.__run, daemon=True)
        self.__threadEvent: threading.Event = threading.Event()
        self.buff: int = 1024
        self.__clients: dict[socket.socket] = {}
    
    def __client(self, client: socket.socket, addr,id:str):
        if not self.__clients.get(id, None): self.__clients[id] = [client]
        else: self.__clients[id].append(client)
        while not self.__threadEvent.is_set():
            data = 

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
    def __init__(self):
        pass