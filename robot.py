from enum import Enum, auto
import threading
from server import Server
from log import Log, LogMessageType, LogType
from system import Event, EventListener, RobotSystem
from RealTime import RealTime

class RobotType(Enum):
    ABB = "abb"
    CAPSTONE = "capstone"

class Robot:
    def __init__(self, name: str, robot_type: RobotType):
        self.robot_name: str = name
        self.robot_type: RobotType = robot_type

        self.system:RobotSystem = RobotSystem(
            event= Event(),
            log=Log()
        )
        self.__server__: Server = Server(self.system)
        with open('./key.txt', 'r') as f:
            OPENAI_API_KEY = f.readline()
            f.close()
        self.__realTime__:RealTime = RealTime(OPENAI_API_KEY)

        self.system.event.sendEvent('server', 'Hello!')

        self.__aiThread__: threading.Thread = None
        self.__aiThreadEvent__: threading.Event = threading.Event()
        self.__serverThread__: threading.Thread = None
        self.__serverThreadEvent__: threading.Event = threading.Event()
        self.__controllerThread__: threading.Thread = None
        self.__controllerThreadEvent__: threading.Event = threading.Event()

        self.system.log.i(LogType.ROBOT, "Load END")

    def server(self):
        threading.Thread(target=self.__server__.run, daemon=True).start()
        while not self.__aiThreadEvent__.is_set(): pass
        self.__server__.close()
        self.system.log.i(LogType.ROBOT, "Server Thread Close")

    def runAI(self):
        self.__realTime__.connect()
        while not self.__aiThreadEvent__.is_set():
            pass
        self.__realTime__.close()
        self.system.log.i(LogType.ROBOT, "AI Thread Close")

    def controller(self):
        pass

    def run(self):
        self.__serverThread__ = threading.Thread(target=self.server, daemon=True)
        self.__serverThread__.start()
        self.system.log.i(LogType.ROBOT, "Start Server Thread")

        self.__aiThread__ = threading.Thread(target=self.runAI, daemon=True)
        self.__aiThread__.start()
        self.system.log.i(LogType.ROBOT, "Start AI Thread")
    def close(self):
        self.__aiThreadEvent__.set()
        self.__serverThreadEvent__.set()
        self.__controllerThreadEvent__.set()

        self.__aiThread__.join()
        self.__serverThread__.join()
        #self.__controllerThread__.join()
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