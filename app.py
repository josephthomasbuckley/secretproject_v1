from flask import Flask, request, redirect, session
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

client_id = '5c748acdbc41475fa3cb4b63c7425139'
client_secret = '68919f727b2244918ca9b692f4d4d0aa'
redirect_uri = 'http://localhost:8888/callback'

app.secret_key = 'random-secret-key'
app.config['SESSION_COOKIE_NAME'] = 'spotify_auth'

# Set up SpotifyOAuth
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=["user-library-read", "user-read-playback-state", "user-read-currently-playing"],
    cache_path=".spotify_cache",
)

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
    return f'Logged in as {user_info["display_name"]}'

if __name__ == '__main__':
    app.run(port=8888)
