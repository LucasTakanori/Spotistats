from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def convert_ms_to_time(ms):
        seconds = divmod(ms, 1000)
        minutes = divmod(ms, 6000)
        hours = divmod(ms, 36000)
        return hours[0], minutes[0], seconds[0]

class SpotifyHandler:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db = self.client["Spotistats"]
   

    def get_all_users(self):
        users_cursor = self.db.Users.find({}, {"_id": 1, "email": 1})
        users_data = [{"_id": user["_id"], "email": user["email"]} for user in users_cursor]
        users = dumps(users_data)
        print("Fetched users' data:", users)
        return dumps(users_data)

    def get_user_data(self, user_id):
        streaming_history = self.db.StreamingHistory
        total_streams = streaming_history.count_documents({})
        total_ms_played = streaming_history.aggregate([{"$group": {"_id": ObjectId(user_id), "total_msPlayed": {"$sum": "$msPlayed"}}}])
        total_unique_tracks = len(streaming_history.distinct("trackName"))
        total_unique_artists = len(streaming_history.distinct("artistName"))

        ms = next(total_ms_played)["total_msPlayed"]
        hours, minutes, seconds = convert_ms_to_time(ms)

        result = {
            "total_streams": total_streams,
            "total_time_played": f"{hours} hours, {minutes} minutes, {seconds} seconds",
            "total_ms_played": ms,
            "total_unique_tracks": total_unique_tracks,
            "total_unique_artists": total_unique_artists
        }

        return result



    def get_user_playlists(self, user_id):
        # Retrieve the user's playlists
        playlists_cursor = self.db.Playlists.find({"id": ObjectId(user_id)})
        
        # Extract the playlist names and return them as JSON
        playlist_names = [playlist["name"] for playlist in playlists_cursor]
        print(playlist_names)
        return playlist_names

    def top_songs_by_time_listened(self, user_id, n_songs=20):
        cid = '60b1b327971648fc8d65036c31e0f676'
        secret = 'afa865ec13b2498ca918e13f2244bf29'
        client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        streaming_history = self.db["StreamingHistory"]
        time_listened_pipeline = [
        {
            "$match": {"id": ObjectId(user_id)}
        },
        {
            "$group": {
                "_id": {"artist": "$artistName", "track": "$trackName"},
                "totalTimeListened": {"$sum": "$msPlayed"}
            }
        },
        {
            "$sort": {"totalTimeListened": -1}
        },
        {
            "$limit": n_songs
        }
        ]

        top_songs_by_time_listened = streaming_history.aggregate(time_listened_pipeline)

        updated_songs = []
        for song in top_songs_by_time_listened:
            song_name = song['_id']['track']
            artist_name = song['_id']['artist']
            time_listened = song['totalTimeListened']
            query = f'track:{song_name} artist:{artist_name}'
            search_result = sp.search(q=query, type='track', limit=1)
            song_info = search_result['tracks']['items'][0]
            spotify_url = song_info['external_urls']['spotify']
            album_image_url = song_info['album']['images'][0]['url']
            updated_songs.append({
                'name': song_name,
                'artist': artist_name,
                'play_count': time_listened,
                'spotify_url': spotify_url,
                'album_image_url': album_image_url
            })
        print(updated_songs)
        return updated_songs

    def get_most_artists(self, user_id, n_artists=20):
        cid = '60b1b327971648fc8d65036c31e0f676'
        secret = 'afa865ec13b2498ca918e13f2244bf29'
        client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        streaming_history = self.db["StreamingHistory"]
        artist_pipeline = [
        {
            "$match": {"id": ObjectId(user_id)}
        },
        {
            "$group": {
                "_id": "$artistName",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        },
        {
            "$limit": n_artists
        }
        ]

        top_artists = streaming_history.aggregate(artist_pipeline)

        
        top_artists = [(artist_info["_id"], artist_info["count"]) for artist_info in streaming_history.aggregate(artist_pipeline)]

        updated_artists = []
        for artist_name, play_count in top_artists:
            search_result = sp.search(q=artist_name, type='artist', limit=1)
            artist_info = search_result['artists']['items'][0]
            image_url = artist_info['images'][0]['url']
            spotify_url = artist_info['external_urls']['spotify']
            updated_artists.append({
                'name': artist_name,
                'plays': play_count,
                'image_url': image_url,
                'spotify_url': spotify_url
            })

        return updated_artists


    def get_most_songs(self, user_id, n_songs=20):
        cid = '60b1b327971648fc8d65036c31e0f676'
        secret = 'afa865ec13b2498ca918e13f2244bf29'
        client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        streaming_history = self.db["StreamingHistory"]
        song_pipeline = [
        {
            "$match": {"id": ObjectId(user_id)}
        },
        {
            "$group": {
                "_id": {"artist": "$artistName", "track": "$trackName"},
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        },
        {
            "$limit": n_songs
        }
        ]

        top_songs = [
            {
                "artist": artist_info["_id"]["artist"],
                "track": artist_info["_id"]["track"],
                "count": artist_info["count"]
            }
            for artist_info in streaming_history.aggregate(song_pipeline)
        ]


        updated_songs = []
        for song in top_songs:
            song_name = song['track']
            artist_name = song['artist']
            time_listened = song['count']
            query = f'track:{song_name} artist:{artist_name}'
            search_result = sp.search(q=query, type='track', limit=1)
            song_info = search_result['tracks']['items'][0]
            spotify_url = song_info['external_urls']['spotify']
            album_image_url = song_info['album']['images'][0]['url']
            updated_songs.append({
                'name': song_name,
                'artist': artist_name,
                'play_count': time_listened,
                'spotify_url': spotify_url,
                'album_image_url': album_image_url
            })
        print(updated_songs)
        return updated_songs