import os,mau,exhaust,light,drycontact,time,json
if os.name == 'nt':
    import RPi_test.GPIO as GPIO
else:
    import RPi.GPIO as GPIO

heat_sensor_timer=300
#there are only 25 GPIO pins available for input/output.
#the additional 15 are grounds, constant powers, and reserved for hats.
available_pins=[i for i in range(2,28)]
#inputs: fan switch,light switch,heat sensor, micro switch
channels_in = [14,15,18,23]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(channels_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

off=0
on=1
#hmi=GPIO.input(14)
devices=[]
def get_devices():
    def load_devices():
        try:
            with open(rf"logs/devices/device_list.json","r") as read_file:
                data = json.load(read_file)
            return data
        except FileNotFoundError:
            print("logic.get_devices().load_devices(): FileNotFoundError; Creating file")
            with open(rf"logs/devices/device_list.json","w+") as read_file:
                data={}
                json.dump(data, read_file,indent=0)
            return load_devices()


    loaded_devices=load_devices()
    for d in loaded_devices:
        if d != "default" and not any(j for j in devices if j.name == d):
            i=eval(f"{loaded_devices[d]}(name=\"{d}\")")
            if i.pin in available_pins:
                available_pins.remove(i.pin)
                set_pin_mode(i)
            devices.append(i)

def set_pin_mode(device):
    if device.pin==0:
        print(f"logic.set_pin_mode(): {device}.pin == 0")
    else:
        if device.mode=="in":
            GPIO.setup(device.pin,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
        elif device.mode=="out":
            GPIO.setup(device.pin, GPIO.OUT)
        else:
            print(f"logic.set_pin_mode(): {device}.mode is not \"in\" or \"out\"")

def exfans_on():
    for i in (i for i in devices if isinstance(i,exhaust.Exhaust)):
        if i.pin!=0:
            GPIO.output(i.pin,on)
            i.on()

def exfans_off():
    for i in (i for i in devices if isinstance(i,exhaust.Exhaust)):
        GPIO.output(i.pin,off)
        i.off()

def maufans_on():
    for i in (i for i in devices if isinstance(i,mau.Mau)):
        if i.pin!=0:
            GPIO.output(i.pin,on)
            i.on()

def maufans_off():
    for i in (i for i in devices if isinstance(i,mau.Mau)):
        GPIO.output(i.pin,off)
        i.off()

def lights_on():
    for i in (i for i in devices if isinstance(i,light.Light)):
        if i.pin!=0:
            GPIO.output(i.pin,on)
            i.on()

def lights_off():
    for i in (i for i in devices if isinstance(i,light.Light)):
        GPIO.output(i.pin,off)
        i.off()

def dry_on():
    for i in (i for i in devices if isinstance(i,drycontact.DryContact)):
        if i.pin!=0:
            GPIO.output(i.pin,on)
            i.on()

def dry_off():
    for i in (i for i in devices if isinstance(i,drycontact.DryContact)):
        GPIO.output(i.pin,off)
        i.off()

def save_devices(*args):
    for i in devices:
        i.write()

def update_devices(*args):
    for i in devices:
        i.update()

def pin_off(pin):
    GPIO.output(pin,off)


mau1=mau.Mau(8)
dry_contact=12
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
    all_pins=[i for i in range(2,28)]
    GPIO.setup(all_pins, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

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
            'heat_override':0,
            'short_duration':0
        }

        self.moli={
            'exhaust':off,
            'mau':off,
            'lights':off,
            'dry_contact':off,
            'maint_override':off,
            'maint_override_light':off
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
            dry_on()
            exfans_off()
            maufans_off()
            if self.moli['maint_override_light']==1:
                lights_on()
            elif self.moli['maint_override_light']==0:
                lights_off()
        else:

            dry_on()

            if self.moli['exhaust']==on or fan_switch_on():
                exfans_on()
                self.milo['exhaust']=on
            elif self.moli['exhaust']==off or not fan_switch_on():
                exfans_off()
                self.milo['exhaust']=off
            if self.moli['mau']==on or fan_switch_on():
                maufans_on()
                self.milo['mau']=on
            elif self.moli['mau']==off or not fan_switch_on():
                maufans_off()
                self.milo['mau']=off
            if heat_sensor_active():
                self.milo['heat_sensor']=on
                self.heat_trip()
            else:
                self.milo['heat_sensor']=off
            if self.moli['lights']==on or light_switch_on():
                lights_on()
                self.milo['lights']=on
            elif self.moli['lights']==off or not light_switch_on():
                lights_off()
                self.milo['lights']=off
    def heat_trip(self):
        self.sensor_target=time.time()+heat_sensor_timer
        self.aux_state.append('heat_sensor')
        print('heat trip')

    def heat_sensor(self):
            if self.sensor_target>=time.time():
                exfans_on()
                maufans_on()
                self.milo['exhaust']=on
                self.milo['mau']=on
                self.milo['heat_sensor']=on
                print('heat timer active')
            else:
                if self.moli['exhaust']==off and self.moli['mau']==off:
                    exfans_off()
                    maufans_off()
                self.milo['exhaust']=off
                self.milo['mau']=off
                self.milo['heat_sensor']=off
                clean_list(self.aux_state,'heat_sensor')


    def trouble(self):
        if heat_sensor_active() and not self.moli['exhaust']==1:
            self.milo['troubles']['heat_override']=1
        else:
            self.milo['troubles']['heat_override']=0

        if heat_sensor_timer==10:
            self.milo['troubles']['short_duration']=1
        else:
            self.milo['troubles']['short_duration']=0

    def fire(self):
        if not self.fired:
            exfans_on()
            maufans_off()
            lights_off()
            dry_off()
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
get_devices()
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