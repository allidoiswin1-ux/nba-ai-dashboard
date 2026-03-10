import streamlit as st
import pandas as pd

from data_engine import get_today_games, get_player_stats, get_team_pace
from ai_model import train_projection_model, generate_ai_projections
from prop_engine import generate_prop_table


st.set_page_config(page_title="NBA AI Props Dashboard")

st.title("🏀 NBA AI Betting Model")


st.header("Today's Games")

games = get_today_games()

st.dataframe(games)


st.header("Loading Player Data")

players = get_player_stats()

pace = get_team_pace()


st.header("Training AI Projection Model")

model = train_projection_model(players, pace)


st.header("Generating AI Projections")

proj = generate_ai_projections(model, players, pace)


st.header("Prop Edge Model")

props = generate_prop_table(proj)

df = pd.DataFrame(props)

df = df.sort_values("Edge %", ascending=False)

st.dataframe(df)


st.header("Best Bets")

best = df[df["Edge %"] > 6]

st.dataframe(best)
