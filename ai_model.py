import pandas as pd
from sklearn.linear_model import LinearRegression


def train_projection_model(player_data, pace_data):

    df = player_data.merge(pace_data, on="TEAM_ID")

    X = df[[
        "MIN",
        "PACE",
        "OFF_RATING",
        "DEF_RATING"
    ]]

    y = df["PTS"]

    model = LinearRegression()

    model.fit(X, y)

    return model


def generate_ai_projections(model, player_data, pace_data):

    df = player_data.merge(pace_data, on="TEAM_ID")

    X = df[[
        "MIN",
        "PACE",
        "OFF_RATING",
        "DEF_RATING"
    ]]

    df["AI_PROJ"] = model.predict(X)

    return df
