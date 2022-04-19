import os
import traceback
import kivy
import logic,lang_dict,pindex
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

kivy.require('2.0.0')
current_language=lang_dict.english

if os.name == 'nt':
    preferences_path='hood_control.ini'
    generic_image=r'media\drops_crop.jpg'
    language_image=r'media\language_icon-1.png'
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
    language_image=r'media/language_icon-1.png'
    settings_icon=r'media/tiny gear.png'
    trouble_icon=r'media/trouble icon.png'
    trouble_icon_dull=r'media/trouble icon dull.png'
    logo=r'media/qt=q_95.png'
    report_current=r'media/report.jpg'
    report_original=r'media/report.jpg'

class LayoutButton(FloatLayout,Button):
    pass

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

class DisplayLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
                    Color(255/255, 255/255, 255/255,.95)
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])
    def update_text(self,text,*args):
        self.text=f'[size=25][color=#000000]{text}[/color][/size]'

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


        quick=ToggleButton(text=current_language['quick'],
                    size_hint =(.96, .45),
                    pos_hint = {'x':.02, 'y':.53},
                    background_down='',
                    background_color=(47/250, 247/250, 54/250,.85),
                    markup=True)
        self.widgets['quick']=quick
        quick.ref='quick'
        quick.bind(on_press=self.quick_start)

        fans=ToggleButton(text=current_language['fans'],
                    size_hint =(.45, .35),
                    pos_hint = {'x':.03, 'y':.15},
                    background_down='',
                    background_color=(0/250, 159/250, 232/250,.85),
                    markup=True)
        self.widgets['fans']=fans
        fans.ref='fans'
        fans.bind(on_press=self.fans_switch)

        lights=ToggleButton(text=current_language['lights'],
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

        alert=Button(text=current_language['alert'],
                    size_hint =(.96, .45),
                    pos_hint = {'x':.02, 'y':.5},
                    background_normal='',
                    background_down='',
                    background_color=(190/250, 10/250, 10/250,.9),
                    markup=True)
        self.widgets['alert']=alert
        alert.ref='alert'

        acknowledge=Button(text=current_language['acknowledge'],
                    size_hint =(.45, .40),
                    pos_hint = {'x':.03, 'y':.05},
                    background_normal='',
                    background_down='',
                    background_color=(255/255, 121/255, 0/255,.99),
                    markup=True)
        self.widgets['acknowledge']=acknowledge
        acknowledge.ref='acknowledge'
        acknowledge.bind(on_release=self.acknowledgement)


        reset=Button(text=current_language['reset'],
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

        back=Button(text=current_language['settings_back'],
                        size_hint =(.4, .25),
                        pos_hint = {'x':.02, 'y':.02},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='settings_back'
        back.bind(on_press=self.settings_back)

        logs=Button(text=current_language['logs'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['logs']=logs
        logs.ref='logs'
        logs.bind(on_release=self.device_logs)

        sys_report=Button(text=current_language['sys_report'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.56},
                        background_normal='',
                        background_color=(180/255, 10/255, 10/255,.9),
                        markup=True)
        self.widgets['sys_report']=sys_report
        sys_report.ref='sys_report'
        sys_report.bind(on_release=self.sys_report)

        preferences=Button(text=current_language['preferences'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.34},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['preferences']=preferences
        preferences.ref='preferences'
        preferences.bind(on_release=self.preferences_func)

        train=Button(text=current_language['train'],
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


        about=Button(text=current_language['about'],
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

        english=Button(text="[size=30][b][color=#000000]  English [/color][/b][/size]",
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.9},
                        background_normal='',
                        background_color=(0/250, 70/250, 90/250,.9),
                        markup=True)
        self.widgets['english']=english
        

        spanish=Button(text="[size=30][b][color=#000000]  Español [/color][/b][/size]",
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

        about_back_button=Button(text=current_language['about_back'],
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
        self.widgets['overlay_layout'].add_widget(about_back_button)
        self.widgets['overlay_menu'].open()

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

        back=Button(text=current_language['report_back'],
                    size_hint =(.4, .15),
                    pos_hint = {'x':.06, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_press=self.Report_back)

        back_main=Button(text=current_language['report_back_main'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.52, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_press=self.Report_back_main)

        # report_image=ScatterImage(
        #     source=report_current,
        #     size_hint_y=2,
        #     size_hint_x=.95,
        #     pos_hint = {'center_x':.5, 'y':1},
        #     do_rotation=False,
        #     do_translation=False,
        #     scale_min=.8,
        #     scale_max=1.4,
        #     auto_bring_to_front=False
        #     )
        # self.widgets['report_image']=report_image

        report_image=Image(
            source=report_current,
            size_hint_y=2.5,
            size_hint_x=.95
            )
        self.widgets['report_image']=report_image

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
        report_scroll.add_widget(report_image)
        self.add_widget(report_scroll)
        self.add_widget(back)
        self.add_widget(back_main)

    def Report_back (self,button):
        self.widgets['report_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='settings'
    def Report_back_main (self,button):
        self.widgets['report_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'

class PreferenceScreen(Screen):
    def __init__(self, **kwargs):
        super(PreferenceScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=Button(text=current_language['preferences_back'],
                        size_hint =(.4, .25),
                        pos_hint = {'x':.02, 'y':.02},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='preferences_back'
        back.bind(on_press=self.settings_back)

        back_main=Button(text=current_language['preferences_back_main'],
                        size_hint =(.48, .25),
                        pos_hint = {'x':.49, 'y':.02},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_press=self.settings_back_main)

        heat_sensor=Button(text=current_language['heat_sensor'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.05, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['heat_sensor']=heat_sensor
        heat_sensor.ref='heat_sensor'
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

        clean_mode=Button(text=current_language['clean_mode'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.78},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['clean_mode']=clean_mode
        clean_mode.ref='clean_mode'
        clean_mode.bind(on_release=self.clean_mode_func)

        commission=Button(text=current_language['commission'],
                        size_hint =(.4, .20),
                        pos_hint = {'x':.54, 'y':.56},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['commission']=commission
        commission.ref='commission'
        commission.bind(on_release=self.commission_func)

        pins=Button(text=current_language['pins'],
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

        duration_1=Button(text=current_language['duration_1'],
                        size_hint =(.3, .50),
                        pos_hint = {'x':.02, 'y':.3},
                        background_normal='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['duration_1']=duration_1
        duration_1.ref='duration_1'

        duration_2=Button(text=current_language['duration_2'],
                        size_hint =(.3, .50),
                        pos_hint = {'x':.35, 'y':.3},
                        background_normal='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['duration_2']=duration_2
        duration_1.ref='duration_2'

        duration_3=Button(text=current_language['duration_3'],
                        size_hint =(.3, .50),
                        pos_hint = {'x':.68, 'y':.3},
                        background_normal='',
                        background_color=(0/250, 159/250, 232/250,.9),
                        markup=True)
        self.widgets['duration_3']=duration_3
        duration_1.ref='duration_3'

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
            text=current_language['maint_overlay_warning_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},
        )
        self.widgets['warning_text']=warning_text
        warning_text.ref='maint_overlay_warning_text'

        continue_button=Button(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['continue_button']=continue_button
        continue_button.ref='continue_button'

        cancel_button=Button(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_down='',
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

        disable_button=Button(text=current_language['disable_button'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 121/255, 0/255,.9),
                        markup=True)
        self.widgets['disable_button']=disable_button
        disable_button.ref='disable_button'

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
    def pins_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='pin'

class PinScreen(Screen):
    def __init__(self, **kwargs):
        super(PinScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        self.pin=''
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=Button(text=current_language['pin_back'],
                    size_hint =(.4, .15),
                    pos_hint = {'x':.06, 'y':.02},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='pin_back'
        back.bind(on_press=self.Pin_back)

        back_main=Button(text=current_language['pin_back_main'],
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

        one=Button(text="[size=35][b][color=#000000] 1 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.85},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['one']=one
        one.bind(on_press=self.one_func)

        two=Button(text="[size=35][b][color=#000000] 2 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.2, 'y':.85},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['two']=two
        two.bind(on_press=self.two_func)

        three=Button(text="[size=35][b][color=#000000] 3 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.4, 'y':.85},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['three']=three
        three.bind(on_press=self.three_func)

        four=Button(text="[size=35][b][color=#000000] 4 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.65},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['four']=four
        four.bind(on_press=self.four_func)

        five=Button(text="[size=35][b][color=#000000] 5 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.2, 'y':.65},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['five']=five
        five.bind(on_press=self.five_func)

        six=Button(text="[size=35][b][color=#000000] 6 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.4, 'y':.65},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['six']=six
        six.bind(on_press=self.six_func)

        seven=Button(text="[size=35][b][color=#000000] 7 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.45},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['seven']=seven
        seven.bind(on_press=self.seven_func)

        eight=Button(text="[size=35][b][color=#000000] 8 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.2, 'y':.45},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['eight']=eight
        eight.bind(on_press=self.eight_func)

        nine=Button(text="[size=35][b][color=#000000] 9 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.4, 'y':.45},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['nine']=nine
        nine.bind(on_press=self.nine_func)

        zero=Button(text="[size=35][b][color=#000000] 0 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.25},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['zero']=zero
        zero.bind(on_press=self.zero_func)

        backspace=Button(text="[size=35][b][color=#000000] <- [/color][/b][/size]",
            size_hint =(.35, .15),
            pos_hint = {'x':.2, 'y':.25},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['backspace']=backspace
        backspace.bind(on_press=self.backspace_func)

        enter=Button(text="[size=35][b][color=#000000] -> [/color][/b][/size]",
            size_hint =(.15, .75),
            pos_hint = {'x':.6, 'y':.25},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['enter']=enter
        enter.bind(on_press=self.enter_func)

        
        display=DisplayLabel(text=f'[size=25][color=#000000]{self.pin}[/color][/size]',
        size_hint =(.67, .10),
        pos_hint = {'x':.152, 'y':.77},
        valign='middle',
        halign='center',
        markup=True)
        self.widgets['display']=display

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
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def Pin_back_main(self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    def one_func(self,button):
        if len(self.pin)<11:
            self.pin+='1'
        self.widgets['display'].update_text(self.pin)
    def two_func(self,button):
        if len(self.pin)<11:   
            self.pin+='2'
        self.widgets['display'].update_text(self.pin)
    def three_func(self,button):
        if len(self.pin)<11:
            self.pin+='3'
        self.widgets['display'].update_text(self.pin)
    def four_func(self,button):
        if len(self.pin)<11:
            self.pin+='4'
        self.widgets['display'].update_text(self.pin)
    def five_func(self,button):
        if len(self.pin)<11:
            self.pin+='5'
        self.widgets['display'].update_text(self.pin)
    def six_func(self,button):
        if len(self.pin)<11:
            self.pin+='6'
        self.widgets['display'].update_text(self.pin)
    def seven_func(self,button):
        if len(self.pin)<11:
            self.pin+='7'
        self.widgets['display'].update_text(self.pin)
    def eight_func(self,button):
        self.pin+='8'
        self.widgets['display'].update_text(self.pin)
    def nine_func(self,button):
        if len(self.pin)<11:
            self.pin+='9'
        self.widgets['display'].update_text(self.pin)
    def zero_func(self,button):
        if len(self.pin)<11:
            self.pin+='0'
        self.widgets['display'].update_text(self.pin)
    def backspace_func(self,button):
        self.pin=self.pin[0:-1]
        self.widgets['display'].update_text(self.pin)
    def enter_func(self,button):
        if hasattr(pindex.Pindex,f'p{self.pin}'):
            eval(f'pindex.Pindex.p{self.pin}()')
        self.pin=''
        self.widgets['display'].update_text(self.pin)

class TroubleScreen(Screen):
    def __init__(self, **kwargs):
        super(TroubleScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=generic_image, allow_stretch=True, keep_ratio=False)

        back=Button(text=current_language['trouble_back'],
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
        Clock.schedule_once(partial(language_setter,config=self.config_))
        self.context_screen=ScreenManager()
        self.context_screen.add_widget(ControlGrid(name='main'))
        self.context_screen.add_widget(ActuationScreen(name='alert'))
        self.context_screen.add_widget(SettingsScreen(name='settings'))
        self.context_screen.add_widget(ReportScreen(name='report'))
        self.context_screen.add_widget(PreferenceScreen(name='preferences'))
        self.context_screen.add_widget(PinScreen(name='pin'))
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

def language_setter(*args,config=None):
    if config:
        global current_language
        lang_pref=config['preferences']['language']
        current_language=eval(f'lang_dict.{lang_pref}')
    for screen in App.get_running_app().root.screens:
        for i in screen.children:
            for ii in i.children:
                for iii in ii.children:
                    if hasattr(iii,'text') and hasattr(iii,'ref'):
                        if iii.text!='':
                            iii.text=current_language[str(iii.ref)]
                if hasattr(ii,'text') and hasattr(ii,'ref'):
                    if ii.text!='':
                        ii.text=current_language[str(ii.ref)]
            if hasattr(i,'text') and hasattr(i,'ref'):
                if i.text!='':
                    i.text=current_language[str(i.ref)]

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