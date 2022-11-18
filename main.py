import os,json,time
import traceback
from kivy.config import Config

from exhaust import Exhaust
from mau import Mau
from light import Light
from drycontact import DryContact
from gas_valve import GasValve
from micro_switch import MicroSwitch
from switch_light import SwitchLight
from switch_fans import SwitchFans
from heat_sensor import HeatSensor

Config.set('kivy', 'keyboard_mode', 'systemanddock')
import kivy
import logic,lang_dict,pindex,general
if os.name == 'nt':
    import RPi_test.GPIO as GPIO
else:
    import RPi.GPIO as GPIO
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics import BorderImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.core.window import Window
from threading import Thread
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.screenmanager import FallOutTransition
from kivy.uix.screenmanager import RiseInTransition
from kivy.clock import Clock
from functools import partial
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color
from kivy.properties import ListProperty
import configparser
import preferences
from kivy.uix.settings import SettingsWithNoMenu
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.effectwidget import EffectWidget
from kivy.uix.effectwidget import HorizontalBlurEffect, VerticalBlurEffect
from kivy.uix.popup import Popup
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.graphics.transformation import Matrix
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.uix.carousel import Carousel
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.spinner import Spinner
from kivy.graphics import RoundedRectangle
from kivy.uix.progressbar import ProgressBar
from circle_progress_bar import CircularProgressBar


kivy.require('2.0.0')
current_language=lang_dict.english

if os.name == 'nt':
    preferences_path='hood_control.ini'
    generic_image=r'media\patrick-tomasso-GXXYkSwndP4-unsplash.jpg'
    language_image=r'media\language_icon-1.png'
    settings_icon=r'media\tiny gear.png'
    trouble_icon=r'media\trouble icon.png'
    trouble_icon_dull=r'media\trouble icon dull.png'
    logo=r'media\qt=q_95.png'
    report_current=r'media\report.jpg'
    report_original=r'media\report.jpg'
    left_arrow_image=r'media\left_arrow.png'
    right_arrow_image=r'media\right_arrow.png'
    stock_photo_test=r'media\download.jpeg'
    qr_link =r'media\frame.png'
    add_device_icon=r'media\icons8-edit-64.png'
    add_device_down=r'media\icons8-edit-64_down.png'
    delete_normal=r'media\delete_normal.png'
    delete_down=r'media\delete_down.png'
    reset_valve=r'media\redo.png'

if os.name == 'posix':
    preferences_path='/home/pi/Pi-ro-safe/hood_control.ini'
    Window.fullscreen = 'auto'
    generic_image=r'media/patrick-tomasso-GXXYkSwndP4-unsplash.jpg'
    language_image=r'media/language_icon-1.png'
    settings_icon=r'media/tiny gear.png'
    trouble_icon=r'media/trouble icon.png'
    trouble_icon_dull=r'media/trouble icon dull.png'
    logo=r'media/qt=q_95.png'
    report_current=r'media/report.jpg'
    report_original=r'media/report.jpg'
    left_arrow_image=r'media/left_arrow.png'
    right_arrow_image=r'media/right_arrow.png'
    stock_photo_test=r'media/download.jpeg'
    qr_link =r'media/frame.png'
    add_device_icon=r'media/icons8-edit-64.png'
    add_device_down=r'media/icons8-edit-64_down.png'
    delete_normal=r'media/delete_normal.png'
    delete_down=r'media/delete_down.png'
    reset_valve=r'media/redo.png'

class PinPop(Popup):
    def __init__(self,name, **kwargs):
        super().__init__(size_hint=(.8, .8),
        background = 'atlas://data/images/defaulttheme/button',
        title=current_language[f'{name}_overlay'],
        title_color=[0, 0, 0, 1],
        title_size='38',
        title_align='center',
        separator_color=[255/255, 0/255, 0/255, .5],
        **kwargs)
        self.widgets={}
        self.overlay_layout=FloatLayout()
        self.add_widget(self.overlay_layout)

class ScatterImage(Image,Scatter):

    def reset(self):
        self.transform= Matrix().scale(1, 1, 1)

    def on_transform_with_touch(self,touch):
        if self.scale<1:
            pass
        return super(ScatterImage, self).on_transform_with_touch(touch)

    def on_touch_up(self, touch):
        self.reset()
        return super(ScatterImage, self).on_touch_up(touch)

class OutlineScroll(ScrollView):
    def __init__(self, **kwargs):
        super(OutlineScroll,self).__init__(**kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
                    Color(0,0,0,.85)
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])

class IconButton(ButtonBehavior, Image):
    pass

class RoundedButton(Button):
    def __init__(self,**kwargs):
        super(RoundedButton,self).__init__(**kwargs)
        self.bg_color=kwargs["background_color"]
        self.background_color = (self.bg_color[0], self.bg_color[1], self.bg_color[2], 0)  # Invisible background color to regular button

        with self.canvas.before:
            if self.background_normal=="":
                self.shape_color = Color(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
            if self.background_down=="":
                self.shape_color = Color(self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape,state=self.color_swap)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size
    def color_swap(self,*args):
        if self.state=="normal":
            if self.background_normal=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]
        if self.state=="down":
            if self.background_down=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]

class RoundedToggleButton(ToggleButton):
    def __init__(self,**kwargs):
        super(RoundedToggleButton,self).__init__(**kwargs)
        self.bg_color=kwargs["background_color"]
        self.background_color = (self.bg_color[0], self.bg_color[1], self.bg_color[2], 0)  # Invisible background color to regular button

        with self.canvas.before:
            if self.background_normal=="":
                self.shape_color = Color(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
            if self.background_down=="":
                self.shape_color = Color(self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape,state=self.color_swap)
    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size
    def color_swap(self,*args):
        if self.state=="normal":
            if self.background_normal=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]
        if self.state=="down":
            if self.background_down=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]

class LayoutButton(FloatLayout,RoundedButton):
    pass

class trouble_template(Button):
    def __init__(self,trouble_tag,trouble_text='',link_text=None,ref_tag=None, **kwargs):
        if link_text == None:
            link_text=''
        else:
            link_text='\n'+str(link_text)
        super().__init__(text=f'''[size=24][b]{trouble_tag}[/b][/size]
        [size=18][i]{trouble_text}[/i][/size][size=30][color=#de2500][i][ref={ref_tag}]{link_text}[/ref][/i][/color][/size]''',
        markup=True,
        size_hint_y=None,
        size_hint_x=1,
        color = (0,0,0,1),
        background_down='',
        background_normal='',
        background_color=(245/250, 216/250, 41/250,.85),
        **kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        self.bind(state=self.color_swap)
        with self.canvas.before:
            Color(245/250, 216/250, 41/250,.85)
            self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def color_swap(self,*args):
        if self.state=="normal":
            self.background_color=(245/250, 216/250, 41/250,.85)
        if self.state=="down":
            self.background_color=((245/250)*.5, (216/250)*.5, (41/250)*.5,(.85)*.5)
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])

class ScrollItemTemplate(Button):
    def __init__(self,Item_tag,Item_text='',link_text=None,ref_tag=None,color=(245/250, 216/250, 41/250,.85),**kwargs):
        if link_text == None:
            link_text=''
        else:
            link_text='\n'+str(link_text)
        super().__init__(text=f'''[size=24][b]{Item_tag}[/b][/size]
        [size=18][i]{Item_text}[/i][/size][size=30][color=#de2500][i][ref={ref_tag}]{link_text}[/ref][/i][/color][/size]''',
        markup=True,
        size_hint_y=None,
        size_hint_x=1,
        color = (0,0,0,1),
        **kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
            Color(color[0],color[1],color[2],color[3])
            self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])

class DisplayLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
                    Color(255/255, 255/255, 255/255,1)
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])
    def update_text(self,text,*args):
        self.text=f'[size=25][color=#000000]{text}[/color][/size]'

class ExactLabel(Label):
    def __init__(self,label_color=(0,0,0,0), **kwargs):
        super().__init__(**kwargs)
        self.size_hint=(None,None)
        with self.canvas.before:
                    Color(label_color[0],label_color[1],label_color[2],label_color[3])
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        Clock.schedule_once(self.align_to_parent)

    def align_to_parent(self,*args):
        if self.parent:
            self.size=self.parent.size
    def update_rect(self, *args):
        self.size=self.texture_size
        self.rect.pos = self.pos
        self.rect.size = (self.texture_size[0], self.texture_size[1])

class EventpassGridLayout(GridLayout):
    pass

class ColorProgressBar(ProgressBar):
    def __init__(self, **kwargs):
        super(ColorProgressBar).__init__(**kwargs)

        with self.canvas.before:
            self.background=BorderImage

class ControlGrid(Screen):
    def quick_start(self,button):
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
            logic.fs.moli['exhaust']=1
            logic.fs.moli['mau']=1
        elif button.state == 'normal':
            print('fans off by switch')
            logic.fs.moli['exhaust']=0
            logic.fs.moli['mau']=0
    
    def lights_switch(self,button):
        if button.state == 'down':
            print('lights on by switch')
            logic.fs.moli['lights']=1
        elif button.state == 'normal':
            print('lights off by switch')
            logic.fs.moli['lights']=0

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1]=='m':
            print('sytem actuation')
            GPIO.micro=1
        elif keycode[1]=='c':
            print('sytem rearmed')
            GPIO.heatsensor=0
            GPIO.micro=0
        elif keycode[1]=='h':
            print('heat sensor activated')
            GPIO.heatsensor=1
            self.fans_switch(self.widgets['fans'])

    def _keyboard_closed(self):
        print("keyboard unbound")

    def __init__(self, **kwargs):
        super(ControlGrid, self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)
        self._keyboard=Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)


        quick=RoundedToggleButton(text=current_language['quick'],
                    size_hint =(.96, .45),
                    pos_hint = {'x':.02, 'y':.53},
                    background_down='',
                    background_color=(47/250, 247/250, 54/250,.85),
                    markup=True)
        self.widgets['quick']=quick
        quick.ref='quick'
        quick.bind(on_press=self.quick_start)

        fans=RoundedToggleButton(text=current_language['fans'],
                    size_hint =(.45, .35),
                    pos_hint = {'x':.03, 'y':.15},
                    background_down='',
                    background_color=(0/250, 159/250, 232/250,.85),
                    markup=True)
        self.widgets['fans']=fans
        fans.ref='fans'
        fans.bind(on_press=self.fans_switch)

        lights=RoundedToggleButton(text=current_language['lights'],
                    size_hint =(.45, .35),
                    pos_hint = {'x':.52, 'y':.15},
                    background_down='',
                    background_color=(245/250, 216/250, 41/250,.85),
                    markup=True)
        self.widgets['lights']=lights
        lights.ref='lights'
        lights.bind(on_press=self.lights_switch)

        settings_button=IconButton(source=settings_icon, allow_stretch=True, keep_ratio=True)
        settings_button.size_hint =(.10, .10)
        settings_button.pos_hint = {'x':.01, 'y':.02}
        self.widgets['settings_button']=settings_button
        settings_button.bind(on_press=self.open_settings)

        trouble_button=IconButton(source=trouble_icon_dull, allow_stretch=True, keep_ratio=True)
        trouble_button.size_hint =(.10, .10)
        trouble_button.pos_hint = {'x':.89, 'y':.02}
        self.widgets['trouble_button']=trouble_button
        trouble_button.bind(on_press=self.open_trouble)
        trouble_button.color=(1,1,1,.15)

        fs_logo=Image(source=logo,
                size_hint_x=.25,
                size_hint_y=.25,
                pos_hint = {'x':.2, 'center_y':.07})

        version_info=Label(text=current_language['version_info'],
                markup=True,
                pos_hint = {'x':.15, 'center_y':.07})
        version_info.ref='version_info'

        self.add_widget(bg_image)
        self.add_widget(quick)
        self.add_widget(fans)
        self.add_widget(lights)
        self.add_widget(settings_button)
        self.add_widget(trouble_button)
        self.add_widget(fs_logo)
        self.add_widget(version_info)

    def open_settings(self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='settings'
    def open_trouble(self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='trouble'

class ActuationScreen(Screen):

    def acknowledgement(self,button):
        print('actuation acknowledged')
        self.anime.cancel_all(self.widgets['alert'])
        self.widgets['alert'].background_color=(190/255, 10/255, 10/255,.9)
        self.widgets['alert'].text=current_language['alert_acknowledged']


    def reset_system(self,button):
            print('system reset')
            GPIO.heatsensor=0
            GPIO.micro=0
            self.widgets['alert'].text=current_language['alert']
            self.anime.cancel_all(self.widgets['alert'])
            self.pulse()
            self.parent.transition = SlideTransition(direction='right')

    def pulse(self):
            self.anime = Animation(background_color=(249/250, 0/250, 0/250,1), duration=1.5)+Animation(background_color=(249/250, 200/250, 200/250,1), duration=.2)
            self.anime.repeat = True
            self.anime.start(self.widgets['alert'])

    def __init__(self, **kwargs):
        super(ActuationScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        alert=RoundedButton(text=current_language['alert'],
                    size_hint =(.96, .45),
                    pos_hint = {'x':.02, 'y':.5},
                    background_normal='',
                    background_down='',
                    background_color=(190/250, 10/250, 10/250,.9),
                    markup=True)
        self.widgets['alert']=alert
        alert.ref='alert'

        acknowledge=RoundedButton(text=current_language['acknowledge'],
                    size_hint =(.45, .40),
                    pos_hint = {'x':.03, 'y':.05},
                    background_normal='',
                    background_down='',
                    background_color=(255/255, 121/255, 0/255,.99),
                    markup=True)
        self.widgets['acknowledge']=acknowledge
        acknowledge.ref='acknowledge'
        acknowledge.bind(on_release=self.acknowledgement)


        reset=RoundedButton(text=current_language['reset'],
                    size_hint =(.45, .40),
                    pos_hint = {'x':.52, 'y':.05},
                    background_normal='',
                    background_down='',
                    background_color=(255/255, 121/255, 0/255,.99),
                    markup=True)
        self.widgets['reset']=reset
        reset.ref='reset'
        reset.bind(on_release=self.reset_system)
        self.pulse()

        self.add_widget(bg_image)
        self.add_widget(alert)
        self.add_widget(acknowledge)
        self.add_widget(reset)

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['settings_back'],
                        size_hint =(.4, .25),
                        pos_hint = {'x':.02, 'y':.02},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='settings_back'
        back.bind(on_press=self.settings_back)

        logs=RoundedButton(text=current_language['logs'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['logs']=logs
        logs.ref='logs'
        logs.bind(on_release=self.device_logs)

        sys_report=RoundedButton(text=current_language['sys_report'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.56},
                        background_normal='',
                        background_color=(180/255, 10/255, 10/255,.9),
                        markup=True)
        self.widgets['sys_report']=sys_report
        sys_report.ref='sys_report'
        sys_report.bind(on_release=self.sys_report)

        preferences=RoundedButton(text=current_language['preferences'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.34},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['preferences']=preferences
        preferences.ref='preferences'
        preferences.bind(on_release=self.preferences_func)

        train=RoundedButton(text=current_language['train'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['train']=train
        train.ref='train'
        train.bind(on_release=self.train_func)

        language_icon=Image(
            source=language_image,
            pos_hint = {'center_x':.5, 'center_y':.53},
            size_hint =(1, 1))

        language=LayoutButton(text='',
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.56},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['language']=language
        language.bind(on_release=self.language_func)


        about=RoundedButton(text=current_language['about'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.34},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['about']=about
        about.ref='about'
        about.bind(on_release=self.about_func)

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/button',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=[255/255, 0/255, 0/255, .5]
        )
        self.widgets['overlay_menu']=overlay_menu

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        overlay_menu.add_widget(overlay_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(logs)
        self.add_widget(sys_report)
        self.add_widget(preferences)
        self.add_widget(train)
        language.add_widget(language_icon)
        self.add_widget(language)
        self.add_widget(about)
        
    def language_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.auto_dismiss=True
        overlay_menu.title=''
        overlay_menu.separator_height=0
        self.widgets['overlay_layout'].clear_widgets()

        english=RoundedButton(text="[size=30][b][color=#000000]  English [/color][/b][/size]",
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.9},
                        background_normal='',
                        background_color=(0/250, 70/250, 90/250,.9),
                        markup=True)
        self.widgets['english']=english
        

        spanish=RoundedButton(text="[size=30][b][color=#000000]  Español [/color][/b][/size]",
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.7},
                        background_normal='',
                        background_color=(0/250, 70/250, 90/250,.9),
                        markup=True)
        self.widgets['spanish']=spanish

        def english_func(button):
            global current_language
            config=App.get_running_app().config_
            current_language=lang_dict.english
            config.set('preferences','language','english')
            with open('hood_control.ini','w') as configfile:
                config.write(configfile)
            language_setter()
            self.widgets['overlay_menu'].dismiss()
        english.bind(on_release=english_func)

        def spanish_func(button):
            global current_language
            config=App.get_running_app().config_
            current_language=lang_dict.spanish
            config.set('preferences','language','spanish')
            with open('hood_control.ini','w') as configfile:
                config.write(configfile)
            language_setter()
            self.widgets['overlay_menu'].dismiss()
        spanish.bind(on_release=spanish_func)

        self.widgets['overlay_layout'].add_widget(english)
        self.widgets['overlay_layout'].add_widget(spanish)
        self.widgets['overlay_menu'].open()

    def about_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        about_text=Label(
            text=current_language['about_overlay_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},
        )
        self.widgets['about_text']=about_text
        about_text.ref='about_overlay_text'

        about_qr=Image(source=qr_link,
            allow_stretch=False,
            keep_ratio=True,
            size_hint =(.45,.45),
            pos_hint = {'x':.6, 'y':.58})

        about_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['about_back_button']=about_back_button
        about_back_button.ref='about_back'

        def about_overlay_close(button):
            self.widgets['overlay_menu'].dismiss()
        about_back_button.bind(on_press=about_overlay_close)

        self.widgets['overlay_layout'].add_widget(about_text)
        self.widgets['overlay_layout'].add_widget(about_qr)
        self.widgets['overlay_layout'].add_widget(about_back_button)
        self.widgets['overlay_menu'].open()

    def settings_back (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def device_logs (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='devices'
    def sys_report (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='report'
    def preferences_func (self,button):
        self.parent.transition = SlideTransition(direction='up')
        #App.get_running_app().open_settings()
        self.manager.current='preferences'
    def train_func (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='train'
    def language_func (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.language_overlay()
    def about_func (self,button):
        self.parent.transition = SlideTransition(direction='right')
        #self.manager.current='sys_report'
        self.about_overlay()

class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super(ReportScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['report_back'],
                    size_hint =(.4, .15),
                    pos_hint = {'x':.06, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_press=self.Report_back)

        back_main=RoundedButton(text=current_language['report_back_main'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.52, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_press=self.Report_back_main)

        date_label=DisplayLabel(
            text='',
            markup=True,
            size_hint =(.135, .045),
            pos_hint = {'center_x':.88, 'center_y':.865})
        self.widgets['date_label']=date_label

        report_image=Image(
            source=report_current
            )
        self.widgets['report_image']=report_image

        scroll_layout=RelativeLayout(
            size_hint_y=2.5,
            size_hint_x=.95
        )

        report_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=1,
            size_hint_x=.95,
            pos_hint = {'center_x':.525, 'center_y':.5}
            )
        self.widgets['report_scroll']=report_scroll

        report_scatter = Scatter(
            size_hint=(None, None),
            size=self.widgets['report_image'].size,
            pos_hint = {'center_x':.5, 'center_y':.55},
            do_rotation=False,
            scale_min=1,
            scale_max=3,
            auto_bring_to_front=False
            )
        self.widgets['report_scatter']=report_scatter

        self.add_widget(bg_image)
        scroll_layout.add_widget(report_image)
        scroll_layout.add_widget(date_label)
        report_scroll.add_widget(scroll_layout)
        self.add_widget(report_scroll)
        self.add_widget(back)
        self.add_widget(back_main)

    def on_pre_enter(self):
        self.date_setter()
    def Report_back (self,button):
        self.widgets['report_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='settings'
    def Report_back_main (self,button):
        self.widgets['report_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def date_setter(self):
        report_date=self.widgets['date_label']
        config=App.get_running_app().config_
        saved_date=config["documents"]["inspection_date"]
        report_date.text=f'[color=#000000]{saved_date}[/color]'

class DevicesScreen(Screen):
    def __init__(self, **kw):
        super(DevicesScreen,self).__init__(**kw)
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)
        self.widgets={}
        self.ud={}

        back=RoundedButton(text=current_language['report_back'],
                    size_hint =(.4, .15),
                    pos_hint = {'x':.06, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_press=self.devices_back)

        back_main=RoundedButton(text=current_language['report_back_main'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.52, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_press=self.devices_back_main)

        device_details=ScrollItemTemplate(current_language['no_device'],color=(120/255, 120/255, 120/255,.85))
        self.widgets['device_details']=device_details
        device_details.ref='no_device'

        device_layout=EventpassGridLayout(
            size_hint_y=None,
            size_hint_x=1,
            cols=1,
            padding=10,
            spacing=(1,5))
        self.widgets['device_layout']=device_layout
        device_layout.bind(minimum_height=device_layout.setter('height'))

        device_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=None,
            size_hint_x=1,
            size_hint =(.9, .80),
            pos_hint = {'center_x':.5, 'y':.18})
        self.widgets['device_scroll']=device_scroll

        overlay_menu=Popup(
            size_hint=(.98, .98),
            background = 'atlas://data/images/defaulttheme/button',
            title_color=[0, 0, 0, 1],
            title_size='30',
            title_align='center',
            separator_color=[255/255, 0/255, 0/255, .5])
        overlay_menu.bind(on_open=self.resize)
        self.widgets['overlay_menu']=overlay_menu

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        overlay_menu.add_widget(overlay_layout)

        device_layout.add_widget(device_details)
        device_scroll.add_widget(device_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(device_scroll)

    def resize(self,popup,*args):
        pass

    def info_overlay(self,device,open=True):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=f'{device.name} Details'
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        info_add_icon=IconButton(source=add_device_icon,
                        size_hint =(.15, .15),
                        pos_hint = {'x':.85, 'y':.95})
        self.widgets['info_add_icon']=info_add_icon
        info_add_icon.color=(1,1,1,.5)
        info_add_icon.bind(on_release=partial(self.info_add_icon_func,device))
        info_add_icon.bind(state=self.icon_change)

        delete_icon=IconButton(source=delete_normal,
                        size_hint =(.2, .2),
                        pos_hint = {'x':.0, 'y':.90})
        self.widgets['delete_icon']=delete_icon
        delete_icon.color=(1,1,1,.8)
        delete_icon.bind(on_release=partial(self.delete_icon_func,device))
        delete_icon.bind(state=self.delete_icon_change)


        info_type=ExactLabel(text=f"[size=18]Device Type:                    {device.type}[/size]",
                        color=(0,0,0,1),
                        pos_hint = {'x':.05, 'y':.9},
                        markup=True)

        info_pin=ExactLabel(text=f"[size=18]Device GPIO Pin:             {device.pin}[/size]",
                        color=(0,0,0,1),
                        pos_hint = {'x':.05, 'y':.8},
                        markup=True)

        info_run_time=ExactLabel(text=f"[size=18]Device Run Time:           {general.Convert_time(device.run_time)}[/size]",
                color=(0,0,0,1),
                pos_hint = {'x':.05, 'y':.7},
                markup=True)

        info_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .15),
                        pos_hint = {'x':.05, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['info_back_button']=info_back_button
        info_back_button.ref='about_back'
        info_back_button.bind(on_press=self.info_overlay_close)

        info_gv_reset=IconButton(source=reset_valve,
                        size_hint =(.12, .12),
                        pos_hint = {'x':.15, 'y':.98})
        info_gv_reset.color=(1,1,1,.8)
        self.widgets['info_gv_reset']=info_gv_reset
        info_gv_reset.bind(on_press=partial(self.info_gv_reset_func,device))

        # self.widgets['overlay_layout'].add_widget(info_text)
        self.widgets['overlay_layout'].add_widget(info_add_icon)
        self.widgets['overlay_layout'].add_widget(delete_icon)
        self.widgets['overlay_layout'].add_widget(info_type)
        self.widgets['overlay_layout'].add_widget(info_pin)
        self.widgets['overlay_layout'].add_widget(info_run_time)
        self.widgets['overlay_layout'].add_widget(info_back_button)
        if isinstance(device,GasValve) :
            self.widgets['overlay_layout'].add_widget(info_gv_reset)
        if open:
            self.widgets['overlay_menu'].open()

    def info_gv_reset_func(self,device,*args):
        device.latched=True

    def delete_device_overlay(self,device,open=True):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=f'Delete {device.name}?'
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        delete_back_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.9, .15),
                        pos_hint = {'x':.05, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['delete_back_button']=delete_back_button
        delete_back_button.ref='cancel_button'
        delete_back_button.bind(on_press=partial(self.delete_overlay_close,device))

        delete_confirm_button=RoundedButton(text="Delete",
                        size_hint =(.4, .10),
                        pos_hint = {'x':.3, 'y':.35},
                        background_normal='',
                        background_color=(180/255, 10/255, 10/255,.9),
                        markup=True)
        self.widgets['delete_confirm_button']=delete_confirm_button
        delete_confirm_button.ref='about_back'
        delete_confirm_button.bind(on_press=partial(self.create_clock,device),on_touch_up=self.delete_clock)

        delete_device_text=ExactLabel(text=f"""[size=18][color=#000000]Deleting device will remove all existing data and
terminate the associated GPIO pin usage immediately.
        
Only proceed if necessary; This action cannot be undone.[/color][/size]""",
                        color=(0,0,0,1),
                        pos_hint = {'x':.25, 'y':.7},
                        markup=True)

        # delete_progress=ProgressBar(
        #     max=1000,
        #     size_hint =(.30, .10),
        #     pos_hint = {'x':.35, 'y':.42},)
        # self.widgets['delete_progress']=delete_progress

        delete_progress=CircularProgressBar()
        delete_progress._widget_size=200
        delete_progress._progress_colour=(180/255, 10/255, 10/255,1)
        self.widgets['delete_progress']=delete_progress

        self.widgets['overlay_layout'].add_widget(delete_back_button)
        self.widgets['overlay_layout'].add_widget(delete_confirm_button)
        self.widgets['overlay_layout'].add_widget(delete_device_text)
        self.widgets['overlay_layout'].add_widget(delete_progress)
        if open:
            self.widgets['overlay_menu'].open()

    def progress_bar_update(self,dt,*args):
        self.widgets['delete_progress'].pos=self.widgets['delete_confirm_button'].last_touch.pos
        if not self.widgets['delete_progress'].parent:
            self.widgets['overlay_layout'].add_widget(self.widgets['delete_progress'])
        if self.widgets['delete_progress'].value >= 1000: # Checks to see if progress_bar.value has met 1000
            return False # Returning False schedule is canceled and won't repeat
        self.widgets['delete_progress'].value += 1000/2*dt # Updates progress_bar's progress

    def delete_overlay_close(self,device,button):
        self.info_overlay(device,False)

    def delete_device_confirm(self,device,*args):
        logic.devices.remove(device)
        logic.pin_off(device.pin)
        logic.available_pins.append(device.pin)
        logic.available_pins.sort()
        os.remove(rf"logs/devices/{device.name}.json")
        with open(rf"logs/devices/device_list.json","r+") as read_file:
            d_list=json.load(read_file)
            del d_list[device.name]
            read_file.seek(0)
            json.dump(d_list,read_file,indent=0)
            read_file.truncate()
        self.aggregate_devices()
        self.widgets['overlay_menu'].dismiss()

    def create_clock(self,device,*args):
        scheduled_delete=partial(self.delete_device_confirm,device)
        Clock.schedule_once(scheduled_delete, 2)
        self.ud['event'] = scheduled_delete
        Clock.schedule_interval(self.progress_bar_update,.0001)
        self.ud['event_bar'] = self.progress_bar_update

    def delete_clock(self,*args):
        if 'event' in self.ud:
            Clock.unschedule(self.ud['event'])
        if 'event_bar' in self.ud:
            Clock.unschedule(self.ud['event_bar'])
            self.widgets['delete_progress'].value=0
            self.widgets['overlay_layout'].remove_widget(self.widgets['delete_progress'])

    def info_overlay_close(self,button):
        self.widgets['overlay_menu'].dismiss()

    def info_add_icon_func(self,device,button):
        self.edit_device_overlay(device)

    def delete_icon_func(self,device,button):
        self.delete_device_overlay(device,open=False)

    def icon_change(self,button,state):
        if state=='down':
            button.source=add_device_down
        else:
            button.source=add_device_icon
    def delete_icon_change(self,button,state):
        if state=='down':
            button.source=delete_down
        else:
            button.source=delete_normal

    def new_device_overlay(self,open=True):
        class InfoShelf():
            def __init__(self) -> None:
                self.name='default'
                self.type='Exfan'
                self.pin=0
                self.color=(170/255, 0/255, 0/255,.85)
                self.run_time=0
                self.device_types={
                    "Exfan":"exhaust.Exhaust",
                    "MAU":"mau.Mau",
                    "Light":"light.Light",
                    "Dry":"drycontact.DryContact",
                    "GV":"gas_valve.GasValve",
                    "Micro":"micro_switch.MicroSwitch",
                    "Heat":"heat_sensor.HeatSensor",
                    "Light Switch":"switch_light.SwitchLight",
                    "Fans Switch":"switch_fans.SwitchFans"}
        current_device=InfoShelf()

        overlay_menu=self.widgets['overlay_menu']
        lay_out=self.widgets['overlay_layout']
        overlay_menu.title='Configure New Device'
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        new_device_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.05, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['new_device_back_button']=new_device_back_button
        new_device_back_button.ref='about_back'
        new_device_back_button.bind(on_press=self.new_device_overlay_close)

        new_device_save_button=RoundedButton(text=current_language['save'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.55, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['new_device_save_button']=new_device_save_button
        new_device_save_button.ref='save'
        new_device_save_button.bind(on_press=partial(self.new_device_save,current_device))

        get_name_label=ExactLabel(text="[size=18]Device Name:[/size]",
                        pos_hint = {'x':.05, 'y':.9},
                        color = (0,0,0,1),
                        markup=True)

        get_name=TextInput(multiline=False,
                        focus=False,
                        hint_text="Device name is required",
                        size_hint =(.5, .055),
                        pos_hint = {'x':.40, 'y':.9})
        get_name.bind(on_text_validate=partial(self.get_name_func,current_device))
        get_name.bind(text=partial(self.get_name_func,current_device))

        get_device_label=ExactLabel(text="[size=18]Device Type:[/size]",
                        pos_hint = {'x':.05, 'y':.8},
                        color = (0,0,0,1),
                        markup=True)

        get_device_type=Spinner(
                        text="Exfan",
                        values=("Exfan","MAU","Heat","Light","Dry","GV","Micro","Light Switch","Fans Switch"),
                        size_hint =(.5, .05),
                        pos_hint = {'x':.40, 'y':.8})
        get_device_type.bind(text=partial(self.get_device_type_func,current_device))

        get_device_pin_label=ExactLabel(text="[size=18]Device I/O Pin:[/size]",
                        pos_hint = {'x':.05, 'y':.7},
                        color = (0,0,0,1),
                        markup=True)

        get_device_pin=Spinner(
                        text="Select GPIO Pin; BCM Mode",
                        values=(str(i) for i in logic.available_pins),
                        size_hint =(.5, .05),
                        pos_hint = {'x':.40, 'y':.7})
        get_device_pin.bind(text=partial(self.get_device_pin_func,current_device))

        lay_out.add_widget(get_name_label)
        lay_out.add_widget(get_name)
        lay_out.add_widget(get_device_label)
        lay_out.add_widget(get_device_type)
        lay_out.add_widget(get_device_pin_label)
        lay_out.add_widget(get_device_pin)
        lay_out.add_widget(new_device_back_button)
        lay_out.add_widget(new_device_save_button)
        if open:
            overlay_menu.open()

    def new_device_overlay_close(self,button):
        self.widgets['overlay_menu'].dismiss()

    def new_device_save(self,current_device,button):
        if current_device.name=="default":
            print("main.new_device_save(): can not save device without name")
            return
        data={
            "device_name":current_device.name,
            "gpio_pin":current_device.pin,
            "run_time":current_device.run_time,
            "color":current_device.color}
        with open(rf"logs/devices/{current_device.name}.json","w+") as write_file:
            json.dump(data, write_file,indent=0)
        with open(rf"logs/devices/device_list.json","r+") as read_file:
            d_list=json.load(read_file)
            d_list[current_device.name]=current_device.device_types[current_device.type]
            read_file.seek(0)
            json.dump(d_list,read_file,indent=0)
            read_file.truncate()
        self.aggregate_devices()
        self.widgets['overlay_menu'].dismiss()

    def get_name_func(self,current_device,button,*args):
        current_device.name=button.text
    def get_device_type_func(self,current_device,button,value):
        current_device.type=value
        if value=="Exfan":
            current_device.color=(170/255, 0/255, 0/255,.85)
        elif value=="MAU":
            current_device.color=(0/255, 0/255, 170/255,.85)
        elif value=="Light":
            current_device.color=(170/255, 170/255, 0/255,.85)
        elif value=="Dry":
            current_device.color=(170/255, 85/255, 0/255,.85)
        elif value=="GV":
            current_device.color=(47/250, 247/250, 54/250,.85)
        elif value=="Micro":
            current_device.color=(255/255, 140/255, 25/255,.85)
        elif value=="Heat":
            current_device.color=(75/255, 0/255, 130/255,.85)
        elif value=="Light Switch":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Fans Switch":
            current_device.color=(0/255, 0/255, 0/255,.85)
    def get_device_pin_func(self,current_device,button,value):
        current_device.pin=int(value)

    def edit_device_overlay(self,device):
        class InfoShelf():
            def __init__(self,device) -> None:
                self.name=device.name
                if isinstance(device,Exhaust):
                    self.type="Exfan"
                elif isinstance(device,Mau):
                    self.type="MAU"
                elif isinstance(device,Light):
                    self.type="Light"
                elif isinstance(device,DryContact):
                    self.type="Dry"
                elif isinstance(device,GasValve):
                    self.type="GV"
                elif isinstance(device,MicroSwitch):
                    self.type="Micro"
                elif isinstance(device,HeatSensor):
                    self.type="Heat"
                elif isinstance(device,SwitchLight):
                    self.type="Light Switch"
                elif isinstance(device,SwitchFans):
                    self.type="Fans Switch"
                self.pin=device.pin
                self.color=device.color
                self.run_time=device.run_time
                self.device_types={
                    "Exfan":"exhaust.Exhaust",
                    "MAU":"mau.Mau",
                    "Light":"light.Light",
                    "Dry":"drycontact.DryContact",
                    "GV":"gas_valve.GasValve",
                    "Micro":"micro_switch.MicroSwitch",
                    "Heat":"heat_sensor.HeatSensor",
                    "Light Switch":"switch_light.SwitchLight",
                    "Fans Switch":"switch_fans.SwitchFans"}
        current_device=InfoShelf(device)

        overlay_menu=self.widgets['overlay_menu']
        lay_out=self.widgets['overlay_layout']
        overlay_menu.title='Edit Device Configuration'
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        edit_device_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.05, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['edit_device_back_button']=edit_device_back_button
        edit_device_back_button.ref='about_back'
        edit_device_back_button.bind(on_press=partial(self.edit_device_overlay_close,device))

        edit_device_save_button=RoundedButton(text=current_language['save'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.55, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['edit_device_save_button']=edit_device_save_button
        edit_device_save_button.ref='save'
        edit_device_save_button.bind(on_press=partial(self.edit_device_save,current_device,device))

        get_name_label=ExactLabel(text="[size=18]Device Name:[/size]",
                        pos_hint = {'x':.05, 'y':.9},
                        color = (0,0,0,1),
                        markup=True)

        get_name=TextInput(multiline=False,
                        focus=False,
                        text=f"{device.name}",
                        size_hint =(.5, .055),
                        pos_hint = {'x':.40, 'y':.9})
        get_name.bind(on_text_validate=partial(self.edit_name_func,current_device))
        get_name.bind(text=partial(self.edit_name_func,current_device))

        get_device_label=ExactLabel(text="[size=18]Device Type: (Locked)[/size]",
                        pos_hint = {'x':.05, 'y':.8},
                        color = (0,0,0,1),
                        markup=True)

        get_device_type=Spinner(
                        disabled=True,
                        text=current_device.type,
                        values=("Exfan","MAU","Heat","Light","Dry","Micro","Light Switch","Fans Switch"),
                        size_hint =(.5, .05),
                        pos_hint = {'x':.40, 'y':.8})
        get_device_type.bind(text=partial(self.edit_device_type_func,current_device))

        get_device_pin_label=ExactLabel(text="[size=18]Device I/O Pin:[/size]",
                        pos_hint = {'x':.05, 'y':.7},
                        color = (0,0,0,1),
                        markup=True)

        get_device_pin=Spinner(
                        text=str(device.pin),
                        values=(str(i) for i in logic.available_pins),
                        size_hint =(.5, .05),
                        pos_hint = {'x':.40, 'y':.7})
        get_device_pin.bind(text=partial(self.edit_device_pin_func,current_device))

        lay_out.add_widget(get_name_label)
        lay_out.add_widget(get_name)
        lay_out.add_widget(get_device_label)
        lay_out.add_widget(get_device_type)
        lay_out.add_widget(get_device_pin_label)
        lay_out.add_widget(get_device_pin)
        lay_out.add_widget(edit_device_back_button)
        lay_out.add_widget(edit_device_save_button)

    def edit_device_overlay_close(self,device,button):
        self.info_overlay(device,open=False)

    def edit_device_save(self,current_device,device,button):
        if current_device.name=="default":
            print("main.edit_device_save(): can not save device without name")
            return
        data={
            "device_name":current_device.name,
            "gpio_pin":current_device.pin,
            "run_time":current_device.run_time,
            "color":current_device.color}
        if device.name!=current_device.name:
            os.rename(rf"logs/devices/{device.name}.json",rf"logs/devices/{current_device.name}.json")
        with open(rf"logs/devices/{current_device.name}.json","w") as write_file:
            json.dump(data, write_file,indent=0)
        with open(rf"logs/devices/device_list.json","r+") as read_file:
            d_list=json.load(read_file)
            if device.name!=current_device.name:
                d_list[current_device.name]=d_list.pop(device.name)
            else:
                d_list[current_device.name]=current_device.device_types[current_device.type]
            read_file.seek(0)
            json.dump(d_list,read_file,indent=0)
            read_file.truncate()
        device.name=current_device.name
        if device.pin != current_device.pin:
            logic.available_pins.append(device.pin)
            logic.available_pins.remove(current_device.pin)
            logic.available_pins.sort()
            logic.pin_off(device.pin)
            device.pin=current_device.pin
        self.aggregate_devices()
        self.info_overlay(device,open=False)

    def edit_name_func(self,current_device,button,*args):
        current_device.name=button.text
    def edit_device_type_func(self,current_device,button,value):
        current_device.type=value
        if value=="Exfan":
            current_device.color=(170/255, 0/255, 0/255,.85)
        elif value=="MAU":
            current_device.color=(0/255, 0/255, 170/255,.85)
        elif value=="Light":
            current_device.color=(170/255, 170/255, 0/255,.85)
        elif value=="Dry":
            current_device.color=(170/255, 85/255, 0/255,.85)
        elif value=="GV":
            current_device.color=(47/250, 247/250, 54/250,.85)
        elif value=="Micro":
            current_device.color=(255/255, 140/255, 25/255,.85)
        elif value=="Heat":
            current_device.color=(75/255, 0/255, 130/255,.85)
        elif value=="Light Switch":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Fans Switch":
            current_device.color=(0/255, 0/255, 0/255,.85)
    def edit_device_pin_func(self,current_device,button,value):
        current_device.pin=int(value)


    def devices_back (self,button):
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='settings'
    def devices_back_main (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def info_func (self,device,button):
        self.info_overlay(device)

    def aggregate_devices(self):
        logic.get_devices()
        if logic.devices:
            self.widgets['device_layout'].clear_widgets()
            for i in logic.devices:
                device=ScrollItemTemplate(i.name,color=i.color)
                self.widgets['device_layout'].add_widget(device)
                device.bind(on_release=partial(self.info_func,i))
        else:
            print("main.py aggregate_devices(): no devices")
            self.widgets['device_layout'].clear_widgets()
            self.widgets['device_layout'].add_widget(self.widgets['device_details'])
        new_device=ScrollItemTemplate('Add Device +')
        self.widgets['device_layout'].add_widget(new_device)
        new_device.bind(on_release=self.new_device_func)

    def new_device_func(self,button):
        self.new_device_overlay()

    def on_pre_enter(self):
        self.aggregate_devices()

class TrainScreen(Screen):
    def __init__(self, **kw):
        super(TrainScreen,self).__init__(**kw)
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)
        self.widgets={}

        back=RoundedButton(text=current_language['report_back'],
                    size_hint =(.4, .15),
                    pos_hint = {'x':.06, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_press=self.train_back)

        back_main=RoundedButton(text=current_language['report_back_main'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.52, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_press=self.train_back_main)

        train_details=ScrollItemTemplate(current_language['no_train'],color=(120/255, 120/255, 120/255,.85))
        self.widgets['train_details']=train_details
        train_details.ref='no_train'

        train_layout=EventpassGridLayout(
            size_hint_y=None,
            size_hint_x=1,
            cols=1,
            padding=10,
            spacing=(1,5)
            )
        self.widgets['train_layout']=train_layout
        train_layout.bind(minimum_height=train_layout.setter('height'))

        train_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=None,
            size_hint_x=1,
            size_hint =(.9, .80),
            pos_hint = {'center_x':.5, 'y':.18}
            )
        self.widgets['train_scroll']=train_scroll

        train_layout.add_widget(train_details)
        train_scroll.add_widget(train_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(train_scroll)

    def train_back (self,button):
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='settings'
    def train_back_main (self,button):
            self.parent.transition = SlideTransition(direction='left')
            self.manager.current='main'

class PreferenceScreen(Screen):
    def __init__(self, **kwargs):
        super(PreferenceScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        self.ud={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)
        self.duration_flag=0

        back=RoundedButton(text=current_language['preferences_back'],
                        size_hint =(.4, .25),
                        pos_hint = {'x':.02, 'y':.02},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='preferences_back'
        back.bind(on_press=self.settings_back)

        back_main=RoundedButton(text=current_language['preferences_back_main'],
                        size_hint =(.48, .25),
                        pos_hint = {'x':.49, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_press=self.settings_back_main)

        heat_sensor=RoundedButton(text=current_language['heat_sensor'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['heat_sensor']=heat_sensor
        heat_sensor.ref='heat_sensor'
        heat_sensor.bind(on_release=self.heat_sensor_func)
        heat_sensor.bind(on_release=self.blur_screen)

        temp_1=RoundedButton(text="[size=40][b][color=#000000]  temp_1 [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.56},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['temp_1']=temp_1
        #temp_1.bind(on_release=self.sys_report_func)

        temp_2=RoundedButton(text="[size=40][b][color=#000000]  temp_2 [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.34},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['temp_2']=temp_2
        #preferences.bind(on_release=self.preferences_func)

        clean_mode=RoundedButton(text=current_language['clean_mode'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['clean_mode']=clean_mode
        clean_mode.ref='clean_mode'
        clean_mode.bind(on_release=self.clean_mode_func)

        commission=RoundedButton(text=current_language['commission'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.56},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['commission']=commission
        commission.ref='commission'
        commission.bind(on_release=self.commission_func)

        pins=RoundedButton(text=current_language['pins'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.34},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['pins']=pins
        pins.ref='pins'
        pins.bind(on_release=self.pins_func)

        self.blur = EffectWidget()

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/button',
            title=current_language['heat_overlay'],
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=[255/255, 0/255, 0/255, .5]
        )
        self.widgets['overlay_menu']=overlay_menu
        overlay_menu.ref='heat_overlay'

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout


        overlay_menu.add_widget(overlay_layout)
        self.blur.add_widget(bg_image)
        self.blur.add_widget(back)
        self.blur.add_widget(back_main)
        self.blur.add_widget(heat_sensor)
        self.blur.add_widget(temp_1)
        self.blur.add_widget(temp_2)
        self.blur.add_widget(clean_mode)
        self.blur.add_widget(commission)
        self.blur.add_widget(pins)
        self.add_widget(self.blur)

    def blur_screen(self,button):
        #self.blur.effects = [HorizontalBlurEffect(size=5.0),VerticalBlurEffect(size=5.0)]
        pass

    def unblur_screen(self,button):
        self.blur.effects = [HorizontalBlurEffect(size=0),VerticalBlurEffect(size=0)]

    def heat_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=current_language['heat_overlay']
        overlay_menu.separator_height=1
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        duration_1=RoundedButton(text=current_language['duration_1'],
                        size_hint =(.3, .50),
                        pos_hint = {'x':.02, 'y':.3},
                        background_normal='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['duration_1']=duration_1
        duration_1.ref='duration_1'

        duration_2=RoundedButton(text=current_language['duration_2'],
                        size_hint =(.3, .50),
                        pos_hint = {'x':.35, 'y':.3},
                        background_normal='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['duration_2']=duration_2
        duration_1.ref='duration_2'

        duration_3=RoundedButton(text=current_language['duration_3'],
                        size_hint =(.3, .50),
                        pos_hint = {'x':.68, 'y':.3},
                        background_normal='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['duration_3']=duration_3
        duration_1.ref='duration_3'

        def duration_1_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=300
            config.set('preferences','heat_timer','300')
            with open('hood_control.ini','w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_1.bind(on_release=duration_1_func)

        def duration_2_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=900
            config.set('preferences','heat_timer','900')
            with open('hood_control.ini','w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_2.bind(on_release=duration_2_func)

        def duration_3_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=1800
            config.set('preferences','heat_timer','1800')
            with open('hood_control.ini','w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_3.bind(on_release=duration_3_func)

        self.widgets['overlay_layout'].add_widget(duration_1)
        self.widgets['overlay_layout'].add_widget(duration_2)
        self.widgets['overlay_layout'].add_widget(duration_3)
        self.widgets['overlay_menu'].open()

    def maint_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        warning_text=Label(
            text=current_language['maint_overlay_warning_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},
        )
        self.widgets['warning_text']=warning_text
        warning_text.ref='maint_overlay_warning_text'

        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['continue_button']=continue_button
        continue_button.ref='continue_button'

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            self.override_overlay()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.widgets['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        self.widgets['overlay_layout'].add_widget(warning_text)
        self.widgets['overlay_layout'].add_widget(continue_button)
        self.widgets['overlay_layout'].add_widget(cancel_button)
        self.widgets['overlay_menu'].open()

    def override_overlay(self):
        logic.fs.moli['maint_override']=1
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=False
        self.widgets['overlay_layout'].clear_widgets()

        warning_text=Label(
            text=current_language['override_overlay_warning_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},
        )
        self.widgets['warning_text']=warning_text
        warning_text.ref='override_overlay_warning_text'

        disable_button=RoundedButton(text=current_language['disable_button'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['disable_button']=disable_button
        disable_button.ref='disable_button'

        light_button=RoundedToggleButton(text=current_language['lights'],
                        size_hint =(.2, .25),
                        pos_hint = {'x':.75, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['light_button']=light_button
        light_button.ref='lights'

        # disable_progress=ProgressBar(
        #     max=1000,
        #     size_hint =(.8, .10),
        #     pos_hint = {'x':.10, 'y':.27},)
        # self.widgets['disable_progress']=disable_progress

        disable_progress=CircularProgressBar()
        disable_progress._widget_size=200
        disable_progress._progress_colour=(255/255, 121/255, 0/255,1)
        self.widgets['disable_progress']=disable_progress

        def light_button_func(button):
            if logic.fs.moli['maint_override_light']==1:
                logic.fs.moli['maint_override_light']=0
            else:
                logic.fs.moli['maint_override_light']=1
        light_button.bind(on_press=light_button_func)

        def disable_button_func(button):
            logic.fs.moli['maint_override']=0
            self.widgets['overlay_menu'].dismiss()

        def progress_bar_update(dt,*args):
            self.widgets['disable_progress'].pos=self.widgets['disable_button'].last_touch.pos
            if not self.widgets['disable_progress'].parent:
                self.widgets['overlay_layout'].add_widget(self.widgets['disable_progress'])
            bar=App.get_running_app().context_screen.get_screen('preferences').widgets["disable_progress"]
            if bar.value >= 1000: # Checks to see if progress_bar.value has met 1000
                return False # Returning False schedule is canceled and won't repeat
            bar.value += 1000/3*dt#4.00 # Updates progress_bar's progress



        def create_clock(*args):
            Clock.schedule_once(disable_button_func, 3)
            self.ud['event'] = disable_button_func
            Clock.schedule_interval(progress_bar_update,.01)
            self.ud['event_bar'] = progress_bar_update

        def delete_clock(*args):
            bar=App.get_running_app().context_screen.get_screen('preferences').widgets["disable_progress"]
            if 'event' in self.ud:
                Clock.unschedule(self.ud['event'])
            if 'event_bar' in self.ud:
                self.widgets['overlay_layout'].remove_widget(disable_progress)
                Clock.unschedule(self.ud['event_bar'])
                bar.value=0

        disable_button.bind(
            on_press=create_clock,
            on_touch_up=delete_clock)

        self.widgets['overlay_layout'].add_widget(warning_text)
        self.widgets['overlay_layout'].add_widget(disable_button)
        self.widgets['overlay_layout'].add_widget(light_button)
        self.widgets['overlay_layout'].add_widget(disable_progress)

    def settings_back(self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='settings'
    def settings_back_main(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def heat_sensor_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.heat_overlay()
    def sys_report_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
    def preferences_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
    def clean_mode_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.maint_overlay()
        #self.manager.current='sys_report'
    def commission_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='documents'
    def pins_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='pin'
    def on_enter(self):
        if self.duration_flag:
            self.duration_flag=0
            self.heat_overlay()

class PinScreen(Screen):
    def __init__(self, **kwargs):
        super(PinScreen,self).__init__(**kwargs)
        self.root=App.get_running_app()
        self.date_flag=0
        self.cols = 2
        self.widgets={}
        self.popups=[]
        self.pin=''
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['pin_back'],
                    size_hint =(.4, .15),
                    pos_hint = {'x':.06, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='pin_back'
        back.bind(on_press=self.Pin_back)

        back_main=RoundedButton(text=current_language['pin_back_main'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.52, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='pin_back_main'
        back_main.bind(on_press=self.Pin_back_main)

        num_pad=RelativeLayout(size_hint =(.9, .65),
            pos_hint = {'center_x':.6, 'center_y':.4})
        self.widgets['num_pad']=num_pad

        one=RoundedButton(text="[size=35][b][color=#000000] 1 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.85},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['one']=one
        one.bind(on_release=self.one_func)

        two=RoundedButton(text="[size=35][b][color=#000000] 2 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.2, 'y':.85},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['two']=two
        two.bind(on_release=self.two_func)

        three=RoundedButton(text="[size=35][b][color=#000000] 3 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.4, 'y':.85},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['three']=three
        three.bind(on_release=self.three_func)

        four=RoundedButton(text="[size=35][b][color=#000000] 4 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.65},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['four']=four
        four.bind(on_release=self.four_func)

        five=RoundedButton(text="[size=35][b][color=#000000] 5 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.2, 'y':.65},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['five']=five
        five.bind(on_release=self.five_func)

        six=RoundedButton(text="[size=35][b][color=#000000] 6 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.4, 'y':.65},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['six']=six
        six.bind(on_release=self.six_func)

        seven=RoundedButton(text="[size=35][b][color=#000000] 7 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.45},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['seven']=seven
        seven.bind(on_release=self.seven_func)

        eight=RoundedButton(text="[size=35][b][color=#000000] 8 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.2, 'y':.45},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['eight']=eight
        eight.bind(on_release=self.eight_func)

        nine=RoundedButton(text="[size=35][b][color=#000000] 9 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.4, 'y':.45},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['nine']=nine
        nine.bind(on_release=self.nine_func)

        zero=RoundedButton(text="[size=35][b][color=#000000] 0 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.25},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['zero']=zero
        zero.bind(on_release=self.zero_func)

        backspace=RoundedButton(text="[size=35][b][color=#000000] <- [/color][/b][/size]",
            size_hint =(.35, .15),
            pos_hint = {'x':.2, 'y':.25},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['backspace']=backspace
        backspace.bind(on_release=self.backspace_func)

        enter=RoundedButton(text="[size=35][b][color=#000000] -> [/color][/b][/size]",
            size_hint =(.15, .75),
            pos_hint = {'x':.6, 'y':.25},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['enter']=enter
        enter.bind(on_release=self.enter_func)

        display=DisplayLabel(text=f'[size=25][color=#000000]{self.pin}[/color][/size]',
            size_hint =(.67, .10),
            pos_hint = {'x':.152, 'y':.77},
            valign='middle',
            halign='center',
            markup=True)
        self.widgets['display']=display

        reset_overlay=PinPop('system_reset')
        self.popups.append(reset_overlay)
        self.widgets['reset_overlay']=reset_overlay
        reset_overlay.ref='reset_overlay'
        reset_overlay.widgets['overlay_layout']=reset_overlay.overlay_layout

        reset_text=Label(
            text=current_language['reset_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},
        )
        self.widgets['reset_text']=reset_text
        reset_text.ref='reset_text'

        reset_confirm=RoundedButton(text=current_language['reset_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['reset_confirm']=reset_confirm
        reset_confirm.ref='reset_confirm'

        reset_cancel=RoundedButton(text=current_language['reset_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['reset_cancel']=reset_cancel
        reset_cancel.ref='reset_cancel'

        def reset_confirm_func(button):
            print(self.widgets['reset_overlay'].widgets['overlay_layout'].children )
            if os.name=='posix':
                os.system("sudo reboot")
        reset_confirm.bind(on_release=reset_confirm_func)

        def reset_cancel_func(button):
            self.widgets['reset_overlay'].dismiss()
        reset_cancel.bind(on_release=reset_cancel_func)

        date_overlay=PinPop('date')
        self.popups.append(date_overlay)
        self.widgets['date_overlay']=date_overlay
        date_overlay.ref='date_overlay'
        date_overlay.widgets['overlay_layout']=date_overlay.overlay_layout

        date_text=Label(
            text=current_language['date_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},
        )
        self.widgets['date_text']=date_text
        date_text.ref='date_text'

        date_confirm=RoundedButton(text=current_language['date_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['date_confirm']=date_confirm
        date_confirm.ref='date_confirm'

        date_cancel=RoundedButton(text=current_language['date_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['date_cancel']=date_cancel
        date_cancel.ref='date_cancel'

        def date_confirm_func(button):
            self.date_flag=1
            self.widgets['date_overlay'].dismiss()
        date_confirm.bind(on_release=date_confirm_func)

        def date_cancel_func(button):
            self.widgets['date_overlay'].dismiss()
        date_cancel.bind(on_release=date_cancel_func)
        
        heat_override_overlay=PinPop('heat_override')
        self.popups.append(heat_override_overlay)
        self.widgets['heat_override_overlay']=heat_override_overlay
        heat_override_overlay.ref='heat_overlay'
        heat_override_overlay.widgets['overlay_layout']=heat_override_overlay.overlay_layout

        heat_override_text=Label(
            text=current_language['heat_override_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},
        )
        self.widgets['heat_override_text']=heat_override_text
        heat_override_text.ref='heat_override_text'

        heat_override_confirm=RoundedButton(text=current_language['heat_override_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['heat_override_confirm']=heat_override_confirm
        heat_override_confirm.ref='heat_override_confirm'

        heat_override_cancel=RoundedButton(text=current_language['heat_override_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['heat_override_cancel']=heat_override_cancel
        heat_override_cancel.ref='heat_override_cancel'

        def heat_override_confirm_func(button):
            logic.heat_sensor_timer=10
            config=self.root.config_
            config.set('preferences','heat_timer','10')
            with open('hood_control.ini','w') as configfile:
                config.write(configfile)
            print(self.widgets['heat_override_overlay'].widgets['overlay_layout'].children )
            self.widgets['heat_override_overlay'].dismiss()
        heat_override_confirm.bind(on_release=heat_override_confirm_func)

        def heat_override_cancel_func(button):
            self.widgets['heat_override_overlay'].dismiss()
        heat_override_cancel.bind(on_release=heat_override_cancel_func)

        self.widgets['reset_overlay'].widgets['overlay_layout'].add_widget(reset_text)
        self.widgets['reset_overlay'].widgets['overlay_layout'].add_widget(reset_confirm)
        self.widgets['reset_overlay'].widgets['overlay_layout'].add_widget(reset_cancel)
        self.widgets['date_overlay'].widgets['overlay_layout'].add_widget(date_text)
        self.widgets['date_overlay'].widgets['overlay_layout'].add_widget(date_confirm)
        self.widgets['date_overlay'].widgets['overlay_layout'].add_widget(date_cancel)
        self.widgets['heat_override_overlay'].widgets['overlay_layout'].add_widget(heat_override_text)
        self.widgets['heat_override_overlay'].widgets['overlay_layout'].add_widget(heat_override_confirm)
        self.widgets['heat_override_overlay'].widgets['overlay_layout'].add_widget(heat_override_cancel)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        num_pad.add_widget(one)
        num_pad.add_widget(two)
        num_pad.add_widget(three)
        num_pad.add_widget(four)
        num_pad.add_widget(five)
        num_pad.add_widget(six)
        num_pad.add_widget(seven)
        num_pad.add_widget(eight)
        num_pad.add_widget(nine)
        num_pad.add_widget(zero)
        num_pad.add_widget(backspace)
        num_pad.add_widget(enter)
        self.add_widget(num_pad)
        self.add_widget(display)

    def Pin_back(self,button):
        self.pin=''
        self.widgets['display'].update_text(self.pin)
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def Pin_back_main(self,button):
        self.pin=''
        self.widgets['display'].update_text(self.pin)
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    def on_leave(self):
        self.pin=''
        self.date_flag=0
    def one_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='1'
        self.widgets['display'].update_text(self.pin)
    def two_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):   
            self.pin+='2'
        self.widgets['display'].update_text(self.pin)
    def three_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='3'
        self.widgets['display'].update_text(self.pin)
    def four_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='4'
        self.widgets['display'].update_text(self.pin)
    def five_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='5'
        self.widgets['display'].update_text(self.pin)
    def six_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='6'
        self.widgets['display'].update_text(self.pin)
    def seven_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='7'
        self.widgets['display'].update_text(self.pin)
    def eight_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='8'
        self.widgets['display'].update_text(self.pin)
    def nine_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='9'
        self.widgets['display'].update_text(self.pin)
    def zero_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='0'
        self.widgets['display'].update_text(self.pin)
    def backspace_func(self,button):
        if isinstance(button.last_touch,MouseMotionEvent):
            self.pin=self.pin[0:-1]
        self.widgets['display'].update_text(self.pin)
    def enter_func(self,button):
        if self.date_flag:
            self.date_flag=0
            config=self.root.config_
            month=self.pin[0:2]
            day=self.pin[2:4]
            year=self.pin[4:8]
            config.set('documents','inspection_date',f'{month}-{day}-{year}')
            with open('hood_control.ini','w') as configfile:
                config.write(configfile)
        elif hasattr(pindex.Pindex,f'p{self.pin}'):
            eval(f'pindex.Pindex.p{self.pin}(self)')
        self.pin=''
        self.widgets['display'].update_text(self.pin)

class DocumentScreen(Screen):
    def __init__(self, **kwargs):
        super(DocumentScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text="[size=50][b][color=#000000]  Back [/color][/b][/size]",
                    size_hint =(.4, .15),
                    pos_hint = {'x':.06, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_press=self.Report_back)

        back_main=RoundedButton(text="[size=50][b][color=#000000]  Close Menu [/color][/b][/size]",
                        size_hint =(.4, .15),
                        pos_hint = {'x':.52, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_press=self.Report_back_main)

        left_arrow=IconButton(source=left_arrow_image,
                        size_hint =(.4, .25),
                        pos_hint = {'x':-.1, 'center_y':.55})
        self.widgets['left_arrow']=left_arrow
        left_arrow.bind(on_press=self.left_arrow_func)

        right_arrow=IconButton(source=right_arrow_image,
                        size_hint =(.4, .25),
                        pos_hint = {'x':.7, 'center_y':.55})
        self.widgets['right_arrow']=right_arrow
        right_arrow.bind(on_press=self.right_arrow_func)

        report_scroll=ScrollView(
            bar_width=8,
            bar_margin=20,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=1,
            size_hint_x=1)
        self.widgets['report_scroll']=report_scroll

        report_image=IconButton(
            source=report_current,
            size_hint_y=2,
            size_hint_x=.95,
            pos_hint = {'center_x':.5, 'y':1})

        report_scroll2=ScrollView(
            bar_width=8,
            bar_margin=20,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=1,
            size_hint_x=1)
        self.widgets['report_scroll2']=report_scroll2

        report_image2=IconButton(
            source=report_original,
            size_hint_y=2,
            size_hint_x=.98)

        report_pages=Carousel(loop=True,
        scroll_distance=5000,
        scroll_timeout=0,
        size_hint =(1, .75),
        pos_hint = {'center_x':.5, 'center_y':.60}
        )
        self.widgets['report_pages']=report_pages

        stock_photo=Image(source=stock_photo_test)

        self.add_widget(bg_image)
        report_scroll.add_widget(report_image)
        report_scroll2.add_widget(report_image2)

        report_pages.add_widget(report_scroll)
        report_pages.add_widget(report_scroll2)
        report_pages.add_widget(stock_photo)
        self.add_widget(report_pages)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(left_arrow)
        self.add_widget(right_arrow)

    def Report_back (self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def Report_back_main (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    def left_arrow_func(self,*args):
            self.widgets['report_pages'].load_previous()
    def right_arrow_func(self,*args):
            self.widgets['report_pages'].load_next()

class TroubleScreen(Screen):
    def __init__(self, **kwargs):
        super(TroubleScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['trouble_back'],
                    size_hint =(.4, .15),
                    pos_hint = {'x':.02, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='trouble_back'
        back.bind(on_press=self.trouble_back)

        trouble_details=trouble_template(current_language['no_trouble'])
        self.widgets['trouble_details']=trouble_details
        trouble_details.ref='no_trouble'
        # trouble_details.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        # trouble_details.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))

        trouble_layout=EventpassGridLayout(
            size_hint_y=None,
            size_hint_x=1,
            cols=1,
            padding=10,
            spacing=(1,5)
            )
        self.widgets['trouble_layout']=trouble_layout
        trouble_layout.bind(minimum_height=trouble_layout.setter('height'))

        trouble_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=None,
            size_hint_x=1,
            size_hint =(.9, .80),
            pos_hint = {'center_x':.5, 'y':.18}
            )
        self.widgets['trouble_scroll']=trouble_scroll

        self.add_widget(bg_image)
        trouble_layout.add_widget(trouble_details)
        trouble_scroll.add_widget(trouble_layout)

        self.add_widget(trouble_scroll)
        self.add_widget(back)

    def trouble_back (self,button):
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='main'

def listen(app_object,*args):
    event_log=logic.fs.milo
    pass_flag=False
    if len(app_object.children)== 2:
        widgets=app_object.children[1].widgets
    elif len(app_object.children)== 1:
        widgets=app_object.children[0].widgets
    else:
        pass_flag=True
    if pass_flag:
        pass
    else:
        main_screen=app_object.get_screen('main')
    #exhaust
        if event_log['exhaust']==1:
            if main_screen.widgets['fans'].state=='down':
                main_screen.widgets['fans'].text=current_language['fans']
        elif event_log['exhaust']==0:
            if main_screen.widgets['fans'].state=='down':
                main_screen.widgets['fans'].text=current_language['fans']
    #mau
        if event_log['mau']==1:
            pass
    #lights
        if event_log['lights']==1:
            pass
    #heat sensor
        if event_log['heat_sensor']==1:
            if main_screen.widgets['fans'].state=='normal':
                main_screen.widgets['fans'].text = current_language['fans_heat']
        else:
            if main_screen.widgets['fans'].state=='normal':
                main_screen.widgets['fans'].text=current_language['fans']
    #dry contact
        if event_log['dry_contact']==1:
            pass
    #micro switch
        if event_log['micro_switch']==1:
            if app_object.current!='alert':
                app_object.transition = SlideTransition(direction='left')
                app_object.current='alert'
                app_object.get_screen('preferences').widgets['overlay_menu'].dismiss()
                app_object.get_screen('devices').widgets['overlay_menu'].dismiss()
                app_object.get_screen('settings').widgets['overlay_menu'].dismiss()
                for i in app_object.get_screen('pin').popups:
                    try:
                        i.dismiss()
                    except KeyError:
                        print("main.listen()#micro switch: pop.dismiss() error")

                logic.fs.moli['maint_override']=0
        elif event_log['micro_switch']==0:
            if app_object.current=='alert':
                app_object.get_screen('alert').reset_system(widgets['alert'])
                app_object.transition = SlideTransition(direction='right')
                app_object.current='main'
    #troubles
        trouble_log=event_log['troubles']
        troubles_screen=app_object.get_screen('trouble')
        trouble_display=troubles_screen.widgets['trouble_layout']

        if 1 in trouble_log.values():#if any troubles detected
            main_screen.widgets['trouble_button'].source=trouble_icon
            main_screen.widgets['trouble_button'].color=(1,1,1,1)
            if 'trouble_details' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['trouble_details'])
                del troubles_screen.widgets['trouble_details']
        else:#if no troubles detected
            if main_screen.widgets['trouble_button'].source==trouble_icon:
                main_screen.widgets['trouble_button'].source=trouble_icon_dull
                main_screen.widgets['trouble_button'].color=(1,1,1,.15)
            if 'trouble_details' not in troubles_screen.widgets:
                trouble_details=trouble_template(current_language['no_trouble'])
                troubles_screen.widgets['trouble_details']=trouble_details
                trouble_display.add_widget(trouble_details)
    #heat trouble
        if trouble_log['heat_override']==1:
            if app_object.current!='alert':
                main_screen.widgets['fans'].text =current_language['fans_heat']
                if 'heat_trouble' not in troubles_screen.widgets:
                    heat_trouble=trouble_template(current_language['heat_trouble_title'],
                    current_language['heat_trouble_body'],
                    link_text=current_language['heat_trouble_link'],ref_tag='fans')
                    heat_trouble.ref='heat_trouble'

                    def fan_switch(*args):
                        app_object.get_screen('main').widgets['fans'].state = 'down'
                        app_object.get_screen('main').fans_switch(app_object.get_screen('main').widgets['fans'])

                    heat_trouble.bind(on_release=fan_switch)
                    troubles_screen.widgets['heat_trouble']=heat_trouble
                    troubles_screen.widgets['heat_trouble'].bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    trouble_display.add_widget(heat_trouble)
        elif trouble_log['heat_override']==0:
            if 'heat_trouble' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['heat_trouble'])
                del troubles_screen.widgets['heat_trouble']
    #short duration trouble
        if trouble_log['short_duration']==1:
            if app_object.current!='alert':
                if 'duration_trouble' not in troubles_screen.widgets:
                    duration_trouble=trouble_template(current_language['duration_trouble_title'],
                    current_language['duration_trouble_body'],
                    link_text=current_language['duration_trouble_link'],ref_tag='duration_trouble')
                    duration_trouble.ref='duration_trouble'

                    def duration_overlay(*args):
                        app_object.get_screen('preferences').duration_flag=1
                        app_object.transition = SlideTransition(direction='up')
                        app_object.current='preferences'

                    duration_trouble.bind(on_release=duration_overlay)
                    troubles_screen.widgets['duration_trouble']=duration_trouble
                    troubles_screen.widgets['duration_trouble'].bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    trouble_display.add_widget(duration_trouble)
        elif trouble_log['short_duration']==0:
            if 'duration_trouble' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['duration_trouble'])
                del troubles_screen.widgets['duration_trouble']

    #gas valve trip trouble
        if trouble_log['gv_trip']==1:
            if app_object.current!='alert':
                if 'gasvalve_trouble' not in troubles_screen.widgets:
                    gasvalve_trouble=trouble_template(current_language['gasvalve_trouble_title'],
                    current_language['gasvalve_trouble_body'],
                    link_text=current_language['gasvalve_trouble_link'],ref_tag='gasvalve_trouble')
                    gasvalve_trouble.ref='gasvalve_trouble'

                    gasvalve_trouble.bind(on_release=logic.gv_reset_all)
                    troubles_screen.widgets['gasvalve_trouble']=gasvalve_trouble
                    troubles_screen.widgets['gasvalve_trouble'].bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    trouble_display.add_widget(gasvalve_trouble)
        elif trouble_log['gv_trip']==0:
            if 'gasvalve_trouble' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['gasvalve_trouble'])
                del troubles_screen.widgets['gasvalve_trouble']


class Hood_Control(App):
    def build(self):
        self.config_ = configparser.ConfigParser()
        self.config_.read(preferences_path)
        settings_setter(self.config_)
        Clock.schedule_once(partial(language_setter,config=self.config_))
        self.context_screen=ScreenManager()
        self.context_screen.add_widget(ControlGrid(name='main'))
        self.context_screen.add_widget(ActuationScreen(name='alert'))
        self.context_screen.add_widget(SettingsScreen(name='settings'))
        self.context_screen.add_widget(ReportScreen(name='report'))
        self.context_screen.add_widget(DevicesScreen(name='devices'))
        self.context_screen.add_widget(TrainScreen(name='train'))
        self.context_screen.add_widget(PreferenceScreen(name='preferences'))
        self.context_screen.add_widget(PinScreen(name='pin'))
        self.context_screen.add_widget(DocumentScreen(name='documents'))
        self.context_screen.add_widget(TroubleScreen(name='trouble'))
        listener_event=Clock.schedule_interval(partial(listen, self.context_screen),.75)
        device_update_event=Clock.schedule_interval(partial(logic.update_devices),.75)
        device_save_event=Clock.schedule_interval(partial(logic.save_devices),600)
        return self.context_screen

def settings_setter(config):
    heat_duration=config['preferences']['heat_timer']
    if heat_duration == '300':
        logic.heat_sensor_timer=300
    elif heat_duration == '900':
        logic.heat_sensor_timer=900
    elif heat_duration == '1800':
        logic.heat_sensor_timer=1800

def language_setter(*args,config=None):
    def widget_walker(widget,current_language):
        if hasattr(widget,'children'):
            for i in widget.children:
                widget_walker(i,current_language)
        if hasattr(widget,'text') and hasattr(widget,'ref'):
            if widget.text!='':
                widget.text=current_language[str(widget.ref)]
    if config:
        global current_language
        lang_pref=config['preferences']['language']
        current_language=eval(f'lang_dict.{lang_pref}')
    for i in App.get_running_app().root.screens:
        widget_walker(i,current_language)

logic_control = Thread(target=logic.logic,daemon=True)
logic_control.start()
try:
    Hood_Control().run()
except KeyboardInterrupt:
    print('Keyboard Inturrupt')
    traceback.print_exc()
except:
    traceback.print_exc()
finally:
    logic.save_devices()
    print("devices saved")
    logic.clean_exit()
    print("pins set as inputs")
    quit()