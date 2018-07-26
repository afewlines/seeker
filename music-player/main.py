import os
from enum import Enum, auto
from functools import partial

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from apiinterface import APIInterface as API
from musicqueue import Queue


class BROWSETYPE(Enum):
    playlists = auto()


class MainScreen(Screen):
    pass


class BrowserScreen(Screen):
    def populate(self, category):
        if category == BROWSETYPE.playlists:
            Player.MANAGER.current = 'browser'
            self.ids.scroll.height = Window.height * 0.8
            playlists = API.API.get_all_user_playlist_contents()
            for itr in range(len(playlists)):
                temp = Button(text=playlists[len(
                    playlists) - 1 - itr]['name'], size_hint=(1, None), height=128)
                temp.bind(on_press=partial(Queue.load, 'playlists',
                                           playlists[len(playlists) - 1 - itr]))
                self.ids.list.add_widget(temp)


class LoginScreen(Screen):
    IDLE = True

    def bugem(self, *args):
        if LoginScreen.IDLE:
            LoginScreen.IDLE = False
            print(*args)
            if API.login(*args):
                Player.MANAGER.current = 'browser'


class Player:
    MANAGER = ScreenManager()
    SCREENS = None

    def __init__(self):
        Player.SCREENS = {'main': MainScreen(name='main'),
                          'login': LoginScreen(name='login'),
                          'browser': BrowserScreen(name='browser')}
        for scr in Player.SCREENS:
            Player.MANAGER.add_widget(Player.SCREENS[scr])

        Player.MANAGER.current = 'login'

        if os.path.isfile('qu.eso'):
            f = open('qu.eso', 'r')
            if API.login(*f.read().splitlines()):
                Player.SCREENS['browser'].populate(BROWSETYPE.playlists)
            f.close()

        #Queue('playlists', None)


class MusicPlayerApp(App):
    def build_config(self, config):
        config.setdefaults('section1', {
            'key1': 'value1',
            'key2': '42'
        })

    def build(self):
        sm = Player()
        return sm.MANAGER


if __name__ == '__main__':
    # Config.set('graphics', 'borderless', '1')
    Config.set('graphics', 'width', '1152')
    Config.set('graphics', 'height', '648')
    Config.set('graphics', 'resizable', '1')
    Config.write()
    MusicPlayerApp().run()
