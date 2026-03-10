import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime


def get_today_games():

    today = datetime.today().strftime("%m/%d/%Y")

    games = scoreboardv2.ScoreboardV2(
        game_date=today
    ).get_data_frames()[0]

    return games


def get_team_pace():

    teams = leaguedashteamstats.LeagueDashTeamStats(
        season="2025-26",
        measure_type_detailed_defense="Base"
    ).get_data_frames()[0]

    return teams[[
        "TEAM_ID",
        "TEAM_NAME",
        "PACE",
        "OFF_RATING",
        "DEF_RATING"
    ]]


def get_player_stats():

    players = leaguedashplayerstats.LeagueDashPlayerStats(
        season="2025-26",
        per_mode_detailed="PerGame"
    ).get_data_frames()[0]

    return players[[
        "PLAYER_NAME",
        "TEAM_ID",
        "PTS",
        "REB",
        "AST",
        "MIN"
    ]]
