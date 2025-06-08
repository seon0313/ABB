from log import LogType, LogMessageType

class EventListener:
    def __init__(self, value=None):
        self.getEvent = value
    def setEvent(self, value):
        self.getEvent = value

class Event:
    def __init__(self):
        self.__l: dict[EventListener] = {}
    
    def sendEvent(self,name: str, value: any) -> bool:
        eListner: list = self.__l.get(name)
        if eListner:
            for i in eListner:
                i.getEvent(value)
            return True
        return False
    def addListener(self,name:str, listener: EventListener):
        if not self.__l.get(name, None):
            self.__l[name] = [listener]
        else: self.__l[name].append(listener)
    
    def i(self, logType: LogType, message: str):
        self.sendEvent('log', {'logType': logType, 'logMessageType': LogMessageType.NORMAL, 'message': message})
    def e(self, logType: LogType, message: str):
        self.sendEvent('log', {'logType': logType, 'logMessageType': LogMessageType.ERROR, 'message': message})
    def w(self, logType: LogType, message: str):
        self.sendEvent('log', {'logType': logType, 'logMessageType': LogMessageType.WARNING, 'message': message})
    
    def close(self):
        self.sendEvent('log', {'type': 'close'})

class RobotSystem:
    def __init__(self, name='test', version='test', ip='', password: str='0000'):
        self.values: dict = {}
        self.name: str = name
        self.version: str = version
        self.ip: str = ip
        self.password: str = password

class RobotSystemOldVersion(RobotSystem):
    def __init__(self, event, name='test', version='test', ip='', password = '0000'):
        super().__init__(name, version, ip, password)
        self.event = event