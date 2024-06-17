from kivy.config import Config
from kivy.metrics import dp, sp
Config.set('graphics', 'width', 540)
Config.set('graphics', 'height', 1200)

import random
import json
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Line, Color
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior

tetanus_initial_sick_count = 1
tetanus_infection_rate = 2
tetanus_vaccine_wins = 0
tetanus_base_initial_sick_count = 10
tetanus_base_infection_rate = 2
tetanus_settings_sick_count = 2
tetanus_settings_infection_rate = 2
tetanus_initial_compromised_count = 2
tetanus_settings_compromised_count = 6
tetanus_initial_immunized_count = 20
tetanus_settings_immunized_count = 20
tetanus_settings_vaccinated_count = 0
tetanus_settings_infection_interval = 2
tetanus_game_board = None
tetanus_board = [['healthy' for _ in range(10)] for _ in range(10)]
tetanus_states = ['healthy', 'sick', 'immunized', 'compromised', "dead"]
tetanus_bg = 'bg15.jpg'
tetanus_leaderboard = []
tetanus_cell_numbers = [[random.randint(1, 24) for _ in range(10)] for _ in range(10)]

tetanus_buttons = [[None for _ in range(10)] for _ in range(10)]
class tetanus_ImageButton(ButtonBehavior, Image):
    pass

def tetanus_get_adjacent_cells(x, y):
    adjacent_cells = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 10 and 0 <= ny < 10:
            adjacent_cells.append((nx, ny))
    return adjacent_cells

class tetanus_GameButton(ButtonBehavior, FloatLayout):
    def __init__(self, face_image_source, state_image_source, i, j, **kwargs):
        super(tetanus_GameButton, self).__init__(**kwargs)
        self.i = i
        self.j = j
        self.state_image = Image(source=state_image_source, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.face_image = Image(source=face_image_source, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.state_image)
        self.add_widget(self.face_image)
        self.bind(on_release=self.on_button_release)

    def on_button_release(self, instance):
        print(f"Button at ({self.i}, {self.j}) clicked")
        tetanus_immunize_person(self.i, self.j)

    def update_state(self, new_state_image_source):
        self.state_image.source = new_state_image_source

def tetanus_assign_random_image():
    for i in range(10):
        for j in range(10):
            random_number = tetanus_cell_numbers[i][j]
            state = tetanus_board[i][j]
            face_image_source = 'imgsv2/' + str(random_number) + '.png'
            state_image_source = 'imgsv2/' + state + '.png'
            tetanus_buttons[i][j] = tetanus_GameButton(face_image_source, state_image_source, i, j)
            tetanus_game_board.add_widget(tetanus_buttons[i][j])

tetanus_vaccinated_count = 0
tetanus_infection_interval = 1

def tetanus_infect_person(dt):
    global tetanus_vaccinated_count, tetanus_infection_rate, tetanus_infection_event
    global tetanus_buttons
    if tetanus_is_game_over():
        return
    people = [(i, j) for i in range(10) for j in range(10) if tetanus_board[i][j] in ['immunized', 'healthy', 'compromised', 'sick']]
    random.shuffle(people)
    infected = 0
    for x, y in people:
        if infected >= tetanus_infection_rate:
            break
        if tetanus_board[x][y] == 'immunized':
            tetanus_board[x][y] = 'healthy'
        elif tetanus_board[x][y] == 'healthy':
            tetanus_board[x][y] = 'compromised'
        elif tetanus_board[x][y] == 'compromised':
            tetanus_board[x][y] = 'sick'
        elif tetanus_board[x][y] == 'sick':
            tetanus_board[x][y] = 'dead'
        state_image_source = 'imgsv2/' + tetanus_board[x][y] + '.png'
        tetanus_buttons[x][y].update_state(state_image_source)
        infected += 1
    if tetanus_is_game_over():
        Clock.schedule_once(tetanus_show_game_over_message, 0.25)

def tetanus_immunize_person(x, y):
    global tetanus_vaccinated_count, tetanus_infection_event, tetanus_infection_interval
    print(f"Immunizing person at ({x}, {y})")
    if tetanus_board[x][y] in ['healthy', 'compromised', 'sick']:
        tetanus_board[x][y] = 'immunized'
        state_image_source = 'imgsv2/immunized.png'
        tetanus_buttons[x][y].update_state(state_image_source)
        tetanus_vaccinated_count += 1
        if tetanus_vaccinated_count == 1:
            tetanus_infection_event = Clock.schedule_interval(tetanus_infect_person, tetanus_infection_interval)
        elif tetanus_vaccinated_count % 5 == 0:
            tetanus_infection_event.cancel()
            tetanus_infection_interval *= 0.9
            tetanus_infection_event = Clock.schedule_interval(tetanus_infect_person, tetanus_infection_interval)
    if tetanus_is_game_over():
        tetanus_infection_event.cancel()
        tetanus_show_game_over_message()

tetanus_infection_event = Clock.schedule_interval(tetanus_infect_person, tetanus_infection_interval)

def tetanus_is_game_over():
    for i in range(10):
        for j in range(10):
            if tetanus_board[i][j] == 'dead':
                return True
    return False

def tetanus_show_game_over_message(dt=None):
    global tetanus_initial_sick_count, tetanus_infection_rate, tetanus_vaccine_wins, tetanus_vaccinated_count
    dead_count = sum(tetanus_board[i][j] == 'dead' for i in range(10) for j in range(10))

    if dead_count > 0:
        game_over_message = "Perdiste! Se enfermó un Vulnerable"

    name_input = TextInput(hint_text='Cual es tu nombre?', multiline=False, size_hint_y=0.7, height=30, size_hint_x=0.7)
    institution_input = TextInput(hint_text='De donde sos?', multiline=False, size_hint_y=0.7, height=30, size_hint_x=0.7)
    submit_button = tetanus_ImageButton(source='tick.png', size_hint=(1, 1))
    submit_button.bind(on_release=lambda x: (
    tetanus_add_to_leaderboard(name_input.text, institution_input.text), popup.dismiss(),
    tetanus_reset_game_button_pressed()))

    name_box = BoxLayout(orientation='horizontal')
    name_box.add_widget(Label(text='Nombre:', size_hint_x=0.3))
    name_box.add_widget(name_input)

    institution_box = BoxLayout(orientation='horizontal')
    institution_box.add_widget(Label(text='Institución:', size_hint_x=0.3))
    institution_box.add_widget(institution_input)

    box = BoxLayout(orientation='vertical')
    box.add_widget(name_box)
    box.add_widget(institution_box)
    box.add_widget(Label())
    box.add_widget(submit_button)

    popup = Popup(title=game_over_message, content=box, size_hint=(.95, 0.3), title_align='center', auto_dismiss=False)
    popup.open()
    return name_input, institution_input, submit_button

def tetanus_get_cells_in_range(x, y, r):
    cells = []
    for dx in range(-r, r+1):
        for dy in range(-r, r+1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 10:
                cells.append((nx, ny))
    return cells

def tetanus_reset_game_button_pressed():
    global tetanus_board, tetanus_vaccine_wins, tetanus_initial_sick_count, tetanus_infection_rate, tetanus_initial_compromised_count, tetanus_cell_numbers, tetanus_settings_sick_count, tetanus_settings_infection_rate, tetanus_initial_immunized_count, tetanus_vaccinated_count, tetanus_infection_interval, tetanus_infection_event
    tetanus_board = [['healthy' for _ in range(10)] for _ in range(10)]
    tetanus_vaccine_wins = 0
    tetanus_initial_sick_count = tetanus_settings_sick_count
    tetanus_infection_rate = tetanus_settings_infection_rate
    tetanus_initial_compromised_count = tetanus_settings_compromised_count
    tetanus_initial_immunized_count = tetanus_settings_immunized_count
    tetanus_vaccinated_count = 0
    tetanus_infection_interval = 1
    if tetanus_infection_event:
        tetanus_infection_event.cancel()
    for i in range(10):
        for j in range(10):
            tetanus_cell_numbers[i][j] = random.randint(1, 24)
    for _ in range(tetanus_initial_sick_count):
        x, y = random.randint(0, 9), random.randint(0, 9)
        while tetanus_board[x][y] in ['sick']:
            x, y = random.randint(0, 9), random.randint(0, 9)
        tetanus_board[x][y] = 'sick'
    for _ in range(tetanus_initial_compromised_count):
        x, y = random.randint(0, 9), random.randint(0, 9)
        while tetanus_board[x][y] in ['sick', 'compromised']:
            x, y = random.randint(0, 9), random.randint(0, 9)
        tetanus_board[x][y] = 'compromised'
    for _ in range(tetanus_initial_immunized_count):
        x, y = random.randint(0, 9), random.randint(0, 9)
        while tetanus_board[x][y] in ['sick', 'compromised', 'immunized']:
            x, y = random.randint(0, 9), random.randint(0, 9)
        tetanus_board[x][y] = 'immunized'
    tetanus_game_board.clear_widgets()
    tetanus_assign_random_image()

def tetanus_save_leaderboard():
    with open('leaderboard.json', 'w') as f:
        json.dump(tetanus_leaderboard, f)

def tetanus_load_leaderboard():
    global tetanus_leaderboard
    try:
        with open('leaderboard.json', 'r') as f:
            tetanus_leaderboard = json.load(f)
    except FileNotFoundError:
        tetanus_leaderboard = []

def tetanus_add_to_leaderboard(name, institution):
    global tetanus_infection_interval, tetanus_leaderboard
    round_score = round(10 / tetanus_infection_interval)
    tetanus_leaderboard.append({'name': name, 'institution': institution, 'round': round_score})
    tetanus_leaderboard.sort(key=lambda x: x['round'], reverse=True)
    tetanus_save_leaderboard()

class tetanus_Line(Widget):
    def __init__(self, **kwargs):
        super(tetanus_Line, self).__init__(**kwargs)
        with self.canvas:
            Color(0.75, 0.75, 0.75, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class tetanus_Leaderboard(BoxLayout):
    def __init__(self, **kwargs):
        super(tetanus_Leaderboard, self).__init__(**kwargs)
        self.orientation = 'vertical'
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def add_row(self, row_data, header=False):
        row = BoxLayout(size_hint_y=0.2, height=30, orientation='horizontal')
        widths = [0.1, 0.35, 0.30, 0.15]
        for item, width in zip(row_data, widths):
            label = Label(text=item, bold=header, color=(1, 1, 1, 1), size_hint_x=width, font_size=50)
            row.add_widget(label)
        self.add_widget(row)
        self.add_widget(tetanus_Line(size_hint_y=None, height=2))

def tetanus_show_leaderboard(layout):
    leaderboard_display = tetanus_Leaderboard()
    leaderboard_display.add_row(["Top", "Nombre", "Institución", "Ronda"], header=True)
    entries = sorted(tetanus_leaderboard, key=lambda x: x['round'], reverse=True)
    for i in range(20):
        if i < len(entries):
            entry = entries[i]
            leaderboard_display.add_row([str(i+1), entry['name'], entry['institution'], str(entry['round'])])
        else:
            leaderboard_display.add_row([str(i+1), "", "", ""])

    scroll_view = ScrollView()
    scroll_view.add_widget(leaderboard_display)

    layout.clear_widgets()
    layout.add_widget(scroll_view)

    back_button = tetanus_ImageButton(source='back.png', size_hint=(.2, .05))
    back_button.bind(on_release=lambda x: (tetanus_reset_game_button_pressed(), layout.clear_widgets(), tetanus_build_game_screen(layout)))
    layout.add_widget(back_button)

def tetanus_show_settings(layout):
    settings_layout = BoxLayout(orientation='vertical', padding=10)

    settings_layout.add_widget(Widget(size_hint_y=0.05))

    settings_layout.add_widget(Label(text='Rojos:', font_size=75, size_hint_y=0.05))
    sick_count_slider = Slider(min=0, max=10, value=tetanus_initial_sick_count, step=1, size_hint_y=0.05)
    sick_count_value = Label(text=str(sick_count_slider.value), font_size=75, size_hint_y=0.05)
    sick_count_slider.bind(value=lambda instance, value: setattr(sick_count_value, 'text', str(int(value))))
    settings_layout.add_widget(sick_count_slider)
    settings_layout.add_widget(sick_count_value)

    settings_layout.add_widget(Widget(size_hint_y=0.05))

    settings_layout.add_widget(Label(text='Amarillos:', font_size=75, size_hint_y=0.05))
    compromised_count_slider = Slider(min=0, max=20, value=tetanus_initial_compromised_count, step=1, size_hint_y=0.05)
    compromised_count_value = Label(text=str(compromised_count_slider.value), font_size=75, size_hint_y=0.01)
    compromised_count_slider.bind(value=lambda instance, value: setattr(compromised_count_value, 'text', str(int(value))))
    settings_layout.add_widget(compromised_count_slider)
    settings_layout.add_widget(compromised_count_value)

    settings_layout.add_widget(Widget(size_hint_y=0.05))

    settings_layout.add_widget(Label(text='Verdes:', font_size=75, size_hint_y=0.05))
    verdes_count_slider = Slider(min=0, max=40, value=tetanus_initial_immunized_count, step=1, size_hint_y=0.05)
    verdes_count_value = Label(text=str(verdes_count_slider.value), font_size=75, size_hint_y=0.01)
    verdes_count_slider.bind(value=lambda instance, value: setattr(verdes_count_value, 'text', str(int(value))))
    settings_layout.add_widget(verdes_count_slider)
    settings_layout.add_widget(verdes_count_value)

    settings_layout.add_widget(Widget(size_hint_y=0.05))

    settings_layout.add_widget(Label(text='Infecciones por ronda:', font_size=45, size_hint_y=0.05))
    infection_rate_slider = Slider(min=1, max=5, value=tetanus_infection_rate, step=1, size_hint_y=0.05)
    infection_rate_value = Label(text=str(infection_rate_slider.value), font_size=75, size_hint_y=0.05)
    infection_rate_slider.bind(value=lambda instance, value: setattr(infection_rate_value, 'text', str(int(value))))
    settings_layout.add_widget(infection_rate_slider)
    settings_layout.add_widget(infection_rate_value)

    clear_button = tetanus_ImageButton(source='reset.png', size_hint=(1, .1))
    clear_button.bind(on_release=lambda x: tetanus_show_password_popup())
    settings_layout.add_widget(clear_button)

    settings_layout.add_widget(Widget(size_hint_y=0.05))

    save_button = tetanus_ImageButton(source='save.png', size_hint=(1, .13))
    save_button.bind(on_release=lambda x: (
        tetanus_save_settings(int(sick_count_value.text), int(infection_rate_value.text), int(compromised_count_value.text), int(verdes_count_value.text)),
        tetanus_reset_game_button_pressed(), layout.clear_widgets(), tetanus_build_game_screen(layout)))
    settings_layout.add_widget(save_button)

    layout.clear_widgets()
    layout.add_widget(settings_layout)

def tetanus_save_settings(sick_count, infection_rate_input, compromised_count, verdes_count):
    global tetanus_initial_sick_count, tetanus_infection_rate, tetanus_initial_compromised_count, tetanus_settings_sick_count, tetanus_settings_infection_rate, tetanus_settings_compromised_count, tetanus_settings_immunized_count, tetanus_initial_immunized_count
    tetanus_initial_sick_count = tetanus_settings_sick_count = int(sick_count)
    tetanus_infection_rate = tetanus_settings_infection_rate = int(infection_rate_input)
    tetanus_initial_compromised_count = tetanus_settings_compromised_count = int(compromised_count)
    tetanus_initial_immunized_count = tetanus_settings_immunized_count = int(verdes_count)

def tetanus_show_password_popup():
    password_input = TextInput(password=True, size_hint_y=0.5)

    confirm_button = tetanus_ImageButton(source='tick.png', size_hint=(1, 1))
    confirm_button.bind(on_release=lambda x: tetanus_check_password(popup, password_input.text))

    exit_button = tetanus_ImageButton(source='cross.png', size_hint=(1, 1))
    exit_button.bind(on_release=lambda x: popup.dismiss())

    button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.6)
    button_layout.add_widget(confirm_button)
    button_layout.add_widget(exit_button)

    content = BoxLayout(orientation='vertical')
    content.add_widget(password_input)
    content.add_widget(button_layout)

    popup = Popup(title='Enter password', title_size=35, title_align='center', content=content,
                  size_hint=(0.8, 0.2),
                  auto_dismiss=False)

    popup.open()

def tetanus_check_password(popup, password):
    if password == 'seba1234':
        global tetanus_leaderboard
        tetanus_leaderboard = []
        tetanus_save_leaderboard()
        popup.dismiss()
    else:
        popup.title = 'Wrong password, try again'

def tetanus_show_instructions(instance):
    instructions_popup = Popup(size_hint=(0.8, 0.8), title='INSTRUCCIONES')

    instruction_text = "hay que hacer esto de cero"

    instruction_label = Label(text=instruction_text, font_size=55, size_hint_y=None, height=30, markup=True)
    instruction_label.bind(width=lambda *x: instruction_label.setter('text_size')(instruction_label, (instruction_label.width, None)))
    instruction_label.bind(texture_size=instruction_label.setter('size'))

    close_button = tetanus_ImageButton(source='tick.png', size_hint=(1, .13), height=dp(30))
    close_button.bind(on_release=instructions_popup.dismiss)

    instructions_popup.content = BoxLayout(orientation='vertical', spacing=dp(10))
    instructions_popup.content.add_widget(ScrollView())
    instructions_popup.content.children[0].add_widget(instruction_label)
    instructions_popup.content.add_widget(close_button)

    instructions_popup.open()

def tetanus_build_game_screen(layout):
    global tetanus_game_board
    layout.clear_widgets()

    layout.add_widget(Widget(size_hint_y=None, height='100'))

    layout.canvas.before.add(Rectangle(source=tetanus_bg, pos=layout.pos, size=layout.size, group='background', height=100))
    layout.bind(pos=lambda instance, value: setattr(layout.canvas.before.get_group('background')[1], 'pos', value))
    layout.bind(size=lambda instance, value: setattr(layout.canvas.before.get_group('background')[1], 'size', value))

    top_layout = BoxLayout(size_hint_y=None, height=150, spacing=10, padding=10)

    leaderboard_button = tetanus_ImageButton(source='Ranking.png', size_hint=(1, 1))
    leaderboard_button.bind(on_release=lambda x: tetanus_show_leaderboard(layout))

    instruction_button = tetanus_ImageButton(source='global.png', size_hint=(1, 1))
    instruction_button.bind(on_release=tetanus_show_instructions)

    settings_button = tetanus_ImageButton(source='settings.png', size_hint=(1, 1))
    settings_button.bind(on_release=lambda x: tetanus_show_settings(layout))

    top_layout.add_widget(leaderboard_button)
    top_layout.add_widget(instruction_button)
    top_layout.add_widget(settings_button)
    layout.add_widget(top_layout)

    tetanus_game_board = tetanus_GameBoard()
    layout.add_widget(Widget(size_hint_y=None, height='50sp'))
    layout.add_widget(tetanus_game_board)
    layout.add_widget(Widget(size_hint_y=None, height='50sp'))

    layout.add_widget(Widget(size_hint_y=None, height='200'))
    layout.add_widget(Widget(size_hint_y=None, height='300'))

    image_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='100')

    layout.add_widget(image_layout)

    reset_button = tetanus_ImageButton(source='playagain.png', size_hint=(1, 1))
    reset_button.bind(on_release=lambda x: tetanus_reset_game_button_pressed())
    reset_layout = BoxLayout(padding=20)
    reset_layout.add_widget(Widget())
    reset_layout.add_widget(reset_button)
    reset_layout.add_widget(Widget())
    layout.add_widget(reset_layout)

 #   back_button = tetanus_ImageButton(source='mainmenu.png', size_hint=(None, None), size=('48dp', '48dp'), allow_stretch=True, keep_ratio=False)
 #   back_button.bind(on_release=tetanus_go_back_to_main)
 #   reset_layout.add_widget(back_button)


# Function to handle back action
#def tetanus_go_back_to_main(instance):
#    App.get_running_app().root.current = 'main'

#def tetanus_go_back_to_main(self, instance):
#    self.layout.remove_widget(instance)
#    self.manager.current = 'main'

class tetanus_GameBoard(GridLayout):
    def __init__(self, **kwargs):
        super(tetanus_GameBoard, self).__init__(**kwargs)
        self.cols = 10
        self.row_force_default = True
        self.row_default_height = Window.width / 10
        self.update_images()

    def update_images(self):
        self.clear_widgets()
        for i in range(10):
            for j in range(10):
                random_number = tetanus_cell_numbers[i][j]
                state = tetanus_board[i][j]
                state_image_source = 'imgsv2/' + state + '.png'
                face_image_source = 'imgsv2/' + str(random_number) + '.png'

                tetanus_buttons[i][j] = tetanus_GameButton(face_image_source, state_image_source, i, j)
                self.add_widget(tetanus_buttons[i][j])

    #def add_back_button(self, layout):
    #    back_button = Button(text='Back to Main Menu', size_hint=(1, 1))
    #    back_button.bind(on_release=self.go_back_to_main_menu)
    #    layout.add_widget(back_button)

    # Add this method as well
    #def go_back_to_main_menu(self, instance):
    #    self.manager.current = 'main'

class TetanusApp(App):
    def build(self):
        tetanus_load_leaderboard()
        layout = GridLayout(cols=1)
        tetanus_build_game_screen(layout)
        tetanus_reset_game_button_pressed()
        return layout

    def on_stop(self):
        tetanus_save_leaderboard()

if __name__ == '__main__':
    TetanusApp().run()

