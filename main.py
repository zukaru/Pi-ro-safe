import os
import traceback
import kivy
import logic
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

kivy.require('2.0.0')
    
if os.name == 'nt':
    preferences_path='hood_control.ini'
    generic_image=r'media\lit_hood.jpg'
    settings_icon=r'media\tiny gear.png'
    trouble_icon=r'media\trouble icon.png'
    trouble_icon_dull=r'media\trouble icon dull.png'
    logo=r'media\qt=q_95.png'
    report_current=r'media\report.jpg'
    report_original=r'media\report.jpg'

if os.name == 'posix':
    preferences_path='/home/pi/Desktop/Pi-ro-safe/hood_control.ini'
    Window.fullscreen = 'auto'
    generic_image=r'media/lit_hood.jpg'
    settings_icon=r'media/tiny gear.png'
    trouble_icon=r'media/trouble icon.png'
    trouble_icon_dull=r'media/trouble icon dull.png'
    logo=r'media/qt=q_95.png'
    report_current=r'media/report.jpg'
    report_original=r'media/report.jpg'

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

class trouble_template(Label):
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
        **kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
                    Color(245/250, 216/250, 41/250,.85)
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])

class EventpassGridLayout(GridLayout):
    pass

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


        quick=ToggleButton(text="[size=50][b][color=#000000]  Fans+Lights [/color][/b][/size]",
                    size_hint =(.96, .45),
                    pos_hint = {'x':.02, 'y':.53},
                    background_down='',
                    background_color=(47/250, 247/250, 54/250,.85),
                    markup=True)
        self.widgets['quick']=quick
        quick.bind(on_press=self.quick_start)

        fans=ToggleButton(text="[size=32][b][color=#000000] Fans [/color][/b][/size]",
                    size_hint =(.45, .35),
                    pos_hint = {'x':.03, 'y':.15},
                    background_down='',
                    background_color=(0/250, 159/250, 232/250,.85),
                    markup=True)
        self.widgets['fans']=fans
        fans.bind(on_press=self.fans_switch)

        lights=ToggleButton(text="[size=32][b][color=#000000] Lights [/color][/b][/size]",
                    size_hint =(.45, .35),
                    pos_hint = {'x':.52, 'y':.15},
                    background_down='',
                    background_color=(245/250, 216/250, 41/250,.85),
                    markup=True)
        self.widgets['lights']=lights
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

        version_info=Label(text='[size=22][color=#000000][i]-Version 1.0.0-[/i][/color][/size]',
                markup=True,
                pos_hint = {'x':.15, 'center_y':.07})

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
        self.widgets['alert'].text="[size=32][b][color=#000000]System Activated\n       -Fire Safe-\n   270-761-0637 [/color][/b][/size]"


    def reset_system(self,button):
            print('system reset')
            GPIO.heatsensor=0
            GPIO.micro=0
            self.widgets['alert'].text="[size=75][b][color=#000000]  System Activated [/color][/b][/size]"
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
                    background_color=(255/255, 121/255, 0/255,.99),
                    markup=True)
        self.widgets['acknowledge']=acknowledge
        acknowledge.bind(on_release=self.acknowledgement)


        reset=Button(text="[size=32][b][color=#000000] Reset [/color][/b][/size]",
                    size_hint =(.45, .40),
                    pos_hint = {'x':.52, 'y':.05},
                    background_normal='',
                    background_down='',
                    background_color=(255/255, 121/255, 0/255,.99),
                    markup=True)
        self.widgets['reset']=reset
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

        back=Button(text="[size=50][b][color=#000000]  Back [/color][/b][/size]",
                        size_hint =(.4, .25),
                        pos_hint = {'x':.02, 'y':.02},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['back']=back
        back.bind(on_press=self.settings_back)

        logs=Button(text="[size=40][b][color=#000000]  Device Logs [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['logs']=logs
        logs.bind(on_release=self.device_logs)

        sys_report=Button(text="[size=40][b][color=#000000]  System Report [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.56},
                        background_normal='',
                        background_color=(180/255, 10/255, 10/255,.9),
                        markup=True)
        self.widgets['sys_report']=sys_report
        sys_report.bind(on_release=self.sys_report)

        preferences=Button(text="[size=40][b][color=#000000]  Settings [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.34},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['preferences']=preferences
        preferences.bind(on_release=self.preferences_func)

        train=Button(text="[size=40][b][color=#000000]  Training [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['train']=train
        train.bind(on_release=self.train_func)

        blank=Button(text="[size=40][b][color=#000000][/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.56},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['blank']=blank
        #qr.bind(on_release=self.qr_func)

        about=Button(text="[size=40][b][color=#000000]  About [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.34},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['about']=about
        about.bind(on_release=self.about_func)

        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(logs)
        self.add_widget(sys_report)
        self.add_widget(preferences)
        self.add_widget(train)
        self.add_widget(blank)
        self.add_widget(about)
        
    def settings_back (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def device_logs (self,button):
        self.parent.transition = SlideTransition(direction='down')
        #self.manager.current='logs'
    def sys_report (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='report'
    def preferences_func (self,button):
        self.parent.transition = SlideTransition(direction='up')
        #App.get_running_app().open_settings()
        self.manager.current='preferences'
    def train_func (self,button):
        self.parent.transition = SlideTransition(direction='down')
        #self.manager.current='sys_report'
    def blank_func (self,button):
        self.parent.transition = SlideTransition(direction='down')
        #self.manager.current='sys_report'
    def about_func (self,button):
        self.parent.transition = SlideTransition(direction='right')
        #self.manager.current='sys_report'

class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super(ReportScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=Button(text="[size=50][b][color=#000000]  Back [/color][/b][/size]",
                    size_hint =(.4, .15),
                    pos_hint = {'x':.06, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.bind(on_press=self.Report_back)

        back_main=Button(text="[size=50][b][color=#000000]  Close Menu [/color][/b][/size]",
                        size_hint =(.4, .15),
                        pos_hint = {'x':.52, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.bind(on_press=self.Report_back_main)

        report_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=None,
            size_hint_x=1)
        self.widgets['report_scroll']=report_scroll

        report_image=Image(
            source=report_current,
            size_hint_y=2,
            size_hint_x=.95,
            pos_hint = {'center_x':.5, 'y':1})

        report_scroll2=OutlineScroll(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=None,
            size_hint_x=1)
        self.widgets['report_scroll2']=report_scroll2

        report_image2=Image(
            source=report_original,
            size_hint_y=2,
            size_hint_x=.98)
        # report_image2.bind(on_touch_down=self.switch_page)

        # report_pages=PageLayout(
        #     size_hint =(1, .80),
        #     pos_hint = {'center_x':.5, 'y':.18},
        #     border=50,
        #     swipe_threshold =-1)
        # self.widgets['report_pages']=report_pages
        report_scatter = Scatter(do_rotation=False, do_scale=False,do_translation_y=False)
        report_scatter.add_widget(report_image)

        self.add_widget(bg_image)
        report_scroll.add_widget(report_scatter)
        report_scroll2.add_widget(report_image2)

        self.add_widget(report_scroll)
        # report_pages.add_widget(report_scroll)
        # report_pages.add_widget(report_scroll2)
        # self.add_widget(report_pages)
        self.add_widget(back)
        self.add_widget(back_main)

    def Report_back (self,button):
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='settings'
    def Report_back_main (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def switch_page(self,*args):
        self.widgets['report_pages'].page=0

class PreferenceScreen(Screen):
    def __init__(self, **kwargs):
        super(PreferenceScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=Button(text="[size=50][b][color=#000000]  Back [/color][/b][/size]",
                        size_hint =(.4, .25),
                        pos_hint = {'x':.02, 'y':.02},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['back']=back
        back.bind(on_press=self.settings_back)

        back_main=Button(text="[size=50][b][color=#000000]  Close Menu [/color][/b][/size]",
                        size_hint =(.48, .25),
                        pos_hint = {'x':.49, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.bind(on_press=self.settings_back_main)

        heat_sensor=Button(text="[size=40][b][color=#000000]  Heat Sensor [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['heat_sensor']=heat_sensor
        heat_sensor.bind(on_release=self.heat_sensor_func)
        heat_sensor.bind(on_release=self.blur_screen)

        temp_1=Button(text="[size=40][b][color=#000000]  temp_1 [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.56},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['temp_1']=temp_1
        #temp_1.bind(on_release=self.sys_report_func)

        temp_2=Button(text="[size=40][b][color=#000000]  temp_2 [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.34},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['temp_2']=temp_2
        #preferences.bind(on_release=self.preferences_func)

        clean_mode=Button(text="[size=32][b][color=#000000]  Maint. Override [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['clean_mode']=clean_mode
        clean_mode.bind(on_release=self.clean_mode_func)

        temp_3=Button(text="[size=40][b][color=#000000]  temp_3 [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.56},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['temp_3']=temp_3
        #qr.bind(on_release=self.qr_func)

        temp_4=Button(text="[size=40][b][color=#000000]  temp_4 [/color][/b][/size]",
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.34},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['temp_4']=temp_4
        #about.bind(on_release=self.about_func)

        self.blur = EffectWidget()

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/button',
            title='Heat-Sensor Override Duration',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=[255/255, 0/255, 0/255, .5]
        )
        self.widgets['overlay_menu']=overlay_menu

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
        self.blur.add_widget(temp_3)
        self.blur.add_widget(temp_4)
        self.add_widget(self.blur)

    def blur_screen(self,button):
        pass
        #self.blur.effects = [HorizontalBlurEffect(size=5.0),VerticalBlurEffect(size=5.0)]
    def unblur_screen(self,button):
        self.blur.effects = [HorizontalBlurEffect(size=0),VerticalBlurEffect(size=0)]

    def heat_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title='Heat-Sensor Override Duration'
        overlay_menu.separator_height=1
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        duration_1=Button(text="[size=30][b][color=#000000]  10 Seconds [/color][/b][/size]",
                        size_hint =(.3, .50),
                        pos_hint = {'x':.02, 'y':.3},
                        background_normal='',
                        background_color=(0/250, 70/250, 90/250,.9),
                        markup=True)
        self.widgets['duration_1']=duration_1

        duration_2=Button(text="[size=30][b][color=#000000]  5 Minutes [/color][/b][/size]",
                        size_hint =(.3, .50),
                        pos_hint = {'x':.35, 'y':.3},
                        background_normal='',
                        background_color=(0/250, 70/250, 90/250,.9),
                        markup=True)
        self.widgets['duration_2']=duration_2

        duration_3=Button(text="[size=30][b][color=#000000]  10 Minutes [/color][/b][/size]",
                        size_hint =(.3, .50),
                        pos_hint = {'x':.68, 'y':.3},
                        background_normal='',
                        background_color=(0/250, 70/250, 90/250,.9),
                        markup=True)
        self.widgets['duration_3']=duration_3

        def duration_1_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=10
            config.set('preferences','heat_timer','10')
            with open('hood_control.ini','w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_1.bind(on_release=duration_1_func)

        def duration_2_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=300
            config.set('preferences','heat_timer','300')
            with open('hood_control.ini','w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_2.bind(on_release=duration_2_func)

        def duration_3_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=600
            config.set('preferences','heat_timer','600')
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
            text="""[size=30][color=#000000]Maintenance Override disables heat 
sensors allowing neccessary maintenance 
to take place safely.
You will be locked on this screen untill
override is canceled.

Disable all fans?
  [/color][/size]""",
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},
        )
        self.widgets['warning_text']=warning_text

        continue_button=Button(text="[size=30][b][color=#000000]  Continue [/color][/b][/size]",
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['continue_button']=continue_button

        cancel_button=Button(text="[size=30][b][color=#000000]  Cancel [/color][/b][/size]",
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['cancel_button']=cancel_button

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
            text="""[size=30][color=#000000]Maintenance Override active.
All fans currently disabled.
Disable override by holding down 
DISABLE for 3 seconds.
  [/color][/size]""",
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},
        )
        self.widgets['warning_text']=warning_text

        disable_button=Button(text="[size=30][b][color=#000000]  DISABLE [/color][/b][/size]",
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['disable_button']=disable_button

        def disable_button_func(button):
            logic.fs.moli['maint_override']=0
            self.widgets['overlay_menu'].dismiss()

        def create_clock(widget, touch, *args):
            Clock.schedule_once(disable_button_func, 3)
            touch.ud['event'] = disable_button_func

        def delete_clock(widget, touch, *args):
            if 'event' in touch.ud:
                Clock.unschedule(touch.ud['event'])

        disable_button.bind(
            on_touch_down=create_clock,
            on_touch_up=delete_clock)

        self.widgets['overlay_layout'].add_widget(warning_text)
        self.widgets['overlay_layout'].add_widget(disable_button)

    def settings_back (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='settings'
    def settings_back_main (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def heat_sensor_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.heat_overlay()
    def sys_report_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
    def preferences_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
    def clean_mode_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.maint_overlay()
        #self.manager.current='sys_report'
    def qr_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
        #self.manager.current='sys_report'
    def about_func (self,button):
        self.parent.transition = SlideTransition(direction='left')

class TroubleScreen(Screen):
    def __init__(self, **kwargs):
        super(TroubleScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=Button(text="[size=50][b][color=#000000]  Back [/color][/b][/size]",
                    size_hint =(.4, .15),
                    pos_hint = {'x':.02, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.bind(on_press=self.trouble_back)

        trouble_details=trouble_template('-No active troubles detected-')
        self.widgets['trouble_details']=trouble_details
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
                main_screen.widgets['fans'].text='[size=32][b][color=#000000] Fans [/color][/b][/size]'
        elif event_log['exhaust']==0:
            if main_screen.widgets['fans'].state=='down':
                main_screen.widgets['fans'].text='[size=32][b][color=#000000] Fans [/color][/b][/size]'
    #mau
        if event_log['mau']==1:
            pass
    #lights
        if event_log['lights']==1:
            pass
    #heat sensor
        if event_log['heat_sensor']==1:
            if main_screen.widgets['fans'].state=='normal':
                main_screen.widgets['fans'].text = '[size=32][b][color=#000000]           Fans \n On by Heat Sensor [/color][/b][/size]'
        else:
            if main_screen.widgets['fans'].state=='normal':
                main_screen.widgets['fans'].text='[size=32][b][color=#000000] Fans [/color][/b][/size]'
    #dry contact
        if event_log['dry_contact']==1:
            pass
    #micro switch
        if event_log['micro_switch']==1:
            if app_object.current!='alert':
                app_object.transition = SlideTransition(direction='left')
                app_object.current='alert'
                app_object.get_screen('preferences').widgets['overlay_menu'].dismiss()
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
                trouble_details=trouble_template('-No active troubles detected-')
                troubles_screen.widgets['trouble_details']=trouble_details
                trouble_display.add_widget(trouble_details)
    #heat trouble
        if trouble_log['heat_override']==1:
            if app_object.current!='alert':
                main_screen.widgets['fans'].text = '[size=32][b][color=#000000]           Fans \n On by Heat Sensor [/color][/b][/size]'
                if 'heat_trouble' not in troubles_screen.widgets:
                    heat_trouble=trouble_template('                        -Heat Sensor-',
                    'Unsafe temps detected in hood; fan override activated',
                    link_text='                    Turn on fans',ref_tag='fans')

                    def fan_switch(a,b):
                        app_object.get_screen('main').widgets['fans'].state = 'down'
                        app_object.get_screen('main').fans_switch(app_object.get_screen('main').widgets['fans'])

                    heat_trouble.bind(on_ref_press=fan_switch)
                    troubles_screen.widgets['heat_trouble']=heat_trouble
                    troubles_screen.widgets['heat_trouble'].bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    trouble_display.add_widget(heat_trouble)
        elif trouble_log['heat_override']==0:
            if 'heat_trouble' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['heat_trouble'])
                del troubles_screen.widgets['heat_trouble']


class Hood_Control(App):
    def build(self):
        self.config_ = configparser.ConfigParser()
        self.config_.read(preferences_path)
        settings_setter(self.config_)
        self.context_screen=ScreenManager()
        self.context_screen.add_widget(ControlGrid(name='main'))
        self.context_screen.add_widget(ActuationScreen(name='alert'))
        self.context_screen.add_widget(SettingsScreen(name='settings'))
        self.context_screen.add_widget(ReportScreen(name='report'))
        self.context_screen.add_widget(PreferenceScreen(name='preferences'))
        self.context_screen.add_widget(TroubleScreen(name='trouble'))
        listener_event=Clock.schedule_interval(partial(listen, self.context_screen),.75)
        return self.context_screen


def settings_setter(config):
    heat_duration=config['preferences']['heat_timer']
    if heat_duration == '10':
        logic.heat_sensor_timer=10
    elif heat_duration == '300':
        logic.heat_sensor_timer=300
    elif heat_duration == '600':
        logic.heat_sensor_timer=600

logic_control = Thread(target=logic.logic,daemon=True)
logic_control.start()
try:
    Hood_Control().run()
except KeyboardInterrupt:
    print('Keyboard Inturrupt')
except: 
    traceback.print_exc()
finally:
    logic.clean_exit()
    quit()