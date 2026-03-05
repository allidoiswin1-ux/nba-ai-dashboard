import streamlit as st
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog

st.title("🔥 Best NBA Props Scanner")

st.write("Scanning all active NBA players...")

# Get all active players automatically
all_players = players.get_active_players()

results = []

for p in all_players:

    name = p["full_name"]
    player_id = p["id"]

    try:

        gamelog = playergamelog.PlayerGameLog(player_id=player_id)
        df = gamelog.get_data_frames()[0]

        if len(df) < 5:
            continue

        last10 = df.head(10)["PTS"].mean()
        season = df["PTS"].mean()

        projection = (last10 * 0.65) + (season * 0.35)

        edge = projection - season

        results.append({
            "Player": name,
            "Last10 Avg": round(last10,2),
            "Season Avg": round(season,2),
            "AI Projection": round(projection,2),
            "Edge": round(edge,2)
        })

    except:
        continue


df = pd.DataFrame(results)

df = df.sort_values("Edge", ascending=False)

st.subheader("🏆 Top 30 Best Player Projections")

st.dataframe(df.head(30), use_container_width=True)

st.subheader("📊 All Players")

st.dataframe(df, use_container_width=True)
