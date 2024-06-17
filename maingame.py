from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from tetanus import TetanusApp
from immunocompromized import CompromizedApp


class MainApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        tetanus_button = Button(text='Launch Tetanus App')
        tetanus_button.bind(on_release=self.launch_tetanus)
        layout.add_widget(tetanus_button)

        compromised_button = Button(text='Launch Compromised App')
        compromised_button.bind(on_release=self.launch_compromised)
        layout.add_widget(compromised_button)

        return layout

    def launch_tetanus(self, instance):
        TetanusApp().run()

    def launch_compromised(self, instance):
        CompromizedApp().run()

if __name__ == '__main__':
    MainApp().run()
