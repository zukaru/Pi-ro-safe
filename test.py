from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import BorderImage
from kivy.uix.image import Image

class MyApp(App):
    def build(self):
        root = Widget()
        b = Image(source=r'media\report.jpg',pos=(200,200))
        root.add_widget(b)
        with b.canvas.before:
            BorderImage(
                size=(b.width + 10,b.height+10),
                pos=(b.x-5, b.y-5),
                border=(10, 10, 10, 10))

        return root


MyApp().run()