import os,mau,exhaust,time
import RPi.GPIO as GPIO


#inputs: fan switch,light switch,heat sensor, micro switch
channels_in = [8,10,12,16]

#outputs: ex fan relay, mau relay, lights, additional relays
channels_out = [22,24,26,28]

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(channels_in, GPIO.IN)
GPIO.setup(channels_out, GPIO.OUT)

off=0
on=1
#hmi=GPIO.input(8)

exfan1=exhaust.Exhaust(22)
mau1=mau.Mau(24)
#lights=GPIO.input(26)
lights_pin=26

def heat_sensor():
    return GPIO.input(12,'h')
def micro_switch():
    return GPIO.input(16,'m')

def clean_exit():
    GPIO.cleanup()

def clean_list(list,element):
    while True:
        try:
            list.remove(element)
        except ValueError:
            break

class Logic():
    def __init__(self) -> None:
        self.aux_state=[]
        self.state='Normal'
        self.running=False
        self.shut_off=False
        self.fired=False
        self.sensor_target=time.time()

        self.devices={
            'exhaust':0,
            'mau':0,
            'lights':0,
            'dry_contact':0
        }
        self.conditions={
            'fans':0,
            'lights':0,
            'heat_sensor':0,
            'micro_switch':0
        }

    def normal(self):
        if micro_switch():
            print('micro_switch')
            self.state='Fire'
            self.conditions['micro_switch']=1
        else:
            if self.devices['exhaust']==1:
                GPIO.output(exfan1.pin,on)
                self.conditions['fans']=1
            elif self.devices['exhaust']==0:
                GPIO.output(exfan1.pin,off)
                self.conditions['fans']=0
            if self.devices['mau']==1:
                GPIO.output(mau1.pin,on)
                self.conditions['fans']=1
            elif self.devices['mau']==0:
                GPIO.output(mau1.pin,off)
                self.conditions['fans']=0
            if heat_sensor():
                self.conditions['heat_sensor']=1
                self.heat_trip()
            else:
                self.conditions['heat_sensor']=0
            if self.devices['lights']==1:
                GPIO.output(lights_pin,on)
                self.conditions['lights']=1
            elif self.devices['lights']==0:
                GPIO.output(lights_pin,off)
                self.conditions['lights']=0
            # if self.devices['dry_contact']==1:
            #     GPIO.output(dry_contact.pin,on)
            # elif self.devices['dry_contact']==0:
            #     GPIO.output(dry_contact.pin,off)
                # GPIO.output(dry contacts,on)
                # GPIO.output(dry contacts,on)
            # if fire_mode:
            #     self.running=False
            #     self.state='Fire'
            # elif not self.switch():
            #     self.state='Off'
    def heat_trip(self):
        if self.sensor_target<=time.time():
            self.sensor_target=time.time()+5
            self.aux_state.append('heat_sensor')
            print('tripa')
        elif self.sensor_target>=time.time()+8:
            self.sensor_target=time.time()+20
            self.aux_state.append('heat_sensor')
            print('tripb')
        elif self.sensor_target>=time.time()+5:
            self.sensor_target=time.time()+10
            self.aux_state.append('heat_sensor')
            print('tripc')

    def heat_sensor(self):
            if self.sensor_target>=time.time():
                GPIO.output(exfan1.pin,on)
                self.devices['exhaust']=1
                self.devices['mau']=1
            else:
                GPIO.output(exfan1.pin,off)
                self.devices['exhaust']=0
                self.devices['mau']=0
                clean_list(self.aux_state,'heat_sensor')




    def trouble(self):
        pass

    def fire(self):
        if not self.fired:
            GPIO.output(exfan1.pin,on)
            GPIO.output(mau1.pin,off)
            GPIO.output(lights_pin,off)
            # GPIO.output(dry contacts,on)
            # GPIO.output(dry contacts,on)
            self.fired = True
        if not micro_switch():
            self.fired = False
            self.state='Normal'
            self.conditions['micro_switch']=0

    def auxillary(self):
        if 'Trouble' in self.aux_state:
            self.trouble()
        if 'heat_sensor' in self.aux_state:
            self.heat_sensor()

    def state_manager(self):
        if self.state=='Fire':
            self.fire()
            print("fired state")
        elif self.state=='Normal':
            self.normal()
            print("normal state")

    def update(self):
        self.state_manager()
        self.auxillary()

fs=Logic()
def logic():
    while True:
        fs.update()
        time.sleep(.75)