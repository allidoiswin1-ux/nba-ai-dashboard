import pandas as pd
import requests
import datetime

DATA_FILE = "props_data.csv"

def get_games_today():
    today = datetime.date.today().strftime("%Y%m%d")

    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={today}"

    r = requests.get(url).json()

    games = []

    if "events" in r:
        for event in r["events"]:
            comp = event["competitions"][0]

            home = comp["competitors"][0]["team"]["abbreviation"]
            away = comp["competitors"][1]["team"]["abbreviation"]

            games.append((home, away, f"{away} @ {home}"))

    return games


def get_roster(team):

    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team}/roster"

    try:
        r = requests.get(url).json()
        players = []

        for athlete in r["athletes"]:
            players.append(athlete["fullName"])

        return players[:5]

    except:
        return []


def generate_data():

    games = get_games_today()

    rows = []
    rank = 1

    for home, away, matchup in games:

        home_players = get_roster(home)
        away_players = get_roster(away)

        for player in home_players + away_players:

            rows.append({
                "Rank": rank,
                "Player": player,
                "Matchup": matchup,
                "Book": "DraftKings",
                "Line": 22.5,
                "Projection": 25.1,
                "Edge": 2.6
            })

            rows.append({
                "Rank": rank,
                "Player": player,
                "Matchup": matchup,
                "Book": "FanDuel",
                "Line": 21.5,
                "Projection": 25.1,
                "Edge": 3.6
            })

            rank += 1

    df = pd.DataFrame(rows)

    df.to_csv(DATA_FILE, index=False)

    print("props_data.csv updated with real players")


if name == "main":
    generate_data()
