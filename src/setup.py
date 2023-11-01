import pandas as pd
import streamlit as st

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
        return None 
    

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

def display_data_as_table(data):
    # Create a DataFrame and transpose it for a vertical display
    # Now, before displaying, ensure that all floating-point values are formatted to one decimal place
    data = {k: (f"{v:.1f}" if isinstance(v, float) else v) for k, v in data.items()}
    data_df = pd.DataFrame([data]).transpose().reset_index()
    data_df.columns = ["Statistic", "Value"]

    st.table(data_df)


def display_header():
    # Create a layout with three columns
    col1, col2, col3 = st.columns([0.1, 0.1, 0.1])

    # The first and third columns are placeholders for centering the logo
    with col2:
        st.image("logo.png")  # Display the logo in the second column

    # Display the main title of the page
    st.title("LA Clams Statistics")

