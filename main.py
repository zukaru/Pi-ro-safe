import os,json,time,shutil,math,random
import traceback,errno
from datetime import datetime
from kivy.config import Config

from device_classes.exhaust import Exhaust
from device_classes.mau import Mau
from device_classes.light import Light
from device_classes.drycontact import DryContact
from device_classes.gas_valve import GasValve
from device_classes.micro_switch import MicroSwitch
from device_classes.switch_light import SwitchLight
from device_classes.switch_fans import SwitchFans
from device_classes.heat_sensor import HeatSensor

from messages import messages

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
from kivy.uix.boxlayout import BoxLayout
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
from kivy.graphics import Rectangle, Color, Line, Bezier
from kivy.properties import ListProperty,StringProperty,NumericProperty,ColorProperty
import configparser
import logs.configurations.preferences as preferences
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
from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.graphics.context_instructions import PopMatrix,PushMatrix,Rotate,Scale
from kivy.uix.accordion import Accordion, AccordionItem

kivy.require('2.0.0')
current_language=lang_dict.english

if os.name == 'nt':
    preferences_path='logs/configurations/hood_control.ini'
if os.name == 'posix':
    preferences_path='/home/pi/Pi-ro-safe/logs/configurations/hood_control.ini'
    Window.fullscreen = 'auto'

background_image=r'media/patrick-tomasso-GXXYkSwndP4-unsplash.jpg'
msg_icon_image=r'media/msg_icon.png'
language_image=r'media/higer_res_thick.png'
trouble_icon=r'media/trouble icon_high_res.png'
trouble_icon_dull=r'media/trouble icon_dull_high_res.png'
logo=r'media/fs.png'
report_current=r'logs/sys_report/report.jpg'
report_original=r'logs/sys_report/original_report.jpg'
qr_link =r'media/frame.png'
add_device_icon=r'media/icons8-edit-64.png'
add_device_down=r'media/icons8-edit-64_down.png'
delete_normal=r'media/delete_normal.png'
delete_down=r'media/delete_down.png'
reset_valve=r'media/redo.png'
gray_seperator_line=r'media/line_gray.png'
settings_icon=r'media/menu_lines.png'

class PinPop(Popup):
    def __init__(self,name, **kwargs):
        super().__init__(size_hint=(.8, .8),
        background = 'atlas://data/images/defaulttheme/button',
        title=current_language[f'{name}_overlay'],
        title_color=[0, 0, 0, 1],
        title_size='38',
        title_align='center',
        separator_color=[245/250, 216/250, 41/250,.5],
        **kwargs)
        self.widgets={}
        self.overlay_layout=FloatLayout()
        self.add_widget(self.overlay_layout)

class ScatterImage(Image,Scatter):

    def reset(self):
        self.transform= Matrix().scale(1, 1, 1)

    def on_transform_with_touch(self,touch):
        if self.scale<1:
            return
        return super(ScatterImage, self).on_transform_with_touch(touch)

    def on_touch_up(self, touch):
        self.reset()
        return super(ScatterImage, self).on_touch_up(touch)

class OutlineScroll(ScrollView):
    def __init__(self,bg_color=(0,0,0,1), **kwargs):
        super(OutlineScroll,self).__init__(**kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
                    Color(*bg_color)
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])

class IconButton(ButtonBehavior, Image):
    #uncomment block of code to see hit boxes for your button

    # def __init__(self, **kwargs):
    #     super(IconButton,self).__init__(**kwargs)
    #     with self.canvas.before:
    #             self.colour = Color(0,0,0,1)
    #             self.rect = Rectangle(size=self.size, pos=self.pos)
    #     self.bind(size=self._update_rect, pos=self._update_rect)

    # def _update_rect(self, instance, *args):
    #     self.rect.pos = instance.pos
    #     self.rect.size = instance.size
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
    '''RoundedToggleButton has two key differences from ToggleButton
    
     1- RoundedToggleButton stores background_color as self.bg_color;
     it uses this to keep its round shape colored correctly.
     
     2- RoundedToggleButton toggles on_release.
     this is accomplisehed by overwriting these methods:

    def _do_press(self):
        pass

    def _do_release(self, *args):
        pass

    def on_release(self, *args):
        if (not self.allow_no_selection and
                self.group and self.state == 'down'):
            return

        self._release_group(self)
        self.state = 'normal' if self.state == 'down' else 'down'

    **WARNING**
    The on_release method will change states AFTER callbacks have been dispatched,
    so any callbacks depending on a button object being passed along with a 
    state will need to reverse the expected state value.'''

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

    def _do_press(self):
        pass

    def _do_release(self, *args):
        pass

    def on_release(self, *args):
        if (not self.allow_no_selection and
                self.group and self.state == 'down'):
            return

        self._release_group(self)
        self.state = 'normal' if self.state == 'down' else 'down'

class LayoutButton(FloatLayout,RoundedButton):
    pass

class trouble_template(Button):
    def __init__(self,trouble_tag,trouble_text='',link_text=None,ref_tag=None, **kwargs):
        self.trouble_tag=trouble_tag
        self.trouble_text=trouble_text
        self.link_text=link_text
        self.ref_tag=ref_tag
        if link_text == None:
            link_text=''
        else:
            link_text='\n'+str(current_language[link_text])
        if trouble_text!='':
            trouble_text=current_language[trouble_text]
        super().__init__(text=f'''[size=24][b]{current_language[trouble_tag]}[/b][/size]
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
    def translate(self,current_language):
        try:
            if self.link_text == None:
                link_text=''
            else:
                link_text='\n'+str(current_language[self.link_text])
            if self.trouble_text!='':
                trouble_text=current_language[self.trouble_text]
            else:
                trouble_text=''
            self.text=f'''[size=24][b]{current_language[self.trouble_tag]}[/b][/size]
            [size=18][i]{trouble_text}[/i][/size][size=30][color=#de2500][i][ref={self.ref_tag}]{link_text}[/ref][/i][/color][/size]'''
        except KeyError:
                    print(f'main.py CLASS=trouble_template translate():  {self} has no entry in selected lanuage dict')

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

class RoundedScrollItemTemplate(RoundedButton): 
    def __init__(self,Item_tag,color=(245/250, 216/250, 41/250,.85),**kwargs):
        if color==(245/250, 216/250, 41/250,.9):
            text_color= '#000000'
        else:
            text_color= '#ffffff'
        super(RoundedScrollItemTemplate,self).__init__(text=f'''[color={text_color}][size=24][b]{Item_tag}[/b][/size][/color]''',
        markup=True,
        size_hint_y=None,
        size_hint_x=1,
        background_down='',
        background_color=color,
        **kwargs)

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

class BoxLayoutColor(BoxLayout):
    def __init__(self, **kwargs):
        super(BoxLayoutColor,self).__init__(**kwargs)

        with self.canvas.before:
                Color(0,0,0,.95)
                self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class RelativeLayoutColor(RelativeLayout):
    def __init__(self,bg_color= (.1,.1,.1,.95),**kwargs):
        super(RelativeLayoutColor,self).__init__(**kwargs)
        self.bg_color=bg_color

        with self.canvas.before:
            self.colour=Color(*bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, *args):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class LabelColor(Label):
    bg_color=ColorProperty()
    def __init__(self,bg_color= (.1,.1,.1,.95),**kwargs):
        super(LabelColor,self).__init__(**kwargs)

        with self.canvas.before:
            self.colour = Color(*bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bg_color=bg_color
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, *args):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_bg_color(self, *args):
        self.colour.rgb=self.bg_color

    @property
    def alpha_value(self):
        return self.colour.rgba[3]
    @alpha_value.setter
    def alpha_value(self,value):
        self.colour.rgba[3]=value

class RoundedLabelColor(Label):
    bg_color=ColorProperty()
    def __init__(self,bg_color= (.1,.1,.1,.95),**kwargs):
        super(RoundedLabelColor,self).__init__(**kwargs)
        self.bg_color=bg_color


        with self.canvas.before:
            self.shape_color = Color(*self.bg_color)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_bg_color(self, *args):
        #before __init__ is called the bg_color changes, so we wait untill __init__() to proceed
        if hasattr(self,'shape_color'):
            self.shape_color.rgb=self.bg_color

class RoundedColorLayout(FloatLayout):
    bg_color=ColorProperty()
    def __init__(self,bg_color= (.1,.1,.1,.95),**kwargs):
        super(RoundedColorLayout,self).__init__(**kwargs)
        self.bg_color=bg_color

        with self.canvas.before:
            self.shape_color = Color(*self.bg_color)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

class ClockText(ButtonBehavior,LabelColor):
    def __init__(self, **kwargs):
        super(ClockText,self).__init__(**kwargs)
        self.clock_stack={}
        self.anim_length=.5
        self.animated=False
        self.angle=0
        self.anim_lngth=1
        self.time_size=120
        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=self.angle, origin=self.center)
        with self.canvas.after:
            PopMatrix()
        self.blink_bool=True
        self.bind(on_release=self.animate)
        self.bind(center=self._update)
        self.bind(font_size=self._update)

    def animate(self,*args):
        if self.opacity!=1:
            return
        if self.animated:
            if self.time_size==35:
                self._delete_clock()
                self.animated=False
                self.unrotate()
                self.unslide()
                self.text_unshrink()
                self.unmorph()
        else:
            if self.time_size==120:
                self._create_clock()
                self.animated=True
                self.rotate()
                self.slide()
                self.text_shrink()
                self.morph()

    def _return(self,*args):
        if self.opacity==0:
            self.fade_in()
            self.parent.widgets['widget_carousel'].fade_out()
        if self.time_size==35:
            self.animated=False
            self.unrotate()
            self.unslide()
            self.text_unshrink()
            self.unmorph()
            self.parent.widgets['widget_carousel'].fade_out()

    def _bounce(self,*args):
        App.get_running_app().context_screen.get_screen('main').widgets['widget_carousel'].bounce()

    def _create_clock(self,*args):
        Clock.schedule_once(self._return,10)
        self.clock_stack['event'] = self._return
        Clock.schedule_once(self._bounce,4)
        self.clock_stack['bounce'] = self._bounce

    def _delete_clock(self,*args):
        if 'event' in self.clock_stack:
            Clock.unschedule(self.clock_stack['event'])
        if 'bounce' in self.clock_stack:
            Clock.unschedule(self.clock_stack['bounce'])

    def morph(self):
        anim=Animation(size_hint=(.05,.255),duration=self.anim_lngth/2)
        anim.start(self)
    def unmorph(self):
        anim=Animation(size_hint=(.475,.22),duration=self.anim_lngth/2,t='in_quad')
        anim.start(self)

    def text_shrink(self):
        anim=Animation(time_size=35,duration=self.anim_lngth/2)
        anim.start(self)
    def text_unshrink(self):
        anim=Animation(time_size=120,duration=self.anim_lngth/2)
        anim.start(self)

    def slide(self):
        anim=Animation(pos_hint={'center_x':.05,'center_y':.265},duration=self.anim_lngth/2)
        anim.start(self)
    def unslide(self):
        anim=Animation(pos_hint={'center_x':.5,'center_y':.265},duration=self.anim_lngth/2)
        anim.start(self)

    def rotate(self):
        anim=Animation(angle=-90,duration=self.anim_lngth/2,t='in_quad')
        anim.start(self.rotation)
    def unrotate(self):
        anim=Animation(angle=0,duration=self.anim_lngth/2,t='in_quad')
        anim.start(self.rotation)

    def blink(self):
        self.blink_bool=not self.blink_bool
        if self.blink_bool:
            return '[color=#909090]:[/color]'
        return ':'

    def fade(self,*args):
        if self.opacity==0:
            self.fade_in()
        elif self.opacity==1:
            self.fade_out()

    def fade_in(self):
        self.add_parent()
        anim=Animation(opacity=1,d=self.anim_length)
        anim.start(self)

    def fade_out(self):
        anim=Animation(opacity=0,d=self.anim_length)
        anim.bind(on_complete=partial(self.rm_parent,instance=self))
        anim.start(self)

    def rm_parent(*args,instance=None):
        if instance.parent:
            instance.parent.remove_widget(instance)

    def add_parent(self):
        if not self.parent:
            App.get_running_app().context_screen.get_screen('main').add_widget(self)

    def _update(self,*args):
        self.rotation.origin=self.center
        self.update()

    def update(self, *args):
        #12hour + zero(0) padded decimal minute + am/pm
        self.text =f"[size={int(self.time_size)}][b][color=c0c0c0]{time.strftime('%I'+self.blink()+'%M'+' %p')}"

class Messenger(ButtonBehavior,FloatLayout,LabelColor):
    def __init__(self, **kwargs):
        super(Messenger,self).__init__(**kwargs)
        self.clock_stack={}
        self.widgets={}
        self.anim_d=.25
        self.place_holder=Label()
        self.bind(on_release=self.undock)

    def undock(self,*args):
        if self.size_hint==[1,1]:
            cg=App.get_running_app().context_screen.get_screen('main')
            cgw=cg.widgets
            cl=cgw['clock_label']
            msg=cgw['messenger_button']
            cl._delete_clock()
            self.size_hint =(.475,.22)
            self.pos_hint = {'center_x':.5, 'center_y':.265}
            self.switch_parent()
            self.expand()
            self.align_center()
            self.opaque()
            self.darken()
            msg.clear_widgets()

    def redock(self,*args):
        if self.pos_hint=={'center_x':.5,'center_y':.55}:
            cg=App.get_running_app().context_screen.get_screen('main')
            cgw=cg.widgets
            cl=cgw['clock_label']
            msg=cgw['messenger_button']
            self.contract()
            self.align_bottom()
            self.unopaque()
            self.lighten()
            msg.clear_widgets()
            if cl.opacity==1:
                cl._create_clock()
            else:
                cl._return()

    def switch_parent(self,*args):
        cg=App.get_running_app().context_screen.get_screen('main')
        cgw=cg.widgets
        cl=cgw['clock_label']
        msg=cgw['messenger_button']
        main_screen=App.get_running_app().context_screen.get_screen('main')
        widget_carousel=main_screen.widgets['widget_carousel']
        if self.parent==main_screen:
            if self.place_holder.parent:
                self.place_holder.parent.parent.remove_widget(self.place_holder)
            self.parent.remove_widget(self)
            widget_carousel.add_widget(self)
            widget_carousel.index=-1
            msg.add_widget(cgw['message_label'])
        elif self.parent.parent==widget_carousel:
            self.parent.parent.remove_widget(self)
            main_screen.add_widget(self)
            if not self.place_holder.parent:
                widget_carousel.add_widget(self.place_holder)
                widget_carousel.index=-1
        else:
            print('main.py Messenger switch_parent(): Messenger object has no parent')

    def expand(self,*args):
        anim=Animation(size_hint=(.9,.8),d=self.anim_d,t='in_back')
        anim.start(self)

    def contract(self,*args):
        anim=Animation(size_hint=(.475,.22),d=self.anim_d,t='in_back')
        anim.bind(on_complete=self.switch_parent)
        anim.start(self)

    def fill_slide(self,*args):
        self.size_hint =(1,1)
        self.pos_hint = {'center_x':.5, 'center_y':.5}

    def align_center(self,*args):
        anim=Animation(pos_hint={'center_x':.5,'center_y':.55},d=self.anim_d)
        anim.bind(on_complete=self.populate_widgets)
        anim.start(self)

    def align_bottom(self,*args):
        anim=Animation(pos_hint={'center_x':.5,'center_y':.265},d=self.anim_d,t='in_back')
        anim.bind(on_complete=self.fill_slide)
        anim.start(self)

    def opaque(self,*args):
        anim=Animation(alpha_value=.85,d=self.anim_d)
        anim.start(self)

    def unopaque(self,*args):
        anim=Animation(alpha_value=.3,d=self.anim_d)
        anim.start(self)

    def darken(self,*args):
        anim=Animation(bg_color=[0,0,0,.85],d=self.anim_d)
        anim.start(self)

    def lighten(self,*args):
        anim=Animation(bg_color=[.7,.7,.7,.3],d=self.anim_d)
        anim.start(self)

    def populate_widgets(self,*args):
        scroll_color=(.4,.4,.4,.85)
        yellow=(245/250, 216/250, 41/250,.9)

        cg=App.get_running_app().context_screen.get_screen('main')
        cgw=cg.widgets

        msg_back=RoundedButton(text=current_language['msg_back'],
            size_hint =(.4, .1),
            pos_hint = {'x':.06, 'y':.015},
            background_normal='',
            background_color=yellow,
            markup=True)
        self.widgets['msg_back']=msg_back
        msg_back.ref='msg_back'
        msg_back.bind(on_release=self.redock)

        msg_seperator_line=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            color=(.5,.5,.5,1),
            size_hint =(.5, .001),
            pos_hint = {'x':.01, 'y':.87})
        self.widgets['msg_seperator_line']=msg_seperator_line

        message_title=Label(
            text=current_language['message_title'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.25, 'center_y':.95})
        self.widgets['message_title']=message_title
        message_title.ref='message_title'

        msg_scroll=OutlineScroll(
            size_hint =(.4,.8),
            pos_hint = {'center_x':.75, 'center_y':.45},
            bg_color=scroll_color,
            bar_width=8,
            bar_color=yellow,
            do_scroll_y=True,
            do_scroll_x=False)

        scroll_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5)
        # Make sure the height is such that there is something to scroll.
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        for i in messages.active_messages:
            btn = RoundedButton(
                background_normal='',
                background_color=(.1,.1,.1,1),
                text=i.name,
                size_hint_y=None,
                height=40)
            btn.bind(on_release=partial(self.load_selected_msg,i))
            scroll_layout.add_widget(btn)

        msg_scroll_title=LabelColor(
            bg_color=scroll_color,
            text=current_language['msg_scroll_title'],
            markup=True,
            size_hint =(.4,.1),
            pos_hint = {'center_x':.75, 'center_y':.9})
        self.widgets['msg_scroll_title']=msg_scroll_title
        msg_scroll_title.ref='msg_scroll_title'

        self.load_selected_msg(messages.active_messages[0])

        msg_scroll.add_widget(scroll_layout)

        self.add_widget(msg_back)
        self.add_widget(msg_seperator_line)
        self.add_widget(message_title)
        self.add_widget(msg_scroll)
        self.add_widget(msg_scroll_title)

    def load_selected_msg(self,message,*args):
        try:
            self.remove_widget(self.widgets['selected_msg_title'])
            self.remove_widget(self.widgets['selected_msg_body'])
        except KeyError:
            pass
        selected_msg_title=Label(
            text=f'[size=26][color=#ffffff][b][i][u]{message.title}',
            markup=True,
            halign='center',
            size_hint =(.4,.1),
            pos_hint = {'center_x':.25, 'center_y':.8})
        self.widgets['selected_msg_title']=selected_msg_title
        selected_msg_title.ref='selected_msg_title'
        self.add_widget(selected_msg_title)

        selected_msg_body=Label(
            text=f'[size=20][color=#ffffff]{message.body}',
            markup=True,
            halign='center',
            size_hint =(.4,.1),
            pos_hint = {'center_x':.25, 'center_y':.5})
        self.widgets['selected_msg_body']=selected_msg_body
        selected_msg_body.ref='selected_msg_body'
        self.add_widget(selected_msg_body)

    def evoke(self,*args):
        cg=App.get_running_app().context_screen.get_screen('main')
        wc=cg.widgets['widget_carousel']
        cl=cg.widgets['clock_label']

        if cl.time_size!=120 or cl.opacity!=1:
            return
        if len(messages.active_messages)<2:
            return
        if not App.get_running_app().config_.getboolean('preferences','evoke'):
            return
        if messages.active_messages[0].gravity>=10\
            or random.randint(0,10)-messages.active_messages[0].gravity<=0:
                cg.widget_fade()
                cl.fade()
                Clock.schedule_once(cg.widget_fade,5)
                self.clock_stack['widget_fade']=cg.widget_fade
                Clock.schedule_once(cl.fade,5)
                self.clock_stack['fade']=cl.fade
                if wc.opacity==0:
                    cg.widgets['widget_carousel'].index=1

    def _delete_clock(self,*args):
        if 'widget_fade' in self.clock_stack:
            Clock.unschedule(self.clock_stack['widget_fade'])
        if 'fade' in self.clock_stack:
            Clock.unschedule(self.clock_stack['fade'])

    def on_touch_down(self, touch):
        self._delete_clock()
        return super().on_touch_down(touch)

class BigWheel(Carousel):
    def __init__(self,y_reduction=35, **kwargs):
        super(BigWheel,self).__init__(**kwargs)
        self.y_reduction=y_reduction
        self.anim=Animation()

    def on_index(self,*args):
        super(BigWheel,self).on_index()
        self.anim.cancel_all(self)

    def _position_visible_slides(self, *args):
        slides, index = self.slides, self.index
        no_of_slides = len(slides) - 1
        if not slides:
            return
        x, y, width, height = self.x, self.y, self.width, self.height
        _offset, direction = self._offset, self.direction[0]
        _prev, _next, _current = self._prev, self._next, self._current
        get_slide_container = self.get_slide_container
        last_slide = get_slide_container(slides[-1])
        first_slide = get_slide_container(slides[0])
        skip_next = False
        _loop = self.loop

        if direction in 'rl':
            xoff = x + _offset
            x_prev = {'l': xoff + width, 'r': xoff - width}
            x_next = {'l': xoff - width, 'r': xoff + width}
            if _prev:
                _prev.pos = (x_prev[direction], y)
            elif _loop and _next and index == 0:
                # if first slide is moving to right with direction set to right
                # or toward left with direction set to left
                if ((_offset > 0 and direction == 'r') or
                        (_offset < 0 and direction == 'l')):
                    # put last_slide before first slide
                    last_slide.pos = (x_prev[direction], y)
                    skip_next = True
            if _current:
                _current.pos = (xoff, y)
            if skip_next:
                return
            if _next:
                _next.pos = (x_next[direction], y)
            elif _loop and _prev and index == no_of_slides:
                if ((_offset < 0 and direction == 'r') or
                        (_offset > 0 and direction == 'l')):
                    first_slide.pos = (x_next[direction], y)
        if direction in 'tb':
            yoff = y + _offset

            y_prev = {'t': yoff - height, 'b': yoff + height}
            y_next = {'t': yoff + height, 'b': yoff - height}
            if _prev:
                _prev.pos = (x, y_prev[direction]+self.y_reduction)
            elif _loop and _next and index == 0:
                if ((_offset > 0 and direction == 't') or
                        (_offset < 0 and direction == 'b')):
                    last_slide.pos = (x, y_prev[direction]+self.y_reduction)
                    skip_next = True
            if _current:
                _current.pos = (x, yoff)
            if skip_next:
                return
            if _next:
                _next.pos = (x, y_next[direction]-self.y_reduction)
            elif _loop and _prev and index == no_of_slides:
                if ((_offset < 0 and direction == 't') or
                        (_offset > 0 and direction == 'b')):
                    first_slide.pos = (x, y_next[direction]-self.y_reduction)

    def _insert_visible_slides(self, _next_slide=None, _prev_slide=None):
        get_slide_container = self.get_slide_container

        previous_slide = _prev_slide if _prev_slide else self.previous_slide
        if previous_slide:
            self._prev = get_slide_container(previous_slide)
        else:
            self._prev = None

        current_slide = self.current_slide
        if current_slide:
            self._current = get_slide_container(current_slide)
        else:
            self._current = None

        next_slide = _next_slide if _next_slide else self.next_slide
        if next_slide:
            self._next = get_slide_container(next_slide)
        else:
            self._next = None

        if self._prev_equals_next:
            setattr(self, '_prev' if self._prioritize_next else '_next', None)

        super_remove = super(Carousel, self).remove_widget
        for container in self.slides_container:
            super_remove(container)

        if self._prev and self._prev.parent is not self:
            super(Carousel, self).add_widget(self._prev)
        if self._next and self._next.parent is not self:
            super(Carousel, self).add_widget(self._next)
        if self._current:
            super(Carousel, self).add_widget(self._current)

    def on__offset(self, *args):
        self._trigger_position_visible_slides()
        # if reached full offset, switch index to next or prev
        direction = self.direction[0]
        _offset = self._offset
        width = self.width
        height = self.height
        index = self.index
        if self._skip_slide is not None or index is None:
            return

        # Move to next slide?
        if (direction == 'r' and _offset <= -width) or \
                (direction == 'l' and _offset >= width) or \
                (direction == 't' and _offset-self.y_reduction <= - height) or \
                (direction == 'b' and _offset >= height):
            if self.next_slide:
                self.index += 1

        # Move to previous slide?
        elif (direction == 'r' and _offset >= width) or \
                (direction == 'l' and _offset <= -width) or \
                (direction == 't' and _offset+self.y_reduction >= height) or \
                (direction == 'b' and _offset <= -height):
            if self.previous_slide:
                self.index -= 1

        elif self._prev_equals_next:
            new_value = (_offset < 0) is (direction in 'rt')
            if self._prioritize_next is not new_value:
                self._prioritize_next = new_value
                if new_value is (self._next is None):
                    self._prev, self._next = self._next, self._prev

    def _start_animation(self, *args, **kwargs):
        # compute target offset for ease back, next or prev
        new_offset = 0
        direction = kwargs.get('direction', self.direction)[0]
        is_horizontal = direction in 'rl'
        extent = self.width if is_horizontal else self.height
        min_move = kwargs.get('min_move', self.min_move)
        _offset = kwargs.get('offset', self._offset)

        if _offset < min_move * -extent:
            new_offset = -extent
        elif _offset > min_move * extent:
            new_offset = extent

        # if new_offset is 0, it wasnt enough to go next/prev
        dur = self.anim_move_duration
        if new_offset == 0:
            dur = self.anim_cancel_duration

        # detect edge cases if not looping
        len_slides = len(self.slides)
        index = self.index
        if not self.loop or len_slides == 1:
            is_first = (index == 0)
            is_last = (index == len_slides - 1)
            if direction in 'rt':
                towards_prev = (new_offset > 0)
                towards_next = (new_offset < 0)
            else:
                towards_prev = (new_offset < 0)
                towards_next = (new_offset > 0)
            if (is_first and towards_prev) or (is_last and towards_next):
                new_offset = 0

        self.anim = Animation(_offset=new_offset, d=dur, t=self.anim_type)
        self.anim.cancel_all(self)

        def _cmp(*l):
            if self._skip_slide is not None:
                self.index = self._skip_slide
                self._skip_slide = None

        self.anim.bind(on_complete=_cmp)
        self.anim.start(self)

class BigWheelClock(Carousel):
    clock_stack={}
    def __init__(self,y_reduction=60, **kwargs):
        super(BigWheelClock,self).__init__(**kwargs)
        self.y_reduction=y_reduction
        self.anim=Animation()

    def on_touch_move(self, touch):
        cl=App.get_running_app().context_screen.get_screen('main').widgets['clock_label']
        cl._delete_clock()
        cl._create_clock()
        return super().on_touch_move(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
        return super().on_touch_up(touch)

    def _set_sys_time(*args):
        if Clock.get_boottime()>5:
            if App.get_running_app().context_screen.has_screen('main'):
                w=App.get_running_app().context_screen.get_screen('main').widgets
                h=w['hour_wheel'].index+1
                m=w['minute_wheel'].index
                p='pm' if w['ampm_wheel'].index % 2 else 'am'
                if os.name=='posix':
                        os.system(f'sudo date -s {h}:{m}{p}')
                else:
                    print('main.py BigWheelClock _set_sys_time(): \n  >>time set: ',f'{h}:{str(m).zfill(2)}{p}')

    def _create_clock(self,*args):
        Clock.schedule_once(self._set_sys_time, 2)
        self.clock_stack['event'] = self._set_sys_time

    def _delete_clock(self,*args):
        if 'event' in self.clock_stack:
            Clock.unschedule(self.clock_stack['event'])

    def on_index(self,*args):
        super(BigWheelClock,self).on_index()
        self.anim.cancel_all(self)
        self._delete_clock()#if timer exists, restart it
        self._create_clock()#start timer to call self._set_sys_time()


    def set_index(self,*args,cat=None):
        h=int(time.strftime('%I'))
        m=int(time.strftime('%M'))
        p=time.strftime('%p')
        if cat=='hour':
            for index,i in enumerate(self.slides):
                index+=1
                if index==h:
                    self.index=index-1
                    return
        elif cat =='minute':
            for index,i in enumerate(self.slides):
                if index==m:
                    self.index=index
                    return
        elif cat =='ampm':
            for index,i in enumerate(self.slides):
                if i.text[-2:]==p:
                    self.index=index
                    return

    def _position_visible_slides(self, *args):
        slides, index = self.slides, self.index
        no_of_slides = len(slides) - 1
        if not slides:
            return
        x, y, width, height = self.x, self.y, self.width, self.height
        _offset, direction = self._offset, self.direction[0]
        _prev, _next, _current = self._prev, self._next, self._current
        get_slide_container = self.get_slide_container
        last_slide = get_slide_container(slides[-1])
        first_slide = get_slide_container(slides[0])
        skip_next = False
        _loop = self.loop

        if direction in 'rl':
            xoff = x + _offset
            x_prev = {'l': xoff + width, 'r': xoff - width}
            x_next = {'l': xoff - width, 'r': xoff + width}
            if _prev:
                _prev.pos = (x_prev[direction], y)
            elif _loop and _next and index == 0:
                # if first slide is moving to right with direction set to right
                # or toward left with direction set to left
                if ((_offset > 0 and direction == 'r') or
                        (_offset < 0 and direction == 'l')):
                    # put last_slide before first slide
                    last_slide.pos = (x_prev[direction], y)
                    skip_next = True
            if _current:
                _current.pos = (xoff, y)
            if skip_next:
                return
            if _next:
                _next.pos = (x_next[direction], y)
            elif _loop and _prev and index == no_of_slides:
                if ((_offset < 0 and direction == 'r') or
                        (_offset > 0 and direction == 'l')):
                    first_slide.pos = (x_next[direction], y)
        if direction in 'tb':
            yoff = y + _offset

            y_prev = {'t': yoff - height, 'b': yoff + height}
            y_next = {'t': yoff + height, 'b': yoff - height}
            if _prev:
                _prev.pos = (x, y_prev[direction]+self.y_reduction)
            elif _loop and _next and index == 0:
                if ((_offset > 0 and direction == 't') or
                        (_offset < 0 and direction == 'b')):
                    last_slide.pos = (x, y_prev[direction]+self.y_reduction)
                    skip_next = True
            if _current:
                _current.pos = (x, yoff)
            if skip_next:
                return
            if _next:
                _next.pos = (x, y_next[direction]-self.y_reduction)
            elif _loop and _prev and index == no_of_slides:
                if ((_offset < 0 and direction == 't') or
                        (_offset > 0 and direction == 'b')):
                    first_slide.pos = (x, y_next[direction]-self.y_reduction)

    def _insert_visible_slides(self, _next_slide=None, _prev_slide=None):
        get_slide_container = self.get_slide_container

        previous_slide = _prev_slide if _prev_slide else self.previous_slide
        if previous_slide:
            self._prev = get_slide_container(previous_slide)
        else:
            self._prev = None

        current_slide = self.current_slide
        if current_slide:
            self._current = get_slide_container(current_slide)
        else:
            self._current = None

        next_slide = _next_slide if _next_slide else self.next_slide
        if next_slide:
            self._next = get_slide_container(next_slide)
        else:
            self._next = None

        if self._prev_equals_next:
            setattr(self, '_prev' if self._prioritize_next else '_next', None)

        super_remove = super(Carousel, self).remove_widget
        for container in self.slides_container:
            super_remove(container)

        if self._prev and self._prev.parent is not self:
            super(Carousel, self).add_widget(self._prev)
        if self._next and self._next.parent is not self:
            super(Carousel, self).add_widget(self._next)
        if self._current:
            super(Carousel, self).add_widget(self._current)

    def on__offset(self, *args):
        self._trigger_position_visible_slides()
        # if reached full offset, switch index to next or prev
        direction = self.direction[0]
        _offset = self._offset
        width = self.width
        height = self.height
        index = self.index
        if self._skip_slide is not None or index is None:
            return

        # Move to next slide?
        if (direction == 'r' and _offset <= -width) or \
                (direction == 'l' and _offset >= width) or \
                (direction == 't' and _offset-self.y_reduction <= - height) or \
                (direction == 'b' and _offset >= height):
            if self.next_slide:
                self.index += 1

        # Move to previous slide?
        elif (direction == 'r' and _offset >= width) or \
                (direction == 'l' and _offset <= -width) or \
                (direction == 't' and _offset+self.y_reduction >= height) or \
                (direction == 'b' and _offset <= -height):
            if self.previous_slide:
                self.index -= 1

        elif self._prev_equals_next:
            new_value = (_offset < 0) is (direction in 'rt')
            if self._prioritize_next is not new_value:
                self._prioritize_next = new_value
                if new_value is (self._next is None):
                    self._prev, self._next = self._next, self._prev

    def _start_animation(self, *args, **kwargs):
        # compute target offset for ease back, next or prev
        new_offset = 0
        direction = kwargs.get('direction', self.direction)[0]
        is_horizontal = direction in 'rl'
        extent = self.width if is_horizontal else self.height
        min_move = kwargs.get('min_move', self.min_move)
        _offset = kwargs.get('offset', self._offset)

        if _offset < min_move * -extent:
            new_offset = -extent
        elif _offset > min_move * extent:
            new_offset = extent

        # if new_offset is 0, it wasnt enough to go next/prev
        dur = self.anim_move_duration
        if new_offset == 0:
            dur = self.anim_cancel_duration

        # detect edge cases if not looping
        len_slides = len(self.slides)
        index = self.index
        if not self.loop or len_slides == 1:
            is_first = (index == 0)
            is_last = (index == len_slides - 1)
            if direction in 'rt':
                towards_prev = (new_offset > 0)
                towards_next = (new_offset < 0)
            else:
                towards_prev = (new_offset < 0)
                towards_next = (new_offset > 0)
            if (is_first and towards_prev) or (is_last and towards_next):
                new_offset = 0

        self.anim = Animation(_offset=new_offset, d=dur, t=self.anim_type)
        self.anim.cancel_all(self)

        def _cmp(*l):
            if self._skip_slide is not None:
                self.index = self._skip_slide
                self._skip_slide = None

        self.anim.bind(on_complete=_cmp)
        self.anim.start(self)

class AnimatedCarousel(Carousel):
    def __init__(self, **kwargs):
        super(AnimatedCarousel,self).__init__(**kwargs)
        self.opacity=0
        self.anim_length=.5

    def on_touch_move(self, touch):
        cl=App.get_running_app().context_screen.get_screen('main').widgets['clock_label']
        cl._delete_clock()
        cl._create_clock()
        return super().on_touch_move(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
        return super().on_touch_up(touch)

    def fade_in(self):
        anim=Animation(opacity=1,d=self.anim_length)
        anim.start(self)

    def fade_out(self):
        anim=Animation(opacity=0,d=self.anim_length/2)
        anim.bind(on_complete=partial(self.rm_parent,instance=self))
        anim.start(self)

    def rm_parent(*args,instance=None):
        if instance.parent:
            instance.parent.remove_widget(instance)

    def on_touch_down(self, touch):
        if self.opacity==1 and self._offset==0:
            return super(AnimatedCarousel,self).on_touch_down(touch)

    def bounce(self,*args):
        anim=Animation(_offset=-100,d=.5,t='out_quad')+Animation(_offset=0,d=.25,t='in_quad')
        anim.start(self)

    def bounce_progress(self,progress,*args):
        def out(progress):
            p = 1.-progress / 1.
            # if p < (.25 / 2.75):
            #     return -7.5625 * p * p + progress
            if p < (1.0 / 2.75):
                return 7.5625 * p * p + (progress-p)
            if p < (2.0 / 2.75):
                p -= (1.5 / 2.75)
                return 7.5625 * p * p + .75 
            elif p < (2.5 / 2.75):
                p -= (2.25 / 2.75)
                return 7.5625 * p * p + .9375
            else:
                p -= (2.625 / 2.75)
                return 7.5625 * p * p + .984375
        return 1.0-out(progress)

#<<<<<<<<<<>>>>>>>>>>#

class ControlGrid(Screen):
    def fans_switch(self,button):
        if button.state == 'normal':
            logic.fs.moli['exhaust']=1
            logic.fs.moli['mau']=1
        elif button.state == 'down':
            logic.fs.moli['exhaust']=0
            logic.fs.moli['mau']=0

    def lights_switch(self,button):
        if button.state == 'normal':
            logic.fs.moli['lights']=1
        elif button.state == 'down':
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
        self.ud={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self._keyboard=Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.value_up=Animation(value=1000,d=4.2,t='in_out_quad')
        self.value_down=Animation(value=0,d=1,t='in_out_circ')
        self.fade=Animation(opacity=0,d=1)
        self._fade_in=Animation(opacity=1,d=.5)

        def remove_ramp(*args):
            if 'ramp_progress' in self.widgets:
                self.remove_widget(self.widgets['ramp_progress'])
                del self.widgets['ramp_progress']
            if 'event_bar' in self.ud:
                Clock.unschedule(self.ud['event_bar'])
                del self.ud['event_bar']
            if 'ramp_text' in self.widgets:
                self.remove_widget(self.widgets['ramp_text'])
                del self.widgets['ramp_text']
        self.fade.bind(on_complete=remove_ramp)

        fans=RoundedToggleButton(text=current_language['fans'],
                    size_hint =(.45, .5),
                    pos_hint = {'x':.03, 'y':.4},
                    background_down='',
                    background_color=(0/250, 159/250, 232/250,.85),
                    markup=True)
        self.widgets['fans']=fans
        fans.ref='fans'
        fans.bind(on_release=self.fans_switch)
        fans.bind(on_release=self.ramp_animate)

        lights=RoundedToggleButton(text=current_language['lights'],
                    size_hint =(.45, .5),
                    pos_hint = {'x':.52, 'y':.4},
                    background_down='',
                    background_color=(245/250, 216/250, 41/250,.85),
                    markup=True)
        self.widgets['lights']=lights
        lights.ref='lights'
        lights.bind(on_release=self.lights_switch)

        clock_label=ClockText(
            markup=True,
            size_hint =(.475,.22),
            pos_hint = {'center_x':.5, 'center_y':.265},
            bg_color=(.2,.2,.2,.65))
        self.widgets['clock_label']=clock_label
        clock_label.bind(on_release=self.widget_fade)

        widget_carousel=AnimatedCarousel(
            size_hint =(.475,.22),
            pos_hint = {'center_x':.5, 'center_y':.265},
            loop=True,
            ignore_perpendicular_swipes=True)
        self.widgets['widget_carousel']=widget_carousel

        clock_set_layout=RelativeLayoutColor(bg_color= (.1,.1,.1,.85))

        hour_wheel=BigWheelClock(
            size_hint =(.25, .9),
            pos_hint = {'x':.0, 'center_y':.5},
            direction='top',
            loop=True)
        self.widgets['hour_wheel']=hour_wheel

        for i in range(12):
            _hour=Label(
                text=f'[size=80][b][color=c0c0c0]{i+1}',
                markup=True,)
            hour_wheel.add_widget(_hour)

        delimiter_dots=Label(
            size_hint =(.25, .9),
            pos_hint = {'x':.2, 'center_y':.5},
            text=f'[size=80][b][color=c0c0c0]:',
            markup=True)

        minute_wheel=BigWheelClock(
            size_hint =(.25, .9),
            pos_hint = {'x':.4, 'center_y':.5},
            direction='top',
            loop=True)
        self.widgets['minute_wheel']=minute_wheel

        for i in range(60):
            i=str(i)
            _minute=Label(
                text=f'[size=80][b][color=c0c0c0]{i.zfill(2)}',
                markup=True)
            minute_wheel.add_widget(_minute)

        ampm_wheel=BigWheelClock(
            size_hint =(.25, .9),
            pos_hint = {'x':.7, 'center_y':.5},
            direction='top',
            loop=True,
            y_reduction=70)
        self.widgets['ampm_wheel']=ampm_wheel

        for i in ['AM','PM','AM','PM']:
            _ampm=Label(
                text=f'[size=60][b][color=c0c0c0]{i}',
                markup=True)
            ampm_wheel.add_widget(_ampm)

        messenger_button=Messenger(
            bg_color=(.7,.7,.7,.3),
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['messenger_button']=messenger_button
        fans.bind(on_press=self.widgets['messenger_button'].evoke)
        lights.bind(on_press=self.widgets['messenger_button'].evoke)

        message_label=Label(
            text=current_language['message_label'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.5},
            halign='center',
            valign='center')
        message_label.bind(size=message_label.setter('text_size'))
        self.widgets['message_label']=message_label
        message_label.ref='message_label'

        settings_button=RoundedButton(
                    size_hint =(.18, .1),
                    pos_hint = {'x':.02, 'y':.015},
                    background_down='',
                    background_color=(250/250, 250/250, 250/250,.9),
                    markup=True)
        self.widgets['settings_button']=settings_button
        settings_button.bind(on_press=self.open_settings)

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        menu_icon=Image(source=settings_icon,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.135, .038),
                    pos_hint = {'x':.043, 'y':.045})
        menu_icon.center=settings_button.center

        trouble_button=IconButton(source=trouble_icon_dull, allow_stretch=True, keep_ratio=True)
        trouble_button.size_hint =(.10, .10)
        trouble_button.pos_hint = {'x':.75, 'y':.02}
        self.widgets['trouble_button']=trouble_button
        trouble_button.bind(on_press=self.open_trouble)
        trouble_button.color=(1,1,1,.15)

        language_button=IconButton(source=language_image, allow_stretch=True, keep_ratio=True)
        language_button.size_hint =(.10, .10)
        language_button.pos_hint = {'x':.61, 'y':.02}
        self.widgets['language_button']=language_button
        language_button.bind(on_press=self.language_func)
        language_button.color=(1,1,1,.65)

        msg_icon=IconButton(source=msg_icon_image, allow_stretch=True, keep_ratio=True)
        msg_icon.size_hint =(.10, .10)
        msg_icon.pos_hint = {'x':.47, 'y':.02}
        self.widgets['msg_icon']=msg_icon
        msg_icon.bind(on_press=self.msg_icon_func)
        msg_icon.color=(1,1,1,.65)

        fs_logo=IconButton(source=logo,
                size_hint_x=.1,
                size_hint_y=.1,
                allow_stretch=True,
                keep_ratio=True,
                pos_hint = {'x':.89, 'y':.02},
                color=(.7,.7,.7))
        fs_logo.bind(on_release=self.about_func)

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/bubble',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=[255/255, 0/255, 0/255, .5])
        overlay_menu.bind(on_touch_down=overlay_menu.dismiss)
        self.widgets['overlay_menu']=overlay_menu

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        overlay_menu.add_widget(overlay_layout)
        clock_set_layout.add_widget(hour_wheel)
        clock_set_layout.add_widget(delimiter_dots)
        clock_set_layout.add_widget(minute_wheel)
        clock_set_layout.add_widget(ampm_wheel)
        widget_carousel.add_widget(clock_set_layout)
        messenger_button.add_widget(message_label)
        widget_carousel.add_widget(messenger_button)

        self.add_widget(bg_image)
        self.add_widget(fans)
        self.add_widget(lights)
        self.add_widget(settings_button)
        self.add_widget(seperator_line)
        self.add_widget(menu_icon)
        self.add_widget(trouble_button)
        self.add_widget(language_button)
        self.add_widget(msg_icon)
        self.add_widget(fs_logo)
        self.add_widget(clock_label)

    def ramp_animate(self,button,*args):
        fb=self.widgets['fans'] #fans button

        def fade_out(*args):
            if 'ramp_progress' not in self.widgets:
                return
            if 'ramp_text' not in self.widgets:
                return

            self.fade.cancel(self.widgets['ramp_progress'])
            self.fade.cancel(self.widgets['ramp_text'])
            self.fade.start(self.widgets['ramp_progress'])
            self.fade.start(self.widgets['ramp_text'])
            self.value_up.cancel(self.widgets['ramp_progress'])
            if self.widgets['ramp_progress'].value<1000:
                self.value_down.start(self.widgets['ramp_progress'])


        def fade_in(*args):
            if 'ramp_progress' not in self.widgets:
                ramp_progress=CircularProgressBar()
                ramp_progress.widget_size=int(fb.height*.9)
                ramp_progress._background_colour=(0,0,0,0)
                ramp_progress._progress_colour=(.1,.1,.1,.85)
                self.widgets['ramp_progress']=ramp_progress
                ramp_progress.pos=self.widgets['fans'].center
                ramp_progress.opacity=0
                self.add_widget(ramp_progress)
            self.value_down.cancel(self.widgets['ramp_progress'])
            self.value_up.start(self.widgets['ramp_progress'])

            if 'ramp_text' not in self.widgets:
                ramp_text=Label(
                    text=current_language['ramp_text'],
                    markup=True,
                    pos = (
                        fb.right-fb.width/2-50,
                        fb.top-fb.height/5*3-50))
                self.widgets['ramp_text']=ramp_text
                ramp_text.ref='ramp_text'
                ramp_text.opacity=0
                self.add_widget(ramp_text)

            def progress_bar_update(dt,*args):
                self.widgets['ramp_progress'].pos=self.widgets['fans'].center
                self.widgets['ramp_text'].pos=(
                    fb.right-fb.width/2-self.widgets['ramp_text'].width/2,
                    fb.top-fb.height/5*3-self.widgets['ramp_text'].height/2)
                if self.widgets['ramp_progress'].value >= 1000: # Checks to see if progress_bar.value has met 1000
                    fade_out()
                    return False # Returning False schedule is canceled and won't repeat

            if 'event_bar' not in self.ud:
                Clock.schedule_interval(progress_bar_update,.01)
                self.ud['event_bar'] = progress_bar_update

            self.fade.cancel(self.widgets['ramp_progress'])
            self.fade.cancel(self.widgets['ramp_text'])
            if self.widgets['ramp_text'].opacity<1:
                self._fade_in.start(self.widgets['ramp_text'])
            if self.widgets['ramp_progress'].opacity<1:
                self._fade_in.start(self.widgets['ramp_progress'])

        if button.state=='down':
            #if fans are turned off
            fade_out()
        if button.state=='normal':
            #if fans are turned on
            fade_in()

    def widget_fade(self,*args):
        if not (self.widgets['clock_label'].opacity==0 or self.widgets['clock_label'].opacity==1):
            return
        if self.widgets['clock_label'].time_size==35 or self.widgets['clock_label'].time_size==120:
            if self.widgets['widget_carousel'] not in self.children:
                self.update_msg_card()
                self.add_widget(self.widgets['widget_carousel'],-2)
                self.widgets['widget_carousel'].index=0
                self.widgets['widget_carousel'].fade_in()
                self.widgets['hour_wheel'].set_index(cat='hour')
                self.widgets['minute_wheel'].set_index(cat='minute')
                self.widgets['ampm_wheel'].set_index(cat='ampm')
            else:
                if self.widgets['widget_carousel'].opacity!=1:
                    return
                self.widgets['widget_carousel'].fade_out()
    def open_settings(self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='settings'
    def open_trouble(self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='trouble'
    def language_func (self,button):
        self.language_overlay()
    def update_msg_card(self,*args):
        self.widgets['message_label'].text=f'[size=50][color=#ffffff][b]{messages.active_messages[0].card}'
    def msg_icon_func (self,button):
        if self.widgets['clock_label'].opacity!=1:
            return
        if self.widgets['messenger_button'].pos_hint=={'center_x':.5,'center_y':.55}:
            return
        self.widget_fade()
        if self.widgets['clock_label'].time_size==120:
            self.widgets['widget_carousel'].index=1
        self.widgets['clock_label'].animate()
    def on_pre_leave(self, *args):
        self.widgets['messenger_button'].redock()

    def language_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,0)
        overlay_menu.auto_dismiss=True
        overlay_menu.title=''
        overlay_menu.separator_height=0
        self.widgets['overlay_layout'].clear_widgets()

        english=RoundedButton(text="[size=30][b][color=#000000]  English [/color][/b][/size]",
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.7},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['english']=english

        spanish=RoundedButton(text="[size=30][b][color=#000000]  Español [/color][/b][/size]",
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.3},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['spanish']=spanish

        def english_func(button):
            global current_language
            config=App.get_running_app().config_
            current_language=lang_dict.english
            config.set('preferences','language','english')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            language_setter()
            self.widgets['overlay_menu'].dismiss()
        english.bind(on_release=english_func)

        def spanish_func(button):
            global current_language
            config=App.get_running_app().config_
            current_language=lang_dict.spanish
            config.set('preferences','language','spanish')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            language_setter()
            self.widgets['overlay_menu'].dismiss()
        spanish.bind(on_release=spanish_func)

        self.widgets['overlay_layout'].add_widget(english)
        self.widgets['overlay_layout'].add_widget(spanish)
        self.widgets['overlay_menu'].open()

    def about_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        about_text=Label(
            text=current_language['about_overlay_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['about_text']=about_text
        about_text.ref='about_overlay_text'

        version_info=Label(text=current_language['version_info_white'],
                markup=True,
                pos_hint = {'x':-.05, 'center_y':.6})
        version_info.ref='version_info'

        about_qr=Image(source=qr_link,
            allow_stretch=False,
            keep_ratio=True,
            size_hint =(.45,.45),
            pos_hint = {'x':.6, 'y':.58})

        qr_label=Label(text='[size=16][color=#ffffff]firesafeextinguisher.com[/color][/size]',
                markup=True,
                pos_hint = {'x':.33, 'center_y':.55})
        qr_label.ref='qr_label'

        about_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['about_back_button']=about_back_button
        about_back_button.ref='about_back'

        def about_overlay_close(button):
            self.widgets['overlay_menu'].dismiss()
        about_back_button.bind(on_press=about_overlay_close)

        self.widgets['overlay_layout'].add_widget(about_text)
        self.widgets['overlay_layout'].add_widget(version_info)
        self.widgets['overlay_layout'].add_widget(about_qr)
        self.widgets['overlay_layout'].add_widget(qr_label)
        self.widgets['overlay_layout'].add_widget(about_back_button)
        self.widgets['overlay_menu'].open()

    def about_func (self,button):
        self.about_overlay()

class ActuationScreen(Screen):
    def __init__(self, **kwargs):
        super(ActuationScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        alert=RoundedLabelColor(text=current_language['alert'],
                    size_hint =(.96, .45),
                    pos_hint = {'x':.02, 'y':.5},
                    bg_color=(249/250, 25/250, 25/250,.85),
                    markup=True)
        self.widgets['alert']=alert
        alert.ref='alert'

        action_box=RoundedColorLayout(
            bg_color=(.25,.25,.25,.85),
            size_hint =(.35, .40),
            pos_hint = {'x':.02, 'center_y':.25},)
        self.widgets['action_box']=action_box

        with action_box.canvas.before:
           Color(.1,.1,.1,1)
           action_box.msg_lines=Line(points=[100,100,100,100],width=1.5,group='action')

        def update_action_box_lines(*args):
            #vertical left section
            x1=int(action_box.width*.025+action_box.x)
            y1=int(action_box.height*.05+action_box.y)
            x2=int(action_box.width*.025+action_box.x)
            y2=int(action_box.height*.95+action_box.y)

            #horizontal top section
            x3=int(action_box.width*.025+action_box.x)
            y3=int(action_box.height*.95+action_box.y)
            x4=int(action_box.width*.975+action_box.x)
            y4=int(action_box.height*.95+action_box.y)

            #vertical right section
            x5=int(action_box.width*.975+action_box.x)
            y5=int(action_box.height*.95+action_box.y)
            x6=int(action_box.width*.975+action_box.x)
            y6=int(action_box.height*.05+action_box.y)

            #horizontal bottom section
            x7=int(action_box.width*.975+action_box.x)
            y7=int(action_box.height*.05+action_box.y)
            x8=int(action_box.width*.025+action_box.x)
            y8=int(action_box.height*.05+action_box.y)

            action_box.msg_lines.points=(x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7,x8,y8)
        action_box.bind(pos=update_action_box_lines, size=update_action_box_lines)

        acknowledge=RoundedToggleButton(
            text=current_language['acknowledge'],
            size_hint =(.85, .20),
            pos_hint = {'center_x':.5, 'center_y':.725},
            # background_normal='',
            background_down='',
            background_color=(.1,.1,.1,.85),
            markup=True)
        self.widgets['acknowledge']=acknowledge
        acknowledge.ref='acknowledge'
        acknowledge.bind(on_release=self.acknowledge_func)

        service=RoundedButton(
            text=current_language['service'],
            size_hint =(.85, .20),
            pos_hint = {'center_x':.5, 'center_y':.275},
            # background_normal='',
            background_down='',
            background_color=(.1,.1,.1,.85),
            markup=True)
        self.widgets['service']=service
        service.ref='service'
        service.bind(on_release=self.service_func)

        dialogue_box=RoundedColorLayout(
            bg_color=(.1,.1,.1,.9),
            size_hint =(.5, .40),
            pos_hint = {'center_x':.7, 'center_y':.25},)
        self.widgets['dialogue_box']=dialogue_box

        with dialogue_box.canvas.before:
           Color(.25,.25,.25,1)
           dialogue_box.msg_lines=Line(points=[100,100,100,100],width=1.5,group='action')

        def update_dialogue_box_lines(*args):
            #vertical left section
            x1=int(dialogue_box.width*.025+dialogue_box.x)
            y1=int(dialogue_box.height*.05+dialogue_box.y)
            x2=int(dialogue_box.width*.025+dialogue_box.x)
            y2=int(dialogue_box.height*.75+dialogue_box.y)

            #horizontal top section
            x3=int(dialogue_box.width*.025+dialogue_box.x)
            y3=int(dialogue_box.height*.75+dialogue_box.y)
            x4=int(dialogue_box.width*.975+dialogue_box.x)
            y4=int(dialogue_box.height*.75+dialogue_box.y)

            #vertical right section
            x5=int(dialogue_box.width*.975+dialogue_box.x)
            y5=int(dialogue_box.height*.75+dialogue_box.y)
            x6=int(dialogue_box.width*.975+dialogue_box.x)
            y6=int(dialogue_box.height*.05+dialogue_box.y)

            #horizontal bottom section
            x7=int(dialogue_box.width*.975+dialogue_box.x)
            y7=int(dialogue_box.height*.05+dialogue_box.y)
            x8=int(dialogue_box.width*.025+dialogue_box.x)
            y8=int(dialogue_box.height*.05+dialogue_box.y)

            dialogue_box.msg_lines.points=(x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7,x8,y8)
        dialogue_box.bind(pos=update_dialogue_box_lines, size=update_dialogue_box_lines)

        dialogue_title=RoundedLabelColor(
            bg_color=(.25,.25,.25,.0),
            size_hint =(.9, .2),
            pos_hint = {'center_x':.5, 'center_y':.875},
            text=current_language['acknowledge'],
            markup=True)
        self.widgets['dialogue_title']=dialogue_title
        dialogue_title.ref='dialogue_title'

        dialogue_body=RoundedLabelColor(
            bg_color=(.25,.25,.25,.0),
            size_hint =(.9, .5),
            pos_hint = {'center_x':.5, 'center_y':.35},
            text=current_language['acknowledge'],
            markup=True)
        self.widgets['dialogue_body']=dialogue_body
        dialogue_body.ref='dialogue_body'

        self.pulse()

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/bubble',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=[255/255, 0/255, 0/255, .5])
        self.widgets['overlay_menu']=overlay_menu

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        overlay_menu.add_widget(overlay_layout)

        self.add_widget(bg_image)
        self.add_widget(alert)
        self.add_widget(action_box)
        action_box.add_widget(acknowledge)
        action_box.add_widget(service)
        self.add_widget(dialogue_box)
        dialogue_box.add_widget(dialogue_title)
        dialogue_box.add_widget(dialogue_body)

    def on_pre_enter(self,*args):
        self.anime.cancel_all(self.widgets['alert'])
        self.pulse()
        self.widgets['acknowledge'].text=current_language['acknowledge']
        self.widgets['acknowledge'].disabled=False
        self.widgets['acknowledge'].state='normal'

    def acknowledge_func(self,button):
        print('actuation acknowledged')
        self.anime.cancel_all(self.widgets['alert'])
        self.widgets['alert'].bg_color=(249/250, 25/250, 25/250,.85)
        # self.widgets['alert'].text=current_language['alert_acknowledged']
        button.text="[size=28][color=#ffffff]Acknowledged"
        button.disabled=True

    def service_func(self,*args):
        self.service_overlay()

    def pulse(self):
            self.anime = Animation(bg_color=(249/250, 200/250, 200/250,.85), duration=.2)+Animation(bg_color=(249/250, 0/250, 0/250,1), duration=1.5)
            self.anime.repeat = True
            self.anime.start(self.widgets['alert'])

    def service_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.8)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        service_back_button=RoundedButton(
            text=current_language['about_back'],
            size_hint =(.9, .1),
            pos_hint = {'x':.05, 'y':.05},
            background_normal='',
            background_color=(245/250, 216/250, 41/250,.9),
            markup=True)
        self.widgets['service_back_button']=service_back_button
        service_back_button.ref='about_back'

        service_enter_button=RoundedButton(
            text=current_language['enter'],
            size_hint =(.9, .1),
            pos_hint = {'x':.05, 'y':.45},
            background_normal='',
            background_color=(.25,.25,.25,1),
            markup=True)
        self.widgets['service_enter_button']=service_enter_button
        service_back_button.ref='enter'

        pin_layout=FloatLayout(
            size_hint =(.5, .25),
            pos_hint = {'center_x':.5, 'center_y':.75})
        self.widgets['pin_layout']=pin_layout

        with pin_layout.canvas.before:
           Color(.25,.25,.25,1)
           pin_layout.box_lines=Line(points=[100,100,100,100],width=1.5,group='action')
           pin_layout.divider_line1=Line(points=[100,100,100,100],width=1.5,group='action')
           pin_layout.divider_line2=Line(points=[100,100,100,100],width=1.5,group='action')
           pin_layout.divider_line3=Line(points=[100,100,100,100],width=1.5,group='action')

        def update_pin_layout_lines(*args):
            #vertical left section
            x1=int(pin_layout.width*0+pin_layout.x)
            y1=int(pin_layout.height*0+pin_layout.y)
            x2=int(pin_layout.width*0+pin_layout.x)
            y2=int(pin_layout.height*1+pin_layout.y)

            #horizontal top section
            x3=int(pin_layout.width*0+pin_layout.x)
            y3=int(pin_layout.height*1+pin_layout.y)
            x4=int(pin_layout.width*1+pin_layout.x)
            y4=int(pin_layout.height*1+pin_layout.y)

            #vertical right section
            x5=int(pin_layout.width*1+pin_layout.x)
            y5=int(pin_layout.height*1+pin_layout.y)
            x6=int(pin_layout.width*1+pin_layout.x)
            y6=int(pin_layout.height*0+pin_layout.y)

            #horizontal bottom section
            x7=int(pin_layout.width*1+pin_layout.x)
            y7=int(pin_layout.height*0+pin_layout.y)
            x8=int(pin_layout.width*0+pin_layout.x)
            y8=int(pin_layout.height*0+pin_layout.y)

            #divider lines
            x9=int(pin_layout.width*.25+pin_layout.x)
            y9=int(pin_layout.height*0+pin_layout.y)
            x10=int(pin_layout.width*.25+pin_layout.x)
            y10=int(pin_layout.height*1+pin_layout.y)

            x11=int(pin_layout.width*.5+pin_layout.x)
            y11=int(pin_layout.height*0+pin_layout.y)
            x12=int(pin_layout.width*.5+pin_layout.x)
            y12=int(pin_layout.height*1+pin_layout.y)

            x13=int(pin_layout.width*.75+pin_layout.x)
            y13=int(pin_layout.height*0+pin_layout.y)
            x14=int(pin_layout.width*.75+pin_layout.x)
            y14=int(pin_layout.height*1+pin_layout.y)

            pin_layout.box_lines.points=(x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7,x8,y8)
            pin_layout.divider_line1.points=(x9,y9,x10,y10)
            pin_layout.divider_line2.points=(x11,y11,x12,y12)
            pin_layout.divider_line3.points=(x13,y13,x14,y14)
        pin_layout.bind(pos=update_pin_layout_lines, size=update_pin_layout_lines)

        pin_1=BigWheel(
            size_hint =(.25, .975),
            pos_hint = {'center_x':.125, 'center_y':.495},
            direction='top',
            loop=True,
            y_reduction=60
            )
        self.widgets['pin_1']=pin_1

        for i in range(10):
            _digit=Label(
                text=f'[size=80][b][color=c0c0c0]{i}',
                markup=True,)
            pin_1.add_widget(_digit)
        
        pin_2=BigWheel(
            size_hint =(.25, .975),
            pos_hint = {'center_x':.375, 'center_y':.495},
            direction='top',
            loop=True,
            y_reduction=60
            )
        self.widgets['pin_2']=pin_2

        for i in range(10):
            _digit=Label(
                text=f'[size=80][b][color=c0c0c0]{i}',
                markup=True,)
            pin_2.add_widget(_digit)

        pin_3=BigWheel(
            size_hint =(.25, .975),
            pos_hint = {'center_x':.625, 'center_y':.495},
            direction='top',
            loop=True,
            y_reduction=60
            )
        self.widgets['pin_3']=pin_3

        for i in range(10):
            _digit=Label(
                text=f'[size=80][b][color=c0c0c0]{i}',
                markup=True,)
            pin_3.add_widget(_digit)

        pin_4=BigWheel(
            size_hint =(.25, .975),
            pos_hint = {'center_x':.875, 'center_y':.495},
            direction='top',
            loop=True,
            y_reduction=60
            )
        self.widgets['pin_4']=pin_4

        for i in range(10):
            _digit=Label(
                text=f'[size=80][b][color=c0c0c0]{i}',
                markup=True,)
            pin_4.add_widget(_digit)

        def service_overlay_close(button):
            self.widgets['overlay_menu'].dismiss()
        service_back_button.bind(on_release=service_overlay_close)

        def return_to_actuationscreen(*args):
            App.get_running_app().service_pin_entered=False

        def service_enter_func(*args):
            pin=''.join(
                (str(pin_1.index),
                str(pin_2.index),
                str(pin_3.index),
                str(pin_4.index)))
            pin_1.index,pin_2.index,pin_3.index,pin_4.index=0,0,0,0
            if pin!='1000':
                return
            App.get_running_app().service_pin_entered=True
            self.parent.transition = SlideTransition(direction='right')
            App.get_running_app().context_screen.current='main'
            Clock.schedule_once(return_to_actuationscreen,300)
            self.widgets['overlay_menu'].dismiss()

        service_enter_button.bind(on_release=service_enter_func)

        pin_layout.add_widget(pin_1)
        pin_layout.add_widget(pin_2)
        pin_layout.add_widget(pin_3)
        pin_layout.add_widget(pin_4)

        self.widgets['overlay_layout'].add_widget(pin_layout)
        self.widgets['overlay_layout'].add_widget(service_enter_button)
        self.widgets['overlay_layout'].add_widget(service_back_button)
        self.widgets['overlay_menu'].open()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['settings_back'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.06, 'y':.015},
                        background_down='',
                        background_color=(200/255, 200/255, 200/255,.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='settings_back'
        back.bind(on_press=self.settings_back)

        version_info=RoundedButton(text=current_language['version_info'],
                markup=True,
                background_normal='',
                background_color=(245/250, 216/250, 41/250,.5),
                size_hint =(.18, .1),
                pos_hint = {'x':.75, 'y':.015},)
        version_info.ref='version_info'
        version_info.bind(on_release=self.about_func)

        logs=RoundedButton(text=current_language['logs'],
                        size_hint =(.9, .18),
                        pos_hint = {'x':.05, 'y':.78},
                        background_down='',
                        background_color=(200/255, 200/255, 200/255,.9),
                        markup=True)
        self.widgets['logs']=logs
        logs.ref='logs'
        logs.bind(on_release=self.device_logs)

        sys_report=RoundedButton(text=current_language['sys_report'],
                        size_hint =(.9, .18),
                        pos_hint = {'x':.05, 'y':.51},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.9),#180/255, 10/255, 10/255,.9
                        markup=True)
        self.widgets['sys_report']=sys_report
        sys_report.ref='sys_report'
        sys_report.bind(on_release=self.sys_report)

        preferences=RoundedButton(text=current_language['preferences'],
                        size_hint =(.9, .18),
                        pos_hint = {'x':.05, 'y':.24},
                        background_down='',
                        background_color=(200/255, 205/255, 200/255,.9),
                        markup=True)
        self.widgets['preferences']=preferences
        preferences.ref='preferences'
        preferences.bind(on_release=self.preferences_func)

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/button',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=[255/255, 0/255, 0/255, .5])
        self.widgets['overlay_menu']=overlay_menu

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        overlay_menu.add_widget(overlay_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(version_info)
        self.add_widget(logs)
        self.add_widget(sys_report)
        self.add_widget(preferences)
        self.add_widget(seperator_line)

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
        self.manager.current='preferences'

    def about_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        about_text=Label(
            text=current_language['about_overlay_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['about_text']=about_text
        about_text.ref='about_overlay_text'

        version_info=Label(text=current_language['version_info_white'],
                markup=True,
                pos_hint = {'x':-.05, 'center_y':.6})
        version_info.ref='version_info'

        about_qr=Image(source=qr_link,
            allow_stretch=False,
            keep_ratio=True,
            size_hint =(.45,.45),
            pos_hint = {'x':.6, 'y':.58})

        qr_label=Label(text='[size=16][color=#ffffff]firesafeextinguisher.com[/color][/size]',
                markup=True,
                pos_hint = {'x':.33, 'center_y':.55})
        qr_label.ref='qr_label'

        about_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['about_back_button']=about_back_button
        about_back_button.ref='about_back'

        def about_overlay_close(button):
            self.widgets['overlay_menu'].dismiss()
        about_back_button.bind(on_press=about_overlay_close)

        self.widgets['overlay_layout'].add_widget(about_text)
        self.widgets['overlay_layout'].add_widget(version_info)
        self.widgets['overlay_layout'].add_widget(about_qr)
        self.widgets['overlay_layout'].add_widget(qr_label)
        self.widgets['overlay_layout'].add_widget(about_back_button)
        self.widgets['overlay_menu'].open()

    def about_func (self,button):
        self.about_overlay()

class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super(ReportScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}

        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.widgets['bg_image']=bg_image

        back=RoundedButton(text=current_language['report_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_press=self.Report_back)

        back_main=RoundedButton(text=current_language['report_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_press=self.Report_back_main)

        date_label=DisplayLabel(
            text='',
            markup=True,
            size_hint =(.14, .05),
            pos_hint = {'center_x':.883, 'center_y':.843})
        self.widgets['date_label']=date_label

        pending_watermark=Label(
            text=current_language['pending_watermark'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.75})
        pending_watermark.opacity=.6
        self.widgets['pending_watermark']=pending_watermark
        pending_watermark.ref='pending_watermark'

        pending_watermark2=Label(
            text=current_language['pending_watermark'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.5})
        pending_watermark2.opacity=.6
        self.widgets['pending_watermark2']=pending_watermark2
        pending_watermark2.ref='pending_watermark'

        pending_watermark3=Label(
            text=current_language['pending_watermark'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.25})
        pending_watermark3.opacity=.6
        self.widgets['pending_watermark3']=pending_watermark3
        pending_watermark.ref='pending_watermark'

        report_image=Image(
            source=report_current,
            nocache=True)
        self.widgets['report_image']=report_image

        no_report_info_title=Label(
            text=current_language['no_report_info_title'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.85})
        self.widgets['no_report_info_title']=no_report_info_title
        no_report_info_title.ref='no_report_info_title'

        no_report_info=LabelColor(
            text=current_language['no_report_info'],
            halign="center",
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['no_report_info']=no_report_info
        no_report_info.ref='no_report_info'

        scroll_layout=RelativeLayout(
            size_hint_y=2.5,
            size_hint_x=.95)
        self.widgets['scroll_layout']=scroll_layout

        report_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=1,
            size_hint_x=.95,
            pos_hint = {'center_x':.525, 'center_y':.5})
        report_scroll.bar_color=(245/250, 216/250, 41/250,.75)
        report_scroll.bar_inactive_color=(245/250, 216/250, 41/250,.55)
        self.widgets['report_scroll']=report_scroll

        report_scatter = Scatter(
            size_hint=(None, None),
            size=self.widgets['report_image'].size,
            pos_hint = {'center_x':.5, 'center_y':.55},
            do_rotation=False,
            scale_min=1,
            scale_max=3,
            auto_bring_to_front=False)
        self.widgets['report_scatter']=report_scatter

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})
        self.widgets['seperator_line']=seperator_line

        self.add_widget(bg_image)
        scroll_layout.add_widget(report_image)
        scroll_layout.add_widget(date_label)
        report_scroll.add_widget(scroll_layout)
        if report_image.texture:
            self.add_widget(report_scroll)
        else:
            self.add_widget(no_report_info)
            self.add_widget(no_report_info_title)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(seperator_line)

    def check_pending(self):
        if App.get_running_app().report_pending==False:
            if self.widgets['pending_watermark'] in self.widgets['scroll_layout'].children:
                self.widgets['scroll_layout'].remove_widget(self.widgets['pending_watermark'])
                self.widgets['scroll_layout'].remove_widget(self.widgets['pending_watermark2'])
                self.widgets['scroll_layout'].remove_widget(self.widgets['pending_watermark3'])
        else:
            if self.widgets['pending_watermark'] not in self.widgets['scroll_layout'].children:
                self.widgets['scroll_layout'].add_widget(self.widgets['pending_watermark'])
                self.widgets['scroll_layout'].add_widget(self.widgets['pending_watermark2'])
                self.widgets['scroll_layout'].add_widget(self.widgets['pending_watermark3'])


    def on_enter(self):
        self.check_pending()
    def on_pre_enter(self):
        self.date_setter()
        self.widgets['report_image'].reload()
        self.refresh_widget()
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
    def refresh_widget(self):
        self.clear_widgets()
        self.add_widget(self.widgets['bg_image'])
        if self.widgets['report_image'].texture:
            self.add_widget(self.widgets['report_scroll'])
        else:
            self.add_widget(self.widgets['no_report_info'])
            self.add_widget(self.widgets['no_report_info_title'])
        self.add_widget(self.widgets['back'])
        self.add_widget(self.widgets['back_main'])
        self.add_widget(self.widgets['seperator_line'])

class DevicesScreen(Screen):
    def __init__(self, **kw):
        super(DevicesScreen,self).__init__(**kw)
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.widgets={}
        self.ud={}

        back=RoundedButton(text=current_language['report_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_press=self.devices_back)

        back_main=RoundedButton(text=current_language['report_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
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
            # size_hint_y=None,
            # size_hint_x=1,
            size_hint =(.9, .80),
            pos_hint = {'center_x':.5, 'y':.18})
        device_scroll.bar_color=(245/250, 216/250, 41/250,.75)
        device_scroll.bar_inactive_color=(245/250, 216/250, 41/250,.55)
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

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        device_layout.add_widget(device_details)
        device_scroll.add_widget(device_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(device_scroll)
        self.add_widget(seperator_line)

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

        info_admin_hint=ExactLabel(text=f"[size=18]Enable Admin mode to edit device[/size]",
                color=(0,0,0,1),
                pos_hint = {'x':.33, 'y':.18},
                markup=True)
        self.widgets['info_admin_hint']=info_admin_hint

        info_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .15),
                        pos_hint = {'x':.05, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=(255/255, 50/255, 50/255,.85),
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
        self.check_admin_mode()

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
                        background_color=(245/250, 216/250, 41/250,.9),
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
                self.color=(0/255, 0/255, 0/255,.85)
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
                        background_color=(255/255, 50/255, 50/255,.85),
                        markup=True)
        self.widgets['new_device_back_button']=new_device_back_button
        new_device_back_button.ref='about_back'
        new_device_back_button.bind(on_press=self.new_device_overlay_close)

        new_device_save_button=RoundedButton(text=current_language['save'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.55, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=(100/255, 255/255, 100/255,.85),
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
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="MAU":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Light":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Dry":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="GV":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Micro":
            current_device.color=(170/255, 0/255, 0/255,.85)
        elif value=="Heat":
            current_device.color=(0/255, 0/255, 0/255,.85)
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
                        background_color=(255/255, 50/255, 50/255,.85),
                        markup=True)
        self.widgets['edit_device_back_button']=edit_device_back_button
        edit_device_back_button.ref='about_back'
        edit_device_back_button.bind(on_press=partial(self.edit_device_overlay_close,device))

        edit_device_save_button=RoundedButton(text=current_language['save'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.55, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=(100/255, 255/255, 100/255,.85),
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
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="MAU":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Light":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Dry":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="GV":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Micro":
            current_device.color=(170/255, 0/255, 0/255,.85)
        elif value=="Heat":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Light Switch":
            current_device.color=(0/255, 0/255, 0/255,.85)
        elif value=="Fans Switch":
            current_device.color=(0/255, 0/255, 0/255,.85)
    def edit_device_pin_func(self,current_device,button,value):
        current_device.pin=int(value)


    def devices_back (self,button):
        self.widgets['device_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='settings'
    def devices_back_main (self,button):
        self.widgets['device_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def info_func (self,device,button):
        self.info_overlay(device)

    def aggregate_devices(self):
        logic.get_devices()
        if logic.devices:
            self.widgets['device_layout'].clear_widgets()
            for i in logic.devices:
                device=RoundedScrollItemTemplate(i.name,color=i.color)
                self.widgets['device_layout'].add_widget(device)
                device.bind(on_release=partial(self.info_func,i))
        else:
            print("main.py aggregate_devices(): no devices")
            self.widgets['device_layout'].clear_widgets()
            self.widgets['device_layout'].add_widget(self.widgets['device_details'])
        new_device=RoundedScrollItemTemplate(
                        '[/color][color=#000000]Add Device +',
                        color=(200/250, 200/250, 200/250,.85))
        self.widgets['device_layout'].add_widget(new_device)
        new_device.bind(on_release=self.new_device_func)

    def new_device_func(self,button):
        self.new_device_overlay()

    def check_admin_mode(self):
        if App.get_running_app().admin_mode_start>time.time():
            self.widgets['info_add_icon'].disabled=False
            self.widgets['delete_icon'].disabled=False
            self.widgets['info_add_icon'].color=(1,1,1,.5)
            self.widgets['delete_icon'].color=(1,1,1,.8)
            self.widgets['overlay_layout'].remove_widget(self.widgets['info_admin_hint'])

        else:
            self.widgets['overlay_layout'].add_widget(self.widgets['info_admin_hint'])
            self.widgets['info_add_icon'].disabled=True
            self.widgets['delete_icon'].disabled=True
            self.widgets['info_add_icon'].color=(1,1,1,.15)
            self.widgets['delete_icon'].color=(1,1,1,.15)

    def on_pre_enter(self):
        self.aggregate_devices()

class TrainScreen(Screen):
    def __init__(self, **kw):
        super(TrainScreen,self).__init__(**kw)
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.widgets={}

        back=RoundedButton(text=current_language['report_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_press=self.train_back)

        back_main=RoundedButton(text=current_language['report_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
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

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        train_layout.add_widget(train_details)
        train_scroll.add_widget(train_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(train_scroll)
        self.add_widget(seperator_line)

    def train_back (self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def train_back_main (self,button):
            self.parent.transition = SlideTransition(direction='down')
            self.manager.current='main'

class PreferenceScreen(Screen):
    def __init__(self, **kwargs):
        super(PreferenceScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        self.ud={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.duration_flag=0

        back=RoundedButton(text=current_language['preferences_back'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.06, 'y':.015},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='preferences_back'
        back.bind(on_press=self.settings_back)

        back_main=RoundedButton(text=current_language['preferences_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_press=self.settings_back_main)

        pref_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint =(.9, .85),
            pos_hint = {'center_x':.5, 'y':.14})
        pref_scroll.bar_color=(245/250, 216/250, 41/250,.75)
        pref_scroll.bar_inactive_color=(245/250, 216/250, 41/250,.55)
        self.widgets['pref_scroll']=pref_scroll

        scroll_layout=EventpassGridLayout(
            size_hint_y=1.8,
            size_hint_x=.95,
            cols=1,
            padding=10,
            spacing=(1,35))
        self.widgets['scroll_layout']=scroll_layout
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        heat_sensor=RoundedButton(text=current_language['heat_sensor'],
                        size_hint =(1, 1),
                        #pos_hint = {'x':.01, 'y':.9},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['heat_sensor']=heat_sensor
        heat_sensor.ref='heat_sensor'
        heat_sensor.bind(on_release=self.heat_sensor_func)

        msg_center=RoundedButton(text=current_language['msg_center'],
                        size_hint =(1, 1),
                        #pos_hint = {'x':.01, 'y':.9},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['msg_center']=msg_center
        msg_center.ref='msg_center'
        msg_center.bind(on_release=self.msg_center_func)

        train=RoundedButton(text=current_language['train'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.6},
                        background_down='',
                        disabled=True,
                        background_color=(100/250, 100/250, 100/250,.9),
                        markup=True)
        self.widgets['train']=train
        train.ref='train'
        train.bind(on_release=self.train_func)

        about=RoundedButton(text=current_language['about'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.7},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['about']=about
        about.ref='about'
        about.bind(on_release=self.about_func)

        account=RoundedButton(text=current_language['account'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.7},
                        background_down='',
                        background_color=(100/250, 100/250, 100/250,.9),#(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['account']=account
        account.ref='account'
        account.bind(on_release=self.account_func)
        account.disabled=True

        clean_mode=RoundedButton(text=current_language['clean_mode'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.8},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['clean_mode']=clean_mode
        clean_mode.ref='clean_mode'
        clean_mode.bind(on_release=self.clean_mode_func)

        commission=RoundedButton(text=current_language['commission'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.5},
                        background_down='',
                        disabled=True,
                        background_color=(100/250, 100/250, 100/250,.9),
                        markup=True)
        self.widgets['commission']=commission
        commission.ref='commission'
        commission.bind(on_release=self.commission_func)

        pins=RoundedButton(text=current_language['pins'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.4},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['pins']=pins
        pins.ref='pins'
        pins.bind(on_release=self.pins_func)

        self.blur = EffectWidget()

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/bubble',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=[255/255, 0/255, 0/255, .5])
        self.widgets['overlay_menu']=overlay_menu
        overlay_menu.ref='heat_overlay'

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})


        overlay_menu.add_widget(overlay_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        scroll_layout.add_widget(heat_sensor)
        scroll_layout.add_widget(clean_mode)
        scroll_layout.add_widget(msg_center)
        scroll_layout.add_widget(train)
        scroll_layout.add_widget(commission)
        scroll_layout.add_widget(account)
        scroll_layout.add_widget(about)
        scroll_layout.add_widget(pins)
        pref_scroll.add_widget(scroll_layout)
        self.add_widget(pref_scroll)
        self.add_widget(seperator_line)

    def heat_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        overlay_title=Label(text=current_language['heat_overlay'],
                        pos_hint = {'x':.0, 'y':.5},
                        markup=True)
        self.widgets['overlay_title']=overlay_title
        overlay_title.ref='heat_overlay'

        duration_1=RoundedButton(text=current_language['duration_1'],
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.5},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['duration_1']=duration_1
        duration_1.ref='duration_1'

        duration_2=RoundedButton(text=current_language['duration_2'],
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.3},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['duration_2']=duration_2
        duration_1.ref='duration_2'

        duration_3=RoundedButton(text=current_language['duration_3'],
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.1},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['duration_3']=duration_3
        duration_1.ref='duration_3'

        def duration_1_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=300
            config.set('preferences','heat_timer','300')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_1.bind(on_release=duration_1_func)

        def duration_2_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=900
            config.set('preferences','heat_timer','900')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_2.bind(on_release=duration_2_func)

        def duration_3_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=1800
            config.set('preferences','heat_timer','1800')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_3.bind(on_release=duration_3_func)

        self.widgets['overlay_layout'].add_widget(overlay_title)
        self.widgets['overlay_layout'].add_widget(duration_1)
        self.widgets['overlay_layout'].add_widget(duration_2)
        self.widgets['overlay_layout'].add_widget(duration_3)
        self.widgets['overlay_menu'].open()

    def maint_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        warning_text=Label(
            text=current_language['maint_overlay_warning_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['warning_text']=warning_text
        warning_text.ref='maint_overlay_warning_text'

        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['continue_button']=continue_button
        continue_button.ref='continue_button'

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
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
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['warning_text']=warning_text
        warning_text.ref='override_overlay_warning_text'

        disable_button=RoundedButton(text=current_language['disable_button'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
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

        disable_progress=CircularProgressBar()
        disable_progress._widget_size=200
        disable_progress._progress_colour=(245/250, 216/250, 41/250,1)
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
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['about_text']=about_text
        about_text.ref='about_overlay_text'

        version_info=Label(text=current_language['version_info_white'],
                markup=True,
                pos_hint = {'x':-.05, 'center_y':.6})
        version_info.ref='version_info'

        about_qr=Image(source=qr_link,
            allow_stretch=False,
            keep_ratio=True,
            size_hint =(.45,.45),
            pos_hint = {'x':.6, 'y':.58})

        qr_label=Label(text='[size=16][color=#ffffff]firesafeextinguisher.com[/color][/size]',
                markup=True,
                pos_hint = {'x':.33, 'center_y':.55})
        qr_label.ref='qr_label'

        about_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['about_back_button']=about_back_button
        about_back_button.ref='about_back'

        def about_overlay_close(button):
            self.widgets['overlay_menu'].dismiss()
        about_back_button.bind(on_press=about_overlay_close)

        self.widgets['overlay_layout'].add_widget(about_text)
        self.widgets['overlay_layout'].add_widget(version_info)
        self.widgets['overlay_layout'].add_widget(about_qr)
        self.widgets['overlay_layout'].add_widget(qr_label)
        self.widgets['overlay_layout'].add_widget(about_back_button)
        self.widgets['overlay_menu'].open()

    def msg_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        config=App.get_running_app().config_

        with overlay_menu.canvas.before:
           overlay_menu.msg_lines=Line(rounded_rectangle=(100, 100, 200, 200, 10, 10, 10, 10, 100),group='msg')

        def update_lines(*args):
            x=int(overlay_menu.width*.2)
            y=int(overlay_menu.height*.5)
            width=int(overlay_menu.width*.25)
            height=int(overlay_menu.height*.5)
            overlay_menu.msg_lines.rounded_rectangle=(x, y, width, height, 10, 10, 10, 10, 100)
        overlay_menu.bind(pos=update_lines, size=update_lines)

        # canvas is drawn to before widgets pos and size are set by parent.
        # update lines is bound to listen for changes to size and pos so it
        # can be updated accordingly.
        # however since the overlay is shared between different menus it does
        # not update its pos again after the drawing instructions are cleared,
        # this leads to the lines being drawn wrong again.
        # we call update_lines() while adding our message widgets to the overlay
        # to reposition the lines correctly before opening
        update_lines()

        def _swap_color(button,*args):
            if button.state=='down':
                button.bg_color=(245/250, 216/250, 41/250,.85)
            if button.state=='normal':
                button.bg_color=(.5,.5,.5,1)


        overlay_title=Label(text=current_language['msg_overlay'],
                        pos_hint = {'x':.0, 'y':.5},
                        markup=True)
        self.widgets['overlay_title']=overlay_title
        overlay_title.ref='msg_overlay'

        evoke_title=Label(text=current_language['evoke_title'],
                        pos_hint = {'center_x':.2, 'center_y':.88},
                        markup=True)
        self.widgets['evoke_title']=evoke_title
        evoke_title.ref='evoke_title'

        msg_evoke_on=RoundedToggleButton(text=current_language['msg_evoke_on'],
                        size_hint =(.2, .125),
                        pos_hint = {'center_x':.2, 'y':.65},
                        background_down='',
                        background_color=(.5,.5,.5,.85),
                        markup=True,
                        group='evoke',
                        allow_no_selection=False)
        self.widgets['msg_evoke_on']=msg_evoke_on
        msg_evoke_on.ref='msg_evoke_on'
        msg_evoke_on.unbind(state=msg_evoke_on.color_swap)
        msg_evoke_on.bind(state=_swap_color)
        msg_evoke_on.bind(state=msg_evoke_on.color_swap)

        msg_evoke_off=RoundedToggleButton(text=current_language['msg_evoke_off'],
                        size_hint =(.2, .125),
                        pos_hint = {'center_x':.2, 'y':.45},
                        background_down='',
                        background_color=(.5,.5,.5,.85),
                        markup=True,
                        group='evoke',
                        allow_no_selection=False)
        self.widgets['msg_evoke_off']=msg_evoke_off
        msg_evoke_off.ref='msg_evoke_off'
        msg_evoke_off.unbind(state=msg_evoke_off.color_swap)
        msg_evoke_off.bind(state=_swap_color)
        msg_evoke_off.bind(state=msg_evoke_off.color_swap)

        is_evoke=config.getboolean('preferences','evoke')
        if is_evoke:
            msg_evoke_on.state='down'
            _swap_color(msg_evoke_off)
        else:
            msg_evoke_off.state='down'
            _swap_color(msg_evoke_on)


        def msg_evoke_on_func(button):
            config.set('preferences','evoke','True')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
        msg_evoke_on.bind(on_release=msg_evoke_on_func)

        def msg_evoke_off_func(button):
            config.set('preferences','evoke','False')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
        msg_evoke_off.bind(on_release=msg_evoke_off_func)


        def on_dismiss(self,*args):
            overlay_menu.canvas.before.remove_group("msg")

        self.widgets['overlay_layout'].add_widget(overlay_title)
        self.widgets['overlay_layout'].add_widget(evoke_title)
        self.widgets['overlay_layout'].add_widget(msg_evoke_on)
        self.widgets['overlay_layout'].add_widget(msg_evoke_off)
        overlay_menu.bind(on_dismiss=on_dismiss)
        overlay_menu.open()

    def settings_back(self,button):
        self.widgets['pref_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='settings'
    def settings_back_main(self,button):
        self.widgets['pref_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def heat_sensor_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.heat_overlay()
    def msg_center_func(self,button):
        self.msg_overlay()
    def train_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='train'
    def about_func (self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.about_overlay()
    def account_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='account'
    def clean_mode_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.maint_overlay()
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
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['pin_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='pin_back'
        back.bind(on_press=self.Pin_back)

        back_main=RoundedButton(text=current_language['pin_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
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
            background_color=(255/255, 100/255, 100/255,.85),
            markup=True)
        self.widgets['backspace']=backspace
        backspace.bind(on_release=self.backspace_func)

        enter=RoundedButton(text="[size=35][b][color=#000000] -> [/color][/b][/size]",
            size_hint =(.15, .75),
            pos_hint = {'x':.6, 'y':.25},
            background_down='',
            background_color=(100/255, 255/255, 100/255,.85),
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
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['reset_text']=reset_text
        reset_text.ref='reset_text'

        reset_confirm=RoundedButton(text=current_language['reset_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['reset_confirm']=reset_confirm
        reset_confirm.ref='reset_confirm'

        reset_cancel=RoundedButton(text=current_language['reset_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['reset_cancel']=reset_cancel
        reset_cancel.ref='reset_cancel'

        def reset_confirm_func(button):
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
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['date_text']=date_text
        date_text.ref='date_text'

        date_confirm=RoundedButton(text=current_language['date_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['date_confirm']=date_confirm
        date_confirm.ref='date_confirm'

        date_cancel=RoundedButton(text=current_language['date_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
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
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['heat_override_text']=heat_override_text
        heat_override_text.ref='heat_override_text'

        heat_override_confirm=RoundedButton(text=current_language['heat_override_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['heat_override_confirm']=heat_override_confirm
        heat_override_confirm.ref='heat_override_confirm'

        heat_override_cancel=RoundedButton(text=current_language['heat_override_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['heat_override_cancel']=heat_override_cancel
        heat_override_cancel.ref='heat_override_cancel'

        def heat_override_confirm_func(button):
            logic.heat_sensor_timer=10
            config=self.root.config_
            config.set('preferences','heat_timer','10')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            self.widgets['heat_override_overlay'].dismiss()
        heat_override_confirm.bind(on_release=heat_override_confirm_func)

        def heat_override_cancel_func(button):
            self.widgets['heat_override_overlay'].dismiss()
        heat_override_cancel.bind(on_release=heat_override_cancel_func)

        admin_overlay=PinPop('admin')
        self.popups.append(admin_overlay)
        self.widgets['admin_overlay']=admin_overlay
        admin_overlay.ref='admin_overlay'
        admin_overlay.widgets['overlay_layout']=admin_overlay.overlay_layout

        admin_text=Label(
            text=current_language['admin_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['admin_text']=admin_text
        admin_text.ref='admin_text'

        admin_confirm=RoundedButton(text=current_language['admin_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['admin_confirm']=admin_confirm
        admin_confirm.ref='admin_confirm'

        admin_cancel=RoundedButton(text=current_language['admin_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['admin_cancel']=admin_cancel
        admin_cancel.ref='admin_cancel'

        def admin_confirm_func(button):
            App.get_running_app().admin_mode_start=time.time()+900#admin mode lasts 15 minutes
            self.widgets['admin_overlay'].dismiss()
        admin_confirm.bind(on_release=admin_confirm_func)

        def admin_cancel_func(button):
            self.widgets['admin_overlay'].dismiss()
        admin_cancel.bind(on_release=admin_cancel_func)

        report_pending_overlay=PinPop('report_pending')
        self.popups.append(report_pending_overlay)
        self.widgets['report_pending_overlay']=report_pending_overlay
        report_pending_overlay.ref='report_pending_overlay'
        report_pending_overlay.widgets['overlay_layout']=report_pending_overlay.overlay_layout

        report_pending_text=Label(
            text=current_language['report_pending_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['report_pending_text']=report_pending_text
        report_pending_text.ref='report_pending_text'

        report_pending_confirm=RoundedButton(text=current_language['report_pending_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['report_pending_confirm']=report_pending_confirm
        report_pending_confirm.ref='report_pending_confirm'

        report_pending_cancel=RoundedButton(text=current_language['report_pending_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['report_pending_cancel']=report_pending_cancel
        report_pending_cancel.ref='report_pending_cancel'

        def report_pending_confirm_func(button):
            if App.get_running_app().report_pending==True:
                App.get_running_app().report_pending=False
            else:
                App.get_running_app().report_pending=True
            report_pending_setter_func()
            self.widgets['report_pending_overlay'].dismiss()
        report_pending_confirm.bind(on_release=report_pending_confirm_func)

        def report_pending_cancel_func(button):
            self.widgets['report_pending_overlay'].dismiss()
        report_pending_cancel.bind(on_release=report_pending_cancel_func)

        def report_pending_setter_func():
            config=App.get_running_app().config_
            config.set('config','report_pending',f'{App.get_running_app().report_pending}')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)

        mount_overlay=PinPop('mount')
        self.popups.append(mount_overlay)
        self.widgets['mount_overlay']=mount_overlay
        mount_overlay.ref='mount_overlay'
        mount_overlay.widgets['overlay_layout']=mount_overlay.overlay_layout

        mount_text=Label(
            text=current_language['mount_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['mount_text']=mount_text
        mount_text.ref='mount_text'

        mount_confirm=RoundedButton(text=current_language['mount_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['mount_confirm']=mount_confirm
        mount_confirm.ref='mount_confirm'

        mount_cancel=RoundedButton(text=current_language['mount_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['mount_cancel']=mount_cancel
        mount_cancel.ref='mount_cancel'

        def mount_confirm_func(button):
            self.widgets['mount_overlay'].dismiss()
            self.parent.transition = SlideTransition(direction='left')
            self.manager.current='mount'
        mount_confirm.bind(on_release=mount_confirm_func)

        def mount_cancel_func(button):
            self.widgets['mount_overlay'].dismiss()
        mount_cancel.bind(on_release=mount_cancel_func)

        self.widgets['reset_overlay'].widgets['overlay_layout'].add_widget(reset_text)
        self.widgets['reset_overlay'].widgets['overlay_layout'].add_widget(reset_confirm)
        self.widgets['reset_overlay'].widgets['overlay_layout'].add_widget(reset_cancel)
        self.widgets['date_overlay'].widgets['overlay_layout'].add_widget(date_text)
        self.widgets['date_overlay'].widgets['overlay_layout'].add_widget(date_confirm)
        self.widgets['date_overlay'].widgets['overlay_layout'].add_widget(date_cancel)
        self.widgets['heat_override_overlay'].widgets['overlay_layout'].add_widget(heat_override_text)
        self.widgets['heat_override_overlay'].widgets['overlay_layout'].add_widget(heat_override_confirm)
        self.widgets['heat_override_overlay'].widgets['overlay_layout'].add_widget(heat_override_cancel)
        self.widgets['admin_overlay'].widgets['overlay_layout'].add_widget(admin_text)
        self.widgets['admin_overlay'].widgets['overlay_layout'].add_widget(admin_confirm)
        self.widgets['admin_overlay'].widgets['overlay_layout'].add_widget(admin_cancel)
        self.widgets['report_pending_overlay'].widgets['overlay_layout'].add_widget(report_pending_text)
        self.widgets['report_pending_overlay'].widgets['overlay_layout'].add_widget(report_pending_confirm)
        self.widgets['report_pending_overlay'].widgets['overlay_layout'].add_widget(report_pending_cancel)
        self.widgets['mount_overlay'].widgets['overlay_layout'].add_widget(mount_text)
        self.widgets['mount_overlay'].widgets['overlay_layout'].add_widget(mount_confirm)
        self.widgets['mount_overlay'].widgets['overlay_layout'].add_widget(mount_cancel)

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

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
        self.add_widget(seperator_line)

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
            timestamp=datetime.now()
            timestamp=timestamp.replace(day=1,month=int(month),year=int(year))
            config.set('timestamps','System Inspection',f'{timestamp }')
            with open(preferences_path,'w') as configfile:
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
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text="[size=50][b][color=#000000]  Back [/color][/b][/size]",
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_press=self.Report_back)

        back_main=RoundedButton(text="[size=50][b][color=#000000]  Close Menu [/color][/b][/size]",
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_press=self.Report_back_main)

        doc_pages=PageLayout()

        test1=ScatterImage(
            source=report_current,
            size_hint_x = .95,
            pos_hint = {'center_x':.5, 'y':.18},
            do_rotation=False,
            scale_min=.5,
            scale_max=3.)

        test2=Image(source=report_current)

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        self.add_widget(bg_image)
        self.add_widget(test1)
        self.add_widget(seperator_line)
        # doc_pages.add_widget(test2)
        # self.add_widget(doc_pages)

        # left_arrow=IconButton(source=left_arrow_image,
        #                 size_hint =(.4, .25),
        #                 pos_hint = {'x':-.1, 'center_y':.55})
        # self.widgets['left_arrow']=left_arrow
        # left_arrow.bind(on_press=self.left_arrow_func)

        # right_arrow=IconButton(source=right_arrow_image,
        #                 size_hint =(.4, .25),
        #                 pos_hint = {'x':.7, 'center_y':.55})
        # self.widgets['right_arrow']=right_arrow
        # right_arrow.bind(on_press=self.right_arrow_func)

        # report_scroll=ScrollView(
        #     bar_width=8,
        #     bar_margin=20,
        #     do_scroll_y=True,
        #     do_scroll_x=False,
        #     size_hint_y=1,
        #     size_hint_x=1)
        # self.widgets['report_scroll']=report_scroll

        # report_image=IconButton(
        #     source=report_current,
        #     size_hint_y=2,
        #     size_hint_x=.95,
        #     pos_hint = {'center_x':.5, 'y':1})

        # report_scroll2=ScrollView(
        #     bar_width=8,
        #     bar_margin=20,
        #     do_scroll_y=True,
        #     do_scroll_x=False,
        #     size_hint_y=1,
        #     size_hint_x=1)
        # self.widgets['report_scroll2']=report_scroll2

        # report_image2=IconButton(
        #     source=report_original,
        #     size_hint_y=2,
        #     size_hint_x=.98)

        # report_pages=Carousel(loop=True,
        # scroll_distance=5000,
        # scroll_timeout=1,
        # size_hint =(1, .75),
        # pos_hint = {'center_x':.5, 'center_y':.60}
        # )
        # self.widgets['report_pages']=report_pages

        # stock_photo=Image(source=stock_photo_test)

        
        # report_scroll.add_widget(report_image)
        # report_scroll2.add_widget(report_image2)

        # report_pages.add_widget(report_scroll)
        # report_pages.add_widget(report_scroll2)
        # report_pages.add_widget(stock_photo)
        # self.add_widget(report_pages)
        self.add_widget(back)
        self.add_widget(back_main)
        # self.add_widget(left_arrow)
        # self.add_widget(right_arrow)

    def Report_back (self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def Report_back_main (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    # def left_arrow_func(self,*args):
    #         self.widgets['report_pages'].load_previous()
    # def right_arrow_func(self,*args):
    #         self.widgets['report_pages'].load_next()

class TroubleScreen(Screen):
    def __init__(self, **kwargs):
        super(TroubleScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['trouble_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.02, 'y':.015},
                    background_down='',
                    background_color=(200/250, 200/250, 200/250,.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='trouble_back'
        back.bind(on_press=self.trouble_back)

        trouble_details=trouble_template('no_trouble')
        self.widgets['trouble_details']=trouble_details
        trouble_details.ref='no_trouble'

        trouble_layout=GridLayout(
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

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        self.add_widget(trouble_scroll)
        self.add_widget(back)
        self.add_widget(seperator_line)

    def trouble_back (self,button):
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='main'

class MountScreen(Screen):
    def __init__(self, **kw):
        super(MountScreen,self).__init__(**kw)
        self.rename_text=''
        if os.name=='nt':
            self.internal_path=r'logs'
            self.external_path=r'logs'
        else:
            self.internal_path=r'/home/pi/Pi-ro-safe/logs'
            self.external_path=r'/media/pi'
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['preferences_back'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.06, 'y':.015},
                        background_down='',
                        background_color=(200/250, 200/250, 200/250,.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='preferences_back'
        back.bind(on_press=self.settings_back)

        back_main=RoundedButton(text=current_language['preferences_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_press=self.settings_back_main)

        file_selector_external=FileChooserIconView(
            dirselect=True,
            rootpath=self.external_path)
        self.widgets['file_selector_external']=file_selector_external

        file_layout_external=BoxLayoutColor(
            orientation='vertical',
            size_hint =(.4, .45),
            pos_hint = {'center_x':.75, 'y':.5})

        internal_label=Label(
            text=current_language['internal_label'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.25, 'y':.95},)
        self.widgets['internal_label']=internal_label
        internal_label.ref='internal_label'

        file_selector_internal=FileChooserIconView(
            dirselect=True,
            rootpath=(self.internal_path))
        self.widgets['file_selector_internal']=file_selector_internal

        file_layout_internal=BoxLayoutColor(
            orientation='vertical',
            size_hint =(.4, .45),
            pos_hint = {'center_x':.25, 'y':.5})

        external_label=Label(
            text=current_language['external_label'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.75, 'y':.95},)
        self.widgets['external_label']=external_label
        external_label.ref='external_label'

        instruction_label=LabelColor(
            text=current_language['instruction_label'],
            markup=True,
            size_hint =(.4, .35),
            pos_hint = {'center_x':.25, 'y':.14},)
        self.widgets['instruction_label']=instruction_label
        instruction_label.ref='instruction_label'

        import_button=RoundedButton(text=current_language['import_button'],
            size_hint =(.19, .1),
            pos_hint = {'center_x':.645, 'y':.39},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.9),
            markup=True)
        self.widgets['import_button']=import_button
        import_button.ref='import_button'
        import_button.bind(on_press=self.import_button_func)

        export_button=RoundedButton(text=current_language['export_button'],
            size_hint =(.19, .1),
            pos_hint = {'center_x':.855, 'y':.39},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.9),
            markup=True)
        self.widgets['export_button']=export_button
        export_button.ref='export_button'
        export_button.bind(on_press=self.export_button_func)

        rename_button=RoundedButton(text=current_language['rename_button'],
            size_hint =(.19, .1),
            pos_hint = {'center_x':.645, 'y':.265},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.9),
            markup=True)
        self.widgets['rename_button']=rename_button
        rename_button.ref='rename_button'
        rename_button.bind(on_press=self.rename_button_func)

        del_button=RoundedButton(text=current_language['del_button'],
            size_hint =(.19, .1),
            pos_hint = {'center_x':.855, 'y':.265},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.9),
            markup=True)
        self.widgets['del_button']=del_button
        del_button.ref='del_button'
        del_button.bind(on_press=self.del_button_func)

        refresh_button=RoundedButton(text=current_language['refresh_button'],
            size_hint =(.4, .1),
            pos_hint = {'center_x':.75, 'y':.14},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.9),
            markup=True)
        self.widgets['refresh_button']=refresh_button
        refresh_button.ref='refresh_button'
        refresh_button.bind(on_press=self.refresh_button_func)

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/bubble',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=[255/255, 0/255, 0/255, .5])
        self.widgets['overlay_menu']=overlay_menu
        overlay_menu.ref='heat_overlay'

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        seperator_line=Image(source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.98, .001),
            pos_hint = {'x':.01, 'y':.13})

        file_layout_external.add_widget(file_selector_external)
        file_layout_internal.add_widget(file_selector_internal)
        overlay_menu.add_widget(overlay_layout)
        self.add_widget(bg_image)
        self.add_widget(internal_label)
        self.add_widget(external_label)
        self.add_widget(file_layout_external)
        self.add_widget(file_layout_internal)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(seperator_line)
        self.add_widget(instruction_label)
        self.add_widget(import_button)
        self.add_widget(export_button)
        self.add_widget(rename_button)
        self.add_widget(del_button)
        self.add_widget(refresh_button)

    def import_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        internal_selection=self.widgets['file_selector_internal'].selection[0] if self.widgets['file_selector_internal'].selection else self.widgets['file_selector_internal'].selection
        external_selection=self.widgets['file_selector_external'].selection[0] if self.widgets['file_selector_external'].selection else self.widgets['file_selector_external'].selection
        #ensure that only one selection is made
        if external_selection:
            #internal selection can be cwd, so with external selection we have double selection
            double_selection=True
        else:
            #no external selection made
            double_selection=False

        if self.widgets['file_selector_internal'].selection:
                #overwrite selection
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                dst_path=self.widgets['file_selector_internal'].selection[0]
        else:
            #can copy to cwd(current working directory)
            dst_path=self.widgets['file_selector_internal'].path

        import_text=Label(
            text=current_language['import_text']+f'[size=26]{os.path.basename(external_selection)}({general.file_or_dir(external_selection)}) >> {os.path.basename(dst_path)}({general.file_or_dir(dst_path)})?[/size]' if double_selection else current_language['import_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['import_text']=import_text
        import_text.ref='import_text' if double_selection else 'import_text_fail'

        import_unique_text=Label(
            text='',
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['import_unique_text']=import_unique_text

        background_state='background_normal' if double_selection else 'background_down'
        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on double_slection value
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['continue_button']=continue_button
        continue_button.ref='continue_button'
        if double_selection:
            continue_button.disabled=False
        else:
            continue_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            try:
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                src=self.widgets['file_selector_external'].selection[0]
            except IndexError:
                print('main.py MountScreen import_button_func(): src not selected')
                self.widgets['import_unique_text'].text="[size=20][color=#ffffff]You must make a selection from external storage to import[/color][/size]"
                return
            if self.widgets['file_selector_internal'].selection:
                #overwrite selection
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                dst=self.widgets['file_selector_internal'].selection[0]
            else:
                #can copy to cwd(current working directory)
                dst=self.widgets['file_selector_internal'].path

            if os.path.isdir(src):
                if os.path.isdir(dst):
                    dst=os.path.join(dst,os.path.basename(os.path.normpath(src)))
                else:
                    print('main.py MountScreen import_button_func(): can not copy dir over file')
                    self.widgets['import_unique_text'].text="[size=20][color=#ffffff]Can not overwrite a file with a folder[/color][/size]"
                    return
            try:
                shutil.copytree(src, dst,dirs_exist_ok=True)
            except OSError as exc:
                if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                    shutil.copy(src, dst)
                else: raise
            self.refresh_button_func()
            self.widgets['overlay_menu'].dismiss()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.refresh_button_func()
            self.widgets['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        self.widgets['overlay_layout'].add_widget(import_text)
        self.widgets['overlay_layout'].add_widget(import_unique_text)
        self.widgets['overlay_layout'].add_widget(continue_button)
        self.widgets['overlay_layout'].add_widget(cancel_button)
        self.widgets['overlay_menu'].open()

    def export_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        internal_selection=self.widgets['file_selector_internal'].selection[0] if self.widgets['file_selector_internal'].selection else self.widgets['file_selector_internal'].selection
        external_selection=self.widgets['file_selector_external'].selection[0] if self.widgets['file_selector_external'].selection else self.widgets['file_selector_external'].selection
        #ensure that only one selection is made
        if internal_selection:
            #external selection can be cwd, so with internal selection we have double selection
            double_selection=True
        else:
            #no internal selection made
            double_selection=False

        if self.widgets['file_selector_external'].selection:
                #overwrite selection
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                dst_path=self.widgets['file_selector_external'].selection[0]
        else:
            #can copy to cwd(current working directory)
            dst_path=self.widgets['file_selector_external'].path

        export_text=Label(
            text=current_language['export_text']+f'[size=26]{os.path.basename(internal_selection)}({general.file_or_dir(internal_selection)}) >> {os.path.basename(dst_path)}({general.file_or_dir(dst_path)})?[/size]' if double_selection else current_language['export_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['export_text']=export_text
        export_text.ref='export_text' if double_selection else 'export_text_fail'

        export_unique_text=Label(
            text='',
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['export_unique_text']=export_unique_text

        background_state='background_normal' if double_selection else 'background_down'
        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on double_slection value
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['continue_button']=continue_button
        continue_button.ref='continue_button'
        if double_selection:
            continue_button.disabled=False
        else:
            continue_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            try:
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                src=self.widgets['file_selector_internal'].selection[0]
            except IndexError:
                print('main.py MountScreen export_button_func(): src not selected')
                self.widgets['export_unique_text'].text="[size=20][color=#ffffff]You must make a selection from internal storage to export[/color][/size]"
                return
            if self.widgets['file_selector_external'].selection:
                #overwrite selection
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                dst=self.widgets['file_selector_external'].selection[0]
            else:
                #can copy to cwd(current working directory)
                dst=self.widgets['file_selector_external'].path

            if os.path.isdir(src):
                if os.path.isdir(dst):
                    dst=os.path.join(dst,os.path.basename(os.path.normpath(src)))
                else:
                    print('main.py MountScreen export_button_func(): can not copy dir over file')
                    self.widgets['export_unique_text'].text="[size=20][color=#ffffff]Can not overwrite a file with a folder[/color][/size]"
                    return
            try:
                shutil.copytree(src, dst,dirs_exist_ok=True)
            except OSError as exc:
                if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                    shutil.copy(src, dst)
                else: raise
            self.refresh_button_func()
            self.widgets['overlay_menu'].dismiss()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.refresh_button_func()
            self.widgets['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        self.widgets['overlay_layout'].add_widget(export_text)
        self.widgets['overlay_layout'].add_widget(export_unique_text)
        self.widgets['overlay_layout'].add_widget(continue_button)
        self.widgets['overlay_layout'].add_widget(cancel_button)
        self.widgets['overlay_menu'].open()

    def del_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        internal_selection=self.widgets['file_selector_internal'].selection[0] if self.widgets['file_selector_internal'].selection else self.widgets['file_selector_internal'].selection
        external_selection=self.widgets['file_selector_external'].selection[0] if self.widgets['file_selector_external'].selection else self.widgets['file_selector_external'].selection
        #ensure that only one selection is made
        if bool(external_selection)^bool(internal_selection):
            single_selection=True
            selected_item_path=internal_selection if internal_selection else external_selection
            selected_item=os.path.basename(internal_selection) if internal_selection else os.path.basename(external_selection)
            view_port=self.widgets['file_selector_internal'] if self.widgets['file_selector_internal'].selection else self.widgets['file_selector_external']
            if selected_item_path == view_port.path or selected_item_path == self.internal_path or selected_item_path == self.external_path:
                #opening or closing a folder sets selection to cwd,
                #although that is a single selection it is undesirable to
                #delete the cwd so we treat it as unselected
                single_selection=False
        else:
            #selected multiple files or no selection made
            single_selection=False

        del_text=Label(
            text=current_language['del_text']+f'[size=26]{selected_item}?[/size]' if single_selection else current_language['del_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['del_text']=del_text
        del_text.ref='del_text' if single_selection else 'del_text_fail'

        background_state='background_normal' if single_selection else 'background_down'
        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on single_slection value
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['continue_button']=continue_button
        continue_button.ref='continue_button'
        if single_selection:
            continue_button.disabled=False
        else:
            continue_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            if os.path.isdir(selected_item_path):
                shutil.rmtree(selected_item_path)
            else:
                os.remove(selected_item_path)
            self.refresh_button_func()
            self.widgets['overlay_menu'].dismiss()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.refresh_button_func()
            self.widgets['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        self.widgets['overlay_layout'].add_widget(del_text)
        self.widgets['overlay_layout'].add_widget(continue_button)
        self.widgets['overlay_layout'].add_widget(cancel_button)
        self.widgets['overlay_menu'].open()

    def rename_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        internal_selection=self.widgets['file_selector_internal'].selection[0] if self.widgets['file_selector_internal'].selection else self.widgets['file_selector_internal'].selection
        external_selection=self.widgets['file_selector_external'].selection[0] if self.widgets['file_selector_external'].selection else self.widgets['file_selector_external'].selection
        #ensure that only one selection is made
        if bool(external_selection)^bool(internal_selection):
            single_selection=True
            selected_item_path=internal_selection if internal_selection else external_selection
            selected_item=os.path.basename(internal_selection) if internal_selection else os.path.basename(external_selection)
            view_port=self.widgets['file_selector_internal'] if self.widgets['file_selector_internal'].selection else self.widgets['file_selector_external']
            if selected_item_path == view_port.path or selected_item_path == self.internal_path or selected_item_path == self.external_path:
                #opening or closing a folder sets selection to cwd,
                #although that is a single selection it is undesirable to
                #rename the cwd so we treat it as unselected
                single_selection=False
        else:
            #selected multiple files or no selection made
            single_selection=False

        rename_text=Label(
            text=current_language['rename_text']+f'[size=26]{selected_item}?[/size]' if single_selection else current_language['rename_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['rename_text']=rename_text
        rename_text.ref='rename_text' if single_selection else 'rename_text_fail'

        background_state='background_normal' if single_selection else 'background_down'
        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on single_slection value
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['continue_button']=continue_button
        continue_button.ref='continue_button'
        if single_selection:
            continue_button.disabled=False
        else:
            continue_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            self.rename_input_overlay()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.refresh_button_func()
            self.widgets['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        self.widgets['overlay_layout'].add_widget(rename_text)
        self.widgets['overlay_layout'].add_widget(continue_button)
        self.widgets['overlay_layout'].add_widget(cancel_button)
        self.widgets['overlay_menu'].open()

    def rename_input_overlay(self):
        self.rename_text=''
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=(0,0,0,.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        internal_selection=self.widgets['file_selector_internal'].selection[0] if self.widgets['file_selector_internal'].selection else self.widgets['file_selector_internal'].selection
        external_selection=self.widgets['file_selector_external'].selection[0] if self.widgets['file_selector_external'].selection else self.widgets['file_selector_external'].selection
        #ensure that only one selection is made
        if bool(external_selection)^bool(internal_selection):
            single_selection=True
            selected_item_path=internal_selection if internal_selection else external_selection
            selected_item=os.path.basename(internal_selection) if internal_selection else os.path.basename(external_selection)
            view_port=self.widgets['file_selector_internal'] if self.widgets['file_selector_internal'].selection else self.widgets['file_selector_external']
            if selected_item_path == view_port.path or selected_item_path == self.internal_path or selected_item_path == self.external_path:
                #opening or closing a folder sets selection to cwd,
                #although that is a single selection it is undesirable to
                #rename the cwd so we treat it as unselected
                single_selection=False
        else:
            #selected multiple files or no selection made
            single_selection=False

        rename_input_text=Label(
            text=current_language['rename_input_text']+f'[size=26]{selected_item}[/size]' if single_selection else current_language['rename_input_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.65},)
        self.widgets['rename_input_text']=rename_input_text
        rename_input_text.ref='rename_input_text' if single_selection else 'rename_input_text_fail'

        rename_unique_text=Label(
            text=current_language['rename_unique_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['rename_unique_text']=rename_unique_text
        rename_unique_text.ref='rename_unique_text'

        get_name=TextInput(multiline=False,
                        focus=False,
                        hint_text="Enter new file/folder name",
                        font_size=26,
                        size_hint =(.5, .1),
                        pos_hint = {'center_x':.50, 'center_y':.65})
        self.widgets['get_name']=get_name
        get_name.bind(on_text_validate=partial(self.get_name_func))
        get_name.bind(text=partial(self.get_name_func))

        background_state='background_normal' if single_selection else 'background_down'
        save_button=RoundedButton(text=current_language['save_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on single_slection value
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['save_button']=save_button
        save_button.ref='save_button'
        if single_selection:
            save_button.disabled=False
        else:
            save_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=(245/250, 216/250, 41/250,.85),
                        markup=True)
        self.widgets['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def save_button_func(path,button,*args):
            if self.rename_text:
                new_path=os.path.join(os.path.dirname(path),self.rename_text)
                try:
                    os.rename(path,new_path)
                    self.refresh_button_func()
                    self.widgets['overlay_menu'].dismiss()
                except FileExistsError:
                    if not self.widgets['rename_unique_text'].parent:
                        self.widgets['overlay_layout'].add_widget(self.widgets['rename_unique_text'])
                    self.widgets['get_name'].text=''
            else:
                if not self.widgets['rename_unique_text'].parent:
                        self.widgets['overlay_layout'].add_widget(self.widgets['rename_unique_text'])

        save_button.bind(on_release=partial(save_button_func,selected_item_path))

        def cancel_button_func(button):
            self.refresh_button_func()
            self.widgets['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        self.widgets['overlay_layout'].add_widget(rename_input_text)
        self.widgets['overlay_layout'].add_widget(get_name)
        self.widgets['overlay_layout'].add_widget(save_button)
        self.widgets['overlay_layout'].add_widget(cancel_button)

    def get_name_func(self,button,*args):
        self.rename_text=button.text

    def settings_back(self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='pin'
    def settings_back_main(self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    def import_button_func(self,button):
        self.import_overlay()
    def export_button_func(self,*args):
        self.export_overlay()
    def rename_button_func(self,*args):
        self.rename_overlay()
    def del_button_func(self,*args):
        self.del_overlay()
    def refresh_button_func(self,*args):
        self.widgets['file_selector_external']._update_files()
        self.widgets['file_selector_internal']._update_files()
        self.widgets['file_selector_external'].selection=[]
        self.widgets['file_selector_internal'].selection=[]

class AccountScreen(Screen):
    def __init__(self, **kwargs):
        super(AccountScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(
            text=current_language['settings_back'],
            size_hint =(.4, .1),
            pos_hint = {'x':.06, 'y':.015},
            background_down='',
            background_color=(200/255, 200/255, 200/255,.9),
            markup=True)
        self.widgets['back']=back
        back.ref='settings_back'
        back.bind(on_press=self.account_back)

        back_main=RoundedButton(
            text=current_language['preferences_back_main'],
            size_hint =(.4, .1),
            pos_hint = {'x':.52, 'y':.015},
            background_normal='',
            background_color=(245/250, 216/250, 41/250,.9),
            markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_press=self.account_back_main)

        screen_name=Label(
            text=current_language['screen_name'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.15, 'center_y':.925},)
        self.widgets['screen_name']=screen_name
        screen_name.ref='screen_name'

        information_box=RoundedColorLayout(
            bg_color=(0,0,0,.85),
            size_hint =(.35, .25),
            pos_hint = {'center_x':.225, 'center_y':.75},)
        self.widgets['information_box']=information_box

        information_title=Label(
            text=current_language['information_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['information_title']=information_title
        information_title.ref='information_title'

        information_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})




        details_box=RoundedColorLayout(
            bg_color=(0,0,0,.85),
            size_hint =(.35, .4),
            pos_hint = {'center_x':.225, 'center_y':.4},)
        self.widgets['details_box']=details_box

        details_title=Label(
            text=current_language['details_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['details_title']=details_title
        details_title.ref='details_title'

        details_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})



        status_box=RoundedColorLayout(
            bg_color=(0,0,0,.85),
            size_hint =(.35, .675),
            pos_hint = {'center_x':.6, 'center_y':.5375},)
        self.widgets['status_box']=status_box

        status_title=Label(
            text=current_language['status_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['status_title']=status_title
        status_title.ref='status_title'

        status_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})

        status_scroll=OutlineScroll(
            size_hint =(.9,.75),
            pos_hint = {'center_x':.5, 'center_y':.45},
            bg_color=(1,1,1,.15),
            bar_width=8,
            bar_color=(245/250, 216/250, 41/250,.9),
            bar_inactive_color=(245/250, 216/250, 41/250,.35),
            do_scroll_y=True,
            do_scroll_x=False)

        status_scroll_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5)

        # Make sure the height is such that there is something to scroll.
        status_scroll_layout.bind(minimum_height=status_scroll_layout.setter('height'))

        for i in range(20):#status_request:
            btn = RoundedButton(
                background_normal='',
                background_color=(.1,.1,.1,1),
                text=str(i),
                size_hint_y=None,
                height=40)
            # btn.bind(on_release=partial(self.load_selected_msg,i))
            status_scroll_layout.add_widget(btn)


        side_bar_box=RoundedColorLayout(
            bg_color=(.5,.5,.5,.85),
            size_hint =(.175, .675),
            pos_hint = {'center_x':.9, 'center_y':.5375},)
        self.widgets['status_box']=status_box

        side_bar_reconnect=RoundedButton(
            text=current_language['side_bar_reconnect'],
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.875},
            background_normal='',
            background_color=(0,0,0,.9),
            markup=True)
        self.widgets['side_bar_reconnect']=side_bar_reconnect
        side_bar_reconnect.ref='side_bar_reconnect'
        # side_bar_reconnect.bind(on_press=self.side_bar_reconnect)

        side_bar_unlink=RoundedButton(
            text=current_language['side_bar_unlink'],
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.6875},
            background_normal='',
            background_color=(0,0,0,.9),
            markup=True)
        self.widgets['side_bar_unlink']=side_bar_unlink
        side_bar_unlink.ref='side_bar_unlink'
        # side_bar_unlink.bind(on_press=self.side_bar_unlink)

        side_bar_add=RoundedButton(
            text=current_language['side_bar_add'],
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.5},
            background_normal='',
            background_color=(0,0,0,.9),
            markup=True)
        self.widgets['side_bar_add']=side_bar_add
        side_bar_add.ref='side_bar_add'
        # side_bar_add.bind(on_press=self.side_bar_add)

        side_bar_remove=RoundedButton(
            text=current_language['side_bar_remove'],
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.3125},
            background_normal='',
            background_color=(0,0,0,.9),
            markup=True)
        self.widgets['side_bar_remove']=side_bar_remove
        side_bar_remove.ref='side_bar_remove'
        # side_bar_remove.bind(on_press=self.side_bar_remove)

        side_bar_refresh=RoundedButton(
            text=current_language['side_bar_refresh'],
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.125},
            background_normal='',
            background_color=(0,0,0,.9),
            markup=True)
        self.widgets['side_bar_refresh']=side_bar_refresh
        side_bar_refresh.ref='side_bar_refresh'
        # side_bar_refresh.bind(on_press=self.side_bar_refresh)




        account_admin_hint=ExactLabel(text=f"[size=18][color=#ffffff]Enable Admin mode to edit fields[/size]",
                color=(0,0,0,1),
                pos_hint = {'center_x':.5, 'y':.14},
                markup=True)
        self.widgets['account_admin_hint']=account_admin_hint

        seperator_line=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.98, .001),
            pos_hint = {'x':.01, 'y':.13})


        information_box.add_widget(information_title)
        information_box.add_widget(information_seperator)

        details_box.add_widget(details_title)
        details_box.add_widget(details_seperator)

        status_box.add_widget(status_title)
        status_box.add_widget(status_seperator)
        status_box.add_widget(status_scroll)
        status_scroll.add_widget(status_scroll_layout)

        side_bar_box.add_widget(side_bar_reconnect)
        side_bar_box.add_widget(side_bar_unlink)
        side_bar_box.add_widget(side_bar_add)
        side_bar_box.add_widget(side_bar_remove)
        side_bar_box.add_widget(side_bar_refresh)

        self.add_widget(bg_image)
        self.add_widget(screen_name)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(seperator_line)
        self.add_widget(account_admin_hint)
        self.add_widget(information_box)
        self.add_widget(details_box)
        self.add_widget(status_box)
        self.add_widget(side_bar_box)

    def account_back (self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def account_back_main (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'

    def check_admin_mode(self,*args):
        if App.get_running_app().admin_mode_start>time.time():
            pass


    def on_pre_enter(self, *args):
        self.check_admin_mode()
        return super().on_pre_enter(*args)

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
            if App.get_running_app().service_pin_entered:
                pass
            elif app_object.current!='alert':
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
                trouble_details=trouble_template('no_trouble')
                troubles_screen.widgets['trouble_details']=trouble_details
                trouble_display.add_widget(trouble_details)
    #heat trouble
        if trouble_log['heat_override']==1:
            if app_object.current!='alert':
                main_screen.widgets['fans'].text =current_language['fans_heat']
                if 'heat_trouble' not in troubles_screen.widgets:
                    heat_trouble=trouble_template('heat_trouble_title',
                    'heat_trouble_body',
                    link_text='heat_trouble_link',ref_tag='fans')
                    heat_trouble.ref='heat_trouble'

                    def fan_switch(*args):
                        app_object.get_screen('main').widgets['fans'].state = 'down'
                        app_object.get_screen('main').fans_switch(app_object.get_screen('main').widgets['fans'])

                    heat_trouble.bind(on_release=fan_switch)
                    heat_trouble.bind(on_ref_press=fan_switch)
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
                    duration_trouble=trouble_template('duration_trouble_title',
                    'duration_trouble_body',
                    link_text='duration_trouble_link',ref_tag='duration_trouble')
                    duration_trouble.ref='duration_trouble'

                    def duration_overlay(*args):
                        app_object.get_screen('preferences').duration_flag=1
                        app_object.transition = SlideTransition(direction='up')
                        app_object.current='preferences'

                    duration_trouble.bind(on_release=duration_overlay)
                    duration_trouble.bind(on_ref_press=duration_overlay)
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
                    gasvalve_trouble=trouble_template('gasvalve_trouble_title',
                    'gasvalve_trouble_body',
                    link_text='gasvalve_trouble_link',ref_tag='gasvalve_trouble')
                    gasvalve_trouble.ref='gasvalve_trouble'

                    gasvalve_trouble.bind(on_release=logic.gv_reset_all)
                    gasvalve_trouble.bind(on_ref_press=logic.gv_reset_all)
                    troubles_screen.widgets['gasvalve_trouble']=gasvalve_trouble
                    troubles_screen.widgets['gasvalve_trouble'].bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    trouble_display.add_widget(gasvalve_trouble)
        elif trouble_log['gv_trip']==0:
            if 'gasvalve_trouble' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['gasvalve_trouble'])
                del troubles_screen.widgets['gasvalve_trouble']


class Hood_Control(App):
    def build(self):
        self.service_pin_entered=False
        self.admin_mode_start=time.time()
        self.report_pending=False#overwritten in settings_setter() from config file
        self.config_ = configparser.ConfigParser()
        self.config_.read(preferences_path)
        settings_setter(self.config_)
        Clock.schedule_once(partial(language_setter,config=self.config_))
        self.context_screen=ScreenManager()
        # self.context_screen.add_widget(AccountScreen(name='account'))
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
        self.context_screen.add_widget(MountScreen(name='mount'))
        self.context_screen.add_widget(AccountScreen(name='account'))
        listener_event=Clock.schedule_interval(partial(listen, self.context_screen),.75)
        device_update_event=Clock.schedule_interval(partial(logic.update_devices),.75)
        device_save_event=Clock.schedule_interval(partial(logic.save_devices),600)
        Clock.schedule_interval(self.context_screen.get_screen('main').widgets['clock_label'].update, 1)
        Clock.schedule_once(messages.refresh_active_messages)
        Clock.schedule_interval(messages.refresh_active_messages,10)
        return self.context_screen

def settings_setter(config):
    heat_duration=config['preferences']['heat_timer']
    if heat_duration == '300':
        logic.heat_sensor_timer=300
    elif heat_duration == '900':
        logic.heat_sensor_timer=900
    elif heat_duration == '1800':
        logic.heat_sensor_timer=1800
    report_status=config.getboolean('config','report_pending')
    App.get_running_app().report_pending=report_status

def language_setter(*args,config=None):
    def widget_walker(widget,current_language):
        if isinstance(widget,trouble_template):
            widget.translate(current_language)
            return
        if hasattr(widget,'children'):
            for i in widget.children:
                widget_walker(i,current_language)
        if hasattr(widget,'text') and hasattr(widget,'ref'):
            if widget.text!='':
                try:
                    widget.text=current_language[str(widget.ref)]
                except KeyError:
                    print(f'main.py lanuguage_setter():  {widget} has no entry in selected lanuage dict')
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