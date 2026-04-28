import pandas as pd

movies = pd.read_csv('movies.dat', sep='::', engine='python',
                     names=['movieId','title','genres'], encoding='latin-1')

ratings = pd.read_csv('ratings.dat', sep='::', engine='python',
                      names=['userId','movieId','rating','timestamp'], encoding='latin-1')

movies.to_csv('movies.csv', index=False)
ratings.to_csv('ratings.csv', index=False)

print(f"✅ Movies: {len(movies)}")
print(f"✅ Ratings: {len(ratings)}")
