from sklearn.linear_model import LinearRegression


def train_model(players, teams):

    df = players.merge(teams, on="TEAM_ID")

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


def create_projections(model, players, teams):

    df = players.merge(teams, on="TEAM_ID")

    X = df[[
        "MIN",
        "PACE",
        "OFF_RATING",
        "DEF_RATING"
    ]]

    df["PROJECTION"] = model.predict(X)

    return df
