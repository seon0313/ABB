from log import Log, LogType, LogMessageType
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
    
    def i(self, logType: LogType, message: str):
        self.sendEvent('log', {'logType': logType, 'logMessageType': LogMessageType.NORMAL, 'message': message})
    def e(self, logType: LogType, message: str):
        self.sendEvent('log', {'logType': logType, 'logMessageType': LogMessageType.ERROR, 'message': message})
    def w(self, logType: LogType, message: str):
        self.sendEvent('log', {'logType': logType, 'logMessageType': LogMessageType.WARNING, 'message': message})
    
    def close(self):
        self.sendEvent('log', {'type': 'close'})

class RobotSystem:
    def __init__(self, event: Event, name='test', version='test', ip=''):
        self.event: Event = event
        self.values: dict = {}
        self.name: str = name
        self.version: str = version
        self.ip: str = ip