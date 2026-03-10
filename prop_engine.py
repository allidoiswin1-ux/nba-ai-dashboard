import numpy as np
from scipy.stats import norm


def hit_probability(projection, line):

    std = projection * 0.25

    prob = 1 - norm.cdf(line, projection, std)

    return prob * 100


def calculate_edge(probability):

    sportsbook = 50

    return probability - sportsbook


def generate_prop_table(players):

    props = []

    for _, row in players.iterrows():

        line = round(row["AI_PROJ"] - 1)

        prob = hit_probability(row["AI_PROJ"], line)

        edge = calculate_edge(prob)

        props.append({

            "Player": row["PLAYER_NAME"],
            "Projection": round(row["AI_PROJ"],2),
            "Line": line,
            "Hit %": round(prob,2),
            "Edge %": round(edge,2)

        })

    return props
