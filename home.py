import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ---------- Streamlit Config ----------
st.set_page_config(page_title="Spotify Stats Viewer", layout="wide")

# ---------- Spotify Credentials ----------
CLIENT_ID = "your-client-id"  # 🔁 Replace with your real values
CLIENT_SECRET = "your-client-secret"
REDIRECT_URI = "https://your-streamlit-app.streamlit.app"  # 🔁 Replace with your deployed app URL

# ---------- OAuth Setup ----------
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-top-read",
    show_dialog=True,
    cache_path=".cache"
)

# ---------- Session State ----------
if "token_info" not in st.session_state:
    st.session_state.token_info = None

# ---------- Login Flow ----------
if not st.session_state.token_info:
    auth_url = auth_manager.get_authorize_url()
    st.subheader("Login with your Spotify account")
    st.markdown(f"[Click here to authorize Spotify]({auth_url})")

    response_url = st.text_input("Paste the full URL you were redirected to after login:")
    if response_url:
        code = auth_manager.parse_response_code(response_url)
        if code:
            token_info = auth_manager.get_access_token(code, as_dict=True)
            st.session_state.token_info = token_info
            st.experimental_rerun()
else:
    # ---------- Authenticated ----------
    sp = spotipy.Spotify(auth=st.session_state.token_info["access_token"])

    st.title("Spotify Stats Viewer")

    # ---------- Sidebar ----------
    st.sidebar.title("Navigation")
    view = st.sidebar.radio("View", ["Top Tracks", "Top Artists", "Top Genres"])
    time_ranges = {
        "Last 4 Weeks": "short_term",
        "Last 6 Months": "medium_term",
        "All Time": "long_term"
    }
    time_range = st.sidebar.selectbox("Select Time Range", list(time_ranges.keys()))
    tr_key = time_ranges[time_range]

    # ---------- Views ----------
    if view == "Top Tracks":
        st.header(f"🎵 Your Top Tracks ({time_range})")
        results = sp.current_user_top_tracks(limit=10, time_range=tr_key)
        for idx, item in enumerate(results['items']):
            st.subheader(f"{idx+1}. {item['name']}")
            st.caption(f"By {item['artists'][0]['name']}")
            if item['preview_url']:
                st.audio(item['preview_url'])
            st.image(item['album']['images'][0]['url'], width=150)
            st.markdown("---")

    elif view == "Top Artists":
        st.header(f"🎤 Your Top Artists ({time_range})")
        results = sp.current_user_top_artists(limit=10, time_range=tr_key)
        for idx, artist in enumerate(results['items']):
            st.subheader(f"{idx+1}. {artist['name']}")
            st.caption(f"Genres: {', '.join(artist['genres'])}")
            st.image(artist['images'][0]['url'], width=150)
            st.markdown(f"[Open on Spotify]({artist['external_urls']['spotify']})")
            st.markdown("---")

    elif view == "Top Genres":
        st.header(f"📊 Your Top Genres ({time_range})")
        results = sp.current_user_top_artists(limit=50, time_range=tr_key)
        genre_counts = {}
        for artist in results['items']:
            for genre in artist['genres']:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_genres:
            genre_labels = [g[0].title() for g in top_genres]
            genre_values = [g[1] for g in top_genres]
            st.bar_chart(dict(zip(genre_labels, genre_values)))
        else:
            st.info("No genres found.")

    st.markdown("---")
    st.caption("Made with ❤️ by Adarsh")
