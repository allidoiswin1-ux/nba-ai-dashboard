import streamlit as st
import pandas as pd
import numpy as np
import math

from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog

st.title("🔥 Best NBA Props Scanner")

stat = st.selectbox(
    "Stat Type",
    ["PTS","REB","AST"]
)

line = st.number_input("Example Sportsbook Line", value=20.5)

num_players = st.slider("Players To Scan", 5, 50, 20)

player_list = players.get_active_players()

results = []

for p in player_list[:num_players]:

    try:

        player_id = p["id"]
        name = p["full_name"]

        gamelog = playergamelog.PlayerGameLog(player_id=player_id)
        df = gamelog.get_data_frames()[0]

        last10 = df.head(10)[stat].mean()
        season = df[stat].mean()

        projection = (last10*0.65)+(season*0.35)

        std = df[stat].std()

        if std == 0:
            prob_over = 0.5
        else:
            prob_over = 1-(0.5*(1+math.erf((line-projection)/(std*math.sqrt(2)))))

        edge = projection-line

        results.append({
            "Player":name,
            "Projection":round(projection,2),
            "Line":line,
            "Edge":round(edge,2),
            "Prob Over %":round(prob_over*100,1)
        })

    except:
        pass

df_results = pd.DataFrame(results)

df_results = df_results.sort_values("Edge",ascending=False)

st.dataframe(df_results)
