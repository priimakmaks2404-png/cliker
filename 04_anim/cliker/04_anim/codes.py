from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout


class FontViewer(App):
    def build(self):
        root = ScrollView(size_hint=(1, 1))
        layout = GridLayout(cols=8, padding=5, spacing=5,
                            size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # диапазон Private Use Area, где обычно сидят иконки
        for code in range(0xE000, 0xE200):
            box = BoxLayout(orientation="vertical",
                            size_hint=(None, None), size=(80, 100))

            # сама иконка
            icon = Label(
                text=chr(code),
                font_name='assets/typicons.ttf',  # путь к твоему шрифту
                font_size='28sp',
                size_hint=(1, 0.7),
                halign='center',
                valign='middle'
            )
            icon.bind(size=icon.setter('text_size'))

            # подпись с кодом
            label = Label(
                text=f"U+{code:04X}",
                font_size='10sp',
                size_hint=(1, 0.3),
                halign='center',
                valign='middle'
            )
            label.bind(size=label.setter('text_size'))

            box.add_widget(icon)
            box.add_widget(label)
            layout.add_widget(box)

        root.add_widget(layout)
        return root


if __name__ == "__main__":
    FontViewer().run()
