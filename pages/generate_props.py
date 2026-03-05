1"}
import pandas as pd
import requests
import datetime

DATA_FILE = "props_data.csv"

def get_games_today():
    today = datetime.date.today().strftime("%Y%m%d")

    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={today}"

    response = requests.get(url)
    data = response.json()

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

    for i, game in enumerate(games):

        rows.append({
            "Rank": i + 1,
            "Player": f"Player {i+1}",
            "Matchup": game,
            "Book": "DraftKings",
            "Line": 22.5,
            "Projection": 25.1,
            "Edge": "+2.6"
        })

        rows.append({
            "Rank": i + 1,
            "Player": f"Player {i+1}",
            "Matchup": game,
            "Book": "FanDuel",
            "Line": 21.5,
            "Projection": 25.1,
            "Edge": "+3.6"
        })

    df = pd.DataFrame(rows)

    df.to_csv(DATA_FILE, index=False)

    print("Props data generated")


if name == "main":
    generate_dat
    games = get_games_today()

rows = []

for i, game in enumerate(games):

    rows.append({
        "Rank": i + 1,
        "Player": f"Player {i+1}",
        "Matchup": game,
        "Book": "DraftKings",
        "Line": 22.5,
        "Projection": 25.1,
        "Edge": "+2.6"
    })

    rows.append({
        "Rank": i + 1,
        "Player": f"Player {i+1}",
        "Matchup": game,
        "Book": "FanDuel",
        "Line": 21.5,
        "Projection": 25.1,
        "Edge": "+3.6"
    })

df = pd.DataFrame(rows)

df.to_csv(DATA_FILE, index=False)

print("Props data generated")
