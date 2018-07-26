from gmusicapi import Mobileclient


class APIInterface:
    API = None

    def login(user, passwd, and_id=None):
        APIInterface.API = Mobileclient(debug_logging=True)
        if not and_id:
            and_id = Mobileclient.FROM_MAC_ADDRESS
        return APIInterface.API.login(user, passwd, and_id)
