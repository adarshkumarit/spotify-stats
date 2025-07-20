import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import urlencode
import os

# ---------- 🎧 Streamlit Page Config ----------
st.set_page_config(page_title="🎧 Spotify Stats", layout="wide")

# ---------- 🌸 Retro CSS Styling ----------
st.markdown("""
    <style>
    body, .stApp {
        background-color: black !important;
        color: limegreen !important;
        font-family: "Courier New", monospace;
    }
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1525032194464-24d2b402fa4d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stCaption, .css-10trblm, label, .stText {
        color: limegreen !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111;
        color: limegreen !important;
    }
    .css-1d391kg {
        color: limegreen !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- 🎛 Sidebar Navigation ----------
st.sidebar.title("🖥️ Navigation")
view = st.sidebar.radio("Select View:", ["🎵 Top Tracks", "🎤 Top Artists", "📊 Top Genres"])
ranges = {"Last 4 Weeks": "short_term", "Last 6 Months": "medium_term", "All Time": "long_term"}
range_name = st.sidebar.selectbox("Select Time Range:", list(ranges.keys()))
time_range = ranges[range_name]

# ---------- 🛡️ Spotify OAuth Setup ----------
scope = "user-top-read"
sp_oauth = SpotifyOAuth(
    client_id=st.secrets["SPOTIPY_CLIENT_ID"],
    client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
    redirect_uri=st.secrets["SPOTIPY_REDIRECT_URI"],
    scope=scope,
    show_dialog=True
)

token_info = sp_oauth.get_cached_token()

if not token_info:
    auth_url = sp_oauth.get_authorize_url()
    st.warning("🔒 You need to log in to Spotify to continue.")
    st.markdown(f"[🔐 Click here to log in to Spotify]({auth_url})")
    st.stop()

# ---------- ✅ Spotify Authenticated Client ----------
sp = spotipy.Spotify(auth=token_info['access_token'])

# ---------- 📊 Content Based on View ----------
if view == "🎵 Top Tracks":
    st.header(f"🎵 Your Top Tracks ({range_name})")
    results = sp.current_user_top_tracks(limit=10, time_range=time_range)
    for idx, item in enumerate(results['items']):
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(item['album']['images'][0]['url'], width=80)
        with col2:
            st.subheader(f"{idx + 1}. {item['name']}")
            st.caption(f"By {item['artists'][0]['name']}")
            if item['preview_url']:
                st.audio(item['preview_url'], format="audio/mp3")
            else:
                st.write("No preview available.")
        st.divider()

elif view == "🎤 Top Artists":
    st.header(f"🎤 Your Top Artists ({range_name})")
    results = sp.current_user_top_artists(limit=10, time_range=time_range)
    for idx, artist in enumerate(results['items']):
        col1, col2 = st.columns([1, 5])
        with col1:
            if artist['images']:
                st.image(artist['images'][0]['url'], width=80)
        with col2:
            st.subheader(f"{idx + 1}. {artist['name']}")
            genres = ", ".join(artist['genres']) if artist['genres'] else "Unknown"
            st.caption(f"Genres: {genres}")
            st.markdown(f"[🔗 Open on Spotify]({artist['external_urls']['spotify']})")
        st.divider()

elif view == "📊 Top Genres":
    st.header(f"📊 Your Top Genres ({range_name})")
    results = sp.current_user_top_artists(limit=50, time_range=time_range)
    genre_count = {}
    for artist in results['items']:
        for genre in artist['genres']:
            genre_count[genre] = genre_count.get(genre, 0) + 1

    if genre_count:
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:10]
        top_genres = {genre.title(): count for genre, count in sorted_genres}
        st.area_chart(top_genres)
        st.markdown("### 📝 Genre Breakdown")
        for idx, (genre, count) in enumerate(top_genres.items()):
            st.markdown(f"{idx + 1}. **{genre}** — {count} artists")
    else:
        st.info("No genre data available.")

# ---------- 🖋 Footer ----------
st.markdown("---")
st.caption("🖤 Made with love by Adarsh • Contact: ishuwilltell@gmail.com")
