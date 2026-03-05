import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2

st.set_page_config(page_title="NBA Prop Scanner", layout="wide")

st.title("🔥 NBA Prop Scanner")

STAT = st.selectbox("Stat Type", ["PTS", "REB", "AST"])

ODDS_API_KEY = "PASTE_YOUR_ODDS_API_KEY_HERE"

today = datetime.today().strftime("%m/%d/%Y")


# -----------------------------
# CACHE DATA (1 HOUR REFRESH)
# -----------------------------

@st.cache_data(ttl=3600)
def get_games():
    board = scoreboardv2.ScoreboardV2(game_date=today)
    return board.get_data_frames()[0]


@st.cache_data(ttl=3600)
def get_boxscore(game_id):
    box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    return box.get_data_frames()[0]


@st.cache_data(ttl=3600)
def get_odds():

    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "player_points,player_rebounds,player_assists",
        "bookmakers": "draftkings,fanduel"
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        return []

    return r.json()


# -----------------------------
# GET TONIGHT'S GAMES
# -----------------------------

games = get_games()

if games.empty:
    st.warning("No NBA games tonight")
    st.stop()

st.write(f"Games tonight: {len(games)}")


# -----------------------------
# GET PLAYERS IN TONIGHT'S GAMES
# -----------------------------

players = []

for _, game in games.iterrows():

    game_id = game["GAME_ID"]

    try:

        box = get_boxscore(game_id)

        home = game["HOME_TEAM_ABBREVIATION"]
        away = game["VISITOR_TEAM_ABBREVIATION"]

        matchup = f"{away} @ {home}"

        for _, row in box.iterrows():

            players.append({
                "Player": row["PLAYER_NAME"],
                "Team": row["TEAM_ABBREVIATION"],
                "Matchup": matchup,
                "PTS": row["PTS"],
                "REB": row["REB"],
                "AST": row["AST"]
            })

    except:
        continue


players_df = pd.DataFrame(players)


# -----------------------------
# GET SPORTSBOOK LINES
# -----------------------------

odds_data = get_odds()

lines = []

for game in odds_data:

    for book in game.get("bookmakers", []):

        book_name = book["title"]

        for market in book.get("markets", []):

            stat_map = {
                "player_points": "PTS",
                "player_rebounds": "REB",
                "player_assists": "AST"
            }

            stat_type = stat_map.get(market["key"])

            for outcome in market.get("outcomes", []):

                lines.append({
                    "Player": outcome.get("description"),
                    "Line": outcome.get("point"),
                    "Book": book_name,
                    "Stat": stat_type
                })


lines_df = pd.DataFrame(lines)


# -----------------------------
# MERGE MODEL + SPORTSBOOK
# -----------------------------

df = players_df.merge(lines_df, how="left", on="Player")

df = df[df["Stat"] == STAT]


if df.empty:
    st.warning("No prop data available yet")
    st.stop()


# -----------------------------
# PROJECTION MODEL
# -----------------------------

df["Projection"] = df[STAT] * 1.15

df["Edge"] = df["Projection"] - df["Line"]

df["Probability"] = 50 + (df["Edge"] * 6)

df["Probability"] = df["Probability"].clip(50, 80)


# -----------------------------
# RANK BEST PROPS
# -----------------------------

df = df.sort_values("Edge", ascending=False)

df.insert(0, "Rank", range(1, len(df) + 1))


# -----------------------------
# DISPLAY RESULTS
# -----------------------------

st.subheader("🔥 Best Props Tonight")

st.dataframe(
    df[
        [
            "Rank",
            "Player",
            "Matchup",
            "Book",
            "Line",
            "Projection",
            "Edge",
            "Probability"
        ]
    ],
    use_container_width=True
)
