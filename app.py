from flask import Flask, request, redirect, session
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

import pandas as pd 
from rymscraper import rymscraper, RymUrl

app = Flask(__name__)

client_id = 'c400bb430d4d498f81f6e3cdb91c4297'
client_secret = 'd1666b600fd64f83a96bba77c063a569'
redirect_uri = 'http://localhost:8888/callback'

app.secret_key = 'random-secret-key'
app.config['SESSION_COOKIE_NAME'] = 'spotify_auth'

# Set up SpotifyOAuth
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=["user-library-read", "user-read-playback-state", "user-read-currently-playing", "playlist-read-private", "user-top-read", "user-read-private"],
    cache_path=".spotify_cache",
)
# Scrape rym for the data:
def rymScraper(song_list):
    network = rymscraper.RymNetwork()
    list_album_infos = network.get_albums_infos(names=song_list)
    df = pd.DataFrame(list_album_infos)
    print(df[['Name', 'RYM Rating']])

@app.route('/')
def index():
    return 'Hello! <a href="/login">Login with Spotify</a>'

@app.route('/login')
def login():
    return redirect(sp_oauth.get_authorize_url())

@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect('/profile')

@app.route('/profile')
def profile():
    token_info = session.get('token_info', None)

    if not token_info:
        return redirect('/login')

    sp = Spotify(auth=token_info['access_token'])
    user_info = sp.current_user()
    top_artist_info = sp.current_user_top_artists(limit=20, offset=0, time_range='short_term')
    top_song_info = sp.current_user_top_tracks(limit=5, offset=0, time_range='short_term')
    top_song_info2 = sp.current_user_top_tracks(limit=5, offset=5, time_range='short_term')
    l = []
    output = [ ( x['artists'][0]['name'] + (" - ") + x['album']['name']) for x in top_song_info['items']]
    output2 = [( x['artists'][0]['name'] + (" - ") + x['album']['name']) for x in top_song_info2['items']]
    print([output, output2])
    rymScraper(output)
    return f'Logged in as {user_info["display_name"]}'

if __name__ == '__main__':
    app.run(port=8888)


