import streamlit as st
import pandas as pd
from collections import Counter

# Function to load data
@st.cache_data
def load_data():
    return pd.read_csv('team_stats.csv')

# Function to format the numbers in the DataFrame
def format_float(val):
    if isinstance(val, float):
        return f"{val:.1f}"
    return val


def get_player_data(data, player_name):
    """Retrieve data entries where the player was involved or on the field."""
    player_actions = data[data['Player Involved'] == player_name]
    player_on_field = data[data['Player Positions'].str.contains(player_name, na=False)]
    return player_actions, player_on_field


def calculate_statistic(data, filter_conditions, stat_field, aggregation='sum'):
    """Calculate statistics based on specified conditions."""
    filtered_data = data[filter_conditions]
    if aggregation == 'sum':
        return filtered_data[stat_field].sum()
    elif aggregation == 'count':
        return filtered_data.shape[0]
    else:
        return None  # or some default value
    

def extract_positions(player_on_field, player_name):
    """Extract the positions a player has played during the games."""
    all_positions = []
    for positions in player_on_field['Player Positions']:
        if pd.notnull(positions):
            position_entries = positions.split(', ')
            for entry in position_entries:
                name, position = entry.split(' as ')
                if name.strip() == player_name:
                    all_positions.append(position.strip())
    return all_positions


def calculate_average_per_game(total, games_played):
    """Calculate the average value per game."""
    return total / games_played if games_played else 0


def calculate_quarterback_stats(data, player_name):
    """Calculate passing yards when the player is a quarterback."""
    qb_plays = data[data['Player Positions'].apply(lambda x: player_name + ' as Quarterback' in x if x is not None else False)]
    if qb_plays.empty:
        return 'N/A'  # Return 'N/A' if there are no plays with the player as a quarterback

    completed_passes = qb_plays[(qb_plays['Offense/Defense'] == 'Offense') & (qb_plays['Pass Outcome'] == 'Complete')]
    total_passing_yards = completed_passes['Yards'].sum()

    return total_passing_yards

def calculate_offensive_defensive_plays(player_on_field):
    """Calculate the number of offensive and defensive plays."""
    player_on_field_offense = player_on_field[player_on_field['Offense/Defense'] == 'Offense']
    player_on_field_defense = player_on_field[player_on_field['Offense/Defense'] == 'Defense']

    offensive_plays = player_on_field_offense.shape[0]
    defensive_plays = player_on_field_defense.shape[0]

    return offensive_plays, defensive_plays



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
        'Average Passing Yards per Game': avg_passing_yards_per_game,
        'Average Rushing Yards per Game': avg_rushing_yards_per_game,
        'Average Receiving Yards per Game': avg_receiving_yards_per_game,
        'Average Rushing TDs per Game': avg_rushing_tds_per_game,
        'Average Receiving TDs per Game': avg_receiving_tds_per_game,
        'Average # Flags Pulled per Game': avg_flags_pulled_per_game,
        'Average Sacks per Game': avg_sacks_per_game,
        'Average # Offensive Plays on Field per Game': avg_offensive_plays,
        'Average # Defensive Plays on Field per Game': avg_defensive_plays,
        'Most Common Offensive Position': most_common_offensive_position,
        'Most Common Defensive Position': most_common_defensive_position
    }

    # Add to the statistics dictionary
    avg_stats['Average # Offensive Plays on Field per Game'] = avg_offensive_plays
    avg_stats['Average # Defensive Plays on Field per Game'] = avg_defensive_plays

    # Add to the statistics dictionary
    avg_stats['Average Passing Yards per Game'] = avg_passing_yards_per_game

    return avg_stats


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
        'Rushing yards': total_rushing_yards,
        'Receiving yards': total_receiving_yards,
        'Rushing TDs': total_rushing_tds,
        'Receiving TDs': total_receiving_tds,
        'Sacks': sacks,
        'Flags pulled': flags_pulled,
        'Successful offensive plays (%)': pct_successful_offense,
        'Successful defensive plays (%)': pct_successful_defense,
        'Most Common Offensive Position': most_common_offensive_position,
        'Most Common Defensive Position': most_common_defensive_position
    }

    # Add these to the game-specific statistics dictionary
    game_stats['Number of offensive plays'] = offensive_plays
    game_stats['Number of defensive plays'] = defensive_plays
    # Add to the game-specific statistics dictionary
    game_stats['Passing yards'] = total_passing_yards

    # Convert the statistics to a DataFrame
    stats_df = pd.DataFrame([game_stats])

    return stats_df




# def calculate_average_stats(data, player_name):
#     # Data for actions the player was directly involved in
#     player_actions = data[data['Player Involved'] == player_name]

#     # Data for plays where the player was on the field
#     player_on_field = data[data['Player Positions'].str.contains(player_name, na=False)]

#     # Separate the data based on 'Offense' or 'Defense'
#     player_on_field_offense = player_on_field[player_on_field['Offense/Defense'] == 'Offense']
#     player_on_field_defense = player_on_field[player_on_field['Offense/Defense'] == 'Defense']

#     # Number of games played is the number of unique game weeks the player participated in
#     games_played = player_on_field['Week'].nunique()

#     # Total and average calculations
#     total_rushing_yards = player_actions[(player_actions['Action'] == 'Run') & (player_actions['Offense/Defense'] == 'Offense')]['Yards'].sum()
#     avg_rushing_yards_per_game = total_rushing_yards / games_played if games_played else 0

#     total_receiving_yards = player_actions[(player_actions['Action'] == 'Pass') & (player_actions['Offense/Defense'] == 'Offense')]['Yards'].sum()
#     avg_receiving_yards_per_game = total_receiving_yards / games_played if games_played else 0

#     total_rushing_tds = player_actions[(player_actions['Touchdown Type'] == 'Rushing Touchdown') & (player_actions['Offense/Defense'] == 'Offense')].shape[0]
#     avg_rushing_tds_per_game = total_rushing_tds / games_played if games_played else 0

#     total_receiving_tds = player_actions[(player_actions['Touchdown Type'] == 'Passing Touchdown') & (player_actions['Offense/Defense'] == 'Offense')].shape[0]
#     avg_receiving_tds_per_game = total_receiving_tds / games_played if games_played else 0

#     sacks = player_actions[(player_actions['Action'] == 'Sack') & (player_actions['Offense/Defense'] == 'Defense')].shape[0]
#     avg_sacks = sacks / games_played if games_played else 0

#     flags_pulled = player_actions[(player_actions['Action'] == 'Flag Pull') & (player_actions['Offense/Defense'] == 'Defense')].shape[0] + sacks
#     avg_flags_pulled_per_game = flags_pulled / games_played if games_played else 0

#     avg_offensive_plays = player_on_field_offense.shape[0] / games_played if games_played else 0
#     avg_defensive_plays = player_on_field_defense.shape[0] / games_played if games_played else 0

#     # Extract positions the player has played
#     all_positions = []
#     for positions in player_on_field['Player Positions']:
#         if pd.notnull(positions):
#             position_entries = positions.split(', ')
#             for entry in position_entries:
#                 name, position = entry.split(' as ')
#                 if name.strip() == player_name:
#                     all_positions.append(position.strip())

#     # Offensive and defensive positions
#     offensive_positions_set = set(['Quarterback', 'Wide Receiver', 'Running Back', 'Tight End', 'Center'])
#     defensive_positions_set = set(['Pass Rusher', 'Corner Back', 'Safety'])

#     player_offensive_positions = [pos for pos in all_positions if pos in offensive_positions_set]
#     player_defensive_positions = [pos for pos in all_positions if pos in defensive_positions_set]

#     most_common_offensive_position = Counter(player_offensive_positions).most_common(1)[0][0] if player_offensive_positions else 'N/A'
#     most_common_defensive_position = Counter(player_defensive_positions).most_common(1)[0][0] if player_defensive_positions else 'N/A'

#     # Calculating average passing yards specifically for when the player is a quarterback
#     qb_plays = data[data['Player Positions'].apply(lambda x: player_name + ' as Quarterback' in x if x is not None else False)]
#     completed_passes = qb_plays[(qb_plays['Offense/Defense'] == 'Offense') & (qb_plays['Pass Outcome'] == 'Complete')]
#     total_passing_yards = completed_passes['Yards'].sum()
#     avg_passing_yards_per_game = total_passing_yards / games_played if games_played and completed_passes.shape[0] > 0 else 'N/A'

#     # Compile all the statistics
#     avg_stats = {
#         'Games Played (w/stats available)': games_played,
#         'Average Passing Yards per Game': avg_passing_yards_per_game,
#         'Average Rushing Yards per Game': avg_rushing_yards_per_game,
#         'Average Receiving Yards per Game': avg_receiving_yards_per_game,
#         'Average Rushing TDs per Game': avg_rushing_tds_per_game,
#         'Average Receiving TDs per Game': avg_receiving_tds_per_game,
#         'Average # Flags Pulled per Game': avg_flags_pulled_per_game,
#         'Average Sacks per Game': avg_sacks,
#         'Average # Offensive Plays on Field per Game': avg_offensive_plays,
#         'Average # Defensive Plays on Field per Game': avg_defensive_plays,
#         'Most Common Offensive Position': most_common_offensive_position,
#         'Most Common Defensive Position': most_common_defensive_position
#     }

#     return avg_stats

# # Function to calculate the statistics for the selected player and week
# def calculate_individual_player_stats(data, selected_week, selected_player):
#     # Filter data based on selected week and player
#     week_data = data[data['Week'] == selected_week]
#     player_actions = week_data[week_data['Player Involved'] == selected_player]
#     player_on_field = week_data[week_data['Player Positions'].str.contains(selected_player, na=False)]

#     # Separate the data based on 'Offense' or 'Defense'
#     player_on_field_offense = player_on_field[player_on_field['Offense/Defense'] == 'Offense']
#     player_on_field_defense = player_on_field[player_on_field['Offense/Defense'] == 'Defense']

#     offensive_plays = len(player_on_field_offense)
#     defensive_plays = len(player_on_field_defense)

#     # Total and average calculations
#     total_rushing_yards = player_actions[(player_actions['Action'] == 'Run') & (player_actions['Offense/Defense'] == 'Offense')]['Yards'].sum()

#     total_receiving_yards = player_actions[(player_actions['Action'] == 'Pass') & (player_actions['Offense/Defense'] == 'Offense')]['Yards'].sum()

#     total_rushing_tds = player_actions[(player_actions['Touchdown Type'] == 'Rushing Touchdown') & (player_actions['Offense/Defense'] == 'Offense')].shape[0]

#     total_receiving_tds = player_actions[(player_actions['Touchdown Type'] == 'Passing Touchdown') & (player_actions['Offense/Defense'] == 'Offense')].shape[0]

#     sacks = player_actions[(player_actions['Action'] == 'Sack') & (player_actions['Offense/Defense'] == 'Defense')].shape[0]

#     flags_pulled = player_actions[(player_actions['Action'] == 'Flag Pull') & (player_actions['Offense/Defense'] == 'Defense')].shape[0] + sacks

#     successful_offense = len(player_on_field[player_on_field['Offense/Defense'] == 'Offense'][player_on_field['Yards'] > 0])
#     pct_successful_offense = (successful_offense/offensive_plays) * 100 if offensive_plays > 0 else 0
#     successful_defense = len(player_on_field[player_on_field['Offense/Defense'] == 'Defense'][player_on_field['Yards'] <= 0])
#     pct_successful_defense = (successful_defense/defensive_plays) * 100 if defensive_plays > 0 else 0


#     # Extract positions the player has played
#     all_positions = []
#     for positions in player_on_field['Player Positions']:
#         if pd.notnull(positions):
#             position_entries = positions.split(', ')
#             for entry in position_entries:
#                 name, position = entry.split(' as ')
#                 if name.strip() == selected_player:
#                     all_positions.append(position.strip())

#     # Offensive and defensive positions
#     offensive_positions_set = set(['Quarterback', 'Wide Receiver', 'Running Back', 'Tight End', 'Center'])
#     defensive_positions_set = set(['Pass Rusher', 'Corner Back', 'Safety'])

#     player_offensive_positions = [pos for pos in all_positions if pos in offensive_positions_set]
#     player_defensive_positions = [pos for pos in all_positions if pos in defensive_positions_set]

#     most_common_offensive_position = Counter(player_offensive_positions).most_common(1)[0][0] if player_offensive_positions else 'N/A'
#     most_common_defensive_position = Counter(player_defensive_positions).most_common(1)[0][0] if player_defensive_positions else 'N/A'

    # # Calculating average passing yards specifically for when the player is a quarterback
    # qb_plays = data[data['Player Positions'].apply(lambda x: selected_player + ' as Quarterback' in x if x is not None else False)]
    # completed_passes = qb_plays[(qb_plays['Offense/Defense'] == 'Offense') & (qb_plays['Pass Outcome'] == 'Complete')]
    # total_passing_yards = completed_passes['Yards'].sum() if qb_plays.shape[0] > 0 else 'N/A'

#     receptions = len(player_actions[player_actions['Action'] == 'Pass'])
#     completions = len(player_actions[player_actions['Pass Outcome'] == 'Complete'])
    
#     # Initialize the stats
#     stats = {
#         'Passing yards': total_passing_yards,
#         'Rushing yards': total_rushing_yards,
#         'Receiving yards': total_receiving_yards,
#         'Rushing TDs': total_rushing_tds,
#         'Receiving TDs': total_receiving_tds,
#         'Complete receptions': completions,
#         'Attempted Receptions': receptions,
#         'Reception %': (completions / receptions) * 100 if receptions > 0 else 0,
#         'Flags pulled': flags_pulled,
#         'Number of defensive possessions played': len(player_on_field_defense),
#         '% Successful defensive plays': pct_successful_defense,
#         'Number of offensive possessions played': len(player_on_field_offense),
#         '% Successful offensive plays': pct_successful_offense,

#     }

#     stats_df = pd.DataFrame([stats]) 
    
#     return stats_df




def main():

    st.set_page_config(
        page_title="LA Clams Stats",
        page_icon="🏈"
    )

    hide_menu_style = """
    <style>
    #MainMenu {visability: hidden;}
    footer {visibility: hidden;}
    </style>
    """

    st.markdown(hide_menu_style, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.1,0.1,0.1])

    with col1:
        st.write("")

    with col2:
        st.image("logo.png")

    with col3:
        st.write("")

    st.title("LA Clams Statistics")

    # Load data
    data = load_data()

    st.subheader("🍁 Fall 2023 Season 🍁")
    
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

        # Accumulate totals
        total_clams_points += clams_points_scored
        total_opponent_points += opponent_points_scored
        total_plays += plays
        total_offensive_plays += offensive_plays
        total_defensive_plays += defensive_plays
        total_passing_tds += passing_tds  # assuming you calculate this per game
        total_rushing_tds += rushing_tds  # assuming you calculate this per game
        total_interceptions_offense += interceptions_offense  # assuming you calculate this per game
        total_interceptions_defense += interceptions_defense  # assuming you calculate this per game
        total_rushing_yards += rushing_yards  # assuming you calculate this per game
        total_receiving_yards += receiving_yards  # assuming you calculate this per game
        total_tds += total_tds_game  # assuming you calculate total touchdowns per game
        total_flags_pulled += flags_pulled  # assuming you calculate this per game
        successful_conversions += conversions_made  # assuming you calculate this per game
        attempted_conversions += conversions_attempted  # assuming you calculate this per game
        total_penalties += penalties  # assuming you calculate this per game

    # Now, calculate the average statistics over the season
    num_games= len(weeks_with_data)
    avg_clams_points = round(total_clams_points / num_games, 1)
    avg_opponent_points = round(total_opponent_points / num_games, 1)
    avg_plays = round(total_plays / num_games, 1)
    avg_offensive_plays = round(total_offensive_plays / num_games, 1)
    avg_defensive_plays = round(total_defensive_plays / num_games, 1)
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

    # Create a summary dictionary for the season averages
    season_averages_summary = {
        'Games Played (w/stats)': num_games,
        'Average LA Clams Points per Game': f"{avg_clams_points:.1f}",
        'Average Opponent Points per Game': f"{avg_opponent_points:.1f}",
        'Average Total Plays per Game': f"{avg_plays:.1f}",
        'Average Offensive Plays per Game': f"{avg_offensive_plays:.1f}",
        'Average Defensive Plays per Game': f"{avg_defensive_plays:.1f}",
        'Average Passing TDs per Game': f"{avg_passing_tds:.1f}",
        'Average Rushing TDs per Game': f"{avg_rushing_tds:.1f}",
        'Average Interceptions (while on Offense) per Game': f"{avg_interceptions_offense:.1f}",
        'Average Interceptions (while on Defense) per Game': f"{avg_interceptions_defense:.1f}",
        'Average Rushing Yards per Game': f"{avg_rushing_yards:.1f}",
        'Average Receiving Yards per Game': f"{avg_receiving_yards:.1f}",
        'Average Total TDs per Game': f"{avg_total_tds:.1f}",
        'Average Flags Pulled per Game': f"{avg_flags_pulled:.1f}",
        'Average Successful Conversions per Game': f"{avg_successful_conversions:.1f}",
        'Average Attempted Conversions per Game': f"{avg_attempted_conversions:.1f}",
        'Average Conversion Rate (%)': f"{avg_conversion_rate:.1f}",
        'Average Penalties per Game': f"{avg_penalties:.1f}",
}

    # Display the season average summary
    st.subheader('Season Averages')
    # Apply the formatting function to the DataFrame before displaying it
    season_averages_summary_df = pd.DataFrame([season_averages_summary]).applymap(format_float)
    season_averages_summary_df = season_averages_summary_df.transpose().reset_index()
    season_averages_summary_df.columns = ["Statistic", "Value"]
    st.table(season_averages_summary_df)

    st.subheader("Individual Game Statistics")

    all_weeks = ['Week ' + str(i) for i in range(1, 11)]  # for weeks 1 through 10

    # Create a dropdown to select the Week
    week_selection = st.selectbox('Select a Week', all_weeks)

    # Extracting the week number from the selection
    week_number = int(week_selection.split(' ')[1])  # Converts 'Week 2' to 2, for example

    if week_number not in data['Week'].unique():
        # If the selected week is not in the dataset, display an error message
        st.error(f"Unfortunately, no stats were captured for {week_selection}. Alternatively, the week you have selected is in the future. Please select another week.")
    else:
        # Filter data for the selected Week
        week_data = data[data['Week'] == week_number]

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
            'Int (while on offense)': interceptions_offense,
            'Int (while on defense)': interceptions_defense,
            'Total Rushing Yards': total_rushing_yards,
            'Total Receiving Yards': total_receiving_yards,
            'Total TDs': total_tds,
            'Total Flags Pulled': total_flags_pulled,
            'Successful Conversions': successful_conversions,
            'Attempted Conversions': attempted_conversions,
            'Conversion Rate': conversion_rate,
            'Total Penalties': total_penalties,
        }


        # Display the summary as a table
        df = pd.DataFrame([summary])

        df.index = range(1, len(df) + 1)

        # Transpose the dataframe and reset its index for display
        transposed_df = df.head(1).transpose().reset_index()
        transposed_df.columns = ["Statistic", "Value"]

        transposed_df['Value'] = transposed_df['Value'].apply(lambda x: round(x, 1) if isinstance(x, float) else x)

        st.table(transposed_df)
    
    # Exclude 'No specific player', 'NaN', and get unique player names
    # Dropna removes any 'NaN' values, and unique gets the unique values from the series
    player_names = data[data['Player Involved'] != 'No specific player']['Player Involved'].dropna().unique()
    
    # Sort player names in alphabetical order
    sorted_player_names = sorted(player_names)

    st.subheader("Individual Player Stats")
    
    # Dropdown to select a player
    selected_player = st.selectbox('Select a player', sorted_player_names)
    
    # Get the average statistics for the selected player
    player_stats = calculate_average_stats(data, selected_player)
    
    # Display the stats
    st.subheader(f'Season stats for {selected_player}')

    # Display the summary as a table
    df = pd.DataFrame.from_records([player_stats])

    df.index = range(1, len(df) + 1)

    # Transpose the dataframe and reset its index for display
    transposed_df = df.head(1).transpose().reset_index()
    transposed_df.columns = ["Statistic", "Value"]

    transposed_df['Value'] = transposed_df['Value'].apply(lambda x: round(x, 1) if isinstance(x, float) else x)

    st.table(transposed_df)

    st.subheader("Per-game player stats")

    # Dropdown to select the week
    week = st.selectbox('Select Week', options=data['Week'].unique())

    # Dropdown to select the player
    selected_player = st.selectbox('Select Player', options=sorted_player_names)

    # Calculate stats for the selected player and week
    player_stats = calculate_individual_player_stats(data, week, selected_player)

    # Display the stats in the app
    st.write(f"Stats for {selected_player} in week {week}:")

    player_stats.index = range(1, len(df) + 1)

    # Transpose the dataframe and reset its index for display
    transposed_df = player_stats.head(1).transpose().reset_index()
    transposed_df.columns = ["Statistic", "Value"]

    transposed_df['Value'] = transposed_df['Value'].apply(lambda x: round(x, 1) if isinstance(x, float) else x)

    st.table(transposed_df)

if __name__ == "__main__":
    main()