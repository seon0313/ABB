import RPi.GPIO as GPIO

class MotorPWM:
    def __init__(self,motorPinEN: int, motorPinA: int, motorPinB: int, reverse: bool = False):
        self.__pinA: int = motorPinA
        self.__pinB: int = motorPinB
        self.__pinEN: int = motorPinEN

        self.reverse: bool = reverse

        GPIO.setup(self.__pinA, GPIO.OUT)
        GPIO.setup(self.__pinB, GPIO.OUT)

        self.__pwm: GPIO.PWM = GPIO.PWM(self.__pinEN, 100)
        self.__pwm.start(0)
    
    def run(self,value):
        self.__pwm.ChangeDutyCycle(value.value)

        if self.reverse:
            GPIO.output(self.__pinA, 1)
            GPIO.output(self.__pinB, 0)
        else:
            GPIO.output(self.__pinA, 0)
            GPIO.output(self.__pinB, 1)
        
        if value.value == value.defaultValue:
            GPIO.output(self.__pinA, 0)
            GPIO.output(self.__pinB, 0)
        

