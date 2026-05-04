import streamlit as st
from recommender import get_recommendations, ensure_user, mark_watched, get_watched_ids
from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://admin:12345@movierecommender.gu56d6o.mongodb.net/?appName=movierecommender")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["movierecommender"]

st.set_page_config(page_title="MoodReel", page_icon="🎬", layout="wide")
st.title("🎬 MoodReel v3 — Mood Based Movie Recommender App")

# --- Sidebar ---
with st.sidebar:
    st.header("👤 Your Profile")
    username = st.text_input("Enter your username", value="guest")


    if username:
        ensure_user(username)
        watched_ids = get_watched_ids(username)
    
    # Fetch user profile from MongoDB
        user_doc = mongo_client["movierecommender"].users.find_one(
            {"username": username},
            {"_id": 0, "created_at": 1, "last_seen": 1}
        )
    
        st.markdown(f"**Movies watched:** {len(watched_ids)}")
        if user_doc and "created_at" in user_doc:
            st.caption(f"Member since: {user_doc['created_at'].strftime('%d %b %Y')}")
        st.caption(f"Last seen: just now")

        if watched_ids:
            movies = list(db.movies.find(
                {"movieId": {"$in": watched_ids}},
                {"_id": 0, "title": 1, "movieId": 1}
            ))
            with st.expander("📋 Watch History"):
                for m in movies:
                    st.write(f"• {m['title']}")

    st.divider()
    st.header("⚙️ Filters")
    min_rating = st.slider("Minimum Rating ⭐", 0.0, 5.0, 0.0, 0.5)
    top_n = st.slider("Number of Results", 5, 20, 10)

# --- Mood Selection ---
st.subheader("How are you feeling?")

mood_options = [
    "happy 😊", "sad 😢", "excited 🤩",
    "scared 😱", "romantic 💕", "thoughtful 🤔", "nostalgic 🌅"
]

col1, col2 = st.columns(2)
with col1:
    mood1 = st.selectbox("Primary mood", mood_options, index=0)
with col2:
    mood2_options = ["None"] + mood_options
    mood2 = st.selectbox("Secondary mood (optional)", mood2_options, index=0)

selected_moods = [mood1.split()[0]]
if mood2 != "None":
    m2 = mood2.split()[0]
    if m2 != selected_moods[0]:
        selected_moods.append(m2)

if min_rating > 0:
    st.info(f"⭐ Filtering for movies rated **{min_rating}+**")
if len(selected_moods) == 2:
    st.info(f"🎭 Mixing moods: **{selected_moods[0]}** + **{selected_moods[1]}**")

# --- Recommend Button ---
if st.button("🎬 Recommend Movies", use_container_width=True):
    with st.spinner("Finding the perfect movies for your mood..."):
        recs = get_recommendations(
            moods=selected_moods,
            top_n=top_n,
            min_rating=min_rating,
            username=username if username != "guest" else None
        )
    st.session_state["recs"] = recs
    st.session_state["moods_label"] = " + ".join(selected_moods)

if "recs" in st.session_state:
    recs = st.session_state["recs"]

    if not recs:
        st.warning("No movies found. Try lowering the minimum rating.")
    else:
        st.subheader(f"Top picks for **{st.session_state['moods_label']}**:")

        # Fresh watched list on every render
        current_watched = get_watched_ids(username) if username and username != "guest" else []

        for i, movie in enumerate(recs, 1):
            rating_val = movie.get('avg_rating')
            rating_display = f"⭐ {rating_val}" if rating_val and rating_val != 'N/A' else "Not rated"

            with st.expander(f"{i}. {movie['title']}  {rating_display}  |  Score: {movie['score']}"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**Genres:** {', '.join(movie['genres'])}")
                    st.write(f"**Year:** {movie['year']}")
                    count = movie.get('rating_count', 0)
                    st.write(f"**Rating:** {rating_display} ({count:,} ratings)")
                with col_b:
                    if username and username != "guest":
                        already_watched = movie["movieId"] in current_watched
                        if already_watched:
                            st.success("✅ Watched")
                        else:
                            if st.button("Mark Watched", key=f"watched_{movie['movieId']}_{i}"):
                                mark_watched(username, movie["movieId"])
                                st.session_state["recs"] = [
                                    m for m in st.session_state["recs"]
                                    if m["movieId"] != movie["movieId"]
                                ]
                                st.rerun()
                    else:
                        st.caption("Enter a username\nto track history")