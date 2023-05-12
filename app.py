import datetime
from flask import Flask, jsonify, render_template
from bson.json_util import dumps
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

def convert_ms_to_time(ms):
    seconds = divmod(ms, 1000)
    minutes = divmod(ms, 6000)
    hours = divmod(ms, 36000)
    return hours[0], minutes[0], seconds[0]


app = Flask(__name__)

MONGO_URI = "mongodb+srv://lucastakanorisanchez:Pito@cluster00.tvlt0bo.mongodb.net"
client = MongoClient(MONGO_URI)
print(client.list_database_names())


# You can import your routes here
# For example, if you have a routes.py file containing your API routes, you can import it as:
# from routes import *

@app.route("/")
def hello():
    return "Welcome to the Spotistats API!"


@app.route("/users", methods=["GET"])
def get_users():
    print("Fetching users from the database")
    clients = MongoClient(MONGO_URI)
    db = clients["Spotistats"]
    # users_cursor = db.Users.find({})    
    # users = dumps(users_cursor)
    # print("Fetched users:", users)
    # return users
    users_cursor = db.Users.find({}, {"_id": 1, "email": 1})
    users_data = [{"_id": user["_id"], "email": user["email"]} for user in users_cursor]
    users = dumps(users_data)
    print("Fetched users' data:", users)
    return users

@app.route("/user/<user_id>/", methods=["GET"])
def user_data(user_id):
    client = MongoClient("mongodb+srv://lucastakanorisanchez:Pito@cluster00.tvlt0bo.mongodb.net/")
    db = client["Spotistats"]
    streaming_history = db["StreamingHistory"]

    total_streams = streaming_history.count_documents({})
    total_ms_played = streaming_history.aggregate([{"$group": {"_id": ObjectId(user_id), "total_msPlayed": {"$sum": "$msPlayed"}}}])
    total_unique_tracks = len(streaming_history.distinct("trackName"))
    total_unique_artists = len(streaming_history.distinct("artistName"))

    ms = next(total_ms_played)["total_msPlayed"]
    hours, minutes, seconds = convert_ms_to_time(ms)

    return {
        "total_streams": total_streams,
        "total_time_played": f"{hours} hours, {minutes} minutes, {seconds} seconds",
        "total_ms_played": ms,
        "total_unique_tracks": total_unique_tracks,
        "total_unique_artists": total_unique_artists
    }



@app.route("/user/<user_id>/playlists", methods=["GET"])
def get_user_playlists(user_id):
    # Connect to the database
    clients = MongoClient(MONGO_URI)
    db = clients["Spotistats"]

    # Retrieve the user's playlists
    playlists_cursor = db.Playlists.find({"id": ObjectId(user_id)})
    
    # Extract the playlist names and return them as JSON
    playlist_names = [playlist["name"] for playlist in playlists_cursor]
    playlists = dumps(playlist_names)
    return playlists

@app.route("/user/<user_id>/top_songs_by_time_listened", methods=["GET"])
def top_songs_by_time_listened(user_id, n_songs=20):
    clients = MongoClient(MONGO_URI)
    db = clients["Spotistats"]
    streaming_history = db["StreamingHistory"]

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

    songs = []
    for song_info in top_songs_by_time_listened:
        artist_name = song_info["_id"]["artist"]
        track_name = song_info["_id"]["track"]        
        play_count = song_info["totalTimeListened"]
        play_count, _ = divmod(play_count, 1000)
        songs.append({"name": track_name, "artist": artist_name, "play_count": play_count})

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("top_songs_for_time.html", songs=songs, user_id=user_id, n_songs=n_songs, timestamp=timestamp)



@app.route("/user/<user_id>/top_artists", methods=["GET"])
def get_most_artists(user_id,n_artists=20):
    clients = MongoClient(MONGO_URI)
    db = clients["Spotistats"]
    streaming_history = db["StreamingHistory"]
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

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("top_artists.html", top_artists=top_artists, timestamp=timestamp, n_artists=n_artists)

@app.route("/user/<user_id>/top_songs", methods=["GET"])
def get_most_songs(user_id,n_songs=20):
    clients = MongoClient(MONGO_URI)
    db = clients["Spotistats"]
    streaming_history = db["StreamingHistory"]
    
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

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("top_songs.html", top_songs=top_songs, timestamp=timestamp, n_songs=n_songs)

if __name__ == "__main__":
    app.run(debug=True)