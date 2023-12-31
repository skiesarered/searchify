import os
import datetime
#import sql
from flask import Flask, flash, redirect, render_template, request, session
from dotenv import load_dotenv
import base64
from requests import post, get
import json
from helper import *
import sqlite3
import time
from datetime import date

#establish connection to db
con = sqlite3.connect("search.db", check_same_thread=False)
db = con.cursor()

# Configure application
app = Flask(__name__)
load_dotenv()

#client id and secret for spotify api
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


# ensure database is only updated once a day
current_date = date.today()
current_date_str = current_date.strftime("%Y/%m/%d")
last_updated = db.execute("SELECT * FROM last_updated")
last_updated = last_updated.fetchone()[0]
if(current_date_str != str(last_updated)):

    # #clears current songs

    # # db.execute("DELETE FROM songs")
    # # con.commit

    #loads songs into database
    OFFSET = 50
    TOTAL_SONGS_TO_SEARCH = 1500
    DELAY = 1
    #TODO: allow for user input for year
    
    YEAR = "2012-2022"
    token = get_token()
    error429 = False

    for i in range(0, TOTAL_SONGS_TO_SEARCH, OFFSET):

        songs = search_for_all_songs(token, i, YEAR)

        #check if error429 was returned
        if songs == {} or error429:
            break;
        
        for song in songs:

            #to prevent error 429
            time.sleep(DELAY)
            features = get_song_features(token, song["id"])

            #check for error429
            if features == {}:
                error429 = True;
                break;
            
            print(song)
            print(features)

            db.execute("INSERT INTO songs VALUES (?,?,?,?,?,?,?)", 
                (song["name"], song["id"], features.get("danceability", 0.5), features.get("energy", 0.5), features.get("tempo", 120), features.get("valence", 0.7), song["artists"][0]["name"])
            #     #(song["name"], song["id"], features.get("danceability"), features.get("energy"), features.get("key"), features.get("loudness"), features.get("speechiness"), features.get("tempo"), features.get("valence"))
            #     (song["name"], song["id"], features["danceability"], features.get["energy"], features.get["key"], features.get["loudness"], features.get["speechiness"], features.get["tempo"], features.get["valence"]
            )
            con.commit()

    print(current_date_str, last_updated)
    db.execute("DELETE FROM last_updated")
    db.execute("INSERT INTO last_updated VALUES(?)", [current_date_str])
    con.commit()

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/manual", methods=["GET", "POST"])
def manual_search():
    if request.method == "POST":
        features = {
            "Danceability": request.form.get("Danceability"),
            "Energy": request.form.get("Energy"),
            #{"name" : "Instrumentalness", "intensity": request.form.get("Instrumentalness")},
            #"Key": request.form.get("Key"),
            #{"name" : "Liveliness", "intensity": request.form.get("Liveliness")},
            #"Loudness": request.form.get("Loudness"),
            #"Speechiness": request.form.get("Speechiness"),
            "Tempo": request.form.get("Tempo"),
            "Valence": request.form.get("Valence")
        }
        # danceability 0.4 - 0.7
        # energy  0.4 - 0.7
        # key 4 - 8
        # loudness 17 - -5
        # speechiness 0.4 - 0.6
        # tempo 90 - 140
        # valence 0.5 - 0.8
        #TODO: REMOVE LOUDNESS AND SPEECHINESS
        matched_songs = db.execute("SELECT * FROM songs WHERE (danceability BETWEEN ? AND ?) AND (energy BETWEEN ? AND ?) AND (tempo BETWEEN ? AND ?) AND (valence BETWEEN ? AND ?)",
                                    (
                                        0 if features["Danceability"] == "low" else 0.8 if features["Danceability"] == "high" else 0.5,
                                        0.5 if features["Danceability"] == "low" else 1.0 if features["Danceability"] == "high" else 0.8,
                                        0 if features["Energy"] == "low" else 0.8 if features["Energy"] == "high" else 0.5,
                                        0.5 if features["Energy"] == "low" else 1.0 if features["Energy"] == "high" else 0.8,
                                        #-20 if features["Loudness"] == "low" else -6 if features["Loudness"] == "high" else -8,
                                        #-8 if features["Loudness"] == "low" else 0 if features["Loudness"] == "high" else -6,
                                        #0 if features["Speechiness"] == "low" else 0.1 if features["Speechiness"] == "high" else 0.06,
                                        #0.06 if features["Speechiness"] == "low" else 1 if features["Speechiness"] == "high" else 0.1,
                                        0 if features["Tempo"] == "low" else 140 if features["Tempo"] == "high" else 100,
                                        100 if features["Tempo"] == "low" else 1000 if features["Tempo"] == "high" else 140,
                                        0 if features["Valence"] == "low" else 0.6 if features["Valence"] == "high" else 0.4,
                                        0.4 if features["Valence"] == "low" else 2 if features["Valence"] == "high" else 0.6
                                    ))
        
        matched_songs_no_duplicates={}
        matched_songs = matched_songs.fetchall()
        for song in matched_songs:
            if song[0] not in matched_songs_no_duplicates:
                matched_songs_no_duplicates[song[0]] = song[6]
        print(matched_songs_no_duplicates)
        return render_template("manual_results.html", features=features, matched_songs=matched_songs_no_duplicates)

    features = [
        {"name" : "Danceability", "description": "Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable."},
        {"name": "Energy", "description": "Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy."},
        # {"name" : "Instrumentalness", "description": "i am instrument"},
        #{"name" : "Key", "description": "i am key"},
        #{"name" : "Liveliness", "description": "i am liveliness"},
        {"name" : "Tempo", "description": "The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration."},
        {"name" : "Valence", "description": "A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry)."}
    ]
    return render_template("manual_search.html", features=features)

@app.route("/song", methods=["GET", "POST"])
def song_search():
    if request.method == "POST":
        token = get_token()

        song_with_spaces = request.form.get("song")
        artist_with_spaces = request.form.get("artist")

        if song_with_spaces == "" or artist_with_spaces == "":
            return render_template("search_by_song.html")
        #replace spaces with '+'
        song = ""
        artist = ""
        
        for char in song_with_spaces:
            if char == ' ':
                song += '+'
            else:
                song += char

        for char in artist_with_spaces:
            if char == ' ':
                artist += '+'
            else:
                artist += char

        song_details = get_song_id(token, song, artist)
        features = get_song_features(token, song_details[2])

        print(song_details)

        matched_songs = db.execute("SELECT * FROM songs WHERE (danceability BETWEEN ? AND ?) AND (energy BETWEEN ? AND ?) AND (tempo BETWEEN ? AND ?) AND (valence BETWEEN ? AND ?)",(

            features.get("danceability", 0.5) - 0.2, 
            features.get("danceability", 0.5) + 0.2, 
            features.get("energy", 0.5) - 0.2,
            features.get("energy", 0.5) + 0.2,  
            features.get("tempo", 120) - 20,
            features.get("tempo", 120) + 20,
            features.get("valence", 0.7) - 0.2,
            features.get("valence", 0.7) + 0.2,

        ))


        matched_songs_no_duplicates={}
        matched_songs = matched_songs.fetchall()
        for song in matched_songs:
            if song[0] not in matched_songs_no_duplicates:
                matched_songs_no_duplicates[song[0]] = song[6]
        print(matched_songs_no_duplicates)
        return render_template("song_results.html", artist=song_details[1], song=song_details[0], matched_songs=matched_songs_no_duplicates)        

        
    return render_template("search_by_song.html")