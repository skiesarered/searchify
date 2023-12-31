from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com./api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)    
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = f"https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    return json_result[0]

#search for all songs from this year, then get the individual audio features, then return the list that match
#https://api.spotify.com/v1/search?q=year%3A2023&type=track
def search_for_all_songs(token, offset, year):
    url = f"https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q=year%3A{year}&type=track&market=SG&limit=50&offset={offset}"
    #query = 
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    if list(json_result.keys())[0] == "error":
        print(result.headers, result.content)
        print(json_result)
        return {};
    return json_result["tracks"]["items"]

    

def get_song_features(token, id):
    #https://api.spotify.com/v1/audio-features/72YGkMqYppwTsktfpOJtVX
    url = f"https://api.spotify.com/v1/audio-features/"
    headers = get_auth_header(token)
    query = f"{id}"
    #query = f"{id}"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    if list(json_result.keys())[0] == "error":
        #print(result.headers, result.content)
        #print(json_result)
        return {};
    return json_result
#def search_for_songs_by_feature(token, features)
#do for tags hipster and new also

def get_song_id(token, title, artist):
#'https://api.spotify.com/v1/search?q=track%3Agrenade+artist%3Abruno+mars&type=track'
    url = f"https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q=track%3A{title}+artist%3A{artist}&type=track&market=us"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return [json_result["tracks"]["items"][0]["name"], json_result["tracks"]["items"][0]["artists"][0]["name"], json_result["tracks"]["items"][0]["id"]]
#token = get_token()
#result = search_for_artist(token, "taylor swift")
