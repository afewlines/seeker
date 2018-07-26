
from enum import Enum, auto

from apiinterface import APIInterface as API


class Queue:
    COUNT = 0
    CONTENTS = []
    DISPLAY = []

    def load(category, target, *args):
        if category == 'playlists':
            for entry in target['tracks']:
                Queue.CONTENTS.append = entry['track']
                Queue.DISPLAY.append  # FINISH IT UP
