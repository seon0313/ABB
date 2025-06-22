from system import RobotSystem
from event import EventListener
from log import LogType
from enum import Enum
from rpiMotorPWM import MotorPWM
import RPi.GPIO as GPIO

class ValueType(Enum):
    RANGE = 0
    VALUE = 1


class Value:
    def __init__(self, valueType: ValueType, minValue: int | float, maxValue: int | float, defaultValue: int | float, controll: MotorPWM):
        self.valueType = valueType
        self.minValue = minValue
        self.maxValue = maxValue
        self.defaultValue = defaultValue
        self.value = self.defaultValue
        self.controll = controll
    
    def setValue(self, value):
        if value < self.minValue: value = self.minValue
        if value > self.maxValue: value = self.maxValue
        self.value = value
    

class Controller:
    def __init__(self, system: RobotSystem):
        self.__system: RobotSystem = system
        self.__handle: dict = None
        self.__motorList: dict[Value] = {}
        self.__moveAngles: dict[Value] = {}
        self.eventListener: EventListener = EventListener('controller', self.__listener)
        GPIO.setmode(GPIO.BOARD)
    
    def __listener(self, *arg):
        self.__handle = arg[0]
        if self.__handle.get('direction') in self.__moveAngles.keys():
            self.__moveAngles[self.__handle.get('direction')][0] = self.__handle.get('value', 0)
            self.__moveAngles[self.__handle.get('direction')][1](self.__moveAngles, self.__motorList)
            self.eventListener.i(LogType.CONTROLLER, f"Move: {self.__handle.get('direction')} value: {self.__moveAngles[self.__handle.get('direction')].value}")
    
    def run(self, event):
        self.eventListener.run()
        while not event.is_set():
            if self.__handle:
                self.eventListener.i(LogType.CONTROLLER, f"get Value! {self.__handle}")
                self.__handle = None
            
            for i in self.__motorList.values():
                i.controll.run(i)
        self.eventListener.close()

class ABBController(Controller):
    def __init__(self, system: RobotSystem):
        super().__init__(system)
        self.__motorList: dict = {
            'top-left' : Value(ValueType.RANGE, minValue=-255, maxValue=255, defaultValue=0, controll=MotorPWM(8,10,12)),
        }
        #self.__motorList['top-right'] = Value(ValueType.RANGE, minValue=-255, maxValue=255, defaultValue=0, controll=MotorPWM())
        #self.__motorList['bottom-left'] = Value(ValueType.RANGE, minValue=-255, maxValue=255, defaultValue=0, controll=MotorPWM())
        #self.__motorList['bottom-right'] = Value(ValueType.RANGE, minValue=-255, maxValue=255, defaultValue=0, controll=MotorPWM())

        self.__moveAngles: dict = {
            'front': [0, self.moveFront],
            'bottom': [0, self.moveBottom],
            'left': [0, self.moveLeft],
            'right': [0, self.moveBottom],
        }

    def moveFront(self, angles: dict, motors: dict):
        speed = angles['front'][0]
        for motor in motors.values():
            motor: Value = motor
            motor.setValue(speed)

    def moveBottom(self, angles: dict, motors: dict):
        speed = angles['bottom'][0]
        for motor in motors.values():
            motor: Value = motor
            motor.setValue(-speed)

    def moveLeft(self, angles: dict, motors: dict):
        speed = angles['left'][0]
        for motor_ in motors.keys():
            motor: Value = motors[motor_]
            motor.setValue(speed if 'left' in motor_ else -speed)

    def moveRight(self, angles: dict, motors: dict):
        speed = angles['right'][0]
        for motor_ in motors.keys():
            motor: Value = motors[motor_]
            motor.setValue(-speed if 'left' in motor_ else speed)

    def run(self, event):
        return super().run(event)