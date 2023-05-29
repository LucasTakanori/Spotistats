import datetime
from flask import Flask, jsonify, render_template
from datetime import datetime
from spotifyHandler import SpotifyHandler
from spotifyHandler import convert_ms_to_time
from flask import render_template
from flask import request, redirect, url_for
import json

app = Flask(__name__)

MONGO_URI = "mongodb+srv://lucastakanorisanchez:Pito@cluster00.tvlt0bo.mongodb.net"
handler = SpotifyHandler(mongo_uri=MONGO_URI)

@app.route("/")
def hello():
    return "Welcome to the Spotistats API!"

@app.route('/users', methods=['GET'])
def get_users():
    users = handler.get_all_users()
    return jsonify(users)

@app.route("/user/<user_id>/", methods=["GET"])
def get_user_data(user_id):
    user_data = handler.get_user_data(user_id)
    playlists = handler.get_user_playlists(user_id)
    top_artists = handler.get_most_artists(user_id)
    top_songs = handler.top_songs_by_time_listened(user_id)

    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("user_data.html",
                        total_streams=user_data["total_streams"],
                        total_time_played=user_data["total_time_played"],
                        total_ms_played=user_data["total_ms_played"],
                        total_unique_tracks=user_data["total_unique_tracks"],
                        total_unique_artists=user_data["total_unique_artists"],
                        playlists=playlists,
                        top_artists=top_artists,
                        top_songs=top_songs,
                        timestamp=timestamp)



@app.route("/user/<user_id>/playlists", methods=["GET"])
def get_user_playlists(user_id):
    playlists = handler.get_user_playlists(user_id)
    return jsonify(playlists)
   

@app.route('/user/<user_id>/top_songs_by_time_listened', methods=['GET'])
def top_songs_by_time_listened(user_id):
    n_songs = request.args.get('n_songs', default=20, type=int)
    songs = handler.top_songs_by_time_listened(user_id, n_songs)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("top_songs_for_time.html", songs=songs, user_id=user_id, n_songs=n_songs, timestamp=timestamp)


@app.route('/user/<user_id>/top_artists', methods=['GET'])
def get_most_artists(user_id):
    n_artists = request.args.get('n_artists', default=20, type=int)
    top_artists = handler.get_most_artists(user_id, n_artists)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("top_artists.html", top_artists=top_artists
                           , timestamp=timestamp, n_artists=n_artists)


@app.route("/user/<user_id>/top_songs", methods=["GET"])
def get_most_songs(user_id, n_songs=20):
    n_songs = request.args.get('n_songs', default=20, type=int)
    top_songs = handler.get_most_songs(user_id, n_songs)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("top_songs.html", top_songs=top_songs, timestamp=timestamp, n_songs=n_songs)

@app.route('/Pito')
def index():
    image_url = 'https://i.scdn.co/image/ab67616d0000b273fc8563c0dc75d79e73c2dca0'
    return render_template('index.html', image_url=image_url)


@app.route('/user_data_form')
def user_data_form():
    return render_template('user_id_form.html')


@app.route('/submit_user_data_form', methods=['POST'])
def submit_user_data_form():
    user_id = request.form['user_id']
    return redirect(url_for('get_user_data', user_id=user_id))

if __name__ == "__main__":
    app.run(debug=True)