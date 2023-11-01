import pandas as pd
from collections import Counter
from src.setup import *


def calculate_season_statistics(data):
    # First, ensure we only include weeks with data
    weeks_with_data = data['Week'].unique()

    # Initialize variables to store total stats
    total_clams_points = 0
    total_opponent_points = 0
    total_plays = 0
    total_offensive_plays = 0
    total_defensive_plays = 0
    total_passing_tds = 0
    total_rushing_tds = 0
    total_interceptions_offense = 0
    total_interceptions_defense = 0
    total_rushing_yards = 0
    total_receiving_yards = 0
    total_tds = 0
    total_flags_pulled = 0
    successful_conversions = 0
    attempted_conversions = 0
    total_penalties = 0
    total_successful_offense = 0
    total_successful_defense = 0
    total_pct_successful_offense = 0
    total_pct_successful_defense = 0
    total_pct_time_offense = 0

    # Calculate statistics for each week and accumulate totals
    for week in weeks_with_data:
        week_data = data[data['Week'] == week]

        # Calculate statistics
        clams_points_scored = week_data[(week_data['Offense/Defense'] == 'Offense') & (week_data['Action'] != 'Pick-Six')]['Points'].sum()
        opponent_points_scored = week_data[(week_data['Offense/Defense'] == 'Defense') | ((week_data['Offense/Defense'] == 'Offense') & (week_data['Action'] == 'Pick-Six'))]['Points'].sum()
        plays = len(week_data)
        offensive_plays = len(week_data[week_data['Offense/Defense'] == 'Offense'])
        defensive_plays = len(week_data[week_data['Offense/Defense'] == 'Defense'])
        passing_tds = len(week_data[(week_data['Offense/Defense'] == 'Offense') & (week_data['Action'] == 'Touchdown') & (week_data['Touchdown Type'] == 'Passing Touchdown')])
        rushing_tds = len(week_data[(week_data['Offense/Defense'] == 'Offense') & (week_data['Action'] == 'Touchdown') & (week_data['Touchdown Type'] == 'Rushing Touchdown')])
        interceptions_offense = len(week_data[(week_data['Offense/Defense'] == 'Offense') & week_data['Action'].isin(['Interception', 'Pick-Six'])])
        interceptions_defense = len(week_data[(week_data['Offense/Defense'] == 'Defense') & week_data['Action'].isin(['Interception', 'Pick-Six'])])
        rushing_yards = week_data[(week_data['Offense/Defense'] == 'Offense') & (week_data['Touchdown Type'] == 'Rushing Touchdown')]['Yards'].sum()
        receiving_yards = week_data[(week_data['Offense/Defense'] == 'Offense') & (week_data['Touchdown Type'] == 'Passing Touchdown')]['Yards'].sum()
        total_tds_game = passing_tds + rushing_tds
        flags_pulled = len(week_data[week_data['Action'] == 'Flag Pull'])
        conversions_made = len(week_data[(week_data['Offense/Defense'] == 'Offense') & (week_data['Conversion Outcome'] == 'Complete')])
        conversions_attempted = len(week_data[(week_data['Offense/Defense'] == 'Offense') & (week_data['Action'] == 'Conversion')])
        penalties = len(week_data[week_data['Action'] == 'Penalty'])
        successful_offense = len(week_data[week_data['Offense/Defense'] == 'Offense'][week_data['Yards'] > 0])
        successful_defense = len(week_data[week_data['Offense/Defense'] == 'Defense'][week_data['Yards'] <= 0])
        pct_successful_offense = (successful_offense/offensive_plays) * 100 if offensive_plays > 0 else 0
        pct_successful_defense = (successful_defense/defensive_plays) * 100 if defensive_plays > 0 else 0
        percent_plays_offense = (offensive_plays / plays) * 100 if plays > 0 else 0


        # Accumulate totals
        total_clams_points += clams_points_scored
        total_opponent_points += opponent_points_scored
        total_plays += plays
        total_offensive_plays += offensive_plays
        total_defensive_plays += defensive_plays
        total_passing_tds += passing_tds
        total_rushing_tds += rushing_tds
        total_interceptions_offense += interceptions_offense
        total_interceptions_defense += interceptions_defense
        total_rushing_yards += rushing_yards
        total_receiving_yards += receiving_yards
        total_tds += total_tds_game
        total_flags_pulled += flags_pulled
        successful_conversions += conversions_made
        attempted_conversions += conversions_attempted
        total_penalties += penalties
        total_successful_offense += successful_offense
        total_successful_defense += successful_defense
        total_pct_successful_offense += pct_successful_offense
        total_pct_successful_defense += pct_successful_defense
        total_pct_time_offense += percent_plays_offense

    # Now, calculate the average statistics over the season
    num_games= len(weeks_with_data)
    avg_clams_points = round(total_clams_points / num_games, 1)
    avg_opponent_points = round(total_opponent_points / num_games, 1)
    avg_plays = round(total_plays / num_games, 1)
    avg_offensive_plays = round(total_offensive_plays / num_games, 1)
    avg_defensive_plays = round(total_defensive_plays / num_games, 1)
    avg_total_successful_offense = round(total_successful_offense / num_games, 1)
    avg_total_successful_defense = round(total_successful_defense / num_games, 1)
    avg_pct_successful_offense = round(total_pct_successful_offense / num_games, 1)
    avg_pct_successful_defense = round(total_pct_successful_defense / num_games, 1)
    avg_passing_tds = round(total_passing_tds / num_games, 1)
    avg_rushing_tds = round(total_rushing_tds / num_games, 1)
    avg_interceptions_offense = round(total_interceptions_offense / num_games, 1)
    avg_interceptions_defense = round(total_interceptions_defense / num_games, 1)
    avg_rushing_yards = round(total_rushing_yards / num_games, 1)
    avg_receiving_yards = round(total_receiving_yards / num_games, 1)
    avg_total_tds = round(total_tds / num_games, 1)
    avg_flags_pulled = round(total_flags_pulled / num_games, 1)
    avg_successful_conversions = round(successful_conversions / num_games, 1)
    avg_attempted_conversions = round(attempted_conversions / num_games, 1)
    avg_conversion_rate = round((avg_successful_conversions / avg_attempted_conversions) * 100 if avg_attempted_conversions > 0 else 0, 1)
    avg_penalties = round(total_penalties / num_games, 1)
    avg_time_offense = round(total_pct_time_offense / num_games, 1)

    # Create a summary dictionary for the season averages
    season_averages_summary = {
        'Games Played (w/stats)': num_games,
        'Average LA Clams Points per Game': f"{avg_clams_points:.1f}",
        'Average Opponent Points per Game': f"{avg_opponent_points:.1f}",
        'Average Total Plays per Game': f"{avg_plays:.1f}",
        'Average Offensive Plays per Game': f"{avg_offensive_plays:.1f}",
        'Average Defensive Plays per Game': f"{avg_defensive_plays:.1f}",
        'Average % Time on Offense': f"{avg_time_offense:.1f}",
        'Average Successful Offensive Plays per Game': f"{avg_total_successful_offense:.1f}",
        'Average Successful Defensive Plays per Game': f"{avg_total_successful_defense:.1f}",
        '% Successful Offensive Plays per Game': f"{avg_pct_successful_offense:.1f}",
        '% Successful Defensive Plays per Game': f"{avg_pct_successful_defense:.1f}",
        'Average Passing TDs per Game': f"{avg_passing_tds:.1f}",
        'Average Rushing TDs per Game': f"{avg_rushing_tds:.1f}",
        'Average Total TDs per Game': f"{avg_total_tds:.1f}",
        'Average Interceptions (while on Offense) per Game': f"{avg_interceptions_offense:.1f}",
        'Average Interceptions (while on Defense) per Game': f"{avg_interceptions_defense:.1f}",
        'Average Rushing Yards per Game': f"{avg_rushing_yards:.1f}",
        'Average Receiving Yards per Game': f"{avg_receiving_yards:.1f}",
        'Average Flags Pulled per Game': f"{avg_flags_pulled:.1f}",
        'Average Successful Conversions per Game': f"{avg_successful_conversions:.1f}",
        'Average Attempted Conversions per Game': f"{avg_attempted_conversions:.1f}",
        'Average Conversion Rate (%)': f"{avg_conversion_rate:.1f}",
        'Average Penalties per Game': f"{avg_penalties:.1f}",
}

    # Display the season average summary
    st.subheader('Season Averages')
    display_data_as_table(season_averages_summary)


def calculate_weekly_statistics(week_data, week_number):
    # Calculate the various statistics
    opponent = week_data['Opponent'].iloc[0]
    clams_points_scored = week_data[(week_data['Offense/Defense'] == 'Offense') & (week_data['Action'] != 'Pick-Six')]['Points'].sum()
    total_points_allowed = week_data[(week_data['Offense/Defense'] == 'Defense') | ((week_data['Offense/Defense'] == 'Offense') & (week_data['Action'] == 'Pick-Six'))]['Points'].sum()
    outcome = "W" if clams_points_scored > total_points_allowed else "L"
    num_plays = len(week_data)
    num_offense_plays = len(week_data[week_data['Offense/Defense'] == 'Offense'])
    num_defense_plays = len(week_data[week_data['Offense/Defense'] == 'Defense'])
    percent_plays_offense = (num_offense_plays / num_plays) * 100 if num_plays > 0 else 0
    percent_plays_defense = (num_defense_plays / num_plays) * 100 if num_plays > 0 else 0
    successful_offense = len(week_data[week_data['Offense/Defense'] == 'Offense'][week_data['Yards'] > 0])
    pct_successful_offense = (successful_offense/num_offense_plays) * 100 if num_offense_plays > 0 else 0
    successful_defense = len(week_data[week_data['Offense/Defense'] == 'Defense'][week_data['Yards'] <= 0])
    pct_successful_defense = (successful_defense/num_defense_plays) * 100 if num_defense_plays > 0 else 0
    passing_tds = len(week_data[week_data['Offense/Defense'] == 'Offense'][week_data['Action'] == 'Touchdown'][week_data['Touchdown Type'] == 'Passing Touchdown'])
    rushing_tds = len(week_data[week_data['Offense/Defense'] == 'Offense'][week_data['Action'] == 'Touchdown'][week_data['Touchdown Type'] == 'Rushing Touchdown'])
    interceptions_offense = len(week_data[(week_data['Offense/Defense'] == 'Offense') & week_data['Action'].isin(['Interception', 'Pick-Six'])])
    interceptions_defense = len(week_data[(week_data['Offense/Defense'] == 'Defense') & week_data['Action'].isin(['Interception', 'Pick-Six'])])
    total_rushing_yards = week_data[week_data['Offense/Defense'] == 'Offense'][week_data['Touchdown Type'] == 'Rushing Touchdown']['Yards'].sum()
    total_receiving_yards = week_data[week_data['Offense/Defense'] == 'Offense'][week_data['Touchdown Type'] == 'Passing Touchdown']['Yards'].sum()
    total_tds = passing_tds + rushing_tds
    total_flags_pulled = len(week_data[week_data['Action'] == 'Flag Pull'])
    successful_conversions = len(week_data[week_data['Offense/Defense'] == 'Offense'][week_data['Conversion Outcome'] == 'Complete'])
    attempted_conversions = len(week_data[week_data['Offense/Defense'] == 'Offense'][week_data['Action'] == 'Conversion'])
    conversion_rate = (successful_conversions / attempted_conversions) * 100 if attempted_conversions > 0 else 0
    total_penalties = len(week_data[week_data['Action'] == 'Penalty'])

    # Create a dictionary for the summary
    summary = {
        'Week': week_number,
        'Opponent Name': opponent,
        'Outcome': outcome,
        'LA Clams Score': clams_points_scored,
        'Opponent Score': total_points_allowed,
        'Total Plays': num_plays,
        'Total Offensive Plays': num_offense_plays,
        'Total Defensive Plays': num_defense_plays,
        '% Plays on Offense': percent_plays_offense,
        'Successful Offensive Plays': successful_offense,
        '% Successful Offensive Plays': pct_successful_offense,
        'Successful Defensive Stops': successful_defense,
        '% Successful Defensive Stops': pct_successful_defense,
        'Passing TDs': passing_tds,
        'Rushing TDs': rushing_tds,
        'Total TDs': total_tds,
        'Int (while on offense)': interceptions_offense,
        'Int (while on defense)': interceptions_defense,
        'Total Rushing Yards': total_rushing_yards,
        'Total Receiving Yards': total_receiving_yards,
        'Total Flags Pulled': total_flags_pulled,
        'Successful Conversions': successful_conversions,
        'Attempted Conversions': attempted_conversions,
        'Conversion Rate': conversion_rate,
        'Total Penalties': total_penalties,
    }

    display_data_as_table(summary)


def calculate_average_stats(data, player_name):
    player_actions, player_on_field = get_player_data(data, player_name)
    
    games_played = player_on_field['Week'].nunique()

    # Calculate various statistics
    total_rushing_yards = calculate_statistic(player_actions, 
                                              (player_actions['Action'] == 'Run') & 
                                              (player_actions['Offense/Defense'] == 'Offense'), 
                                              'Yards')
    avg_rushing_yards_per_game = calculate_average_per_game(total_rushing_yards, games_played)

    total_receiving_yards = calculate_statistic(player_actions, 
                                                (player_actions['Action'] == 'Pass') & 
                                                (player_actions['Offense/Defense'] == 'Offense'), 
                                                'Yards')
    avg_receiving_yards_per_game = calculate_average_per_game(total_receiving_yards, games_played)

    total_rushing_tds = calculate_statistic(player_actions, 
                                            (player_actions['Touchdown Type'] == 'Rushing Touchdown') & 
                                            (player_actions['Offense/Defense'] == 'Offense'), 
                                            None, 
                                            aggregation='count')
    avg_rushing_tds_per_game = calculate_average_per_game(total_rushing_tds, games_played)

    total_receiving_tds = calculate_statistic(player_actions, 
                                              (player_actions['Touchdown Type'] == 'Passing Touchdown') & 
                                              (player_actions['Offense/Defense'] == 'Offense'), 
                                              None, 
                                              aggregation='count')
    avg_receiving_tds_per_game = calculate_average_per_game(total_receiving_tds, games_played)

    sacks = calculate_statistic(player_actions, 
                                (player_actions['Action'] == 'Sack') & 
                                (player_actions['Offense/Defense'] == 'Defense'), 
                                None, 
                                aggregation='count')
    avg_sacks_per_game = calculate_average_per_game(sacks, games_played)

    flags_pulled = calculate_statistic(player_actions, 
                                       (player_actions['Action'] == 'Flag Pull') & 
                                       (player_actions['Offense/Defense'] == 'Defense'), 
                                       None, 
                                       aggregation='count') + sacks
    avg_flags_pulled_per_game = calculate_average_per_game(flags_pulled, games_played)

    # Positions played
    all_positions = extract_positions(player_on_field, player_name)
    offensive_positions = ['Quarterback', 'Wide Receiver', 'Running Back', 'Tight End', 'Center']
    defensive_positions = ['Pass Rusher', 'Corner Back', 'Safety']
    player_offensive_positions = [pos for pos in all_positions if pos in offensive_positions]
    player_defensive_positions = [pos for pos in all_positions if pos in defensive_positions]

    most_common_offensive_position = Counter(player_offensive_positions).most_common(1)[0][0] if player_offensive_positions else 'N/A'
    most_common_defensive_position = Counter(player_defensive_positions).most_common(1)[0][0] if player_defensive_positions else 'N/A'

    # Calculate total passing yards for the season when the player is a quarterback
    total_passing_yards = calculate_quarterback_stats(data, player_name)
    avg_passing_yards_per_game = 'N/A' if total_passing_yards == 'N/A' else total_passing_yards / games_played

    # Calculate number of offensive and defensive plays
    offensive_plays, defensive_plays = calculate_offensive_defensive_plays(player_on_field)

    # Calculate averages based on the number of games played
    avg_offensive_plays = offensive_plays / games_played if games_played else 0
    avg_defensive_plays = defensive_plays / games_played if games_played else 0

    # Compile all the statistics
    avg_stats = {
        'Games Played (w/stats available)': games_played,
        'Most Common Offensive Position': most_common_offensive_position,
        'Most Common Defensive Position': most_common_defensive_position,
        'Average Passing Yards per Game': avg_passing_yards_per_game,
        'Average Rushing Yards per Game': avg_rushing_yards_per_game,
        'Average Receiving Yards per Game': avg_receiving_yards_per_game,
        'Average Rushing TDs per Game': avg_rushing_tds_per_game,
        'Average Receiving TDs per Game': avg_receiving_tds_per_game,
        'Average # Flags Pulled per Game': avg_flags_pulled_per_game,
        'Average Sacks per Game': avg_sacks_per_game,
        'Average # Offensive Plays on Field per Game': avg_offensive_plays,
        'Average # Defensive Plays on Field per Game': avg_defensive_plays,
    }

    display_data_as_table(avg_stats)


def calculate_individual_player_stats(data, selected_week, selected_player):
    # Filter data for the specific player and week
    week_data = data[data['Week'] == selected_week]
    player_actions, player_on_field = get_player_data(week_data, selected_player)

    # Calculate various statistics for the specific game
    total_rushing_yards = calculate_statistic(player_actions, 
                                              (player_actions['Action'] == 'Run') & 
                                              (player_actions['Offense/Defense'] == 'Offense'), 
                                              'Yards')
    
    total_receiving_yards = calculate_statistic(player_actions, 
                                                (player_actions['Action'] == 'Pass') & 
                                                (player_actions['Offense/Defense'] == 'Offense'), 
                                                'Yards')
    
    total_rushing_tds = calculate_statistic(player_actions, 
                                            (player_actions['Touchdown Type'] == 'Rushing Touchdown') & 
                                            (player_actions['Offense/Defense'] == 'Offense'), 
                                            None, 
                                            aggregation='count')
    
    total_receiving_tds = calculate_statistic(player_actions, 
                                              (player_actions['Touchdown Type'] == 'Passing Touchdown') & 
                                              (player_actions['Offense/Defense'] == 'Offense'), 
                                              None, 
                                              aggregation='count')
    
    sacks = calculate_statistic(player_actions, 
                                (player_actions['Action'] == 'Sack') & 
                                (player_actions['Offense/Defense'] == 'Defense'), 
                                None, 
                                aggregation='count')

    flags_pulled = calculate_statistic(player_actions, 
                                       (player_actions['Action'] == 'Flag Pull') & 
                                       (player_actions['Offense/Defense'] == 'Defense'), 
                                       None, 
                                       aggregation='count') + sacks

    # Calculate the success rates
    offensive_plays = player_on_field[player_on_field['Offense/Defense'] == 'Offense']
    successful_offense = offensive_plays[offensive_plays['Yards'] > 0].shape[0]
    pct_successful_offense = (successful_offense / offensive_plays.shape[0]) * 100 if offensive_plays.shape[0] > 0 else 0

    defensive_plays = player_on_field[player_on_field['Offense/Defense'] == 'Defense']
    successful_defense = defensive_plays[defensive_plays['Yards'] <= 0].shape[0]
    pct_successful_defense = (successful_defense / defensive_plays.shape[0]) * 100 if defensive_plays.shape[0] > 0 else 0

    # Extract positions played during the game
    all_positions = extract_positions(player_on_field, selected_player)
    offensive_positions = ['Quarterback', 'Wide Receiver', 'Running Back', 'Tight End', 'Center']
    defensive_positions = ['Pass Rusher', 'Corner Back', 'Safety']

    player_offensive_positions = [pos for pos in all_positions if pos in offensive_positions]
    player_defensive_positions = [pos for pos in all_positions if pos in defensive_positions]

    most_common_offensive_position = Counter(player_offensive_positions).most_common(1)[0][0] if player_offensive_positions else 'N/A'
    most_common_defensive_position = Counter(player_defensive_positions).most_common(1)[0][0] if player_defensive_positions else 'N/A'

    # Calculate passing yards for the specific game when the player is a quarterback
    week_data = data[data['Week'] == selected_week]
    total_passing_yards = calculate_quarterback_stats(week_data, selected_player)

    # Calculate number of offensive and defensive plays
    offensive_plays, defensive_plays = calculate_offensive_defensive_plays(player_on_field)

    # Assemble the game-specific statistics
    game_stats = {
        'Position (Offensive)': most_common_offensive_position,
        'Position (Defense)': most_common_defensive_position,
        'Passing yards': total_passing_yards,
        'Rushing yards': total_rushing_yards,
        'Receiving yards': total_receiving_yards,
        'Rushing TDs': total_rushing_tds,
        'Receiving TDs': total_receiving_tds,
        'Sacks': sacks,
        'Flags pulled': flags_pulled,
        'Number of offensive plays': offensive_plays,
        'Successful offensive plays (%)': pct_successful_offense,
        'Number of defensive plays': defensive_plays,
        'Successful defensive plays (%)': pct_successful_defense,

    }

    display_data_as_table(game_stats)

