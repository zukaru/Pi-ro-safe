import os,mau,exhaust,time
import RPi.GPIO as GPIO

heat_sensor_timer=10
#inputs: fan switch,light switch,heat sensor, micro switch
channels_in = [14,15,18,23]

#outputs: ex fan relay, mau relay, lights, additional relays
channels_out = [25,8,7,12]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(channels_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(channels_out, GPIO.OUT)

off=0
on=1
#hmi=GPIO.input(14)

exfan1=exhaust.Exhaust(25)
mau1=mau.Mau(8)
dry_contact=12
#lights=GPIO.input(7)
lights_pin=7
if os.name == 'nt':
    def heat_sensor_active():
        return GPIO.input(18,'h')
    def micro_switch_active():
        return GPIO.input(23,'m')
    def fan_switch_on():
        return GPIO.input(14,'f')
    def light_switch_on():
        return GPIO.input(15,'l')
if os.name == 'posix':
    def heat_sensor_active():
        return GPIO.input(18)
    def micro_switch_active():
        return  not GPIO.input(23)
    def fan_switch_on():
        return GPIO.input(14)
    def light_switch_on():
        return GPIO.input(15)
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

        '''two dictionaries are used to share data between two threads.
        moli: main out logic in, is written too in main and read in logic.
        milo: main in logic out, is written too in logic and read in main.
        '''
        self.troubles={
            'heat_override':0
        }

        self.moli={
            'exhaust':off,
            'mau':off,
            'lights':off,
            'dry_contact':off,
            'maint_override':off
        }
        self.milo={
            'exhaust':off,
            'mau':off,
            'lights':off,
            'heat_sensor':off,
            'dry_contact':off,
            'micro_switch':off,
            'troubles':self.troubles

        }

    def normal(self):
        if micro_switch_active():
            print('micro_switch')
            self.state='Fire'
            self.milo['micro_switch']=on
        elif self.moli['maint_override']==1:
            GPIO.output(dry_contact,on)
            GPIO.output(lights_pin,on)
            GPIO.output(exfan1.pin,off)
            GPIO.output(mau1.pin,off)
        else:

            GPIO.output(dry_contact,on)

            if self.moli['exhaust']==on or fan_switch_on():
                GPIO.output(exfan1.pin,on)
                self.milo['exhaust']=on
            elif self.moli['exhaust']==off or not fan_switch_on():
                GPIO.output(exfan1.pin,off)
                self.milo['exhaust']=off
            if self.moli['mau']==on or fan_switch_on():
                GPIO.output(mau1.pin,on)
                self.milo['mau']=on
            elif self.moli['mau']==off or not fan_switch_on():
                GPIO.output(mau1.pin,off)
                self.milo['mau']=off
            if heat_sensor_active():
                self.milo['heat_sensor']=on
                self.heat_trip()
            else:
                self.milo['heat_sensor']=off
            if self.moli['lights']==on or light_switch_on():
                GPIO.output(lights_pin,on)
                self.milo['lights']=on
            elif self.moli['lights']==off or not light_switch_on():
                GPIO.output(lights_pin,off)
                self.milo['lights']=off
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
        self.sensor_target=time.time()+heat_sensor_timer
        self.aux_state.append('heat_sensor')
        print('heat trip')

    def heat_sensor(self):
            if self.sensor_target>=time.time():
                GPIO.output(exfan1.pin,on)
                GPIO.output(mau1.pin,on)
                self.milo['exhaust']=on
                self.milo['mau']=on
                self.milo['heat_sensor']=on
                print('heat timer active')
            else:
                if self.moli['exhaust']==off and self.moli['mau']==off:
                    GPIO.output(exfan1.pin,off)
                    GPIO.output(mau1.pin,off)
                self.milo['exhaust']=off
                self.milo['mau']=off
                self.milo['heat_sensor']=off
                clean_list(self.aux_state,'heat_sensor')


    def trouble(self):
        if heat_sensor_active() and not self.moli['exhaust']==1:
            self.milo['troubles']['heat_override']=1
        else:
            self.milo['troubles']['heat_override']=0

    def fire(self):
        if not self.fired:
            GPIO.output(exfan1.pin,on)
            GPIO.output(mau1.pin,off)
            GPIO.output(lights_pin,off)
            GPIO.output(dry_contact,off)
            self.fired = True
        if not micro_switch_active():
            self.fired = False
            self.state='Normal'
            self.milo['micro_switch']=off

    def auxillary(self):
        self.trouble()
        if 'heat_sensor' in self.aux_state and not self.fired:
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

if __name__=='__main__':
    try:
        logic()
    finally:
        clean_exit()