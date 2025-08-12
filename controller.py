from system import RobotSystem
from event import EventListener
from log import LogType
from enum import Enum
from gpiozero import Motor

class ValueType(Enum):
    RANGE = 0
    VALUE = 1

class Controller:
    def __init__(self, system: RobotSystem):
        self.__system: RobotSystem = system
        self.__handle: dict = None
        self.eventListener: EventListener = EventListener('controller', self.__listener)

        self.__motorList: dict = {
            'top-left' : Motor(10,12,enable=8),
            'top-right': Motor(16,18,enable=8),
            'bottom-left' : Motor(22,24,enable=8),
            'bottom-right' : Motor(32,36,enable=8),
        }

        self.__moveAngles: dict = {
            'front': [0, self.moveFront],
            'bottom': [0, self.moveBottom],
            'left': [0, self.moveLeft],
            'right': [0, self.moveBottom],
        }
    
    def __listener(self, *arg):
        self.__handle = arg[0]
        self.eventListener.i(LogType.CONTROLLER, f"Controller: {self.__handle}")
        self.eventListener.i(LogType.CONTROLLER, f"Controller: {type(self.__handle)}")

        
    def run(self, event):
        self.eventListener.run()
        while not event.is_set():
            if self.__handle:
                self.eventListener.i(LogType.CONTROLLER, f"get Value! {self.__handle}")
                if self.__handle.get('direction') in self.__moveAngles.keys():
                    self.__moveAngles[self.__handle.get('direction')][0] = self.__handle.get('value', 0)
                    self.__moveAngles[self.__handle.get('direction')][1](self.__moveAngles, self.__motorList)
                    print(f"Move: {self.__handle.get('direction')} value: {self.__motorList['top-left'].value}", flush=True)
                self.__handle = None
        self.eventListener.close()
    
    def close(self):
        for i in self.__motorList.values():
            i.close()
    
    def moveFront(self, angles: dict, motors: dict):
        speed = angles['front'][0]
        for motor in motors.values():
            motor: Motor = motor
            motor.forward(speed)

    def moveBottom(self, angles: dict, motors: dict):
        speed = angles['bottom'][0]
        for motor in motors.values():
            motor: Motor = motor
            motor.forward(-speed)

    def moveLeft(self, angles: dict, motors: dict):
        speed = angles['left'][0]
        for motor_ in motors.keys():
            motor: Motor = motors[motor_]
            if 'left' in motor_: motor.forward(speed)
            else: motor.backward(speed)

    def moveRight(self, angles: dict, motors: dict):
        speed = angles['right'][0]
        for motor_ in motors.keys():
            motor: Motor = motors[motor_]
            if 'left' in motor_: motor.backward(speed)
            else: motor.forward(speed)