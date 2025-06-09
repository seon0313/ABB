from system import RobotSystem
from event import EventListener
from log import Log, LogType
import threading
import time
from enum import Enum

class ValueType(Enum):
    RANGE = 0
    VALUE = 1


class Value:
    def __init__(self, valueType: ValueType, value: any):
        self.valueType = valueType
        self.value = value

class Controller:
    def __init__(self, system: RobotSystem):
        self.__system: RobotSystem = system
        self.__handle: dict = None
        self.__moveAngles: dict = {
            'front': Value(ValueType.RANGE, 0),
            'back': Value(ValueType.RANGE, 0),
            'left': Value(ValueType.RANGE, 0),
            'right': Value(ValueType.RANGE, 0),
            'rocate': Value(ValueType.VALUE, 0),
            }
        self.eventListener: EventListener = EventListener('controller', self.__listener)
    
    def __listener(self, *arg):
        self.__handle = arg[0]
        if self.__handle.get('direction') in self.__moveAngles.keys():
            self.__moveAngles[self.__handle.get('direction')].value = self.__handle.get('value', 0)
            self.eventListener.i(LogType.CONTROLLER, f"Move: {self.__handle.get('direction')} value: {self.__moveAngles[self.__handle.get('direction')].value}")
    
    def run(self, event: threading.Event):
        self.eventListener.run()
        while not event.is_set():
            if self.__handle:
                self.eventListener.i(LogType.CONTROLLER, f"get Value! {self.__handle}")
                self.__handle = None
        self.eventListener.close()

class ABBController(Controller):
    def __init__(self, system: RobotSystem):
        super().__init__(system)
    def run(self, event):
        return super().run(event)