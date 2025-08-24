from system import RobotSystem
from event import EventListener
from log import LogType
from enum import Enum
from gpiozero import Motor
import threading
import time

class ValueType(Enum):
    RANGE = 0
    VALUE = 1

class Controller:
    def __init__(self, system: RobotSystem):
        self.__system: RobotSystem = system
        self.__handle: dict = None
        self.eventListener: EventListener = EventListener('controller', self.__listener)

        self.__motorList: list = [0, 0, 0, 0]

        self.__moveAngles: dict = {
            'front': self.moveFront,
            'bottom': self.moveBottom,
            'left': self.moveLeft,
            'right': self.moveRight,
            'stop': self.moveStop
        }
        self.__moveLock = threading.Lock()
    
    def __listener(self, *arg):
        self.__handle = arg[0]
        self.eventListener.i(LogType.CONTROLLER, f"Controller: {self.__handle}")
        self.eventListener.i(LogType.CONTROLLER, f"Controller: {type(self.__handle)}")
        if self.__handle.get('direction') in self.__moveAngles.keys():
            self.__moveAngles.get(self.__handle.get('direction', 'stop'), [lambda: print()])()
        self.__handle = None
        self.eventListener.i(LogType.CONTROLLER, str(self.__motorList))

        
    def run(self, event):
        self.eventListener.run()
        motors: list[Motor] = [
            Motor(15,18, enable=14),
            Motor(23,24, enable=25),
            Motor(1,7, enable=8),
            Motor(16, 20, enable=21),
        ]
        while not event.is_set():
            for index, i in enumerate(self.__motorList):
                try:
                    if i >= 0:
                        motors[index].forward(i)
                    else:
                        motors[index].backward(i*-1)
                except: pass
        self.eventListener.close()
    
    def close(self): pass
    
    def moveStop(self):
        for i in range(len(self.__motorList)):
            self.__motorList[i] = 0
    
    def moveFront(self):
        try:
            for i in range(len(self.__motorList)):
                self.__motorList[i] = 1
        except Exception as e:
            # 에러 발생 시 로그를 남깁니다.
            print(f"Error in moveFront: {e}", flush=True)
            self.eventListener.i(LogType.CONTROLLER, f"ERROR in moveFront: {e}")

    def moveBottom(self):
        for i in range(len(self.__motorList)):
            self.__motorList[i] = -1

    def moveLeft(self):
        for i in range(len(self.__motorList)):
            if i != 0 and i != 1: self.__motorList[i] = 1
            else: self.__motorList[i] = -1

    def moveRight(self):
        for i in range(len(self.__motorList)):
            if i != 0 and i != 1: self.__motorList[i] = -1
            else: self.__motorList[i] = 1