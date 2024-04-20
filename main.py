import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth



#a little just in case measure if youre using vs code or a similar product like I am.
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


#replace the stuff below with your actual id and secret
#https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = 'place-here'
SPOTIFY_CLIENT_SECRET = 'place-here'
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'
SPOTIFY_SCOPE = 'playlist-read-private,playlist-modify-public,playlist-modify-private'

sp_auth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                       client_secret=SPOTIFY_CLIENT_SECRET,
                       redirect_uri=SPOTIFY_REDIRECT_URI,
                       scope=SPOTIFY_SCOPE)

sp = spotipy.Spotify(auth_manager=sp_auth)
current_user_id = sp.me()['id']


#playlist stuff- you dont gotta understand much of it
def create_playlist(name, public=True): #if you dont want public, set it to false
    new_playlist = sp.user_playlist_create(current_user_id, name, public=public)
    return new_playlist['id']

def get_user_playlists():
    user_playlists = []
    playlists = sp.current_user_playlists(limit=50)
    while playlists:
        for playlist in playlists['items']:
            if playlist['owner']['id'] == current_user_id:
                user_playlists.append(playlist)
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return user_playlists

def sort_playlists(playlists, sort_by='name'):
    if sort_by == 'tracks':
        return sorted(playlists, key=lambda p: p['tracks']['total'], reverse=True)
    else:
        return sorted(playlists, key=lambda p: p['name'].lower())

def search_playlists(playlists, search_term):
    return [p for p in playlists if search_term.lower() in p['name'].lower()]

def choose_playlist():
    user_playlists = get_user_playlists()
    print("Sort by:\n1: Name\n2: Number of tracks")
    sort_choice = input("Choose a sorting option (default is Name): ").strip()
    sort_by = 'tracks' if sort_choice == '2' else 'name'
    sorted_playlists = sort_playlists(user_playlists, sort_by=sort_by)

    search_query = input("Enter a search term to filter (press enter to skip): ").strip()
    if search_query:
        sorted_playlists = search_playlists(sorted_playlists, search_query)

    for index, playlist in enumerate(sorted_playlists):
        print(f"{index+1}: {playlist['name']} - {playlist['tracks']['total']} tracks")

    if sorted_playlists:
        choice = int(input("Enter the number of the playlist to swipe through: "))
        selected_playlist = sorted_playlists[choice - 1]
        return selected_playlist['id'], selected_playlist['name']
    else:
        print("No playlists found.")
        return None, None
#if you dont want public, set to false
def get_or_create_playlist(name, public=True):
    playlists = get_user_playlists()
    for playlist in playlists:
        if playlist['name'].lower() == name.lower():
            return playlist['id']
    return create_playlist(name, public=public)

def get_playlist_tracks(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id, limit=100)
    while results:
        tracks.extend([item['track']['uri'] for item in results['items'] if item['track']])
        if results['next']:
            results = sp.next(results)
        else:
            break
    return tracks


#DO NOT TOUCH THIS, i did some shenanigans and it broke it for a bit.
def swipe_tracks(playlist_id, playlist_name, left_vibe, right_vibe):
    left_playlist_name = f"{playlist_name} - {left_vibe}"
    right_playlist_name = f"{playlist_name} - {right_vibe}"
    left_playlist_id = get_or_create_playlist(left_playlist_name)
    right_playlist_id = get_or_create_playlist(right_playlist_name)

    left_playlist_tracks = get_playlist_tracks(left_playlist_id)
    right_playlist_tracks = get_playlist_tracks(right_playlist_id)

    results = sp.playlist_tracks(playlist_id, limit=100)
    while results:
        for track in results['items']:
            if track['track']:
                track_name = track['track']['name']
                track_uri = track['track']['uri']

                if track_uri in left_playlist_tracks or track_uri in right_playlist_tracks:
                    continue

                print(f"Track: {track_name}")
                swipe = input(f"Swipe (L for {left_vibe}, R for {right_vibe}, S to skip): ").upper()
                if swipe == 'L':
                    sp.playlist_add_items(left_playlist_id, [track_uri])
                    left_playlist_tracks.append(track_uri)
                elif swipe == 'R':
                    sp.playlist_add_items(right_playlist_id, [track_uri])
                    right_playlist_tracks.append(track_uri)
                elif swipe == 'S':
                    pass
                else:
                    print("Invalid input. Try again.")
        if results['next']:
            results = sp.next(results)
        else:
            results = None


#alter this however you want.
def main():
    print("Let's set up the vibes for your playlists.")
    left_vibe = input("Enter the name for the LEFT vibe (e.g., 'Chill', 'Sad'): ").strip()
    right_vibe = input("Enter the name for the RIGHT vibe (e.g., 'Upbeat', 'Happy'): ").strip()

    playlist_id, playlist_name = choose_playlist()
    if playlist_id and playlist_name:
        swipe_tracks(playlist_id, playlist_name, left_vibe, right_vibe)
    else:
        print("Exiting, no valid playlist selected.")

if __name__ == "__main__":
    main()
