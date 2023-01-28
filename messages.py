


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
                            1,
                            5)}
        for message in self.index.values():
            self.active_messages.append(message)

    def refresh_active_messages(self,*args):
        pass

    def get_gravity(self,item):
        return item.gravity

    @property
    def active_messages(self):
        self._active_messages.sort(key=self.get_gravity,reverse=True)
        return self._active_messages


messages=MessageHandler()



