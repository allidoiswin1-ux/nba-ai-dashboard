import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🔥 NBA Props Scanner")

df = pd.read_csv("props_data.csv")

STAT = st.selectbox("Stat", ["PTS","REB","AST"])

df["Projection"] = df[STAT] * 1.15
df["Edge"] = df["Projection"] - df["Line"]

df = df.sort_values("Edge", ascending=False)

df.insert(0,"Rank",range(1,len(df)+1))

st.dataframe(df)
