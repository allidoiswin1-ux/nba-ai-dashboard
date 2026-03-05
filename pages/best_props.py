import streamlit as st
import pandas as pd
from datetime import datetime
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, scoreboardv2

st.title("🔥 Best NBA Props Today")

today = datetime.today().strftime("%m/%d/%Y")

scoreboard = scoreboardv2.ScoreboardV2(game_date=today)
games_df = scoreboard.get_data_frames()[0]

team_ids = set(games_df["HOME_TEAM_ID"]).union(set(games_df["VISITOR_TEAM_ID"]))

st.write(f"Games today: {len(team_ids)//2}")

active_players = players.get_active_players()

results = []

for p in active_players:

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

        last10 = df.head(10)["PTS"].mean()
        season = df["PTS"].mean()

        projection = (last10 * 0.65) + (season * 0.35)

        # simulate sportsbook line
        line = round(season,1)

        edge = projection - line

        if edge < 1:
            continue

        results.append({
            "Player": name,
            "Sportsbook Line": line,
            "AI Projection": round(projection,2),
            "Edge": round(edge,2),
            "Bet": "OVER"
        })

    except:
        continue


df = pd.DataFrame(results)

if len(df) > 0:

    df = df.sort_values("Edge", ascending=False)

    st.subheader("🔥 TOP 10 BEST BETS TODAY")

    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("All Props")

    st.dataframe(df, use_container_width=True)

else:

    st.warning("No good bets today.")
