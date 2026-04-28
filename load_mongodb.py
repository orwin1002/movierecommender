from pymongo import MongoClient
import pandas as pd
from mood_map import MOOD_MAP

client = MongoClient("mongodb+srv://admin:12345@movierecommender.gu56d6o.mongodb.net/?appName=movierecommender")
db = client["movierecommender"]

# Load movies
movies_df = pd.read_csv('movies.csv')
movies_df['genres'] = movies_df['genres'].apply(lambda x: x.split('|'))

# Insert movies
movies_collection = db["movies"]
movies_collection.drop()

movie_docs = []
for _, row in movies_df.iterrows():
    doc = {
        "movieId": int(row['movieId']),
        "title": row['title'],
        "genres": row['genres'],
        "tags": [],
        "year": row['title'][-5:-1] if '(' in row['title'] else "Unknown"
    }
    movie_docs.append(doc)

movies_collection.insert_many(movie_docs)
print(f"✅ Inserted {len(movie_docs)} movies into MongoDB")

# Load moods
moods_collection = db["moods"]
moods_collection.drop()

mood_docs = []
for mood, mapping in MOOD_MAP.items():
    doc = {
        "mood": mood,
        "mapped_genres": mapping["genres"],
        "mapped_tags": mapping["tags"]
    }
    mood_docs.append(doc)

moods_collection.insert_many(mood_docs)
print(f"✅ Inserted {len(mood_docs)} moods into MongoDB")

# Create indexes
movies_collection.create_index([("genres", 1)])
movies_collection.create_index([("tags", 1)])
movies_collection.create_index([("movieId", 1)], unique=True)
print("✅ Indexes created on MongoDB")

db.users.create_index([("username", 1)], unique=True)
print("✅ Index created on users collection")