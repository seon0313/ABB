from enum import Enum, auto
import threading
from server import Server
from log import Log, LogMessageType, LogType

class RobotType(Enum):
    ABB = "abb"
    CAPSTONE = "capstone"

class Robot:
    def __init__(self, name: str, robot_type: RobotType):
        self.robot_name: str = name
        self.robot_type: RobotType = robot_type

        self.__log__: Log = Log()
        self.__server__: Server = Server()

        self.__aiThread__: threading.Thread = None
        self.__aiThreadEvent__: threading.Event = threading.Event()
        self.__serverThread__: threading.Thread = None
        self.__serverThreadEvent__: threading.Event = threading.Event()
        self.__controllerThread__: threading.Thread = None
        self.__controllerThreadEvent__: threading.Event = threading.Event()

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
        self.__log__.close()

if __name__ == '__main__':
    robot = Robot('ABB Type1', RobotType.ABB)
    robot.close()