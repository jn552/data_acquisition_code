import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import time

# authenticating token
load_dotenv()
token = os.environ["TMDB_TOKEN"]

# storing movies in dictionary identified by movie id
results = {}

# grabbing movies by year
for year in range(2017, 2027):
    start_date = f"{year}-01-01"
    end_date = "2026-11-04" if year == 2026 else f"{year}-12-31"

    for page in range(1, 3):

        # sending request for movie in specified year on pages 1 to 3
        response = requests.get(
            "https://api.themoviedb.org/3/discover/movie",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "primary_release_date.gte": start_date,
                "primary_release_date.lte": end_date,
                "page": page,
                "sort_by": "popularity.desc"
            },
        )
        response.raise_for_status()

        # extracting movie data
        data = response.json()
        movies = data["results"]

        for movie in movies:
            results[movie["id"]] = movie

        # rate limiting to 20 requests per second-- documentation says about 40 req/s
        time.sleep(0.05)

results = list(results.values())
print(f"Done collecting movies. {len(results)} movies collected")

# list to store each movie observation
movie_records = []

print("Starting to grab info for each movie")
# grab more info for each movie that I grabbed in the for loop above
for i, movie in enumerate(results):
    movie_id = movie["id"]

    # requesting data on a specific movie by id
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"append_to_response": "credits"},
    )

    response.raise_for_status()
    data = response.json()

    # rate limiting to 20 requests per second
    time.sleep(0.05)

    # getting movie director
    movie_crew = data.get("credits", {}).get("crew", [])
    directors = [person["name"] for person in movie_crew if person["job"] == "Director"]
    
    # getting release date
    release_date = data.get("release_date")

    # getting the collection a movie belongs to as defined by tmdb
    collection = data.get("belongs_to_collection")
    
    # compiling all gathered data for a single movie
    movie_record = {
        "id": data["id"],
        "title": data.get("title"),
        "vote_avg": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "directors":  directors,
        "release_date": release_date,
        "runtime_minutes": data.get("runtime"),
        "genres": [genre["name"] for genre in data.get("genres", [])],
        "franchise": collection.get("name") if collection else None,
        "franchise_id": collection.get("id") if collection else None,
        "popularity": data.get("popularity"),
        "budget": data.get("budget"),
        "revenue": data.get("revenue")
    }
    movie_records.append(movie_record)

    if i % 25 == 0:
        print(f"info for {i} movies collected")

print("Done collecting info for each movie")

# writing gathered data to json file
Path("data").mkdir(exist_ok=True)

with open("data/movie_raw_data.json", "w") as file:
    json.dump(movie_records, file)

print("Data saved to JSON")
