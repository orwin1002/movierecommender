import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:12345@movierecommender.gu56d6o.mongodb.net/?appName=movierecommender")
db = client["movierecommender"]

print("Loading ratings.csv...")
ratings_df = pd.read_csv('ratings.csv')

print("Calculating average ratings per movie...")
avg_ratings = ratings_df.groupby('movieId')['rating'].agg(['mean', 'count']).reset_index()
avg_ratings.columns = ['movieId', 'avg_rating', 'rating_count']
avg_ratings['avg_rating'] = avg_ratings['avg_rating'].round(2)

print(f"Updating {len(avg_ratings)} movies in MongoDB with ratings...")
updated = 0
for _, row in avg_ratings.iterrows():
    result = db.movies.update_one(
        {"movieId": int(row['movieId'])},
        {"$set": {
            "avg_rating": float(row['avg_rating']),
            "rating_count": int(row['rating_count'])
        }}
    )
    if result.modified_count:
        updated += 1

    if updated % 500 == 0 and updated > 0:
        print(f"  Updated {updated} movies...")

# Add index for fast rating queries
db.movies.create_index([("avg_rating", -1)])
print(f"✅ Updated {updated} movies with average ratings")
print("✅ Index created on avg_rating")

