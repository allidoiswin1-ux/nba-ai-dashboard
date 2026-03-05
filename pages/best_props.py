import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, scoreboardv2

st.set_page_config(page_title="NBA Props Scanner", layout="wide")

st.title("🔥 Best NBA Props Scanner")

if st.button("Refresh Model"):
    st.cache_data.clear()

STAT = st.selectbox("Stat Type", ["PTS","REB","AST"])

today = datetime.today().strftime("%m/%d/%Y")


@st.cache_data(ttl=3600)
def get_today_games(date):
    try:
        board = scoreboardv2.ScoreboardV2(game_date=date)
        return board.get_data_frames()[0]
    except:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_player_logs(player_id):
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=player_id)
        return gamelog.get_data_frames()[0]
    except:
        return pd.DataFrame()


games = get_today_games(today)

if games.empty:
    st.warning("No NBA games today")
    st.stop()

team_ids = set(games["HOME_TEAM_ID"]).union(set(games["VISITOR_TEAM_ID"]))

st.write(f"Games today: {len(team_ids)//2}")


all_players = players.get_active_players()

# LIMIT PLAYERS (major speed fix)
players_to_scan = all_players[:25]

results = []

progress = st.progress(0)

for i,p in enumerate(players_to_scan):

    name = p["full_name"]
    player_id = p["id"]

    try:

        df = get_player_logs(player_id)

        if df.empty:
            continue

        team_id = df.iloc[0]["TEAM_ID"]

        if team_id not in team_ids:
            continue

        if len(df) < 5:
            continue

        last5 = df.head(5)[STAT].mean()
        season = df[STAT].mean()

        projection = (last5 * 0.7) + (season * 0.3)

        line = round(season,1)

        std = df[STAT].std()

        if std == 0:
            prob = 0.5
        else:
            prob = 1 - (
                0.5 * (1 + np.math.erf((line-projection)/(std*np.sqrt(2))))
            )

        edge = projection - line

        results.append({
            "Player": name,
            "Matchup": df.iloc[0]["MATCHUP"],
            "Line": round(line,1),
            "Projection": round(projection,2),
            "Edge": round(edge,2),
            "Over Prob %": round(prob*100,1)
        })

    except:
        continue

    progress.progress((i+1)/len(players_to_scan))


df = pd.DataFrame(results)

if df.empty:
    st.warning("No props found")
    st.stop()

df = df.sort_values(
    ["Over Prob %","Edge"],
    ascending=False
)

df.insert(0,"Rank",range(1,len(df)+1))

st.subheader("🔥 Top Props")

st.dataframe(df, use_container_width=True)
