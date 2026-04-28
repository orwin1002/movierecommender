from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))

def create_user(username: str):
    with driver.session() as session:
        session.run("MERGE (:User {name: $name})", {"name": username})
    print(f"✅ User '{username}' created")

def mark_watched(username: str, movie_id: int):
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User {name: $username}), (m:Movie {movieId: $movieId})
            MERGE (u)-[:WATCHED]->(m)
            RETURN m.title AS title
        """, {"username": username, "movieId": movie_id})
        record = result.single()
        if record:
            print(f"✅ Marked '{record['title']}' as watched for {username}")
        else:
            print(f"⚠️ Movie ID {movie_id} not found in Neo4j")

def get_watched(username: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User {name: $username})-[:WATCHED]->(m:Movie)
            RETURN m.movieId AS movieId, m.title AS title
        """, {"username": username})
        return [{"movieId": r["movieId"], "title": r["title"]} for r in result]

if __name__ == "__main__":
    create_user("testuser")
    mark_watched("testuser", 1)   # Toy Story
    mark_watched("testuser", 2)   # Jumanji
    watched = get_watched("testuser")
    print(f"\nWatched by testuser:")
    for m in watched:
        print(f"  - {m['title']}")
