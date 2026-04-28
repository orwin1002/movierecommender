import time
from recommender import get_recommendations, db

# Experiment 1: Index performance
def experiment_index_performance():
    print("=== Experiment 1: Index Performance ===")
    db.movies.drop_indexes()
    start = time.time()
    list(db.movies.find({"genres": "Comedy"}).limit(100))
    no_index_time = time.time() - start

    db.movies.create_index([("genres", 1)])
    start = time.time()
    list(db.movies.find({"genres": "Comedy"}).limit(100))
    index_time = time.time() - start

    print(f"Without index: {no_index_time:.4f}s")
    print(f"With index:    {index_time:.4f}s")
    print(f"Speedup: {no_index_time/index_time:.1f}x faster")

# Experiment 2: Recommendation time per mood
def experiment_mood_timing():
    print("\n=== Experiment 2: Mood Timing ===")
    moods = ["happy", "sad", "excited", "scared", "romantic"]
    for mood in moods:
        start = time.time()
        results = get_recommendations(mood)
        elapsed = time.time() - start
        print(f"Mood '{mood}': {len(results)} results in {elapsed:.3f}s")

# Experiment 3: Scale test
def experiment_scale():
    print("\n=== Experiment 3: Scale Test ===")
    for limit in [10, 50, 100, 500]:
        start = time.time()
        list(db.movies.find({"genres": "Drama"}).limit(limit))
        elapsed = time.time() - start
        print(f"Fetching {limit} movies: {elapsed:.4f}s")

if __name__ == "__main__":
    experiment_index_performance()
    experiment_mood_timing()
    experiment_scale()