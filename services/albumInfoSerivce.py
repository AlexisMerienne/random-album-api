import requests

DEEZER_ALBUM_URI = "https://api.deezer.com/album/"

def get_album_info(iAlbumId):
    api_url = DEEZER_ALBUM_URI+str(iAlbumId)
    response = requests.get(api_url)
    if response.status_code == 200:
        album_data=response.json()
        if 'error' in album_data:
            print(f"Error for album ID {iAlbumId}: {album_data['error']['message']}")
        else:
            # Extract relevant information
            album_info = {
                "id": album_data["id"],
                "title": album_data["title"],
                "genre": album_data["genres"]["data"][0]["name"],
            }
            return album_info
    else:
        print(f"Failed to fetch data for album ID {iAlbumId}. Status code: {response.status_code}")
        return None
