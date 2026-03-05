}
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import os

# Refresh every hour (3600000 ms)
st_autorefresh(interval=3600000, key="datarefresh")

st.set_page_config(page_title="NBA Props Scanner", layout="wide")

st.title("🔥 NBA Props Scanner")

DATA_FILE = "props_data.csv"

# Load data or generate if missing
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    st.warning("No data file found yet. Generating props data...")

    import generate_props
    generate_props.generate_data()

    df = pd.read_csv(DATA_FILE)

# Stat selector
stat = st.selectbox(
    "Stat",
    ["PTS", "REB", "AST", "3PM"]
)

st.subheader("🔥 Best Props")

# Show table
st.dataframe(df, use_container_width=True
             import generate_props
generate_props.generate_data()

df = pd.read_csv(DATA_FILE)
