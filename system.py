from log import Log
from enum import Enum

class EventListener:
    def __init__(self, value=None):
        self.getEvent = value
    def setEvent(self, value):
        self.getEvent = value

class Event:
    def __init__(self):
        self.__l: dict[EventListener] = {}
    
    def sendEvent(self,name: str, value: any) -> bool:
        eListner: EventListener = self.__l.get(name)
        if eListner:
            eListner.getEvent(value)
            return True
        return False
    def addListener(self,name:str, listener: EventListener):
        self.__l[name] = listener

class RobotSystem:
    def __init__(self, event: Event, log: Log):
        self.event: Event = event
        self.log: Log = log
        self.values: dict = {}