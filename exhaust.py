import os,time
if os.name == 'nt':
    import RPi_test.GPIO as GPIO
else:
    import RPi.GPIO as GPIO

class Exhaust():
    def __init__(self,pin) -> None:
        self.pin=pin
        self.log={}
        self.unsafe_state_trigger=0
        self.state=0
        self.run_time=0
        self.last_state_change=0

    def write(self):
        pass

    def read(self):
        pass

    def on(self):
        if self.state==0:
            self.state=1
            self.last_state_change=time.time()

    def off(self):
        if self.state==1:
            self.state=0
            self.last_state_change=time.time()