#### Search Spotify (SEARCHIFY)
#### Video Demo:  https://youtu.be/SjEKgcdsvzY
#### Description:
This app searches for songs via the Spotify Developer Web API, stores them in a SQLITE3 database, then allows the user to search for songs that have similar music features.
Upon startup, the API checks the SQLITE database search.db for last_updated table values. If not updated today, the API searches for new songs via the Spotify API to upload to the database.

# STARTUP FUNC search_for_all_songs(token, offset, year):
This was originally a feature intended to ensure that the database would always be updated with the current songs. It also has the additional benefit of defending against Error429: too many requests, as there will be limited searches conducted every day via the API.
Within the code, the user can edit:
-how many songs to search
-what year to search the songs
Additional features can be added to allow for a randomisation of the dates to search from, such that the database can be updated with songs from different time periods.
The searches are conducted in 'waves' of 50 as per API documentation, and at 1 second intervals to prevent Error429.

# STARTUP FUNC get_song_features(token, id):
The API then individually searches for each song's music features, and adds them to the SQLITE database.

# PATH /manual_search:
The user is then able to search for songs based on their respective music features, namely:
-Danceability
-Energy
-Tempo
-Valence
The features are banded in high, medium, and low respectively after analysis of the distribution of songs' features.

# PATH /song:
The user is able to input their own song, and are returned songs that have similar audio features. 