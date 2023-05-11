from flask import Flask
from bson.json_util import dumps
from pymongo import MongoClient
from bson import ObjectId

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


@app.route("/user/<user_id>/playlists", methods=["GET"])
def get_user_playlists(user_id):
    # Connect to the database
    clients = MongoClient(MONGO_URI)
    db = clients["Spotistats"]

    # Retrieve the user's playlists
    playlists_cursor = db.Playlists.find({"user_id": ObjectId(user_id)})
    
    # Extract the playlist names and return them as JSON
    playlist_names = [playlist["name"] for playlist in playlists_cursor]
    playlists = dumps(playlist_names)
    return playlists


if __name__ == "__main__":
    app.run(debug=True)