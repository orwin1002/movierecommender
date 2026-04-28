from neo4j import GraphDatabase
import pandas as pd
from mood_map import MOOD_MAP

driver = GraphDatabase.driver("bolt://127.0.0.1:7687",
                               auth=("neo4j", "12345678"))

def run(query, params={}):
    with driver.session() as session:
        session.run(query, params)

# Clear and set up indexes
print("Setting up indexes...")
run("MATCH (n) DETACH DELETE n")

run("CREATE INDEX mood_index IF NOT EXISTS FOR (m:Mood) ON (m.name)")
run("CREATE INDEX genre_index IF NOT EXISTS FOR (g:Genre) ON (g.name)")
run("CREATE INDEX movie_index IF NOT EXISTS FOR (mov:Movie) ON (mov.movieId)")

# Create Mood, Genre, Tag nodes
print("Creating Mood, Genre, Tag nodes...")
for mood, mapping in MOOD_MAP.items():
    run("MERGE (:Mood {name: $name})", {"name": mood})
    for genre in mapping["genres"]:
        run("MERGE (:Genre {name: $name})", {"name": genre})
        run("""
            MATCH (m:Mood {name: $mood}), (g:Genre {name: $genre})
            MERGE (m)-[:MAPS_TO]->(g)
        """, {"mood": mood, "genre": genre})
    for tag in mapping["tags"]:
        run("MERGE (:Tag {name: $name})", {"name": tag.lower()})
        run("""
            MATCH (m:Mood {name: $mood}), (t:Tag {name: $tag})
            MERGE (m)-[:ASSOCIATED_WITH]->(t)
        """, {"mood": mood, "tag": tag.lower()})

print("✅ Mood/Genre/Tag nodes created")

# Load Movies
print("Loading movies into Neo4j (this takes a minute)...")
movies_df = pd.read_csv('movies.csv')

for i, row in movies_df.iterrows():
    genres = row['genres'].split('|')
    run("""
        MERGE (mov:Movie {movieId: $movieId})
        SET mov.title = $title
    """, {"movieId": int(row['movieId']), "title": row['title']})

    for genre in genres:
        run("MERGE (:Genre {name: $name})", {"name": genre})
        run("""
            MATCH (mov:Movie {movieId: $movieId}), (g:Genre {name: $genre})
            MERGE (mov)-[:BELONGS_TO]->(g)
        """, {"movieId": int(row['movieId']), "genre": genre})

    if i % 100 == 0:
        print(f"  Loaded {i} movies...")

print("✅ Movies loaded into Neo4j")
driver.close()