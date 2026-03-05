import streamlit as st
import numpy as np

st.title("NBA AI Prop Finder")

player = st.text_input("Player")

line = st.number_input("Sportsbook Line")

projection = st.number_input("AI Projection")

simulations = np.random.normal(projection,5,10000)

probability = (simulations > line).mean()

edge = projection - line

st.write("Projection:", projection)
st.write("Probability Over:", round(probability*100,2),"%")
st.write("Edge:", round(edge,2))

if probability > 0.60:
    st.success("Strong Over")
elif probability < 0.40:
    st.error("Strong Under")
else:
    st.warning("No Edge")
