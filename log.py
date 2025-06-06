from enum import Enum
import time

class LogType(Enum):
    ALL = -1
    ROBOT = 0
    SERVER = 1
    AI = 2
    CONTROLLER = 3
    BACKGROUND = 4
    REALTIME = 5
    BROADCAST = 6
    

class LogMessageType(Enum):
    NORMAL = 0
    ERROR = 1
    WARNING = 2
    ALL = -1

class Log:
    def __init__(self):
        self.logs = []
        tf = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
        self.logfile = open(f'./log/robot-log_{tf}.txt', 'w', encoding='utf-8')
        self.saveLogLine = 1000
    
    def i(self, logType: LogType, message: str):
        self.addLog(logType, LogMessageType.NORMAL, message)
    def e(self, logType: LogType, message: str):
        self.addLog(logType, LogMessageType.ERROR, message)
    def w(self, logType: LogType, message: str):
        self.addLog(logType, LogMessageType.WARNING, message)

    def addLog(self,logType: LogType, messageType: LogMessageType, message: str):
        msg = (time.time(), logType, messageType, message)
        self.logs.append(msg)
        t = time.strftime('[%Y/%m/%d %H:%M:%S]', time.localtime(time.time()))
        logmsg = f'{t} {logType.name}-{messageType.name} | {message}\n'
        self.logfile.write(logmsg)
        self.logfile.flush()
        print(logmsg, end='')
        if len(self.logs)>self.saveLogLine: self.logs = self.logs[1:]
    
    def getLogs(self, logType:LogType=LogType.ALL,messageType: LogMessageType = LogMessageType.ALL):
        if logType != LogType.ALL:
            f1 = [i for i in tuple(self.logs) if i[1] == logType]
        else: f1 = self.logs

        if messageType != LogMessageType.ALL:
            f2 = [i for i in tuple(f1) if i[2] == messageType]
        else: f2 = f1

        return f2
    def close(self):
        self.logfile.close()