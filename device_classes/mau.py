import os,time,json
import os.path

class Mau():
    color=(0/255, 0/255, 0/255,.85)
    def __init__(self,name="default",pin=0,color=(0/255, 0/255, 0/255,.85)) -> None:
        self.name=name
        self.type='Makeup Air Fan'
        self.pin=pin
        self.mode="out"
        self.color=color
        self.log={}
        self.unsafe_state_trigger=0
        self.state=0
        self.run_time=0
        self.last_state_change=time.time()
        self.initialize()

    def write(self):
        data={
            "device_name":self.name,
            "gpio_pin":self.pin,
            "run_time":self.run_time,
            "color":self.color}
        with open(rf"logs/devices/{self.name}.json","w") as write_file:
            json.dump(data, write_file,indent=0)

    def initialize(self):
        data=self.read()
        if data:
            self.name=data["device_name"]
            self.pin=int(data["gpio_pin"])
            self.run_time=float(data["run_time"])
            self.color=data["color"]

    def read(self):
        try:
            with open(rf"logs/devices/{self.name}.json","r") as read_file:
                data = json.load(read_file)
            return data
        except FileNotFoundError:
            return None

    def on(self):
        if self.state==0:
            self.state=1
            self.last_state_change=time.time()

    def off(self):
        if self.state==1:
            self.state=0
            self.last_state_change=time.time()

    def update(self,*args):
        now=time.time()
        if self.state==1:
            self.run_time+=now-self.last_state_change
            self.last_state_change=now