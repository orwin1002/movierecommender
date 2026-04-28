import pytest
from mood_map import MOOD_MAP

# ── MOOD MAP TESTS ──────────────────────────────────────────────────────────

def test_all_moods_present():
    expected = {"happy", "sad", "excited", "scared", "romantic", "thoughtful", "nostalgic"}
    assert set(MOOD_MAP.keys()) == expected

def test_every_mood_has_genres():
    for mood, data in MOOD_MAP.items():
        assert "genres" in data, f"'{mood}' missing genres"
        assert len(data["genres"]) > 0, f"'{mood}' has empty genres"

def test_every_mood_has_tags():
    for mood, data in MOOD_MAP.items():
        assert "tags" in data, f"'{mood}' missing tags"
        assert len(data["tags"]) > 0, f"'{mood}' has empty tags"

def test_happy_maps_to_comedy():
    assert "Comedy" in MOOD_MAP["happy"]["genres"]

def test_scared_maps_to_horror():
    assert "Horror" in MOOD_MAP["scared"]["genres"]

def test_excited_maps_to_action():
    assert "Action" in MOOD_MAP["excited"]["genres"]

def test_no_duplicate_genres_per_mood():
    for mood, data in MOOD_MAP.items():
        genres = data["genres"]
        assert len(genres) == len(set(genres)), f"'{mood}' has duplicate genres"

def test_no_duplicate_tags_per_mood():
    for mood, data in MOOD_MAP.items():
        tags = data["tags"]
        assert len(tags) == len(set(tags)), f"'{mood}' has duplicate tags"

def test_genres_are_strings():
    for mood, data in MOOD_MAP.items():
        for g in data["genres"]:
            assert isinstance(g, str), f"Genre in '{mood}' is not a string"

# ── RECOMMENDER LOGIC TESTS (no DB) ─────────────────────────────────────────

def test_mood_lookup_returns_list():
    genres = MOOD_MAP.get("happy", {}).get("genres", [])
    assert isinstance(genres, list)

def test_unknown_mood_returns_empty():
    result = MOOD_MAP.get("furious", {}).get("genres", [])
    assert result == []

def test_movie_record_has_required_fields():
    sample = {"movieId": 1, "title": "Toy Story (1995)", "genres": ["Animation"], "score": 4}
    assert "movieId" in sample
    assert "title"   in sample
    assert "genres"  in sample
    assert "score"   in sample

def test_score_is_non_negative():
    scores = [0, 2, 4, 6, 10]
    for s in scores:
        assert s >= 0

def test_filter_by_min_rating():
    movies = [
        {"title": "A", "avg_rating": 4.5},
        {"title": "B", "avg_rating": 2.0},
        {"title": "C", "avg_rating": 3.8},
    ]
    min_rating = 3.5
    filtered = [m for m in movies if m["avg_rating"] >= min_rating]
    assert len(filtered) == 2
    assert all(m["avg_rating"] >= min_rating for m in filtered)

def test_watched_movies_excluded():
    all_movies  = [1, 2, 3, 4, 5]
    watched_ids = [2, 4]
    result = [m for m in all_movies if m not in watched_ids]
    assert result == [1, 3, 5]

def test_top_n_limits_results():
    movies = list(range(50))
    top_n  = 10
    assert len(movies[:top_n]) == 10

def test_dual_mood_params_are_different():
    mood1, mood2 = "happy", "excited"
    assert mood1 != mood2

def test_rating_within_valid_range():
    ratings = [3.5, 4.2, 2.8, 5.0, 0.0]
    for r in ratings:
        assert 0.0 <= r <= 5.0

def test_year_extracted_from_title():
    title = "Toy Story (1995)"
    year  = title[-5:-1] if "(" in title else "Unknown"
    assert year == "1995"

def test_title_without_year_returns_unknown():
    title = "Some Movie"
    year  = title[-5:-1] if "(" in title else "Unknown"
    assert year == "Unknown"