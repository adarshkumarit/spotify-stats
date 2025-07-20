import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ---------- 🎧 Streamlit Page Config ----------
st.set_page_config(page_title="🎧 Spotify Stats", layout="wide")

# ---------- 🌸 Custom CSS ----------
st.markdown("""
    <style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1525032194464-24d2b402fa4d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Courier New', monospace;
        color: #000000 !important;
    }

    h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stCaption, .stText {
        color: #000000 !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.85);
    }

    .stRadio > div, .stSelectbox > div {
        background-color: #ffffffaa;
        border-radius: 10px;
        padding: 0.5rem;
    }

    .stRadio label, .stSelectbox label {
        color: #000000 !important;
        font-size: 16px;
        font-weight: 600;
    }

    footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- 🎧 App Title ----------
st.title("🖥️ Spotify Stats Viewer (Retro Style)")

# ---------- Sidebar ----------
st.sidebar.title("📟 Navigation")
view_option = st.sidebar.radio("Select View:", ["🎵 Top Tracks", "🎤 Top Artists", "📊 Top Genres"])

TIME_RANGES = {
    "Last 4 Weeks": "short_term",
    "Last 6 Months": "medium_term",
    "All Time": "long_term"
}
selected_range = st.sidebar.selectbox("Select Time Range:", list(TIME_RANGES.keys()))
time_range = TIME_RANGES[selected_range]

# ---------- Spotify Authentication ----------
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=st.secrets["SPOTIPY_CLIENT_ID"],
    client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
    redirect_uri=st.secrets["SPOTIPY_REDIRECT_URI"],
    scope="user-top-read",
    show_dialog=True
))

# ---------- Top Tracks ----------
if view_option == "🎵 Top Tracks":
    st.header(f"🎵 Your Top Tracks ({selected_range})")
    try:
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
    except:
        st.error("⚠️ Authorization failed. Please check your credentials.")

# ---------- Top Artists ----------
elif view_option == "🎤 Top Artists":
    st.header(f"🎤 Your Top Artists ({selected_range})")
    try:
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
    except:
        st.error("⚠️ Authorization failed. Please check your credentials.")

# ---------- Top Genres ----------
elif view_option == "📊 Top Genres":
    st.header(f"📊 Your Top Genres ({selected_range})")
    try:
        results = sp.current_user_top_artists(limit=50, time_range=time_range)
        genre_count = {}
        for artist in results['items']:
            for genre in artist['genres']:
                genre_count[genre] = genre_count.get(genre, 0) + 1

        if genre_count:
            sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
            top_genres = dict(sorted_genres[:10])

            # 🎨 Area Chart
            st.markdown("#### 📈 Genre Popularity Chart")
            st.area_chart(top_genres)

            # 🔝 List View
            st.markdown("#### 🔝 Top Genres List")
            for idx, (genre, count) in enumerate(sorted_genres[:10]):
                st.markdown(f"{idx + 1}. **{genre.title()}** — {count} artists")
        else:
            st.info("No genres found.")
    except:
        st.error("⚠️ Authorization failed. Please check your credentials.")

# ---------- Footer ----------
st.markdown("---")
st.caption("🌸 Hello cuties! Hope you liked this page. Share your review at ishuwilltell@gmail.com 💌 — Created by Adarsh.")
