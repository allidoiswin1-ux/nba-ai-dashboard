import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog

st.set_page_config(page_title="NBA Prop AI", layout="wide")

st.title("🏀 NBA Prop AI Dashboard")

player_name = st.text_input("Player Name")

stat = st.selectbox(
    "Stat Type",
    ["PTS","REB","AST"]
)

line = st.number_input("Sportsbook Line", value=0.0)

def get_player_id(name):
    p = players.find_players_by_full_name(name)
    if p:
        return p[0]["id"]
    return None


if player_name:

    player_id = get_player_id(player_name)

    if player_id:

        gamelog = playergamelog.PlayerGameLog(player_id=player_id)
        df = gamelog.get_data_frames()[0]

        last10 = df.head(10)[stat].mean()
        season = df[stat].mean()

        projection = (last10*0.65) + (season*0.35)

        std = df[stat].std()

     std = df[stat].std()

if std == 0:
    prob_over = 0.5
else:
    prob_over = 1 - (
        0.5 * (1 + math.erf((line - projection) / (std * math.sqrt(2))))
    )

edge = projection - line

        col1,col2,col3 = st.columns(3)

        col1.metric("Last 10 Avg",round(last10,2))
        col2.metric("Season Avg",round(season,2))
        col3.metric("AI Projection",round(projection,2))

        st.write("Probability Over:",round(prob_over*100,2),"%")
        st.write("Edge:",round(edge,2))

        if edge > 3:
            st.success("🔥 Strong Over")

        elif edge > 1:
            st.warning("Slight Over")

        else:
            st.error("No Edge")

        st.subheader("Trend")

        fig = plt.figure()
        plt.plot(df.head(15)[stat].values)
        plt.axhline(line)
        plt.title("Last 15 Games")
        plt.xlabel("Games Ago")
        plt.ylabel(stat)

        st.pyplot(fig)
