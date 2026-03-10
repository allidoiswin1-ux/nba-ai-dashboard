import streamlit as st
import pandas as pd

from data_engine import get_today_games, get_player_stats, get_team_data
from ai_model import train_model, create_projections
from prop_engine import build_props_table

st.set_page_config(page_title="NBA AI Prop Model")

st.title("🏀 NBA AI Betting Model")

@st.cache_data
def load_games():
    return get_today_games()

@st.cache_data
def load_players():
    return get_player_stats()

@st.cache_data
def load_teams():
    return get_team_data()

st.header("Today's Games")
games = load_games()
st.dataframe(games)

st.header("Loading Player Data")

players = load_players()
teams = load_teams()

st.header("Training AI Model")

model = train_model(players, teams)

st.header("Generating Projections")

proj = create_projections(model, players, teams)

st.header("Prop Edge Model")

props = build_props_table(proj)

df = pd.DataFrame(props)
df = df.sort_values("Edge %", ascending=False)

st.dataframe(df)

st.header("Best Bets")

best = df[df["Edge %"] > 6]

st.dataframe(best)
