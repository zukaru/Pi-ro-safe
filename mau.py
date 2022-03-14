import os
if os.name == 'nt':
    import RPi_test.GPIO as GPIO
else:
    import RPi.GPIO as GPIO

class Mau():
    def __init__(self,pin) -> None:
        self.pin=pin
        self.log={}

    def write(self):
        pass

    def read(self):
        pass