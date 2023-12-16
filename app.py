import os
import random
import string
import requests
import logging

from flask import Flask, jsonify
from flask_cors import CORS

from decouple import config

from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify

import nltk
from nltk.corpus import words
from nltk import FreqDist

from services import albumInfoSerivce


app = Flask(__name__)
CORS(app)

DEEZER_SEARCH_API = "https://api.deezer.com/search"
DEEZER_ALBUM_URI = "https://www.deezer.com/album/"
SPOTIFY_SEARCH_API = "https://api.spotify.com/v1/search"


SPOTIFY_CLIENT_ID = config("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = config("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = config("SPOTIFY_REDIRECT_URI")

logging.basicConfig(level=logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

# Set the log level for Flask to DEBUG
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)


# Spotify client credentials manager
spotify_client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
)
spotify = Spotify(client_credentials_manager=spotify_client_credentials_manager)

nltk.download('words')
nltk.download('lexique')

# Get a list of English words
english_words = words.words()



def get_random_sequence():
    engliqh_freq_dist = FreqDist(english_words)
    common_words = engliqh_freq_dist.most_common(844)
    common_word_list = [word[0] for word in common_words]

    seq_size = random.choice([3, 4])

    # Adjust the probabilities for getting a number, string, or word
    choice_weights = [1, 1, 8]
    choices = [str(random.randint(1, 10**seq_size - 1)).zfill(seq_size),
               ''.join(random.choice(string.ascii_letters) for _ in range(seq_size)),
               random.choice(common_word_list)]

    return random.choices(choices, weights=choice_weights)[0]


def get_random_album():
    random_sequence = get_random_sequence()
    logging.info(f"Random number: {random_sequence}")
    api_url = f"{DEEZER_SEARCH_API}?q={random_sequence}&type=album"

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            random_object = data[0]
            album_data = albumInfoSerivce.get_album_info(random_object["album"]["id"])
            album_info = {
                "deezer_uri": DEEZER_ALBUM_URI+str(random_object["album"]["id"]),
                "albumInfos" : album_data,
                "cover_medium": random_object["album"]["cover_medium"],
                "title": random_object["album"]["title"],
                "artist_name": random_object["artist"]["name"],
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
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
