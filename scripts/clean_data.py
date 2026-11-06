import pandas as pd

data = pd.read_json("data/movie_raw_data.json")
cleaned_data = data.copy()

# removing NAs in title and release date
cleaned_data = cleaned_data.dropna(subset=["title", "release_date"])

# dropping values that aren't reliable
cleaned_data = cleaned_data[cleaned_data["runtime_minutes"] > 40]  # 40 for feature film definition as per oscars
cleaned_data = cleaned_data[cleaned_data["vote_count"] >= 100] # so we don't have skewed popularity or vote_avg scores
cleaned_data = cleaned_data[cleaned_data["budget"] != 0]
cleaned_data = cleaned_data[cleaned_data["revenue"] != 0]

# adding a release year column
cleaned_data["release_year"] = data["release_date"].str.split("-").str[0]

# adding profit column
cleaned_data["profit"] = data["revenue"] - data["budget"]

cleaned_data.to_json("data/movies_clean.json", orient="records", indent=2)
# cleaned_data.to_csv("data/movies_clean.csv", index=False)
print("Data cleaned and saved.")


