import pandas as pd
import requests
import datetime
import os

DATA_FILE = "props_data.csv"

def get_games_today():
    today = datetime.date.today().strftime("%Y-%m-%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={today}"
    
    r = requests.get(url).json()
    games = []

    for event in r["events"]:
        home = event["competitions"][0]["competitors"][0]["team"]["abbreviation"]
        away = event["competitions"][0]["competitors"][1]["team"]["abbreviation"]
        games.append(f"{away} @ {home}")

    return games


def generate_data():

    games = get_games_today()

    rows = []

    for i, g in enumerate(games):

        rows.append({
            "Rank": i+1,
            "Player": f"Player {i+1}",
            "Matchup": g,
            "Book": "DraftKings",
            "Line": 22.5,
            "Projection": 25.1,
            "Edge": "+2.6"
        })

        rows.append({
            "Rank": i+1,
            "Player": f"Player {i+1}",
            "Matchup": g,
            "Book": "FanDuel",
            "Line": 21.5,
            "Projection": 25.1,
            "Edge": "+3.6"
        })

    df = pd.DataFrame(rows)

    df.to_csv(DATA_FILE, index=False)

    print("Data file created!")


if __name__ == "__main__":
    generate_data()
