from kivy.config import Config
from kivy.metrics import dp, sp
Config.set('graphics', 'width', 540)
Config.set('graphics', 'height', 1200)

import random
import json
import time
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Line, Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior




# Variables - some might not be needed
compromized_initial_sick_count = 1
compromized_infection_rate = 2
compromized_vaccine_wins = 0
compromized_base_initial_sick_count = 10
compromized_base_infection_rate = 2
compromized_settings_sick_count = 1
compromized_settings_infection_rate = 2
compromized_initial_compromised_count = 2
compromized_settings_compromised_count = 2

# Define game_board as a global variable
compromized_game_board = None

# Define the board
compromized_board = [['healthy' for _ in range(10)] for _ in range(10)]
compromized_states = ['healthy', 'sick', 'immunized', 'compromised', "dead"]
compromized_bg = 'bg15.jpg'

# Create the leaderboards
compromized_leaderboard = []

# Defines a random number for each cell on the board, helps with images of people
compromized_cell_numbers = [[random.randint(1, 24) for _ in range(10)] for _ in range(10)]

compromized_game_board = None
compromized_buttons = [[None for _ in range(10)] for _ in range(10)]

class Compromized_ImageButton(ButtonBehavior, Image):
    pass

# Function to get adjacent cells for infection - only vertical and horizontal
def compromized_get_adjacent_cells(x, y):
    adjacent_cells = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Only vertical and horizontal directions
        nx, ny = x + dx, y + dy
        if 0 <= nx < 10 and 0 <= ny < 10:
            adjacent_cells.append((nx, ny))
    return adjacent_cells

#Behavour of each board person to infect and vaccinate
class Compromized_GameButton(ButtonBehavior, FloatLayout):
    def __init__(self, face_image_source, state_image_source, i, j, **kwargs):
        super(Compromized_GameButton, self).__init__(**kwargs)
        self.i = i
        self.j = j
        self.state_image = Image(source=state_image_source, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.face_image = Image(source=face_image_source, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.state_image)
        self.add_widget(self.face_image)
        self.bind(on_release=self.on_button_release)

    def on_button_release(self, instance):
        print(f"Button at ({self.i}, {self.j}) clicked")
        compromized_immunize_person(self.i, self.j)  # Call the immunize_person function when a button is clicked

    def update_state(self, new_state_image_source):
        self.state_image.source = new_state_image_source

#Assign the image of the random number selected in cell_numbers
def compromized_assign_random_image():
    for i in range(10):
        for j in range(10):
            random_number = compromized_cell_numbers[i][j]
            state = compromized_board[i][j]
            face_image_source = 'imgsv2/' + str(random_number) + '.png'
            state_image_source = 'CompromizedImgs/' + state + '.png'
            compromized_buttons[i][j] = Compromized_GameButton(face_image_source, state_image_source, i, j)
            compromized_game_board.add_widget(compromized_buttons[i][j])

# Machine turn, it makes infect people
def compromized_infect_person():
    sick_people = [(i, j) for i in range(10) for j in range(10) if compromized_board[i][j] in ['sick']]
    random.shuffle(sick_people)
    infected = 0
    for x, y in sick_people:
        if infected >= compromized_infection_rate:
            break
        adjacent_cells = compromized_get_adjacent_cells(x, y)
        random.shuffle(adjacent_cells)
        for i, j in adjacent_cells:
            if compromized_board[i][j] == 'healthy':
                compromized_board[i][j] = random.choice(['sick'])
                state_image_source = 'CompromizedImgs/' + compromized_board[i][j] + '.png'
                compromized_buttons[i][j].update_state(state_image_source)
                infected += 1
                if infected >= compromized_infection_rate:
                    break
            elif compromized_board[i][j] == 'compromised':
                compromized_board[i][j] = 'dead'
                state_image_source = 'imgsv2/dead.png'
                compromized_buttons[i][j].update_state(state_image_source)
                print("A compromised person has been infected and is now dead!")
                compromized_show_game_over_message()
                return
    if compromized_is_game_over():
        Clock.schedule_once(lambda dt: compromized_reset_game_player_wins(), 0.25)  # If the game is over, reset the game after a delay

# Players turn, it vaccinates people
def compromized_check_game_over(dt):
    if compromized_is_game_over():
        compromized_reset_game_player_wins()

def compromized_immunize_person(x, y):
    print(f"Immunizing person at ({x}, {y})")
    if compromized_board[x][y] == 'healthy':
        compromized_board[x][y] = 'immunized'
        state_image_source = 'CompromizedImgs/immunized.png'
        compromized_buttons[x][y].update_state(state_image_source)
        if not compromized_is_game_over():
            Clock.schedule_once(lambda dt: compromized_infect_person(), 0.2)
    # Schedule the check_game_over function 0.2 seconds after immunization
    Clock.schedule_once(compromized_check_game_over, 0.2)

# Function to check if game is over
from collections import deque

def compromized_is_game_over():
    for i in range(10):
        for j in range(10):
            if compromized_board[i][j] == 'dead':
                return True

    # Check if there is a path from "sick" to "compromised"
    for i in range(10):
        for j in range(10):
            if compromized_board[i][j] == 'sick':
                if compromized_bfs(i, j):
                    return False

    return True

def compromized_bfs(x, y):
    visited = [[False for _ in range(10)] for _ in range(10)]
    queue = deque([(x, y)])

    while queue:
        x, y = queue.popleft()
        visited[x][y] = True

        for nx, ny in compromized_get_adjacent_cells(x, y):
            if compromized_board[nx][ny] == 'compromised':
                return True
            if not visited[nx][ny] and compromized_board[nx][ny] == 'healthy':
                queue.append((nx, ny))

    return False

# Function to show game over message
def compromized_show_game_over_message():
    global compromized_initial_sick_count, compromized_infection_rate, compromized_vaccine_wins
    dead_count = sum(compromized_board[i][j] == 'dead' for i in range(10) for j in range(10))

    if dead_count > 0:
        game_over_message = "Perdiste! Se enfermó un Vulnerable"
    else:
        compromized_reset_game_player_wins()
        return None, None, None

    name_input = TextInput(hint_text='Cual es tu nombre?', multiline=False, size_hint_y=0.7, height=30, size_hint_x=0.7)
    institution_input = TextInput(hint_text='De donde sos?', multiline=False, size_hint_y=0.7, height=30, size_hint_x=0.7)
    submit_button = Compromized_ImageButton(source='tick.png', size_hint=(1, 1))  # Adjust the size here
    submit_button.bind(on_release=lambda x: (
    compromized_add_to_leaderboard(name_input.text, institution_input.text, compromized_vaccine_wins + 1), popup.dismiss(),
    compromized_reset_game_button_pressed()))

    # Create a BoxLayout for each pair of Label and TextInput
    name_box = BoxLayout(orientation='horizontal')
    name_box.add_widget(Label(text='Nombre:', size_hint_x=0.3))
    name_box.add_widget(name_input)

    institution_box = BoxLayout(orientation='horizontal')
    institution_box.add_widget(Label(text='Institución:', size_hint_x=0.3))
    institution_box.add_widget(institution_input)

    # Create a BoxLayout to hold the name_box, institution_box, and the Button
    box = BoxLayout(orientation='vertical')
    box.add_widget(name_box)
    box.add_widget(institution_box)
    box.add_widget(Label())
    box.add_widget(submit_button)

    # Create a Popup with the BoxLayout as its content
    popup = Popup(title=game_over_message, content=box, size_hint=(.95, 0.3), title_align='center', auto_dismiss=False)
    popup.open()
    return name_input, institution_input, submit_button
def compromized_get_cells_in_range(x, y, r):
    cells = []
    for dx in range(-r, r+1):
        for dy in range(-r, r+1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 10:
                cells.append((nx, ny))
    return cells

# If player wins, it increases the level
def compromized_reset_game_player_wins():
    global compromized_board, compromized_vaccine_wins, compromized_initial_sick_count, compromized_infection_rate, compromized_cell_numbers
    compromized_board = [['healthy' for _ in range(10)] for _ in range(10)]
    compromized_vaccine_wins += 1
    compromized_initial_compromised_count = min(compromized_settings_compromised_count + compromized_vaccine_wins, 9)  # Ensure initial_compromised_count doesn't exceed 9
    if compromized_vaccine_wins % 4 == 0:
        compromized_infection_rate += 1
    else:
        compromized_initial_sick_count = min(compromized_initial_sick_count + 1, 9)
    for i in range(10):
        for j in range(10):
            compromized_cell_numbers[i][j] = random.randint(1, 24)
    # Infect initial_sick_count number of people at the start of the game
    for _ in range(compromized_initial_sick_count):
        x, y = random.randint(0, 9), random.randint(0, 9)
        while compromized_board[x][y] in ['sick']:  # Ensure that a healthy person is infected
            x, y = random.randint(0, 9), random.randint(0, 9)
        compromized_board[x][y] = random.choice(['sick'])
    # Compromise initial_compromised_count number of people at the start of the game
    for _ in range(compromized_initial_compromised_count):
        x, y = random.randint(0, 9), random.randint(0, 9)
        while compromized_board[x][y] in ['sick', 'compromised'] or any(
                compromized_board[i][j] == 'sick' for i, j in compromized_get_cells_in_range(x, y, 2)):
            x, y = random.randint(0, 9), random.randint(0, 9)
        compromized_board[x][y] = 'compromised'
    compromized_game_board.clear_widgets()
    compromized_assign_random_image()

# If reset button is press, or player looses, it resets to the initial game state
def compromized_reset_game_button_pressed():
    global compromized_board, compromized_vaccine_wins, compromized_initial_sick_count, compromized_infection_rate, compromized_initial_compromised_count, compromized_cell_numbers, compromized_settings_sick_count, compromized_settings_infection_rate
    compromized_board = [['healthy' for _ in range(10)] for _ in range(10)]
    compromized_vaccine_wins = 0
    compromized_initial_sick_count = compromized_settings_sick_count
    compromized_infection_rate = compromized_settings_infection_rate
    compromized_initial_compromised_count = compromized_settings_compromised_count
    # Assign a random number to each cell at the start of the game
    for i in range(10):
        for j in range(10):
            compromized_cell_numbers[i][j] = random.randint(1, 24)
    # Infect initial_sick_count number of people at the start of the game
    for _ in range(compromized_initial_sick_count):
        x, y = random.randint(0, 9), random.randint(0, 9)
        while compromized_board[x][y] in ['sick']:  # Ensure that a healthy person is infected
            x, y = random.randint(0, 9), random.randint(0, 9)
        compromized_board[x][y] = random.choice(['sick'])
    # Compromise initial_compromised_count number of people at the start of the game
    for _ in range(compromized_initial_compromised_count):
        x, y = random.randint(0, 9), random.randint(0, 9)
        while compromized_board[x][y] in ['sick', 'compromised'] or any(
                compromized_board[i][j] == 'sick' for i, j in compromized_get_cells_in_range(x, y, 2)):
            x, y = random.randint(0, 9), random.randint(0, 9)
        compromized_board[x][y] = 'compromised'
    compromized_game_board.clear_widgets()
    compromized_assign_random_image()

# Function to save the leaderboards to a file
def compromized_save_leaderboard():
    with open('leaderboard.json', 'w') as f:
        json.dump(compromized_leaderboard, f)

# Function to load the leaderboards from a file
def compromized_load_leaderboard():
    global compromized_leaderboard
    try:
        with open('leaderboard.json', 'r') as f:
            compromized_leaderboard = json.load(f)
    except FileNotFoundError:
        compromized_leaderboard = []

#If a highscore is achieved, it includes it on the Leaderboards
def compromized_add_to_leaderboard(name, institution, round):
    compromized_leaderboard.append({'name': name, 'institution': institution, 'round': round})
    compromized_leaderboard.sort(key=lambda x: x['round'], reverse=True)
    compromized_save_leaderboard()

# Function to show the leaderboard
class Compromized_Line(Widget):
    def __init__(self, **kwargs):
        super(Compromized_Line, self).__init__(**kwargs)
        with self.canvas:
            Color(0.75, 0.75, 0.75, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class Compromized_Leaderboard(BoxLayout):
    def __init__(self, **kwargs):
        super(Compromized_Leaderboard, self).__init__(**kwargs)
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
        self.add_widget(Compromized_Line(size_hint_y=None, height=2))

def compromized_show_leaderboard(layout):
    leaderboard_display = Compromized_Leaderboard()
    leaderboard_display.add_row(["Top", "Nombre", "Institución", "Ronda"], header=True)
    entries = sorted(compromized_leaderboard, key=lambda x: x['round'], reverse=True)
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

    back_button = Compromized_ImageButton(source='back.png', size_hint=(.2, .05))
    back_button.bind(on_release=lambda x: (compromized_reset_game_button_pressed(), layout.clear_widgets(), compromized_build_game_screen(layout)))
    layout.add_widget(back_button)


#Shows the Settings page
def compromized_show_settings(layout):
    # Create a BoxLayout to hold the settings entries
    settings_layout = BoxLayout(orientation='vertical', padding=10)

    # Add some space between the buttons
    settings_layout.add_widget(Widget(size_hint_y=0.05))

    # Add the settings to the settings_layout
    settings_layout.add_widget(Label(text='Rojos:', font_size=75, size_hint_y=0.05))
    sick_count_slider = Slider(min=0, max=10, value=compromized_initial_sick_count, step=1, size_hint_y=0.05)
    sick_count_value = Label(text=str(sick_count_slider.value), font_size=75, size_hint_y=0.05)
    sick_count_slider.bind(value=lambda instance, value: setattr(sick_count_value, 'text', str(int(value))))
    settings_layout.add_widget(sick_count_slider)
    settings_layout.add_widget(sick_count_value)

    # Add some space between the buttons
    settings_layout.add_widget(Widget(size_hint_y=0.05))

    # Add a slider for initial_compromised_count
    settings_layout.add_widget(Label(text='Amarillos:', font_size=75, size_hint_y=0.05))
    compromised_count_slider = Slider(min=0, max=20, value=compromized_initial_compromised_count, step=1, size_hint_y=0.05)
    compromised_count_value = Label(text=str(compromised_count_slider.value), font_size=75, size_hint_y=0.01)
    compromised_count_slider.bind(value=lambda instance, value: setattr(compromised_count_value, 'text', str(int(value))))
    settings_layout.add_widget(compromised_count_slider)
    settings_layout.add_widget(compromised_count_value)

    # Add some space between the buttons
    settings_layout.add_widget(Widget(size_hint_y=0.05))

    # Add a slider to select the background
    settings_layout.add_widget(Label(text='Verdes:', font_size=75, size_hint_y=0.05))
    verdes_count_slider = Slider(min=0, max=40, value=compromized_initial_immunized_count, step=1, size_hint_y=0.05)
    verdes_count_value = Label(text=str(verdes_count_slider.value), font_size=75, size_hint_y=0.01)
    verdes_count_slider.bind(value=lambda instance, value: setattr(verdes_count_value, 'text', str(int(value))))
    settings_layout.add_widget(verdes_count_slider)
    settings_layout.add_widget(verdes_count_value)

    settings_layout.add_widget(Widget(size_hint_y=0.05))

    settings_layout.add_widget(Label(text='Infecciones por ronda:', font_size=45, size_hint_y=0.05))
    infection_rate_slider = Slider(min=1, max=5, value=compromized_infection_rate, step=1, size_hint_y=0.05)
    infection_rate_value = Label(text=str(infection_rate_slider.value), font_size=75, size_hint_y=0.05)
    infection_rate_slider.bind(value=lambda instance, value: setattr(infection_rate_value, 'text', str(int(value))))
    settings_layout.add_widget(infection_rate_slider)
    settings_layout.add_widget(infection_rate_value)

    clear_button = Compromized_ImageButton(source='reset.png', size_hint=(1, .1))
    clear_button.bind(on_release=lambda x: compromized_show_password_popup())
    settings_layout.add_widget(clear_button)

    settings_layout.add_widget(Widget(size_hint_y=0.05))

    save_button = Compromized_ImageButton(source='save.png', size_hint=(1, .13))
    save_button.bind(on_release=lambda x: (
        compromized_save_settings(int(sick_count_value.text), int(infection_rate_value.text), int(compromised_count_value.text), int(verdes_count_value.text)),
        compromized_reset_game_button_pressed(), layout.clear_widgets(), compromized_build_game_screen(layout)))
    settings_layout.add_widget(save_button)

    layout.clear_widgets()
    layout.add_widget(settings_layout)

# Function to save the settings
def compromized_save_settings(compromized_sick_count, compromized_infection_rate_input, compromized_compromised_count, compromized_bg_image):
    global compromized_initial_sick_count, compromized_infection_rate, compromized_initial_compromised_count, compromized_settings_sick_count, compromized_settings_infection_rate, compromized_settings_compromised_count, compromized_bg
    compromized_initial_sick_count = compromized_settings_sick_count = int(compromized_sick_count)
    compromized_infection_rate = compromized_settings_infection_rate = int(compromized_infection_rate_input)
    compromized_initial_compromised_count = compromized_settings_compromised_count = int(compromized_compromised_count)
    compromized_bg = compromized_bg_image

# Function to show a popup for the password
def compromized_show_password_popup():
    compromized_password_input = TextInput(password=True, size_hint_y=0.5)

    compromized_confirm_button = Compromized_ImageButton(source='tick.png', size_hint=(1, 1))
    compromized_confirm_button.bind(on_release=lambda x: compromized_check_password(popup, compromized_password_input.text))

    compromized_exit_button = Compromized_ImageButton(source='cross.png', size_hint=(1, 1))
    compromized_exit_button.bind(on_release=lambda x: popup.dismiss())

    compromized_button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.6)
    compromized_button_layout.add_widget(compromized_confirm_button)
    compromized_button_layout.add_widget(compromized_exit_button)

    compromized_content = BoxLayout(orientation='vertical')
    compromized_content.add_widget(compromized_password_input)
    compromized_content.add_widget(compromized_button_layout)

    popup = Popup(title='Enter password', title_size=35, title_align='center', content=compromized_content,
                  size_hint=(0.8, 0.2),
                  auto_dismiss=False)

    popup.open()

# Function to check the password
def compromized_check_password(popup, password):
    if password == 'seba1234':
        global compromized_leaderboard
        compromized_leaderboard = []
        compromized_save_leaderboard()
        popup.dismiss()
    else:
        popup.title = 'Wrong password, try again'

def compromized_update_rect(instance, value):
    for child in instance.canvas.children:
        if isinstance(child, Rectangle):
            child.pos = instance.pos
            child.size = instance.size

#Shows instruction if FAQ button is pressed
def compromized_show_instructions(instance):
    # Create the popup
    instructions_popup = Popup(size_hint=(0.8, 0.8), title='INSTRUCCIONES')

    # Create the instruction text
    instruction_text = "Tu objetivo es controlar la pandemia y proteger a las personas [color=2e97ee]vulnerables[/color].\n \nCada turno podrás [color=11ea02]vacunar[/color] a una persona, protegiendola y creando inmunidad de rebaño.\n \nLuego, se infectaran dos o tres personas al azar que esten en contacto con personas [color=f21010]infectadas[/color].\n \nSi una persona [color=2e97ee]vulnerable[/color] se infecta, pierdes.\n \nCuando no se pueden enfermar más personas, pasas de ronda, donde hay más focos de [color=f21010]infección[/color] y más personas [color=2e97ee]vulnerables[/color]"

    # Create the label with the instruction text
    instruction_label = Label(text=instruction_text, font_size=55, size_hint_y=None, height=30, markup=True)
    instruction_label.bind(width=lambda *x: instruction_label.setter('text_size')(instruction_label, (instruction_label.width, None)))
    instruction_label.bind(texture_size=instruction_label.setter('size'))

    # Create the close button
    close_button = Compromized_ImageButton(source='tick.png', size_hint=(1, .13), height=dp(30))
    close_button.bind(on_release=instructions_popup.dismiss)

    # Add the instruction label and close button to the popup
    instructions_popup.content = BoxLayout(orientation='vertical', spacing=dp(10))
    instructions_popup.content.add_widget(ScrollView())
    instructions_popup.content.children[0].add_widget(instruction_label)
    instructions_popup.content.add_widget(close_button)

    # Open the popup
    instructions_popup.open()

#Build the main game screen with the board
from kivy.uix.anchorlayout import AnchorLayout

def compromized_build_game_screen(layout):
    global compromized_game_board
    layout.clear_widgets()

    # Add an empty Widget to push the reset button downwards
    layout.add_widget(Widget(size_hint_y=None, height='100'))

    # Add a Rectangle instruction with a source and a group name
    layout.canvas.before.add(Rectangle(source=compromized_bg, pos=layout.pos, size=layout.size, group='background', height=100))
    layout.bind(pos=lambda instance, value: setattr(layout.canvas.before.get_group('background')[1], 'pos', value))
    layout.bind(size=lambda instance, value: setattr(layout.canvas.before.get_group('background')[1], 'size', value))

    # First row with the Leaderboard, instructions and Settings buttons
    top_layout = BoxLayout(size_hint_y=None, height=150, spacing=10, padding=10)

    leaderboard_button = Compromized_ImageButton(source='Ranking.png', size_hint=(1, 1))
    leaderboard_button.bind(on_release=lambda x: compromized_show_leaderboard(layout))

    instruction_button = Compromized_ImageButton(source='global.png', size_hint=(1, 1))
    instruction_button.bind(on_release=compromized_show_instructions)

    settings_button = Compromized_ImageButton(source='settings.png', size_hint=(1, 1))
    settings_button.bind(on_release=lambda x: compromized_show_settings(layout))

    top_layout.add_widget(leaderboard_button)
    top_layout.add_widget(instruction_button)
    top_layout.add_widget(settings_button)
    layout.add_widget(top_layout)


    # The rest of your code remains the same
    # Second row with the labels


    # Third row with the board
    compromized_game_board = Compromized_GameBoard()
    layout.add_widget(Widget(size_hint_y=None, height='50sp'))  # This will push the board to the center
    layout.add_widget(compromized_game_board)
    layout.add_widget(Widget(size_hint_y=None, height='50sp'))
    compromized_game_board.update_images()

    # Add an empty Widget to push the reset button downwards
    layout.add_widget(Widget(size_hint_y=None, height='200'))
    layout.add_widget(Widget(size_hint_y=None, height='100'))
    ###
    # Create a new BoxLayout for the images
    image_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='100')


    # Add the new BoxLayout to the main layout
    layout.add_widget(image_layout)

    # Create a new BoxLayout for the labels
    label_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='30')


    # Add the new BoxLayout to the main layout
    layout.add_widget(label_layout)
    ###

    # Fourth row with the Reset button
    reset_button = Compromized_ImageButton(source='playagain.png', size_hint=(1, 1))
    reset_button.bind(on_release=lambda x: compromized_reset_game_button_pressed())
    reset_layout = BoxLayout(padding=20)
    reset_layout.add_widget(Widget())
    reset_layout.add_widget(reset_button)
    reset_layout.add_widget(Widget())
    layout.add_widget(reset_layout)

    # Back button with the 'playagain.png' image
    #back_button = Compromized_ImageButton(source='mainmenu.png', size_hint=(1, 1))
    #back_button.bind(on_release=go_back_to_menu)
    # Add the back button to your layout, assuming you want it next to the reset button
    #reset_layout.add_widget(back_button)


class Compromized_GameBoard(GridLayout):
    def __init__(self, **kwargs):
        super(Compromized_GameBoard, self).__init__(**kwargs)
        self.cols = 10
        self.row_force_default = True
        self.row_default_height = Window.width / 10  # Make the buttons square
        self.update_images()

    def update_images(self):
        self.clear_widgets()
        for i in range(10):
            for j in range(10):
                random_number = compromized_cell_numbers[i][j]
                state = compromized_board[i][j]
                state_image_source = 'CompromizedImgs/' + state + '.png'
                face_image_source = 'imgsv2/' + str(random_number) + '.png'
                compromized_buttons[i][j] = Compromized_GameButton(face_image_source, state_image_source, i, j)
                self.add_widget(compromized_buttons[i][j])



class CompromizedApp(App):
    def build(self):
        compromized_load_leaderboard()
        layout = GridLayout(cols=1)
        compromized_build_game_screen(layout)
        compromized_reset_game_button_pressed()
        return layout

    def on_stop(self):
        compromized_save_leaderboard()

if __name__ == '__main__':
    compromized_buttons = [[None for _ in range(10)] for _ in range(10)]
    CompromizedApp().run()


