import os
from enum import Enum, auto
from functools import partial

import kivy.metrics as metrics
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import (CardTransition, Screen, ScreenManager,
                                    SlideTransition)
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget

from apiinterface import APIInterface as API
from musicqueue import Queue


class BROWSETYPE(Enum):
    playlists = auto()


class BackgroundBox(BoxLayout):
    pass


class BackgroundGrid(GridLayout):
    pass


class ImageButton(ButtonBehavior, Image):
    pass


class EmptyScreen(Screen):
    pass


class TimeBar(Slider):
    def on_touch_down(self, touch):
        released = super(TimeBar, self).on_touch_down(touch)
        print(touch)
        if self.collide_point(*touch.pos):
            self.is_triggered = True
            if Queue.VLC.is_playing():
                Player.SCREENS['main'].timer(mode=False)
            return False

    def on_touch_up(self, touch):
        released = super(TimeBar, self).on_touch_up(touch)
        if self.is_triggered:
            Player.SCREENS['main'].recv_time_bar()
            if Queue.VLC.is_playing():
                Player.SCREENS['main'].timer(mode=True)
            self.is_triggered = False
            return False


class MainScreen(Screen):
    def on_enter(self):
        Queue.MAINSCREEN = self
        self.active_time_bar = False
        art = None
        self.ids.scroll.height = Window.height
        if Queue.COUNT > 0:
            self.update_queue()
        self.bar_timer = None
        self.timer(mode=True)

    def on_exit(self):
        self.timer()
        self.ids.queue.clear_widgets()

    def timer(self, mode=False):
        if mode:
            if (not self.bar_timer) or (not self.bar_timer.is_triggered):
                self.bar_timer = Clock.schedule_interval(
                    self.update_time_bar, 0.125)
        else:
            try:
                self.bar_timer.cancel()
            except:
                print('   ERROR   Error canceling progressbar')

    def load_art(self, url=None):
        if url:
            self.ids.album_art.source = url
        else:
            self.ids.album_art.source = 'https://res.cloudinary.com/teepublic/image/private/s--HPkOGViW--/t_Preview/b_rgb:ffffff,c_limit,f_jpg,h_630,q_90,w_630/v1524084094/production/designs/2603700_0.jpg'

    def load_info(self, song=None):
        if song:
            self.load_art(song['art'])
            self.ids.title.text = song['title']
            self.ids.artist.text = song['artist']
            self.ids.album.text = song['album']
            while Queue.VLC.get_length() == 0:
                pass
            self.ids.time_duration.text = '{}:{:02}'.format(
                *divmod(int(song['length'] / 1000), 60))
        else:
            pass

    def update_queue(self):
        self.ids.queue.clear_widgets()
        self.load_info(Queue.CONTENTS[0])
        self.ids.queue.add_widget(self.tile_factory(
            Queue.CONTENTS[0], tile=[0, 0, 0, 0.75]))
        for num in range(1, len(Queue.CONTENTS[1:]) + 1):
            self.ids.queue.add_widget(self.tile_factory(Queue.CONTENTS[num]))

    def update_time_bar(self, dt):
        self.ids.progress_bar.value = Queue.VLC.get_position() % 1
        self.ids.time_current.text = '{}:{:02}'.format(
            *divmod(int(Queue.VLC.get_time() / 1000), 60))

    def recv_time_bar(self, *args):
        Queue.set_position(self.ids.progress_bar.value)

    def tile_factory(self, song, tile=[0, 0, 0, 0.5]):
        temp = BackgroundBox(orientation='vertical', size_hint=(
            1, None), height=metrics.dp(90), bcolor=tile)
        template = {'size_hint': (1, None),
                    'height': metrics.dp(40),
                    'text_size': (metrics.dp(300), metrics.dp(60)),
                    'halign': 'left',
                    'color': [1, 1, 1, 1],
                    'valign': 'top'}
        song_deco = '{}\n{}\n'.format(song['artist'], song['album'])

        title = Label(text=song['title'], font_size=metrics.dp(
            15), **template)
        template['height'] = metrics.dp(30)
        template['text_size'] = (metrics.dp(300), None)
        template['color'] = [0.8, 0.8, 0.8, 1]
        deco = Label(text=song_deco, font_size=metrics.dp(
            14), **template)
        temp.add_widget(title)
        temp.add_widget(deco)
        return temp

    def control_press(self, *args, mode=None):
        print('mode: {}'.format(mode))
        if mode == 0:
            if Queue.pause_play():
                self.ids.pauseplay.source = 'graphics/buttons/btn_pause.png'
            else:
                self.ids.pauseplay.source = 'graphics/buttons/btn_play.png'
            return
        Queue.play(mode)


class BrowserScreen(Screen):
    MODE = BROWSETYPE.playlists

    def on_enter(self):
        self.populate()

    def on_exit(self):
        self.ids.list.clear_widgets()

    def populate(self):
        if BrowserScreen.MODE == BROWSETYPE.playlists:
            self.ids.scroll.height = Window.height * 0.8
            playlists = API.API.get_all_user_playlist_contents()
            for itr in range(len(playlists)):
                self.ids.list.add_widget(self.option_factory(
                    playlists[len(playlists) - 1 - itr], 'playlists'))

    def option_factory(self, target, mode):
        temp = Button(text=target['name'], size_hint=(
            1, None), height=metrics.dp(50))
        temp.bind(on_press=partial(Queue.load, mode,
                                   target))
        temp.bind(on_press=partial(Player.change_screen, 'main'))
        return temp


class LoginScreen(Screen):
    IDLE = True

    def on_enter(self):
        if os.path.isfile('qu.eso'):
            f = open('qu.eso', 'r')
            self.login(*f.read().splitlines())
            f.close()

    def login(self, *args):
        debug = False
        if LoginScreen.IDLE:
            LoginScreen.IDLE = False
            if API.login(*args):
                debug = True
                Player.change_screen(
                    'browser', t=CardTransition(direction='down', mode='pop', duration=1))
            LoginScreen.IDLE = True
        return debug


class Player:
    MANAGER = ScreenManager()
    SCREENS = None

    def __init__(self):
        Player.SCREENS = {'empty': EmptyScreen(name='empty'),
                          'main': MainScreen(name='main'),
                          'login': LoginScreen(name='login'),
                          'browser': BrowserScreen(name='browser')}
        for scr in Player.SCREENS:
            Player.MANAGER.add_widget(Player.SCREENS[scr])

        Player.change_screen(
            'login', t=CardTransition(direction='down', mode='push', duration=1))
        BrowserScreen.MODE = BROWSETYPE.playlists

    def change_screen(target, *args, t=None):

        if t:
            Player.MANAGER.transition = t
        else:
            print('   ERROR   Invalid transition settings')
            Player.MANAGER.transition = SlideTransition()

        try:
            Player.MANAGER.current = target
        except:
            print('   ERROR   Screen does not exist')


class MusicPlayerApp(App):
    def build(self):
        sm = Player()
        return sm.MANAGER

    def on_stop(self):
        Queue.exit()


if __name__ == '__main__':
    # Config.set('graphics', 'borderless', '1')
    Config.set('graphics', 'width', '1280')
    Config.set('graphics', 'height', '720')
    Config.set('graphics', 'resizable', '0')
    Config.write()
    MusicPlayerApp().run()
