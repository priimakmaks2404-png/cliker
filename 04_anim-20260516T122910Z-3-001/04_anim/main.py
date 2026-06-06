from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import hex_colormap, colormap
from kivy.animation import Animation
from kivy.metrics import sp, dp
from kivy.uix.image import Image
from kivy import platform
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader


class Menu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    # Перехід до екрана гри
    def go_game(self, *args):
        self.manager.current = "game"
        self.manager.transition.direction = "left"

    # Перехід до екрана налаштувань
    def go_settings(self, *args):
        app.previous_screen = "menu"
        self.manager.current = "settings"
        self.manager.transition.direction = "up"

    # Вихід з програми
    def exit_app(self, *args):
        app.stop()


class Settings(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Повернення до попереднього екрана
    def go_back(self, *args):
        previous = getattr(app, 'previous_screen', 'menu')
        if previous == "game":
            app.returning_to_game_from_settings = True
        direction = "down" if previous == "menu" else "down"
        self.manager.current = previous
        self.manager.transition.direction = direction


# Клас для обертання картинок; в класі, який спадковує потрібно дадати властивість angle
class RotatedImage(Image):
    ...

# КЛАС РИБИ: Обробка кліків, створення "нової" риби
class Fish(RotatedImage):
    # Властивість для забезпечення програвання однієї анімації в один проміжок часу
    anim_play = False
    interaction_block = True
    COEF_MULT = 1.5
    fish_current = None
    fish_index = 0
    hp_current = None
    angle = NumericProperty(0)


    def on_kv_post(self, base_widget):
        self.GAME_SCREEN = self.parent.parent.parent 

        return super().on_kv_post(base_widget)

    def new_fish(self, *args):
        self.fish_current = app.LEVELS[app.LEVEL][self.fish_index]
        self.source = app.FISHES[self.fish_current]['source']
        self.hp_current = app.FISHES[self.fish_current]['hp']

        self.swim()

    def swim(self):
        self.pos = (self.GAME_SCREEN.x - self.width, self.GAME_SCREEN.height / 2) 
        self.opacity = 1
        swim = Animation(x = self.GAME_SCREEN.width / 2 - self.width / 2, duration = 1)
        swim.start(self)

        swim.bind(on_complete=lambda w, a: setattr(self, "interaction_block", False))

    # КЛІК!
    def go_settings(self, *args):
        app.previous_screen = "game"
        self.manager.current = "settings"
        self.manager.transition.direction = "up"

    # Перемогли рибу :)
    def defeated(self):
        self.interaction_block = True
        
        # Воспроизводим звук поражения рыбы
        app.play_sound(app.sound_defeat)
        
        # Анімація обертання
        anim = Animation(angle = self.angle + 360, d = 1, t='in_cubic')
        
        # Запам'ятовуємо старі розмір і позицію для анімації зменьшення
        old_size = self.size.copy()
        old_pos = self.pos.copy()
        # Новий розмір
        new_size = (self.size[0] * self.COEF_MULT * 3, self.size[1] * self.COEF_MULT * 3)
        # Нова позиція риби при збільшенні
        new_pos = (self.pos[0] - (new_size[0] - self.size[0]) / 2, self.pos[1] - (new_size[0] - self.size[1]) / 2)
        # АНІМАЦІЯ ЗБІЛЬШЕННЯ/ЗМЕНЬШЕННЯ
        anim &= Animation(size=(new_size), t='in_out_bounce') + Animation(size=(old_size), duration = 0)
        anim &= Animation(pos=(new_pos), t='in_out_bounce') + Animation(pos=(old_pos), duration = 0)

        # anim = Animation(size=(self.size[0] * self.COEF_MULT * 2, self.size[1] * self.COEF_MULT * 2)) + Animation(size=old_size)
        anim &= Animation(opacity = 0)# + Animation(opacity = 1)
        anim.start(self)


    # КЛІК!
    def on_touch_down(self, touch):
        # Клік не обробляється, якщо не потрпаляє в рибу 
        # або анімація зараз програється або заблокована взаємодія
        if not self.collide_point(*touch.pos) or self.anim_play or self.interaction_block:
            return
        
        if not self.anim_play and not self.interaction_block:
            self.hp_current -= 1
            self.GAME_SCREEN.score += 1
            
            # Воспроизводим звук клика
            app.play_sound(app.sound_click)

            # Клік призвів до змеьшення hp риби
            if self.hp_current > 0:
                # Запам'ятовуємо старі розмір і позицію для анімації зменьшення
                old_size = self.size.copy()
                old_pos = self.pos.copy()

                # Новий розмір
                new_size = ( self.size[0] * self.COEF_MULT, self.size[1] * self.COEF_MULT)
                # Нова позиція риби при збільшенні
                new_pos = (self.pos[0] - (new_size[0] - self.size[0]) / 2,self.pos[1] - (new_size[0] - self.size[1]) / 2)
        
                # АНІМАЦІЯ ЗБІЛЬШЕННЯ/ЗМЕНЬШЕННЯ
                zoom_anim = Animation(size=(new_size), duration=0.05) + Animation(size=(old_size), duration = 0.05)
                zoom_anim &= Animation(pos=(new_pos), duration=0.05) + Animation(pos=(old_pos), duration = 0.05)

                zoom_anim.start(self)
                self.anim_play = True

                zoom_anim.bind(on_complete=lambda *args: setattr(self, "anim_play", False))
            # Клік призвів до знищення риби
            else:
                self.defeated()     

                # Запуск нової риби або анымації завершення рівня після 1 секунди програвання зникнення риби
                if len(app.LEVELS[app.LEVEL]) > self.fish_index + 1:
                    self.fish_index += 1
                    Clock.schedule_once(self.new_fish, 1.2)
                else:
                    Clock.schedule_once(self.GAME_SCREEN.level_complete, 1.2)
                           
        return super().on_touch_down(touch)


class Game(Screen):
    score = NumericProperty(0)

    def on_pre_enter(self, *args):
        if getattr(app, 'returning_to_game_from_settings', False):
            app.returning_to_game_from_settings = False
        else:
            self.score = 0
            app.LEVEL = 0
            self.ids.level_complete.opacity = 0
            self.ids.fish.fish_index = 0

        return super().on_pre_enter(*args)
    
    # Перехід до екрана налаштувань
    def go_settings(self, *args):
        app.previous_screen = "game"
        self.manager.current = "settings"
        self.manager.transition.direction = "up"

    
    def on_enter(self, *args):
        self.start_game()
        
        return super().on_enter(*args)

    def start_game(self):
        self.ids.fish.new_fish()

    def level_complete(self, *args):
        # self.ids.level_complete.opacity = 1
        self.ids.level_complete.opacity = 1
        
        # Воспроизводим звук завершения уровня
        app.play_sound(app.sound_level_complete)
        
        # Проверяем, есть ли следующий уровень
        if app.LEVEL + 1 < len(app.LEVELS):
            # Запланировать переход на следующий уровень через 2 секунды
            Clock.schedule_once(self.next_level, 2)
        else:
            # Игра завершена, планируем возврат в меню через 3 секунды
            Clock.schedule_once(self.game_over, 3)
    
    def next_level(self, *args):
        app.LEVEL += 1
        self.ids.level_complete.opacity = 0
        self.ids.fish.fish_index = 0
        self.ids.fish.new_fish()
    
    def game_over(self, *args):
        self.manager.current = "menu"
        self.manager.transition.direction = "right"


    def go_home(self):
        self.manager.current = "menu"
        self.manager.transition.direction = "right"


class ClickerApp(App):
    LEVEL = 0
    previous_screen = "menu"
    returning_to_game_from_settings = False
    volume = NumericProperty(1.0)

    FISHES = {
    'fish1':
        {'source': 'assets/images/be3dbadd-9ae5-4882-a7c1-db19071013d7.png', 'hp': 10},
    'fish2':
        {'source': 'assets/images/78971469-ca2f-4739-abf8-a228d9636971.png', 'hp': 20}
    }

    LEVELS = [
        ['fish1', 'fish1', 'fish2'],
        ['fish1', 'fish2', 'fish2', 'fish1'],
        ['fish2', 'fish2', 'fish1', 'fish2'],
        ['fish2', 'fish1', 'fish2', 'fish2', 'fish1']
    ]

    def build(self):
        # Загружаем звуки
        self.sound_click = SoundLoader.load('assets/audios/bubble01.mp3')
        self.sound_defeat = SoundLoader.load('assets/audios/fish_def.ogg')
        self.sound_level_complete = SoundLoader.load('assets/audios/level_complete.ogg')
        
        sm = ScreenManager()
        sm.add_widget(Menu(name="menu"))
        sm.add_widget(Game(name="game"))
        sm.add_widget(Settings(name="settings"))

        return sm
    
    def play_sound(self, sound):
        """Воспроизведение звука с учетом громкости"""
        if sound:
            sound.volume = self.volume
            sound.play()

if platform != 'android':
    Window.size = (450, 900)


app = ClickerApp()
app.run()
