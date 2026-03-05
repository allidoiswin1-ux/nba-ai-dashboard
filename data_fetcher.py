import pandas as pd
import requests
from datetime import datetime
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2

ODDS_API_KEY = "PASTE_KEY"

today = datetime.today().strftime("%m/%d/%Y")

def run_data_pull():

    games = scoreboardv2.ScoreboardV2(game_date=today).get_data_frames()[0]

    players = []

    for _, game in games.iterrows():

        game_id = game["GAME_ID"]

        box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]

        home = game["HOME_TEAM_ABBREVIATION"]
        away = game["VISITOR_TEAM_ABBREVIATION"]

        matchup = f"{away} @ {home}"

        for _, row in box.iterrows():

            players.append({
                "Player": row["PLAYER_NAME"],
                "Matchup": matchup,
                "PTS": row["PTS"],
                "REB": row["REB"],
                "AST": row["AST"]
            })

    players_df = pd.DataFrame(players)

    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "player_points,player_rebounds,player_assists",
        "bookmakers": "draftkings,fanduel"
    }

    odds = requests.get(url, params=params).json()

    lines = []

    for game in odds:

        for book in game.get("bookmakers", []):

            for market in book.get("markets", []):

                for outcome in market.get("outcomes", []):

                    lines.append({
                        "Player": outcome.get("description"),
                        "Line": outcome.get("point"),
                        "Book": book["title"]
                    })

    lines_df = pd.DataFrame(lines)

    df = players_df.merge(lines_df, how="left", on="Player")

    df.to_csv("props_data.csv", index=False)

    return df
