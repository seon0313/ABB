from enum import Enum
import threading
from server import Server
from log import Log, LogMessageType, LogType
from system import RobotSystem
from event import Event, EventListener
from RealTime import RealTime
import time
import cv2
import socket
from controller import Controller, ABBController
import multiprocessing as mp
import json

class RobotType(Enum):
    ABB = "abb"
    CAPSTONE = "capstone"

class Robot:
    def __init__(self, name: str, robot_type: RobotType, version: str):
        self.robot_name: str = name
        self.robot_version: str = version
        self.robot_type: RobotType = robot_type

        self.__log: Log = Log()

        self.system:RobotSystem = RobotSystem(
            name=self.robot_name,
            version=self.robot_version
        )

        self.__event: Event = Event(self.system, self.__log)

        self.__server: Server = Server(self.system)
        with open('./key.txt', 'r') as f:
            OPENAI_API_KEY = f.readline()
            f.close()
        self.__realTime: RealTime = RealTime(OPENAI_API_KEY)

        self.__controller: Controller = ABBController(self.system)

        self.__aiThread: mp.Process = None
        self.__aiThreadEvent = mp.Event()
        self.__serverThread: mp.Process = None
        self.__serverThreadEvent = mp.Event()
        self.__controllerThread: mp.Process = None
        self.__controllerThreadEvent = mp.Event()
        self.__backgroundThread: mp.Process = None
        self.__backgroundThreadEvent = mp.Event()
        self.__broadcastServerThread: threading.Thread = None
        self.__broadcastServerThreadEvent: threading.Event = threading.Event()

        self.__Listener = EventListener('test', lambda x: self.__log.i(LogType.EVENT, f'I get Event {x}'))

        self.__log.i(LogType.ROBOT, "Load END")

    def runServer(self):
        self.__server.run(self.__serverThreadEvent)
        self.__server.close()
        self.__log.i(LogType.SERVER, "Server Thread Close")

    def runAI(self):
        self.__log.i(LogType.AI, "AI Thread Close")

    def controller(self):
        self.__controller.run(self.__controllerThreadEvent)
        self.__log.i(LogType.CONTROLLER, "Controller Thread Close")

    def background(self):
        #self.__Listener.run()
        #count = 0
        #while not self.__backgroundThreadEvent.is_set():
        #    self.__Listener.sendEvent('test', f'{count}')
        #    self.__Listener.i(LogType.BACKGROUND, f'send {count}')
        #    count+=1
        #    time.sleep(1)
        #self.__Listener.close()
        self.__log.i(LogType.BACKGROUND, "Background Thread Close")
    
    def broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.__log.i(LogType.BROADCAST, "BroadCast On")
        while not self.__broadcastServerThreadEvent.is_set():
            msg = {
                'ip': socket.gethostbyname(socket.gethostname()),
                'port': 8765,
                'name': self.system.name,
                'version': self.system.version
            }
            sock.sendto(json.dumps(msg).encode('utf8'), ('255.255.255.255', 5891))
            time.sleep(5)
        sock.close()
        self.__log.i(LogType.BROADCAST, "Broadcast Thread Close")

    def run(self):
        self.__event.run()
        while not self.__event.isOpend: pass
        
        self.__broadcastServerThread = threading.Thread(target=self.broadcast, daemon=True)
        self.__broadcastServerThread.start()
        self.__log.i(LogType.BROADCAST, "Start Broadcast Thread")

        self.__serverThread = mp.Process(target=self.runServer)
        self.__serverThread.start()
        self.__log.i(LogType.ROBOT, "Start Server Thread")

        self.__aiThread = mp.Process(target=self.runAI, daemon=True)
        self.__aiThread.start()
        self.__log.i(LogType.ROBOT, "Start AI Thread")

        self.__realTime.connect()
        self.__log.i(LogType.REALTIME, "Start RealTime")

        self.__backgroundThread = mp.Process(target=self.background, daemon=True)
        self.__backgroundThread.start()
        self.__log.i(LogType.ROBOT, "Start Background Thread")

        self.__controllerThread = mp.Process(target=self.controller, daemon=True)
        self.__controllerThread.start()
        self.__log.i(LogType.CONTROLLER, "Start Controller Thread")
    def close(self):
        self.__realTime.close()
        self.__event.sendEvent('server', {'type':'close'})
        self.__broadcastServerThreadEvent.set()
        self.__serverThreadEvent.set()
        self.__aiThreadEvent.set()
        self.__backgroundThreadEvent.set()
        self.__controllerThreadEvent.set()

        self.__broadcastServerThread.join()
        self.__log.i(LogType.ROBOT, "BroadcastServer Close")
        self.__serverThread.terminate()
        self.__serverThread.join()
        self.__log.i(LogType.ROBOT, "Server Close")
        self.__aiThread.join()
        self.__log.i(LogType.ROBOT, "AI Thread Close")
        self.__controllerThread.join(10)
        self.__controllerThread.terminate()
        self.__log.i(LogType.ROBOT, "Controller Close")
        self.__backgroundThread.join()
        self.__log.i(LogType.ROBOT, "Background Close")
        self.__event.close()
        self.__log.i(LogType.ROBOT, "Event Close")
        self.__log.i(LogType.ROBOT, "Robot Off")
        self.__log.close()

if __name__ == '__main__':
    robot = Robot('ABB Type1', RobotType.ABB, '0.1 Alpha')
    robot.run()
    while True:
        if input('if you want quit just press "Q"\n').upper()[-1] == 'Q': break
    robot.close()