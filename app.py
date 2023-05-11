from flask import Flask
from bson.json_util import dumps
from pymongo import MongoClient
from bson import ObjectId

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


if __name__ == "__main__":
    app.run(debug=True)