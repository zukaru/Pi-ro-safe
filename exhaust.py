import os,time,json
if os.name == 'nt':
    import RPi_test.GPIO as GPIO
else:
    import RPi.GPIO as GPIO

class Exhaust():
    def __init__(self,name,pin) -> None:
        self.name=name
        self.pin=pin
        self.log={}
        self.unsafe_state_trigger=0
        self.state=0
        self.run_time=0
        self.last_state_change=0

    def write(self):
        data={
            "device_name":self.name,
            "gpio_pin":self.pin,
            "run_time":self.run_time}
        with open(rf"logs\devices\{self.name}.json","w") as write_file:
            json.dump(data, write_file)


    def read(self):
        with open(rf"logs\devices\{self.name}.json","r") as read_file:
            data = json.load(read_file)
        return data

    def on(self):
        if self.state==0:
            self.state=1
            self.last_state_change=time.time()

    def off(self):
        if self.state==1:
            self.state=0
            self.last_state_change=time.time()

    def update(self):
        pass