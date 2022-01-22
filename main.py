import os,mau,exhaust,time
from turtle import onclick
import RPi.GPIO as GPIO


channels_in = []
channels_out = []
GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)
GPIO.setup(channels_in, GPIO.IN)
GPIO.setup(channels_out, GPIO.OUT)

class Logic():
    def __init__(self) -> None:
        self.aux_states=[]
        self.state='Normal'

    def run(self):
        if not self.running:
            # gpio.clear()
            # turn fan onclick
            # turn on lights
            self.running = True
        # if fire_mode:
        #     self.running=False
        #     self.state='Fire'
        # elif not self.switch():
        #     self.state='Off'

    def switch(self):
        hmi=GPIO.input(8)
        if hmi:
            return True
        else:
            return False

    def off(self):
        pass

    def trouble(self):
        pass

    def fire(self):
        pass

    def aux_state(self):
        pass

    def state_manager(self):
        if self.state=='Normal':
            self.run()
        elif self.state=='Off':
            self.off()
        elif self.state=='Trouble':
            self.trouble()
        elif self.state=='Fire':
            self.fire()

    def update(self):
        self.state_manager()
        self.aux_state()

fs=Logic()
#test
while True:
    time.sleep(.05)
    fs.update()