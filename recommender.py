import os
from datetime import datetime
from neo4j import GraphDatabase
from pymongo import MongoClient

MONGO_URI  = os.environ.get("MONGO_URI", "mongodb+srv://admin:12345@movierecommender.gu56d6o.mongodb.net/?appName=movierecommender")
NEO4J_URI  = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "12345678")

mongo_client = MongoClient(MONGO_URI)
db           = mongo_client["movierecommender"]
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def ensure_user(username: str):
    # Save to Neo4j (for graph relationships)
    with neo4j_driver.session() as session:
        session.run("MERGE (:User {name: $name})", {"name": username})
    
    # Save to MongoDB (for user profile storage)
    from datetime import datetime
    db.users.update_one(
        {"username": username},
        {"$setOnInsert": {
            "username": username,
            "created_at": datetime.utcnow()
        },
        "$set": {
            "last_seen": datetime.utcnow()
        }},
        upsert=True
    )

def mark_watched(username: str, movie_id: int):
    # Save to Neo4j (for graph traversal and exclusion)
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (u:User {name: $username}), (m:Movie {movieId: $movieId})
            MERGE (u)-[:WATCHED]->(m)
            RETURN m.title AS title
        """, {"username": username, "movieId": movie_id})
        record = result.single()
        title = record["title"] if record else None

    # Also save to MongoDB (for profile viewing in Atlas)
    from datetime import datetime
    movie_doc = db.movies.find_one(
        {"movieId": movie_id},
        {"_id": 0, "title": 1, "genres": 1, "avg_rating": 1}
    )
    db.users.update_one(
        {"username": username},
        {"$addToSet": {
            "watched_movies": {
                "movieId": movie_id,
                "title": movie_doc["title"] if movie_doc else title,
                "genres": movie_doc.get("genres", []) if movie_doc else [],
                "avg_rating": movie_doc.get("avg_rating", "N/A") if movie_doc else "N/A",
                "watched_at": datetime.utcnow()
            }
        }}
    )
    return title

def get_watched_ids(username: str):
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (u:User {name: $username})-[:WATCHED]->(m:Movie)
            RETURN m.movieId AS movieId
        """, {"username": username})
        return [r["movieId"] for r in result]

def get_recommendations(moods: list, top_n: int = 10, min_rating: float = 0.0, username: str = None):
    """
    moods      : list of mood strings e.g. ["happy"] or ["happy", "excited"]
    top_n      : number of results
    min_rating : minimum avg_rating filter (0.0 = no filter)
    username   : if provided, exclude already-watched movies
    """

    # Build Cypher dynamically for 1 or 2 moods
    if len(moods) == 1:
        cypher = """
        MATCH (m:Mood {name: $mood1})-[:MAPS_TO]->(g:Genre)<-[:BELONGS_TO]-(mov:Movie)
        WITH mov, COUNT(g) AS genreScore
        OPTIONAL MATCH (mov)-[:HAS_TAG]->(t:Tag)<-[:ASSOCIATED_WITH]-(m:Mood {name: $mood1})
        WITH mov, genreScore, COUNT(t) AS tagScore
        WITH mov, (genreScore * 2 + tagScore) AS totalScore
        ORDER BY totalScore DESC
        LIMIT $top_n
        RETURN mov.movieId AS movieId, totalScore
        """
        params = {"mood1": moods[0], "top_n": top_n * 5}
    else:
        cypher = """
        MATCH (m1:Mood {name: $mood1})-[:MAPS_TO]->(g:Genre)<-[:BELONGS_TO]-(mov:Movie)
        WITH mov, COUNT(g) AS score1
        MATCH (m2:Mood {name: $mood2})-[:MAPS_TO]->(g2:Genre)<-[:BELONGS_TO]-(mov)
        WITH mov, score1, COUNT(g2) AS score2
        WITH mov, (score1 + score2) AS genreScore
        OPTIONAL MATCH (mov)-[:HAS_TAG]->(t:Tag)<-[:ASSOCIATED_WITH]-(mx:Mood)
        WHERE mx.name IN [$mood1, $mood2]
        WITH mov, genreScore, COUNT(t) AS tagScore
        WITH mov, (genreScore * 2 + tagScore) AS totalScore
        ORDER BY totalScore DESC
        LIMIT $top_n
        RETURN mov.movieId AS movieId, totalScore
        """
        params = {"mood1": moods[0], "mood2": moods[1], "top_n": top_n * 5}

    with neo4j_driver.session() as session:
        result = session.run(cypher, params)
        scored = [(record["movieId"], record["totalScore"]) for record in result]

    if not scored:
        return []

    # Get watched movie IDs to exclude
    watched_ids = []
    if username:
        watched_ids = get_watched_ids(username)

    movie_ids = [s[0] for s in scored if s[0] not in watched_ids]
    scores = {s[0]: s[1] for s in scored}

    # MongoDB query with optional rating filter
    mongo_filter = {"movieId": {"$in": movie_ids}}
    if min_rating > 0:
        mongo_filter["avg_rating"] = {"$gte": min_rating}

    movies = db.movies.find(
        mongo_filter,
        {"_id": 0, "movieId": 1, "title": 1, "genres": 1, "year": 1,
         "avg_rating": 1, "rating_count": 1}
    )

    results = []
    for movie in movies:
        movie["score"] = scores.get(movie["movieId"], 0)
        movie.setdefault("avg_rating", "N/A")
        movie.setdefault("rating_count", 0)
        results.append(movie)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    print("\n🎬 Test: Single mood (happy)")
    recs = get_recommendations(["happy"])
    for i, m in enumerate(recs, 1):
        print(f"{i}. {m['title']} | Score: {m['score']} | Rating: {m.get('avg_rating','N/A')}")

    print("\n🎬 Test: Two moods (happy + excited)")
    recs2 = get_recommendations(["happy", "excited"])
    for i, m in enumerate(recs2, 1):
        print(f"{i}. {m['title']} | Score: {m['score']} | Rating: {m.get('avg_rating','N/A')}")

    print("\n🎬 Test: happy, min rating 4.0")
    recs3 = get_recommendations(["happy"], min_rating=4.0)
    for i, m in enumerate(recs3, 1):
        print(f"{i}. {m['title']} | Score: {m['score']} | Rating: {m.get('avg_rating','N/A')}")
