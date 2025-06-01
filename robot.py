from enum import Enum, auto
import threading

from numpy import real
from server import Server
from log import Log, LogMessageType, LogType
from system import Event, EventListener, RobotSystem
from RealTime import RealTime
import time
import random
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
            event= Event(),
            name=self.robot_name,
            version=self.robot_version
        )
        self.__server: Server = Server(self.system)
        with open('./key.txt', 'r') as f:
            OPENAI_API_KEY = f.readline()
            f.close()
        self.__realTime: RealTime = RealTime(OPENAI_API_KEY)

        self.__controller: Controller = ABBController(self.system)

        self.system.event.sendEvent('server', 'Hello!')
        self.system.event.addListener('log', EventListener(self.__logListener))

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

        self.system.event.i(LogType.ROBOT, "Load END")
    
    def __logListener(self, data: dict):
        mt = data.get('logMessageType', None)
        lt = data.get('logType')
        me = data.get('message')
        ty = data.get('type')
        if ty == 'close':
            self.__log.close()
        if mt == LogMessageType.NORMAL:
            self.__log.i(lt, me)
        elif mt == LogMessageType.ERROR:
            self.__log.e(lt, me)
        elif mt == LogMessageType.WARNING:
            self.__log.w(lt, me)

    def runServer(self):
        self.__server.run(self.__serverThreadEvent)
        self.__server.close()
        self.system.event.i(LogType.SERVER, "Server Thread Close")

    def runAI(self):
        self.system.event.i(LogType.AI, "AI Thread Close")

    def controller(self):
        self.__controller.run(self.__controllerThreadEvent)
        self.system.event.i(LogType.CONTROLLER, "Controller Thread Close")

    def background(self):
        while not self.__backgroundThreadEvent.is_set():
            time.sleep(2)
            self.system.values = {
                'motor1': 180,
                'random': random.randrange(0,1000),
                'motor2': 280,
                'input': 'Hello',
            }
            #self.system.event.sendEvent('controller', 'HelloWorld!')
        self.system.event.i(LogType.BACKGROUND, "Background Thread Close")
    
    def broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.system.event.i(LogType.BROADCAST, "BroadCast On")
        while not self.__broadcastServerThreadEvent.is_set():
            msg = {
                'ip': '0.0.0.0',
                'port': 8765,
                'name': self.system.name,
                'version': self.system.version
            }
            sock.sendto(json.dumps(msg).encode('utf8'), ('255.255.255.255', 5891))
            time.sleep(5)
        sock.close()
        self.system.event.i(LogType.BROADCAST, "Broadcast Thread Close")

    def run(self):
        self.__broadcastServerThread = threading.Thread(target=self.broadcast, daemon=True)
        self.__broadcastServerThread.start()
        self.system.event.i(LogType.BROADCAST, "Start Broadcast Thread")
        

        self.__serverThread = mp.Process(target=self.runServer)
        self.__serverThread.start()
        self.system.event.i(LogType.ROBOT, "Start Server Thread")

        self.__aiThread = mp.Process(target=self.runAI, daemon=True)
        self.__aiThread.start()
        self.system.event.i(LogType.ROBOT, "Start AI Thread")



        self.__realTime.connect()
        self.system.event.i(LogType.REALTIME, "Start RealTime")

        self.__backgroundThread = mp.Process(target=self.background, daemon=True)
        self.__backgroundThread.start()
        self.system.event.i(LogType.ROBOT, "Start Background Thread")

        self.__controllerThread = mp.Process(target=self.controller, daemon=True)
        self.__controllerThread.start()
        self.system.event.i(LogType.CONTROLLER, "Start Controller Thread")
    def close(self):
        self.__realTime.close()
        self.system.event.sendEvent('server',{'type':'close'})
        self.__broadcastServerThreadEvent.set()
        self.__serverThreadEvent.set()
        self.__aiThreadEvent.set()
        self.__backgroundThreadEvent.set()
        self.__controllerThreadEvent.set()

        self.__broadcastServerThread.join()
        self.__aiThread.join()
        self.__serverThread.terminate()
        self.__serverThread.join()
        self.__controllerThread.join()
        self.__backgroundThread.join()

        self.__broadcastServerThread.join()
        self.system.event.i(LogType.ROBOT, "Robot Off")
        self.system.event.close()

if __name__ == '__main__':
    robot = Robot('ABB Type1', RobotType.ABB, '0.1 Alpha')
    robot.run()
    while True:
        if input('if you want quit just press "Q" ').upper() == 'Q': break
    robot.close()