import streamlit as st
import pandas as pd
from src.setup import players
from src.metrics import *

# Function to load data
@st.cache_data
def load_data():
    return pd.read_csv('team_stats.csv')

def main():
    # Page configuration
    st.set_page_config(page_title="LA Clams Stats", page_icon="🏈")
    hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    # Display the header and logo
    display_header()

    # Load the data
    data = load_data()  # Make sure to define this function to load your data

    # Display the season title
    st.subheader("🍁 Fall 2023 Season 🍁")

    # Get weeks with data and calculate total stats and season averages
    weeks_with_data = data['Week'].unique()
    calculate_season_statistics(data)

    # Individual game statistics section
    st.subheader("Individual Game Statistics")

    # Week selection dropdown
    week_selection = st.selectbox('Select a Week', ['Week ' + str(i) for i in range(1, 11)])
    week_number = int(week_selection.split(' ')[1])

    # Check if data for the selected week exists
    if week_number in weeks_with_data:
        week_data = data[data['Week'] == week_number]
        weekly_stats = calculate_weekly_statistics(week_data, week_number)
    else:
        # Display error message if no data for the selected week
        st.error(f"No stats available for {week_selection}. Please select another week.")

    #####################################################
    
    # Sort player names in alphabetical order
    sorted_player_names = sorted(players)

    st.subheader("Individual Player Stats")
    
    # Dropdown to select a player
    selected_player = st.selectbox('Select a player', sorted_player_names)
    
    # Display the stats
    st.subheader(f'Season stats for {selected_player}')

    # Get the average statistics for the selected player
    calculate_average_stats(data, selected_player)

    st.subheader("Per-game player stats")

    # Dropdown to select the week
    week = st.selectbox('Select Week', options=data['Week'].unique())

    # Dropdown to select the player
    selected_player = st.selectbox('Select Player', options=sorted_player_names)

    # Display the stats in the app
    st.write(f"Stats for {selected_player} in week {week}:")

    # Calculate stats for the selected player and week
    calculate_individual_player_stats(data, week, selected_player)


if __name__ == "__main__":
    main()