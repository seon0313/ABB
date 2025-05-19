from enum import Enum, auto
import threading
from server import Server
from log import Log, LogMessageType, LogType
from system import Event, EventListener, RobotSystem

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

        self.system.event.sendEvent('server', 'Hello!')

        self.__aiThread__: threading.Thread = None
        self.__aiThreadEvent__: threading.Event = threading.Event()
        self.__serverThread__: threading.Thread = None
        self.__serverThreadEvent__: threading.Event = threading.Event()
        self.__controllerThread__: threading.Thread = None
        self.__controllerThreadEvent__: threading.Event = threading.Event()

        self.system.log.i(LogType.ROBOT, "Load END")

    def server(self):
        pass

    def runAI(self):
        while not self.__aiThreadEvent__.is_set():
            pass

    def controller(self):
        pass

    def run(self):
        self.threading.Thread()
    def close(self):
        self.system.log.i(LogType.ROBOT, "Robot Off")
        self.system.log.close()

if __name__ == '__main__':
    robot = Robot('ABB Type1', RobotType.ABB)
    robot.close()