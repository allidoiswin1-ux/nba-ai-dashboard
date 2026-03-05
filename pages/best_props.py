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

STAT = st.selectbox("Stat Type", ["PTS","REB","AST"])

today = datetime.today().strftime("%m/%d/%Y")

# cache expensive API calls
@st.cache_data(ttl=3600)
def get_today_games(date):
    board = scoreboardv2.ScoreboardV2(game_date=date)
    return board.get_data_frames()[0]

@st.cache_data(ttl=3600)
def get_team_stats():
    return leaguedashteamstats.LeagueDashTeamStats(
        season="2025-26"
    ).get_data_frames()[0]

@st.cache_data(ttl=3600)
def get_active_players():
    return players.get_active_players()


games = get_today_games(today)

if len(games) == 0:
    st.warning("No NBA games today")
    st.stop()

team_ids = set(games["HOME_TEAM_ID"]).union(set(games["VISITOR_TEAM_ID"]))

st.write(f"Games today: {len(team_ids)//2}")

team_stats = get_team_stats()

# defensive rank
def_rank = team_stats.sort_values("PTS").reset_index(drop=True)
def_rank["DEF_RANK"] = def_rank.index + 1
defense_dict = dict(zip(def_rank["TEAM_ID"], def_rank["DEF_RANK"]))

# pace factor
pace_dict = dict(zip(team_stats["TEAM_ID"], team_stats["PACE"]))

active_players = get_active_players()

results = []

progress = st.progress(0)

for i,p in enumerate(active_players):

    name = p["full_name"]
    player_id = p["id"]

    try:

        gamelog = playergamelog.PlayerGameLog(player_id=player_id)
        df = gamelog.get_data_frames()[0]

        if len(df) < 5:
            continue

        team_id = df.iloc[0]["TEAM_ID"]

        if team_id not in team_ids:
            continue

        matchup = df.iloc[0]["MATCHUP"]

        # recent form weighting
        last5 = df.head(5)[STAT].mean()
        last10 = df.head(10)[STAT].mean()
        season = df[STAT].mean()

        projection = (
            last5 * 0.5 +
            last10 * 0.3 +
            season * 0.2
        )

        # pace adjustment
        pace = pace_dict.get(team_id,100)
        projection = projection * (pace / 100)

        sportsbook_line = round(season,1)

        std = df[STAT].std()

        if std == 0:
            prob_over = 0.5
        else:
            prob_over = 1 - (
                0.5 * (1 + np.math.erf((sportsbook_line-projection)/(std*np.sqrt(2))))
            )

        edge = projection - sportsbook_line

        defense_rank = defense_dict.get(team_id,15)

        results.append({
            "Player": name,
            "Matchup": matchup,
            "Opp DEF Rank": defense_rank,
            "Line": sportsbook_line,
            "Projection": round(projection,2),
            "Edge": round(edge,2),
            "Over Prob %": round(prob_over*100,1)
        })

    except:
        continue

    progress.progress((i+1)/len(active_players))


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
