import requests
import pandas as pd
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nba.com/"
}


def get_today_games():

    today = datetime.today().strftime("%m/%d/%Y")

    url = f"https://stats.nba.com/stats/scoreboardv2?GameDate={today}&LeagueID=00&DayOffset=0"

    r = requests.get(url, headers=headers)

    data = r.json()

    games = data["resultSets"][0]["rowSet"]
    columns = data["resultSets"][0]["headers"]

    df = pd.DataFrame(games, columns=columns)

    return df


def get_team_data():

    url = "https://stats.nba.com/stats/leaguedashteamstats?Season=2025-26&MeasureType=Base"

    r = requests.get(url, headers=headers)

    data = r.json()

    teams = data["resultSets"][0]["rowSet"]
    columns = data["resultSets"][0]["headers"]

    df = pd.DataFrame(teams, columns=columns)

    # Safe column detection
    pace_col = [c for c in df.columns if "PACE" in c][0]
    off_col = [c for c in df.columns if "OFF_RATING" in c][0]
    def_col = [c for c in df.columns if "DEF_RATING" in c][0]

    return df[[
        "TEAM_ID",
        pace_col,
        off_col,
        def_col
    ]].rename(columns={
        pace_col: "PACE",
        off_col: "OFF_RATING",
        def_col: "DEF_RATING"
    })


def get_player_stats():

    url = "https://stats.nba.com/stats/leaguedashplayerstats?Season=2025-26&PerMode=PerGame"

    r = requests.get(url, headers=headers)

    data = r.json()

    players = data["resultSets"][0]["rowSet"]
    columns = data["resultSets"][0]["headers"]

    df = pd.DataFrame(players, columns=columns)

    return df[[
        "PLAYER_NAME",
        "TEAM_ID",
        "PTS",
        "REB",
        "AST",
        "MIN"
    ]]
