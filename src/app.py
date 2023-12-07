from flask import Flask, jsonify
import requests
import random

from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify

app = Flask(__name__)

DEEZER_SEARCH_API = "https://api.deezer.com/search"
DEEZER_ALBUM_URI = "https://www.deezer.com/album/"
SPOTIFY_SEARCH_API = "https://api.spotify.com/v1/search"

SPOTIFY_CLIENT_ID = "05f650042c7a43e2b5a450923f97ab27"
SPOTIFY_CLIENT_SECRET = "98786edd46b04055b356fdb3c04ef32d"
SPOTIFY_REDIRECT_URI = "https://myapp.fr"

# Spotify client credentials manager
spotify_client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
)
spotify = Spotify(client_credentials_manager=spotify_client_credentials_manager)



def get_random_number():
    return random.randint(1, 9999)


def get_random_album():
    random_number = get_random_number()
    api_url = f"{DEEZER_SEARCH_API}?q={random_number}&type=album"

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            random_track = random.choice(data)
            album_info = {
                "deezer_uri": DEEZER_ALBUM_URI+str(random_track["album"]["id"]),
                "cover_medium": random_track["album"]["cover_medium"],
                "title": random_track["album"]["title"],
                "artist_name": random_track["artist"]["name"],
            }
            # Search for the same album on Spotify
            spotify_query = f"{album_info['artist_name']} {album_info['title']}"
            spotify_result = spotify.search(q=spotify_query, type='album', limit=1)
            if 'albums' in spotify_result and 'items' in spotify_result['albums']:
                spotify_album = spotify_result['albums']['items'][0]
                album_info["spotify_uri"] = spotify_album["external_urls"]["spotify"]

            return album_info
    return None


@app.route("/album", methods=["GET"])
def random_album():
    album_info = get_random_album()

    if album_info:
        return jsonify(album_info), 200
    else:
        return jsonify({"error": "Unable to fetch random album"}), 500


if __name__ == "__main__":
    app.run(debug=True)