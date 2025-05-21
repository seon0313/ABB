from system import RobotSystem, Event, EventListener
from log import Log, LogType
import threading
import time

class Controller:
    def __init__(self, system: RobotSystem):
        self.__system: RobotSystem = system
        self.__system.log.i(LogType.CONTROLLER, "Controller Load end")
    
    def run(self, event: threading.Event):
        returnValue = None
        def h(*arg):
            nonlocal returnValue
            returnValue = arg
        el = EventListener(h)
        self.__system.event.addListener('controller', el)
        while not event.is_set():
            if returnValue:
                self.__system.log.i(LogType.CONTROLLER, f"get Value! {returnValue}")
            time.sleep(2)

class ABBController(Controller):
    def __init__(self):
        super().__init__()