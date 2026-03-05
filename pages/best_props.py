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

st.set_page_config(page_title="NBA Props Scanner", layout="wide")

st.title("🔥 Best NBA Props Scanner")

if st.button("Refresh Model"):
    st.cache_data.clear()

STAT = st.selectbox("Stat Type", ["PTS","REB","AST"])

today = datetime.today().strftime("%m/%d/%Y")


# ------------------------
# CACHED FUNCTIONS
# ------------------------

@st.cache_data(ttl=3600)
def get_today_games(date):
    board = scoreboardv2.ScoreboardV2(game_date=date)
    return board.get_data_frames()[0]


@st.cache_data(ttl=3600)
def get_team_stats():
    stats = leaguedashteamstats.LeagueDashTeamStats(season="2025-26")
    return stats.get_data_frames()[0]


@st.cache_data(ttl=3600)
def get_player_logs(player_id):
    gamelog = playergamelog.PlayerGameLog(player_id=player_id)
    return gamelog.get_data_frames()[0]


@st.cache_data(ttl=3600)
def get_active_players():
    return players.get_active_players()


# ------------------------
# GET TODAY'S GAMES
# ------------------------

games = get_today_games(today)

if len(games) == 0:
    st.warning("No NBA games today")
    st.stop()

team_ids = set(games["HOME_TEAM_ID"]).union(set(games["VISITOR_TEAM_ID"]))

st.write(f"Games today: {len(team_ids)//2}")


# ------------------------
# TEAM DATA
# ------------------------

team_stats = get_team_stats()

def_rank = team_stats.sort_values("PTS").reset_index(drop=True)
def_rank["DEF_RANK"] = def_rank.index + 1

defense_dict = dict(zip(def_rank["TEAM_ID"], def_rank["DEF_RANK"]))

if "PACE" in team_stats.columns:
    pace_dict = dict(zip(team_stats["TEAM_ID"], team_stats["PACE"]))
elif "PACE_PER_GAME" in team_stats.columns:
    pace_dict = dict(zip(team_stats["TEAM_ID"], team_stats["PACE_PER_GAME"]))
else:
    pace_dict = dict(zip(team_stats["TEAM_ID"], [100]*len(team_stats)))


# ------------------------
# GET PLAYERS FROM TEAMS PLAYING TODAY
# ------------------------

all_players = get_active_players()

players_today = []

for p in all_players:
    try:
        df = get_player_logs(p["id"])
        if len(df) == 0:
            continue

        team_id = df.iloc[0]["TEAM_ID"]

        if team_id in team_ids:
            players_today.append(p)

    except:
        continue


results = []

progress = st.progress(0)

# ------------------------
# PLAYER MODEL
# ------------------------

for i,p in enumerate(players_today):

    name = p["full_name"]
    player_id = p["id"]

    try:

        df = get_player_logs(player_id)

        if len(df) < 5:
            continue

        matchup = df.iloc[0]["MATCHUP"]

        minutes_last5 = df.head(5)["MIN"].mean()
        minutes_season = df["MIN"].mean()

        if minutes_season < 15:
            continue

        stat_per_min = df[STAT].sum() / df["MIN"].sum()

        projected_minutes = (
            minutes_last5 * 0.6 +
            minutes_season * 0.4
        )

        projection = stat_per_min * projected_minutes

        team_id = df.iloc[0]["TEAM_ID"]

        pace = pace_dict.get(team_id,100)

        projection = projection * (pace/100)

        season_avg = df[STAT].mean()

        line = round(season_avg,1)

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
            "Line": round(line,1),
            "Projection": round(projection,2),
            "Edge": round(edge,2),
            "Over Prob %": round(prob*100,1)
        })

    except:
        continue

    progress.progress((i+1)/len(players_today))


# ------------------------
# RESULTS
# ------------------------

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

st.subheader("🔥 Top NBA Props")

st.dataframe(df.head(25), use_container_width=True)

st.subheader("📊 Full Model")

st.dataframe(df, use_container_width=True)
