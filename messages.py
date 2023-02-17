'''messages.py contains all messages and methods to filter,compile, and sort them


MessageHandler holds all messages in a dict called self.index
these messages will be added to self._active_messages based on timestamps
loaded from hood_control.ini compared to Intervals saved with each message.
Then they will be filtered so only one message from each category remains.
(e.g. only one in (sys_5,sys_6,sys_7) will remain)


Messages have these attributes:

name:          used for indexing and filtering categories
title:         displayed in the message center
body:          displayed in the message center
card:          displayed on the message center when minimized
gravity:       used to weigh importance of the message; higher == displayed on card
recurrence:    length of Interval
'''


import configparser,os
from datetime import date,datetime,timedelta
from dataclasses import dataclass,field

if os.name == 'nt':
    preferences_path='logs/configurations/hood_control.ini'
if os.name == 'posix':
    preferences_path='/home/pi/Pi-ro-safe/logs/configurations/hood_control.ini'

@dataclass
class Interval:
    year:int = 0
    month:int = 0
    day:int = 0
    hour:int = 0
    minute:int = 0
    second:float = 0.0

    def __add__(self,other):
        assert type(other)==Interval \
        or type(other)==datetime \
        or type(other)==date \
        or type(other)==timedelta \
        ,f'Cannot add Interval with type {type(other)}'

        if type(other)==Interval:
            return Interval(year=self.year+other.year,
                            month=self.month+other.month,
                            day=self.day+other.day,
                            hour=self.hour+other.hour,
                           minute=self.minute+other.minute,
                           second=self.second+other.second)
        else:
            MONTH_LENGTH={1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

            _month_length=MONTH_LENGTH[other.month]
            _minute,second=divmod(int(self.second+other.second),60)
            _hour,minute=divmod(self.minute+other.minute+_minute,60)
            _day,hour=divmod(self.hour+other.hour+_hour,24)
            _month,day=divmod(self.day+other.day+_day,_month_length)
            _year,month=divmod(self.month+other.month+_month,12)
            year=self.year+other.year+_year

            return type(other)(
                second=second,
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                year=year)

class Message:
    def __init__(self,name,title,body,card,gravity,recurrence) -> 'Message':
        self.name=name
        self.title=title
        self.body=body
        self.card=card
        self.gravity=gravity
        self.recurrence=recurrence



class MessageHandler:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(preferences_path)
        self._active_messages=[]
        self.index={
            'guide':Message('Guide',
                            'Welcome to the Message Center',
'''The Message Center will house relevant
information as it becomes available.
Some recurring reminders may show up here on 
various schedules, while some one-time-events
may push a new message here to alert you.''',
                            'Message Center',
                            0,
                            0),
            'sys_5':Message('System Inspection',
                            'Upcoming System Inspection',
'''Fire suppression systems are required
to be serviced and inspected semi-annually.
The most recent inspection on this system was
conducted five months ago.
Next month a system technician will attempt to 
schedule a visit to service and inspect your system.''',
                            'Upcoming System Inspection',
                            5,
                            Interval(month=5)),
            'sys_6':Message('System Inspection',
                            'System Inspection Due',
'''Your Fire suppression system is now
due for a semi-annual service and inspection.


This month a system technician will attempt to 
schedule a visit to service and inspect your system.''',
                            'System Inspection Due',
                            6,
                            Interval(month=6)),
            'sys_7':Message('System Inspection',
                            'System Inspection Past Due',
'''Your Fire suppression system is past
due for a semi-annual service and inspection.


Please contact your service company to
schedule a visit to service and inspect your system.''',
                            'System Inspection Due',
                            7,
                            Interval(month=7))}

    def refresh_active_messages(self,*args):
        '''attempts to load in every message thats beyond its Interval

        if [timestamps] is missing from hood_control.ini than
        this function will break early and only messages with
        zero recurrence will be loaded(e.g. messages with
        no Interval associated)

        if the message key is missing from hood_control.ini
        the loop will continue, only skipping that messages
        load cycle.
        
        after all current messages have been added
        filter_active_messages() is called to reduce each
        category of message to a single entry.'''
        self._active_messages=[]
        for message in self.index.values():
            if message.recurrence==0:
                self._active_messages.append(message)
                continue
            try:
                self.config['timestamps']
            except (configparser.NoSectionError,configparser.NoOptionError,KeyError):
                print('messages.py refresh_active_messages(): hood_control.ini missing [timestamps] section')
                break
            try:
                self.config['timestamps'][f'{message.name}']
            except (configparser.NoSectionError,configparser.NoOptionError,KeyError):
                print(f'messages.py refresh_active_messages(): hood_control.ini missing <{message.name}> key')
                continue

            if datetime.now()>message.recurrence+datetime.fromisoformat(self.config['timestamps'][f'{message.name}']):
                self._active_messages.append(message)

        self.filter_active_messages()

    def filter_active_messages(self,*args):
        '''leave only one message per category'''

        _system_inspection=max([i for i in self._active_messages if i.name=='System Inspection'],key=lambda message:message.gravity,default=None)

        CATEGORIES={_system_inspection}

        self._active_messages=[]
        for message in self.index.values():
            if message.recurrence==0:
                self._active_messages.append(message)
        for message in CATEGORIES:
            if message:
                self._active_messages.append(message)


    def get_gravity(self,item):
        return item.gravity

    def write(self,key,value=datetime.now()):
        self.config.set('timestamps',f'{key}',f'{value}')
        with open(preferences_path,'w') as configfile:
            self.config.write(configfile)

    @property
    def active_messages(self):
        self._active_messages.sort(key=self.get_gravity,reverse=True)
        return self._active_messages

messages=MessageHandler()
