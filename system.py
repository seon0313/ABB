from log import Log
from enum import Enum

class EventListener:
    def __init__(self, value=None):
        self.getEvent = value
    def setEvent(self, value):
        self.getEvent = value

class Event:
    def __init__(self):
        self.__l__: dict[EventListener] = {}
    
    def sendEvent(self,name: str, value: any) -> bool:
        eListner: EventListener = self.__l__.get(name)
        if eListner:
            eListner.getEvent(value)
            return True
        return False
    def addListener(self,name:str, listener: EventListener):
        self.__l__[name] = listener

class RobotSystem:
    def __init__(self, event: Event, log: Log):
        self.event: Event = event
        self.log: Log = log
        self.values: dict = {}