
from functools import partial
from random import shuffle
from threading import Timer

import vlc

from apiinterface import APIInterface as API


class Queue:
    MAINSCREEN = None
    COUNT = 0
    CONTENTS = []
    VLCINSTANCE = vlc.Instance()
    VLC = VLCINSTANCE.media_player_new()
    TIMER = None

    @staticmethod
    def exit():
        Queue.timer_stop()
        Queue.VLC.stop()

    @staticmethod
    def load(category, target, *args):
        if category == 'playlists':
            for entry in [song for song in target['tracks'] if song['source'] == '2']:
                t = entry['track']
                Queue.CONTENTS.append({'title': t['title'],
                                       'artist': t['artist'],
                                       'album': t['album'],
                                       'id': t['storeId'],
                                       'length': int(t['durationMillis']),
                                       'art': t['albumArtRef'][0]['url']})
                Queue.COUNT += 1
            print('{} song{} added to queue'.format(
                Queue.COUNT, ('s' if Queue.COUNT != 1 else '')))
            shuffle(Queue.CONTENTS)

        elif category == 'stations':
            info = API.API.get_station_info(target['id'], num_tracks=50)
            for entry in [song for song in info['tracks']]:
                Queue.CONTENTS.append({'title': entry['title'],
                                       'artist': entry['artist'],
                                       'album': entry['album'],
                                       'id': entry['storeId'],
                                       'length': int(entry['durationMillis']),
                                       'art': entry['albumArtRef'][0]['url']})
                Queue.COUNT += 1
            print('{} song{} added to queue'.format(
                Queue.COUNT, ('s' if Queue.COUNT != 1 else '')))
            shuffle(Queue.CONTENTS)

        # load first song
        Queue.load_song(Queue.CONTENTS[0])

    @staticmethod
    def timer_stop():
        try:
            Queue.TIMER.cancel()
        except:
            print(' FAILED TO STOP TIMER')

    @staticmethod
    def timer_start():
        # pause until song is loaded
        while Queue.VLC.get_length() == 0:
            pass
        a = (Queue.VLC.get_length() - Queue.VLC.get_time()) / 1000
        Queue.TIMER = Timer(a, partial(Queue.play, 2))
        Queue.TIMER.start()

    @staticmethod
    def load_song(target):
        url = API.API.get_stream_url(target['id'])
        song = Queue.VLCINSTANCE.media_new(url)
        Queue.VLC.stop()
        Queue.VLC.set_media(song)
        song.parse()

    @staticmethod
    def play(mode):
        print(mode, type(mode))
        if mode > 1:
            # stop autoplayer
            Queue.timer_stop()
            # move queue to next song
            Queue.CONTENTS = [*Queue.CONTENTS[1:], Queue.CONTENTS[0]]
            # load song
            Queue.load_song(Queue.CONTENTS[0])
            # play song
            Queue.play(0)

        elif mode < -1:
            # stop autoplayer
            Queue.timer_stop()
            # move queue to previous song
            Queue.CONTENTS = [Queue.CONTENTS[-1], *Queue.CONTENTS[0:-1]]
            # load song
            Queue.load_song(Queue.CONTENTS[0])
            # play song
            Queue.play(0)

        else:
            # play current song
            print('playing', Queue.VLC.play())
            Queue.timer_start()

        Queue.MAINSCREEN.update_queue()

    @staticmethod
    def pause_play():
        if Queue.VLC.is_playing():
            Queue.timer_stop()
            Queue.VLC.pause()
            return False
        else:
            Queue.play(0)
            return True

    @staticmethod
    def set_position(pos):
        if Queue.VLC.is_playing():
            Queue.timer_stop()
        Queue.VLC.set_position(pos)
        if Queue.VLC.is_playing():
            Queue.timer_start()
