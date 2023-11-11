import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt

load_dotenv()

class SpotifyAnalysis:
    def __init__(self):
        """ initializes a spotify connection by passing in the environmental credentials.
        """
        client_id = os.getenv("CLIENT_ID")
        secret = os.getenv("SECRET_ID")
        client_credentials = SpotifyClientCredentials(client_id, secret)
        self.sp = spotipy.Spotify(auth_manager=client_credentials)

    def get_song_list(self, user_id, playlist_id):
        """ gets the track list of the specified playlist from the specified user. 
            Each song is a dictionary with meta data and song features.
            inputs:
                user_id: spotify user id as a string
                playlist_id: spotify playlist id as a string
        """
        playlist = self.sp.user_playlist_tracks(user_id, playlist_id)
        songs = playlist["items"]
        while playlist["next"]:
            playlist = self.sp.next(playlist)
            songs += playlist["items"]
        return songs

    def get_song_info(self, song_list):
        """ pulls the relevant song information from the song list and returns a dictionary where each key represents one song and its value
            is the list [name, album, artist, duration, date_added, popularity, danceability, liveness].
            inputs:
                song_list: a list of dictionaries of songs (outputted by get_song_list)
        """
        song_dict = {}
        for song in song_list:
            try: 
                song_id = song["track"]["id"]
                song_features = self.sp.audio_features(song_id)
                name = song["track"]["name"]
                album = song["track"]["album"]["name"]
                artist = song["track"]["album"]["artists"][0]["name"]
                duration = song["track"]["duration_ms"]
                date_added = song["added_at"]
                popularity = song["track"]["popularity"]
                danceability = song_features[0]["danceability"]
                liveness = song_features[0]["liveness"]
                song_info = [name, album, artist, duration, date_added, popularity, danceability, liveness]
                song_dict[song_id] = song_info
            except:
                continue
        return song_dict
        
    def to_song_df(self, song_dict):
        """ creates a pandas dataframe where each row corresponds to one song and the columns are:
            name, album, artist, duration, date_added, popularity, danceability, liveness
            inputs:
                song_dict: dictionary where each key is one song id and the value is 
                            [name, album, artist, duration, date_added, popularity, danceability, liveness]
        """
        df = pd.DataFrame.from_dict(song_dict, orient='index', 
                                    columns=[
                                        "name", 
                                        "album",
                                        "artist", 
                                        "duration", 
                                        "date_added", 
                                        "popularity", 
                                        "danceability", 
                                        "liveness"
                                        ])
        return df

    def read_csv_to_df(self, file_name):
        """ reads a csv file and generates a pandas dataframe from it using the csv column headers as the dataframe headers
            inputs:
                file_name: name or path to the csv file as a string
        """
        df = pd.read_csv(file_name, header="infer") 
        return df
    
    def music_compatability(self, csv_df, playlist_df):
        """ determines how compatible a playlist is with a person based on how many songs overlap between the playlist
            the csv of favorite songs the person provides
            inputs:
                csv_df: a dataframe constructed out of a csv provided by the user containg their favorite songs.
                        there are two colums: "name" and "artist"
                playlist_df: a dataframe of the songs in the playlist where each row represents one song and has the columns:
                            name, album, artist, duration, date_added, popularity, danceability, liveness
        """
        merged_df = pd.merge(playlist_df, csv_df, on=['name', 'artist'], how='inner')
        percentage_matches = (len(merged_df) / len(playlist_df)) * 100
        compatibility =  f"Song Compatibility: {percentage_matches}%"
        return compatibility

    def artist_chart(self, playlist_df):
        """ creates a pie chart of the artist distribution in a playlist
            inputs:
                playlist_df: a dataframe of the songs in the playlist where each row represents one song and has the columns:
                            name, album, artist, duration, date_added, popularity, danceability, liveness
        """
        artist_counts = playlist_df['artist'].value_counts()
        plt.pie(artist_counts, labels=artist_counts.index, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  
        plt.title('Distribution of Playlist by Artist')
        plt.show()

    def features_over_time(self, playlist_df):
        """ creates a plot where each subplot is how a feature changes over time in a playlist. 
            For example, how danceability changed as songs were added to the playlist
            inputs:
                playlist_df: a dataframe of the songs in the playlist where each row represents one song and has the columns:
                            name, album, artist, duration, date_added, popularity, danceability, liveness
        """
        playlist_df["date_added"] = pd.to_datetime(playlist_df["date_added"], format="%Y-%m-%dT%H:%M:%SZ")
        features = ["danceability", "liveness"]
        num_features = len(features)
        figure, axs = plt.subplots(num_features, 1, figsize=(10, 5 * num_features), sharex=True)
        for i, feature in enumerate(features):
            title = feature.capitalize()
            axs[i].scatter(playlist_df["date_added"], playlist_df[feature], marker='o', label=title)
            axs[i].set_title(f'{title} Over Time')
            axs[i].set_ylabel(title)
            axs[i].grid(True)
        plt.show()

if __name__ == "__main__":
    # creating the spotify object and setting up the dataframe for the playlist
    spotify = SpotifyAnalysis()
    songs = spotify.get_song_list("byggxb8c87y5ydue5n5upf720", "4eOQdmrlVTZZMmwOKnfYlG")
    songs_info_dict = spotify.get_song_info(songs)
    playlist_df = spotify.to_song_df(songs_info_dict)

    # ingesting the inputted csv and finding the compatibilty between the csv songs and the playlist
    csv_df = spotify.read_csv_to_df("mehek_top_songs.csv")
    compatibility = spotify.music_compatability(csv_df, playlist_df)
    print(compatibility)

    # creating plots for the distibution of artists and the change in liveness and danceability over time
    spotify.artist_chart(playlist_df)
    spotify.features_over_time(playlist_df)
