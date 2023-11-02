import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth #add abilty to authenticate
import os
import yaml
from src.setup import get_players

def calculate_points(action, conversion_type=None, conversion_outcome=None):
    points = 0
    if action in ['Touchdown', 'Pick-Six']:  # Correctly check if the action is one of these types
        points = 6  # standard points for a touchdown or pick-six

    # Check if there was an attempted conversion and whether it was successful
    if action == 'Conversion' and conversion_outcome == 'Complete':
        if conversion_type == '1-point':
            points = 1  # points for a successful 1-point conversion
        elif conversion_type == '2-point':
            points = 2  # points for a successful 2-point conversion

    return points

# get credentials for dashboard
with open('credentials.yaml') as file:
    config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

# only if log-in was successful, continue
if authentication_status:

    st.header("LA Clams Statistics Entry Page")

    # Check if the stats CSV exists, if not, create an empty one
    if not os.path.exists('team_stats.csv'):
        columns = [
            'Week', 'Opponent', 'Half', 'Down', 'Yards to Go',
            'Play', 'Offense/Defense', 'Players on Field', 'Player Positions', 'Action', 
            'Player Involved', 'Touchdown Type', 'Pass Outcome', 'Yards', 'Points', 'Notes'
        ]
        pd.DataFrame(columns=columns).to_csv('team_stats.csv', index=False)

    # Initialize or update session state variables
    if 'play_count' not in st.session_state:
        st.session_state.play_count = 0
    if 'week' not in st.session_state:
        st.session_state.week = 1
    if 'opponent' not in st.session_state:
        st.session_state.opponent = ""

    # Set Week number
    new_week = st.number_input('Week:', min_value=1, value=st.session_state.week)
    if new_week != st.session_state.week:
        # When moving to a new week, reset all weekly information
        st.session_state.week = new_week
        st.session_state.play_count = 0
        st.session_state.opponent = ""

    # Information about the game
    if st.session_state.opponent == "":
        st.session_state.opponent = st.text_input('Opponent:', value=st.session_state.opponent)

    # default values
    td_type = None
    conversion_type = None
    conversion_outcome = None

    # Display the play count
    st.write(f"Inputting data for Play: {st.session_state.play_count + 1}")

    # Selecting offense or defense
    offense_or_defense = st.selectbox('Offense or defense?', ['Offense', 'Defense'], key="offense_defense_select")

    # Based on the selection above, present relevant positions
    if offense_or_defense == 'Offense':
        positions = ['Quarterback', 'Wide Receiver', 'Running Back', 'Tight End', 'Center']  # Offense positions
    else:
        positions = ['Pass Rusher', 'Corner Back', 'Safety']  # Defense positions

    # Play info
    half = st.selectbox('Half:', ['1st', '2nd'], key="half_select")
    down = st.number_input('Down (1-4):', min_value=1, max_value=4, value=1, key="down_input")
    yards_to_go = st.number_input('Yards to Go:', min_value=0, value=10, key="yards_to_go_input")

    players = get_players()

    # Multi-select for players on the field
    selected_players = st.multiselect('Select players on the field:', players, key="players_field_multiselect")

    # Check if exactly 7 players are selected
    if len(selected_players) != 7:
        st.warning('Please select exactly 7 players before proceeding.')
        st.stop()

    # Assign positions to selected players, now using the relevant positions list
    player_positions = {player: st.selectbox(f"Position for {player}:", positions, key=f"position_for_{player}") for player in selected_players}
    player_involved_options = ['No specific player', *players]

    # Action info
    action = st.selectbox('Action:', ['Pass', 'Run', 'Flag Pull', 'Touchdown', 'Conversion', 'Interception', 'Forced Fumble', 'Sack', 'Pick-Six', 'Penalty'], key="action_select")

    # Player involved in the action
    player_involved = None
    if action in ('Pass', 'Run', 'Flag Pull', 'Touchdown', 'Conversion', 'Forced Fumble', 'Interception', 'Sack'):
        player_involved = st.selectbox('Who was the player involved (if any)?', player_involved_options, key='player_involved')

    # Additional information based on the type of action
    td_type = pass_outcome = None
    if action == 'Touchdown':
        td_type = st.selectbox('Type of touchdown:', ['Passing Touchdown', 'Rushing Touchdown'], key="td_type_select")
    elif action == 'Pass':
        pass_outcome = st.selectbox('Was the pass complete?', ['Complete', 'Incomplete'], key="pass_outcome_general")
    elif action == 'Conversion':
        conversion_type = st.selectbox('1-point or 2-point conversion?', ['1-point', '2-point'], key="conversion_type_select")
        conversion_outcome = st.selectbox('Was the conversion complete?', ['Complete', 'Incomplete'], key="conversion_outcome_select")

    # Yards info
    yards = st.number_input('Yards gained/lost:', min_value=-100, max_value=100, value=0, key="yards_input")

    # Additional notes
    notes = st.text_area('Any additional notes or details about the play:', key="notes_text_area")

    # Submit the play info
    if st.button('Submit Play Info', key="submit_play_info_button"):
        # Increase the play count for each submission
        st.session_state.play_count += 1

        # Read the current CSV
        df = pd.read_csv('team_stats.csv')

        # Calculate points based on the action
        points = calculate_points(action, conversion_type, conversion_outcome)

        # Append the new data
        new_data = {
            'Week': st.session_state.week,
            'Opponent': st.session_state.opponent,
            'Half': half,
            'Down': down,
            'Yards to Go': yards_to_go,
            'Play': st.session_state.play_count,
            'Offense/Defense': offense_or_defense,
            'Players on Field': ', '.join(selected_players),
            'Player Positions': ', '.join(f"{player} as {position}" for player, position in player_positions.items()),
            'Action': action,
            'Player Involved': player_involved,
            'Touchdown Type': td_type,
            'Pass Outcome': pass_outcome,
            'Conversion Outcome': conversion_outcome,
            'Yards': yards,
            'Points': points,
            'Notes': notes,
        }

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

        # Save the updated CSV
        df.to_csv('team_stats.csv', index=False)
        st.success('Play info saved successfully!')

    # Option to delete a play if a mistake was made
    if st.button('Delete Last Play'):
        if st.session_state.play_count > 0:
            df = pd.read_csv('team_stats.csv')
            # Make sure we're deleting the right play (the most recent for the current week)
            recent_play = df[(df['Week'] == st.session_state.week) & (df['Play'] == st.session_state.play_count)]
            if not recent_play.empty:
                # Correctly update the play_count before deleting the entry from the DataFrame
                st.session_state.play_count -= 1
                # Deleting the row with the most recent play
                df = df.drop(recent_play.index)
                # Save the updated CSV
                df.to_csv('team_stats.csv', index=False)
                st.success('Last play deleted successfully.')
            else:
                st.error('No play available to delete for the current week.')
        else:
            st.error('No plays have been inputted yet for deletion.')

    # Display the current data
    st.subheader('Current Team Stats')
    current_df = pd.read_csv('team_stats.csv')  # This df is loaded after any possible deletion operation above
    st.data_editor(current_df)

    if st.button('Save', key="save"):
        current_df.to_csv('team_stats.csv', index=False)
        st.success('Updated data saved successfully!')

# don't let someone in without the password
elif authentication_status is False:
    st.error('Username/password is incorrect')