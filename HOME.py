import streamlit as st
import pandas as pd
import plotly.express as px

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

    try:
        df = pd.read_csv('player_stats.csv')

        df = df.dropna(subset=['WEEK'])
        df['WEEK'] = df['WEEK'].astype(int)

        weeks = sorted(df['WEEK'].unique())

        st.subheader("🍁 Fall 2023 Season 🍁")

        # TEAM STATISTICS
        team_columns = df.filter(like='TEAM', axis=1).columns.tolist()
        additional_columns = ['GAME', 'RESULT', 'LA CLAMS SCORE', 'OPPONENT SCORE', 'TOTAL PLAYS', 'TOTAL OFFENSIVE PLAYS', 'TOTAL DEFENSIVE PLAYS', '% ON OFFENSE']
        columns_to_display = additional_columns + team_columns
        filtered_df = df[columns_to_display]
        st.subheader(f"Team Statistics")
        filtered_df.index = range(1, len(df) + 1)

        # Transpose the dataframe and reset its index for display
        transposed_df = filtered_df.head(1).transpose().reset_index()
        transposed_df.columns = ["Statistic", "Value"]

        # Remove the word 'TEAM' and convert to title case
        transposed_df['Statistic'] = transposed_df['Statistic'].str.replace('TEAM ', '', case=False).str.title()

        # Round float values in 'Value' column to 1 decimal place
        transposed_df['Value'] = transposed_df['Value'].apply(lambda x: round(x, 1) if isinstance(x, float) else x)

        st.table(transposed_df)

        # PLAYER STATISTICS
        st.subheader("Player Statistics")
        selected_week_player = st.selectbox("Select Week for Player Stats", weeks, index=weeks.index(1) if 1 in weeks else 0)
        players = ["All"] + sorted(df['PLAYER'].unique())
        selected_player = st.selectbox("Select Player", players)

        if selected_player == "All":
            # If "All" is selected, remove columns with "TEAM" in the name
            df = df.drop(columns=team_columns)
            df = df.drop(columns=['NUMBER', 'LA CLAMS SCORE', 'OPPONENT SCORE', 'TOTAL OFFENSIVE PLAYS', 'TOTAL DEFENSIVE PLAYS', 'TOTAL PLAYS', '% ON OFFENSE'])

        
        else:
            df = df[df['PLAYER'] == selected_player]

            relevant_stats_offensive = {
                'QB': ['PLAYER', 'POSITION (OFF)', 'POSITION (DEF)', 'COMPLETED PASSES', 'ATTEMPTED PASSES', 'COMPLETION %', 'PASSING YARDS', 'PASSING TDs', 'INT (OFFENSE)', 'SACKS (ON OFFENSE)', 'CONVERSION POINTS (PASSER)', 'PENALTIES WHILE ON FIELD', 'SUCCESSFUL OFFENSIVE PLAYS', 'OFFENSIVE PLAYS ON FIELD', 'SUCCESSFUL OFFENSIVE %'],
                'RB': ['PLAYER', 'POSITION (OFF)', 'POSITION (DEF)', 'CARRIES', 'RUSHING YARDS', 'RUSHING TDs', 'RECEPTIONS', 'RECEIVING YARDS', 'LONGEST RUSHING TD', 'LONGEST RECEIVING TD', 'LONGEST RUSH', 'AVERAGE RUSH', 'AVERAGE RECEIVING YARDS', 'TOTAL TDs', 'CONVERSION POINTS (RECEIVER)', 'CONVERSION POINTS (RUSHER)', 'SUCCESSFUL OFFENSIVE PLAYS', 'OFFENSIVE PLAYS ON FIELD', 'SUCCESSFUL OFFENSIVE %', 'PENALTIES WHILE ON FIELD'],
                'WR': ['PLAYER', 'POSITION (OFF)', 'POSITION (DEF)', 'CARRIES', 'RUSHING YARDS', 'RUSHING TDs', 'RECEPTIONS', 'RECEIVING YARDS', 'LONGEST RUSHING TD', 'LONGEST RECEIVING TD', 'LONGEST RUSH', 'AVERAGE RUSH', 'AVERAGE RECEIVING YARDS', 'TOTAL TDs', 'CONVERSION POINTS (RECEIVER)', 'CONVERSION POINTS (RUSHER)', 'SUCCESSFUL OFFENSIVE PLAYS', 'OFFENSIVE PLAYS ON FIELD', 'SUCCESSFUL OFFENSIVE %', 'PENALTIES WHILE ON FIELD'],
                'TE': ['PLAYER', 'POSITION (OFF)', 'POSITION (DEF)', 'CARRIES', 'RUSHING YARDS', 'RUSHING TDs', 'RECEPTIONS', 'RECEIVING YARDS', 'LONGEST RUSHING TD', 'LONGEST RECEIVING TD', 'LONGEST RUSH', 'AVERAGE RUSH', 'AVERAGE RECEIVING YARDS', 'TOTAL TDs', 'CONVERSION POINTS (RECEIVER)', 'CONVERSION POINTS (RUSHER)', 'SUCCESSFUL OFFENSIVE PLAYS', 'OFFENSIVE PLAYS ON FIELD', 'SUCCESSFUL OFFENSIVE %', 'PENALTIES WHILE ON FIELD'],
                'C': ['PLAYER', 'POSITION (OFF)', 'POSITION (DEF)', 'CARRIES', 'RUSHING YARDS', 'RUSHING TDs', 'RECEPTIONS', 'RECEIVING YARDS', 'LONGEST RUSHING TD', 'LONGEST RECEIVING TD', 'LONGEST RUSH', 'AVERAGE RUSH', 'AVERAGE RECEIVING YARDS', 'TOTAL TDs', 'CONVERSION POINTS (RECEIVER)', 'CONVERSION POINTS (RUSHER)', 'SUCCESSFUL OFFENSIVE PLAYS', 'OFFENSIVE PLAYS ON FIELD', 'SUCCESSFUL OFFENSIVE %', 'PENALTIES WHILE ON FIELD']
            }
            
            relevant_stats_defensive = {
                'PR': ['FLAGS PULLED', 'SACKS (ON DEF)', 'INT (DEFENSE)', 'DEFENSIVE STOPS', 'DEFENSIVE PLAYS ON FIELD', 'SUCCESSFUL DEFENSIVE %', 'PASS DEFLECTIONS', 'INT RETURN YARDS'],
                'S': ['FLAGS PULLED', 'SACKS (ON DEF)', 'INT (DEFENSE)', 'DEFENSIVE STOPS', 'DEFENSIVE PLAYS ON FIELD', 'SUCCESSFUL DEFENSIVE %', 'PASS DEFLECTIONS', 'INT RETURN YARDS'],
                'CB': ['FLAGS PULLED', 'SACKS (ON DEF)', 'INT (DEFENSE)', 'DEFENSIVE STOPS', 'DEFENSIVE PLAYS ON FIELD', 'SUCCESSFUL DEFENSIVE %', 'PASS DEFLECTIONS', 'INT RETURN YARDS']
            }

            off_position = df['POSITION (OFF)'].iloc[0]
            def_position = df['POSITION (DEF)'].iloc[0]
            
            relevant_columns = ['WEEK']
            if off_position in relevant_stats_offensive:
                relevant_columns.extend(relevant_stats_offensive[off_position])
            if def_position in relevant_stats_defensive:
                relevant_columns.extend(relevant_stats_defensive[def_position])

            df = df[relevant_columns]

        st.write(df[df['WEEK'] == selected_week_player])

        # # For stat variation of a specific player
        # st.subheader("Player Statistics Variation Over Weeks")

        # # Dropdown to select a player
        # players = sorted(df['PLAYER'].unique())
        # selected_player = st.selectbox("Select Player for Stat Variation", players)

        # # Exclude unwanted columns for this section
        # excluded_columns = ['GAME', 'WEEK', 'PLAYER', 'POSITION (OFF)', 'POSITION (DEF)', 'RESULT', 'LA CLAMS SCORE', 'OPPONENT SCORE', 'TOTAL OFFENSIVE PLAYS', 'TOTAL DEFENSIVE PLAYS', 'TOTAL PLAYS', '% ON OFFENSE'] + team_columns
        # stats_columns = [col for col in df.columns if col not in excluded_columns]

        # # Dropdown to select a stat
        # selected_stat = st.selectbox("Select Stat for Variation", stats_columns)

        # # Filter dataframe based on selected player and plot the selected stat
        # player_df = df[df['PLAYER'] == selected_player]
        # fig = px.line(player_df, x='WEEK', y=selected_stat, title=f'{selected_stat} week-by-week for {selected_player}')
        # fig.update_yaxes(rangemode="tozero")
        # fig.update_xaxes(rangemode="tozero")
        # st.plotly_chart(fig)


    except FileNotFoundError:
        st.write("No stats available at the moment. Please add player stats via the Admin page.")

if __name__ == "__main__":
    main()
