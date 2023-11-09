import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()


class SpotifyTracks:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.secret = os.getenv("SECRET_ID")
        self.client_credentials = SpotifyClientCredentials(self.client_id, self.secret)
        self.sp = spotipy.Spotify(auth_manager=self.client_credentials)

    def get_song_list(self, user_id, playlist_id):
        song_ids = []
        playlist = self.sp.user_playlist_tracks(user_id, playlist_id)
        songs = playlist["items"]
        while playlist["next"]:
            playlist = self.sp.next(playlist)
            songs += playlist["items"]
        return songs

    def get_song_info(self, song_list):
        track_dict = {}
 
        for song in song_list:
            song_id = song["track"]["id"]

            song_features = self.sp.audio_features(song_id)

            name = song["track"]["name"]
            album = song["track"]["album"]["name"]
            artist = song["track"]["album"]["artists"][0]["name"]
            duration = song["track"]["duration_ms"]
            release = song["track"]["album"]["release_date"]
            popularity = song["track"]["popularity"]
            danceability = song_features[0]["danceability"]
            liveness = song_features[0]["liveness"]

            song_info = [name, album, artist, duration, release, popularity, danceability, liveness]
            track_dict[song_id] = song_info
        return track_dict
        
    def to_df(self, track_dict):
        df = pd.DataFrame.from_dict(track_dict, orient='index', 
                                    columns=[
                                        "name", 
                                        "album",
                                        "artist", 
                                        "duration", 
                                        "release", 
                                        "popularity", 
                                        "danceability", 
                                        "liveness"
                                        ])
        return df
    # get some csv data
    # do some stat analysis
    # plot graph
        

# https://open.spotify.com/playlist/0wagRN7iDqILEFJZai6qGq?si=f883bdc6000b4150

# https://open.spotify.com/user/byggxb8c87y5ydue5n5upf720?si=37050d2e138446d1


