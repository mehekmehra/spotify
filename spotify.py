import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()
# client_id = os.getenv("CLIENT_ID")
# secret = os.getenv("SECRET")
# client_credentials = SpotifyClientCredentials(client_id, secret)

class SpotifyTracks:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.secret = os.getenv("SECRET_ID")
        self.client_credentials = SpotifyClientCredentials(self.client_id, self.secret)

    def getSongs(self, user_id, playlist_id):
        song_ids = []
        playlist = spotipy.user_playlist(user_id, playlist_id)

        for playlist_item in playlist["tracks"]["items"]:
            song_id = playlist_item["track"]["id"]
            song_ids += [song_id]
        return song_ids
# https://open.spotify.com/playlist/0wagRN7iDqILEFJZai6qGq?si=f883bdc6000b4150