from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window

Window.size = (450, 900)

class MenuScreen(Screen):

        def go_game (self):
                self.manager.current = "game"
        
        def go_settings(self):
                self.manager.current = "settings"
        
        def exit_app(self):
                App.get_running_app().stop()




class Menu(Screen):
        def __init__(self, **kwargs):
                super().__init__(**kwargs)
                # Кнопка Play
                btn_play = Button(text="PLAY", size_hint=(1, 0.15), font_size="20sp")
                btn_play.bind(on_press=self.go_game)
                layout.add_widget(btn_play)
                self.add_widget(layout)
                # Перехід до екрана гри
        def go_game(self, *args):
                self.manager.current = "game"


        # Перехід до екрана налаштувань
        def go_settings(self, *args):
                self.manager.current = "settings"


        # Вихід з програми
        def exit_app(self, *args):
                app.stop()


class Settings(Screen):
   def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

class Game(Screen):
        def __init__(self, **kwargs):
                super().__init__(**kwargs)      

        def menu(self,*args):
               self.manager.current = "menu"

class MediumApp(App):
        def build(self):
                sm = ScreenManager()
                sm.add_widget(Menu(name="menu"))
                sm.add_widget(Game(name="game"))
                sm.add_widget(Settings(name="settings"))
                return sm

# Основний контейнер
layout = BoxLayout(orientation="vertical", padding="20dp", spacing="20dp")

# Текстовий заголовок
lbl_title = Label(text="Main Menu", font_size="40sp", size_hint=(1, 0.2))
layout.add_widget(lbl_title)
size_hint=(1, 0.2)
font_size="40sp"


app = MediumApp()
app.run()
