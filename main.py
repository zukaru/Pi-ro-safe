import os,mau,exhaust,time
import RPi.GPIO as GPIO

#inputs: fan switch,light switch,heat sensor, micro switch
channels_in = [8,10,12,16]

#outputs: ex fan relay, mau relay, lights, additional relays
channels_out = [22,24,26,28]

GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)
GPIO.setup(channels_in, GPIO.IN)
GPIO.setup(channels_out, GPIO.OUT)

off=0
on=1
hmi=GPIO.input(8)

exfan1=exhaust.Exhaust(22)
mau1=mau.Mau(24)
lights=26

class Logic():
    def __init__(self) -> None:
        self.aux_states=[]
        self.state='Normal'

    def run(self):
        if not self.running:
            GPIO.output(exfan1.pin,on)
            GPIO.output(mau1.pin,on)
            GPIO.output(lights,on)
            # GPIO.output(dry contacts,on)
            # GPIO.output(dry contacts,on)
            self.running = True
        # if fire_mode:
        #     self.running=False
        #     self.state='Fire'
        # elif not self.switch():
        #     self.state='Off'

    def switch_lights(self):
        if hmi:
            return True
        else:
            return False
    
    def switch_fans(self):
        if hmi:
            return True
        else:
            return False

    def off(self):
        if not self.off:
            GPIO.output(exfan1.pin,off)
            GPIO.output(mau1.pin,off)
            GPIO.output(lights,off)
            # GPIO.output(dry contacts,off)
            # GPIO.output(dry contacts,off)
            self.off = True

    def trouble(self):
        pass

    def fire(self):
        if not self.fired:
            GPIO.output(exfan1.pin,on)
            GPIO.output(mau1.pin,off)
            GPIO.output(lights,off)
            # GPIO.output(dry contacts,on)
            # GPIO.output(dry contacts,on)
            self.fired = True

    def aux_state(self):
        if self.aux_state=='Trouble':
            self.trouble()

    def state_manager(self):
        if self.state=='Normal':
            self.run()
        elif self.state=='Off':
            self.off()
        elif self.state=='Fire':
            self.fire()

    def update(self):
        self.state_manager()
        self.aux_state()

fs=Logic()


while True:
    time.sleep(.05)
    fs.update()