import kivy
import logic
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from threading import Thread
from queue import Queue

kivy.require('2.0.0')
#Window.fullscreen = 'auto'
datashare=Queue(0)

def clean_list(list,element):
    while True:
        try:
            list.remove(element)
        except ValueError:
            break

class ControlGrid(FloatLayout):
    def test_fire(self,button):
        if button.state == 'down':
            print('all on by switch')
            self.widgets['fans'].state='down'
            self.fans_switch(self.widgets['fans'])
            self.widgets['lights'].state='down'
            self.lights_switch(self.widgets['lights'])
        elif button.state == 'normal':
            print('all off by switch')
            self.widgets['fans'].state='normal'
            self.fans_switch(self.widgets['fans'])
            self.widgets['lights'].state='normal'
            self.lights_switch(self.widgets['lights'])

    def fans_switch(self,button):
        if button.state == 'down':
            print('fans on by switch')
            logic.fs.devices['exhaust']=1
            logic.fs.devices['mnau']=1
        elif button.state == 'normal':
            print('fans off by switch')
            logic.fs.devices['exhaust']=0
            logic.fs.devices['mnau']=0
    
    def lights_switch(self,button):
        if button.state == 'down':
            print('lights on by switch')
            logic.fs.devices['lights']=1
        elif button.state == 'normal':
            print('lights off by switch')
            logic.fs.devices['lights']=0


    def __init__(self, **kwargs):
        super(ControlGrid, self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source='media\istockphoto-1169326482-640x640.jpg', allow_stretch=True, keep_ratio=False)


        quick=ToggleButton(text="[size=50][b][color=#000000]  Hood [/color][/b][/size]",
                    size_hint =(.96, .45),
                    pos_hint = {'x':.02, 'y':.5},
                    background_down='',
                    background_color=(47/250, 247/250, 54/250,.85),
                    markup=True)
        self.widgets['quick']=quick
        quick.bind(on_press=self.test_fire)

        fans=ToggleButton(text="[size=32][b][color=#000000] Fans [/color][/b][/size]",
                    size_hint =(.45, .40),
                    pos_hint = {'x':.03, 'y':.05},
                    background_down='',
                    background_color=(0/250, 159/250, 232/250,.85),
                    markup=True)
        self.widgets['fans']=fans
        fans.bind(on_press=self.fans_switch)

        lights=ToggleButton(text="[size=32][b][color=#000000] Lights [/color][/b][/size]",
                    size_hint =(.45, .40),
                    pos_hint = {'x':.52, 'y':.05},
                    background_down='',
                    background_color=(245/250, 216/250, 41/250,.85),
                    markup=True)
        self.widgets['lights']=lights
        lights.bind(on_press=self.lights_switch)

        self.add_widget(bg_image)
        self.add_widget(quick)
        self.add_widget(fans)
        self.add_widget(lights)

    
class Hood_Control(App):
    def build(self):
        return ControlGrid()


logic_control = Thread(target=logic.logic,daemon=True)
logic_control.start()
try:
    Hood_Control().run()
except KeyboardInterrupt:
    print('Keyboard Inturrupt')
except Exception as e:
    print(e)
finally:
    logic.clean_exit()