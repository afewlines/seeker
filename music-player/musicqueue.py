
from random import shuffle

import vlc

from apiinterface import APIInterface as API


class Queue:
    COUNT = 0
    CONTENTS = []
    VLCINSTANCE = vlc.Instance()
    VLC = VLCINSTANCE.media_player_new()
    TIMER

    def load(category, target, *args):
        if category == 'playlists':
            for entry in [song for song in target['tracks'] if song['source'] == '2']:
                t = entry['track']
                Queue.CONTENTS.append({'title': t['title'],
                                       'artist': t['artist'],
                                       'album': t['album'],
                                       'id': t['storeId'],
                                       'art': t['albumArtRef'][0]['url']})
                Queue.COUNT += 1
            print('{} song{} added to queue'.format(
                Queue.COUNT, ('s' if Queue.COUNT != 1 else '')))
            shuffle(Queue.CONTENTS)

    def play(mode):
        if mode > 0:
            # move queue to next song
            # play song
            pass
        elif mode < 0:
            # move queue to previous song
            # play song
            pass
        else:
            # play current song
            pass

    def pause_play():
        if VLC.is_playing():
            VLC.pause()
            pass
        else:
            Queue.play(0)
