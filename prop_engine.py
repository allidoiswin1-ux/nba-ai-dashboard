from scipy.stats import norm


def hit_probability(projection, line):

    std = projection * 0.25

    probability = 1 - norm.cdf(line, projection, std)

    return probability * 100


def calculate_edge(probability):

    sportsbook = 50

    return probability - sportsbook


def build_props_table(df):

    props = []

    for _, row in df.iterrows():

        line = round(row["PROJECTION"] - 1)

        prob = hit_probability(row["PROJECTION"], line)

        edge = calculate_edge(prob)

        props.append({

            "Player": row["PLAYER_NAME"],
            "Projection": round(row["PROJECTION"], 2),
            "Line": line,
            "Hit %": round(prob, 2),
            "Edge %": round(edge, 2)

        })

    return props
