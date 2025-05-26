from enum import Enum, auto
import threading
from server import Server
from log import Log, LogMessageType, LogType
from system import Event, EventListener, RobotSystem
from RealTime import RealTime
import time
import random
from controller import Controller, ABBController

class RobotType(Enum):
    ABB = "abb"
    CAPSTONE = "capstone"

class Robot:
    def __init__(self, name: str, robot_type: RobotType, version: str):
        self.robot_name: str = name
        self.robot_version: str = version
        self.robot_type: RobotType = robot_type

        self.system:RobotSystem = RobotSystem(
            event= Event(),
            log=Log(),
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

        self.__aiThread: threading.Thread = None
        self.__aiThreadEvent: threading.Event = threading.Event()
        self.__serverThread: threading.Thread = None
        self.__serverThreadEvent: threading.Event = threading.Event()
        self.__controllerThread: threading.Thread = None
        self.__controllerThreadEvent: threading.Event = threading.Event()
        self.__backgroundThread: threading.Thread = None
        self.__backgroundThreadEvent: threading.Event = threading.Event()
        self.__realTimeThread: threading.Thread = None
        self.__realTimeThreadEvent: threading.Event = threading.Event()

        self.system.log.i(LogType.ROBOT, "Load END")

    def server(self):
        threading.Thread(target=self.__server.run, daemon=True).start()
        while not self.__aiThreadEvent.is_set(): pass
        self.__server.close()
        self.system.log.i(LogType.SERVER, "Server Thread Close")

    def runRealTime(self):
        try:
            self.__realTime.connect()
            while not self.__realTimeThreadEvent.is_set():
                pass
            self.__realTime.close()
        except Exception as e:
            self.system.log.e(LogType.REALTIME, e)
        self.system.log.i(LogType.REALTIME, "RealTime Thread Close")
    
    def runAI(self):
        self.system.log.i(LogType.AI, "AI Thread Close")

    def controller(self):
        self.__controller.run(self.__controllerThreadEvent)
        self.system.log.i(LogType.CONTROLLER, "Controller Thread Close")

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
        self.system.log.i(LogType.BACKGROUND, "Background Thread Close")

    def run(self):
        self.__serverThread = threading.Thread(target=self.server, daemon=True)
        self.__serverThread.start()
        self.system.log.i(LogType.ROBOT, "Start Server Thread")

        self.__aiThread = threading.Thread(target=self.runAI, daemon=True)
        self.__aiThread.start()
        self.system.log.i(LogType.ROBOT, "Start AI Thread")

        self.__realTimeThread = threading.Thread(target=self.runRealTime, daemon=True)
        self.__realTimeThread.start()
        self.system.log.i(LogType.REALTIME, "Start RealTime Thread")

        self.__backgroundThread = threading.Thread(target=self.background, daemon=True)
        self.__backgroundThread.start()
        self.system.log.i(LogType.ROBOT, "Start Background Thread")

        self.__controllerThread = threading.Thread(target=self.controller, daemon=True)
        self.__controllerThread.start()
        self.system.log.i(LogType.CONTROLLER, "Start Controller Thread")
    def close(self):
        self.__aiThreadEvent.set()
        self.__serverThreadEvent.set()
        self.__controllerThreadEvent.set()
        self.__backgroundThreadEvent.set()
        self.__realTimeThreadEvent.set()

        self.__aiThread.join()
        self.__serverThread.join()
        self.__controllerThread.join()
        self.__backgroundThread.join()
        self.__realTimeThread.join()
        self.system.log.i(LogType.ROBOT, "Robot Off")
        self.system.log.close()

if __name__ == '__main__':
    robot = Robot('ABB Type1', RobotType.ABB)
    robot.run()
    try:
        while True: pass
    except KeyboardInterrupt:
        pass
    robot.close()