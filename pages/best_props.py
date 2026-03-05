import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from nba_api.stats.static import players
from nba_api.stats.endpoints import (
    playergamelog,
    scoreboardv2,
    leaguedashteamstats
)

st.title("🔥 NBA AI Prop Model (2025-26)")

if st.button("Refresh Model"):
    st.cache_data.clear()

STAT = st.selectbox("Stat Type", ["PTS","REB","AST"])

today = datetime.today().strftime("%m/%d/%Y")


# ----------------------------
# CACHED FUNCTIONS
# ----------------------------

@st.cache_data(ttl=3600)
def get_today_games(date):
    board = scoreboardv2.ScoreboardV2(game_date=date)
    return board.get_data_frames()[0]


@st.cache_data(ttl=3600)
def get_team_stats():
    stats = leaguedashteamstats.LeagueDashTeamStats(
        season="2025-26"
    )
    return stats.get_data_frames()[0]


@st.cache_data(ttl=3600)
def get_player_logs(player_id):
    gamelog = playergamelog.PlayerGameLog(player_id=player_id)
    return gamelog.get_data_frames()[0]


@st.cache_data(ttl=3600)
def get_active_players():
    return players.get_active_players()


# ----------------------------
# LOAD DATA
# ----------------------------

games = get_today_games(today)

if len(games) == 0:
    st.warning("No NBA games today")
    st.stop()

team_ids = set(games["HOME_TEAM_ID"]).union(set(games["VISITOR_TEAM_ID"]))

st.write(f"Games today: {len(team_ids)//2}")

team_stats = get_team_stats()

def_rank = team_stats.sort_values("PTS").reset_index(drop=True)
def_rank["DEF_RANK"] = def_rank.index + 1

defense_dict = dict(zip(def_rank["TEAM_ID"], def_rank["DEF_RANK"]))

pace_dict = dict(zip(team_stats["TEAM_ID"], team_stats["PACE"]))

active_players = get_active_players()

results = []

progress = st.progress(0)


# ----------------------------
# PLAYER MODEL
# ----------------------------

for i,p in enumerate(active_players):

    name = p["full_name"]
    player_id = p["id"]

    try:

        df = get_player_logs(player_id)

        if len(df) < 5:
            continue

        team_id = df.iloc[0]["TEAM_ID"]

        if team_id not in team_ids:
            continue

        matchup = df.iloc[0]["MATCHUP"]

        last5 = df.head(5)[STAT].mean()
        last10 = df.head(10)[STAT].mean()
        season = df[STAT].mean()

        projection = (
            last5 * 0.5 +
            last10 * 0.3 +
            season * 0.2
        )

        pace = pace_dict.get(team_id,100)

        projection = projection * (pace/100)

        line = round(season,1)

        std = df[STAT].std()

        if std == 0:
            prob = 0.5
        else:
            prob = 1 - (
                0.5 * (1 + np.math.erf((line-projection)/(std*np.sqrt(2))))
            )

        edge = projection - line

        defense_rank = defense_dict.get(team_id,15)

        results.append({
            "Player": name,
            "Matchup": matchup,
            "Opp DEF Rank": defense_rank,
            "Line": line,
            "Projection": round(projection,2),
            "Edge": round(edge,2),
            "Over Prob %": round(prob*100,1)
        })

    except:
        continue

    progress.progress((i+1)/len(active_players))


# ----------------------------
# RESULTS
# ----------------------------

df = pd.DataFrame(results)

if len(df) == 0:
    st.warning("No props found")
    st.stop()

df = df[df["Edge"] > 1]

df = df.sort_values(
    ["Over Prob %","Edge"],
    ascending=False
)

df.insert(0,"Rank",range(1,len(df)+1))

st.subheader("🔥 TOP NBA BETS TODAY")

st.dataframe(df.head(25), use_container_width=True)

st.subheader("📊 Full Model Output")

st.dataframe(df, use_container_width=True)
