from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from tetanus import TetanusApp
from immunocompromized import CompromizedApp
from kivy.uix.anchorlayout import AnchorLayout


# Custom button with image
class ImageButton(ButtonBehavior, Image):
    pass

# Define your screens
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.background = Image(source='bg15.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)
        layout = BoxLayout(orientation='vertical')

        btn_tetanus = ImageButton(source='cross.png')
        btn_tetanus.bind(on_release=self.play_tetanus)

        btn_compromised = ImageButton(source='tick.png')
        btn_compromised.bind(on_release=self.play_compromised)

        layout.add_widget(btn_tetanus)
        layout.add_widget(btn_compromised)

        self.add_widget(layout)

    def play_tetanus(self, instance):
        self.manager.current = 'tetanus'

    def play_compromised(self, instance):
        self.manager.current = 'compromised'

class TetanusScreen(Screen):
    def __init__(self, **kwargs):
        super(TetanusScreen, self).__init__(**kwargs)
        self.background = Image(source='bg15.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)
        layout = BoxLayout(orientation='vertical')

        # Your TetanusApp widget
        tetanus_widget = TetanusApp().build()
        layout.add_widget(tetanus_widget)

        # Back button
        back_button = ImageButton(source='mainmenu.png', size_hint=(0.3, 0.3))
        back_button.bind(on_release=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = 'main'

class CompromisedScreen(Screen):
    def __init__(self, **kwargs):
        super(CompromisedScreen, self).__init__(**kwargs)
        self.background = Image(source='bg15.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)
        layout = BoxLayout(orientation='vertical')

        # Your CompromizedApp widget
        compromised_widget = CompromizedApp().build()
        layout.add_widget(compromised_widget)

        # Back button
        back_button = ImageButton(source='mainmenu.png', size_hint=(0.3, 0.3))
        back_button.bind(on_release=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = 'main'

# Create the screen manager
sm = ScreenManager()
sm.add_widget(MainScreen(name='main'))
sm.add_widget(TetanusScreen(name='tetanus'))
sm.add_widget(CompromisedScreen(name='compromised'))

class YourGameApp(App):
    def build(self):
        return sm

if __name__ == '__main__':
    YourGameApp().run()
