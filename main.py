import kivy
import logic
import RPi.GPIO as GPIO
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from threading import Thread
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import FallOutTransition
from kivy.uix.screenmanager import RiseInTransition

kivy.require('2.0.0')
#Window.fullscreen = 'auto'

class ControlGrid(Screen):
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
            logic.fs.devices['mau']=1
        elif button.state == 'normal':
            print('fans off by switch')
            logic.fs.devices['exhaust']=0
            logic.fs.devices['mau']=0
    
    def lights_switch(self,button):
        if button.state == 'down':
            print('lights on by switch')
            logic.fs.devices['lights']=1
        elif button.state == 'normal':
            print('lights off by switch')
            logic.fs.devices['lights']=0

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1]=='m':
            print('sytem actuation')
            GPIO.micro=1
            self.manager.current='alert'
            logic.fs.conditions['micro_switch']=1
        elif keycode[1]=='c':
            print('sytem rearmed')
            self.widgets['fans'].text = '[size=32][b][color=#000000] Fans [/color][/b][/size]'
            GPIO.heatsensor=0
            GPIO.micro=0
            self.manager.current='main'
        elif keycode[1]=='h':
            print('heat sensor activated')
            self.widgets['fans'].text = '[size=32][b][color=#000000]           Fans \n On by Heat Sensor [/color][/b][/size]'
            GPIO.heatsensor=1
            #self.widgets['fans'].state='down'
            self.fans_switch(self.widgets['fans'])

    def _keyboard_closed(self):
        print("keyboard unbound")

    def __init__(self, **kwargs):
        super(ControlGrid, self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source='source code\media\qt=q_95.png', allow_stretch=True, keep_ratio=False)
        self._keyboard=Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)


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

    def micro_actuation():
        ControlGrid.manager.current='alert'

class ActuationScreen(Screen):

    def acknowledgement(self,button):
        print('actuation acknowledged')


    def reset_system(self,button):
            print('system reset')
            self.manager.current='main'

    def __init__(self, **kwargs):
        super(ActuationScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source='source code\media\qt=q_95.png', allow_stretch=True, keep_ratio=False)

        alert=Button(text="[size=75][b][color=#000000]  System Activated [/color][/b][/size]",
                    size_hint =(.96, .45),
                    pos_hint = {'x':.02, 'y':.5},
                    background_normal='',
                    background_down='',
                    background_color=(190/250, 10/250, 10/250,.9),
                    markup=True)
        self.widgets['alert']=alert

        acknowledge=Button(text="[size=32][b][color=#000000] Acknowledge [/color][/b][/size]",
                    size_hint =(.45, .40),
                    pos_hint = {'x':.03, 'y':.05},
                    background_normal='',
                    background_down='',
                    background_color=(217/250, 94/250, 10/250,.99),
                    markup=True)
        self.widgets['acknowledge']=acknowledge
        acknowledge.bind(on_release=self.acknowledgement)


        reset=Button(text="[size=32][b][color=#000000] Reset [/color][/b][/size]",
                    size_hint =(.45, .40),
                    pos_hint = {'x':.52, 'y':.05},
                    background_normal='',
                    background_down='',
                    background_color=(217/250, 94/250, 1/250,.99),
                    markup=True)
        self.widgets['reset']=reset
        reset.bind(on_release=self.reset_system)

        def pulse():
            self.anime = Animation(background_color=(249/250, 0/250, 0/250,1), duration=1.5)+Animation(background_color=(249/250, 200/250, 200/250,1), duration=.2)
            self.anime.repeat = True
            self.anime.start(alert)
        pulse()

        self.add_widget(bg_image)
        self.add_widget(alert)
        self.add_widget(acknowledge)
        self.add_widget(reset)


class Hood_Control(App):
    def build(self):
        context_screen=ScreenManager()#transition=FallOutTransition()
        context_screen.add_widget(ControlGrid(name='main'))
        context_screen.add_widget(ActuationScreen(name='alert'))
        return context_screen

logic_control = Thread(target=logic.logic,daemon=True)
logic_control.start()
try:
    Hood_Control().run()
except KeyboardInterrupt:
    print('Keyboard Inturrupt')
# except Exception as e:
#     print(e)
finally:
    logic.clean_exit()