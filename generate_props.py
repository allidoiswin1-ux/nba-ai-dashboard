import pandas as pd
import requests
import datetime

DATA_FILE = "props_data.csv"

def get_games_today():
    today = datetime.date.today().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={today}"
    
    try:
        response = requests.get(url)
        data = response.json()
    except:
        return []

    games = []

    if "events" in data:
        for event in data["events"]:
            comp = event["competitions"][0]

            home = comp["competitors"][0]["team"]["abbreviation"]
            away = comp["competitors"][1]["team"]["abbreviation"]

            games.append(f"{away} @ {home}")

    return games


def generate_data():

    games = get_games_today()

    rows = []
    rank = 1

    for game in games:

        rows.append({
            "Rank": rank,
            "Player": "Example Player",
            "Matchup": game,
            "Book": "DraftKings",
            "Line": 22.5,
            "Projection": 25.1,
            "Edge": "+2.6"
        })

        rows.append({
            "Rank": rank,
            "Player": "Example Player",
            "Matchup": game,
            "Book": "FanDuel",
            "Line": 21.5,
            "Projection": 25.1,
            "Edge": "+3.6"
        })

        rank += 1

    if len(rows) == 0:
        rows.append({
            "Rank": 1,
            "Player": "No Games Today",
            "Matchup": "N/A",
            "Book": "N/A",
            "Line": 0,
            "Projection": 0,
            "Edge": "0"
        })

    df = pd.DataFrame(rows)

    df.to_csv(DATA_FILE, index=False)

    print("props_data.csv generated")
