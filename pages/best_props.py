import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

st.title("🔥 NBA Props Scanner")

STAT = st.selectbox("Stat", ["PTS","REB","AST"])


# ----------------------------
# SAFE CSV LOADER
# ----------------------------

file_path = "props_data.csv"

if not os.path.exists(file_path):

    st.warning("No data file found yet. Generating placeholder data.")

    df = pd.DataFrame({
        "Player":["Waiting for data"],
        "Matchup":["--"],
        "PTS":[0],
        "REB":[0],
        "AST":[0],
        "Line":[0],
        "Book":["DraftKings"]
    })

else:

    df = pd.read_csv(file_path)


# ----------------------------
# MODEL CALCULATIONS
# ----------------------------

df["Projection"] = df[STAT] * 1.15
df["Edge"] = df["Projection"] - df["Line"]
df["Probability"] = 50 + df["Edge"] * 6

df = df.sort_values("Edge", ascending=False)

df.insert(0,"Rank",range(1,len(df)+1))


# ----------------------------
# DISPLAY
# ----------------------------

st.subheader("🔥 Best Props")

st.dataframe(df[
    ["Rank","Player","Matchup","Book","Line","Projection","Edge","Probability"]
], use_container_width=True)
