import streamlit as st
import pandas as pd
import os
import generate_props

st.set_page_config(page_title="NBA Props Scanner", layout="wide")

st.title("🔥 NBA Props Scanner")

DATA_FILE = "props_data.csv"

# Generate data if file does not exist
if not os.path.exists(DATA_FILE):
    st.warning("Generating props data...")
    generate_props.generate_data()

# Load data
df = pd.read_csv(DATA_FILE)

stat = st.selectbox(
    "Stat",
    ["PTS", "REB", "AST", "3PM"]
)

st.subheader("🔥 Best Props Tonight")

st.dataframe(df, use_container_width=True)
