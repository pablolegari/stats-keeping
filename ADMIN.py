import streamlit as st
import pandas as pd

st.title("Admin Page: Add Player Stats")

# Load the CSV into a DataFrame
df = pd.read_csv('player_stats.csv')

# Input fields for common attributes
st.subheader("Set Game Details")
game = st.selectbox("Game:", ["LA Clams vs. Green Gay Packers"])
week = st.number_input("Week:", min_value=1, max_value=12)
playoffs = st.selectbox("Playoffs", ["Y", "N"])
result = st.selectbox("Result:", ["W", "L"])
clams_score = st.number_input("LA Clams Score", min_value=0)
opp_score = st.number_input("Opponent Score", min_value=0)
# @TODO
# total_off_plays = st.number_input("Total Offensive Plays", min_value=0)
# total_def_plays = st.number_input("Total Defensive Plays", min_value=0)


st.subheader("Player Stats")
# Dropdown for selecting a player
players = df[['PLAYER', 'NUMBER']].drop_duplicates().values.tolist()
selected_player = st.selectbox("Select Player", players, format_func=lambda x: f"{x[0]} - {x[1]}")

# Input fields for other columns
off_position = st.selectbox("Select offensive position:", ['QB', 'RB', 'TE', 'WR', 'C', 'N/A'])
def_position = st.selectbox("Select defensive position:", ["CB", "PR", "S", "N/A"])
tds = st.number_input("TDs:", min_value=0)
completions = st.number_input("Completed Passes:", min_value=0)
attempts = st.number_input("Attempted Passes:", min_value=0)
completion_pct = (completions / attempts) * 100 if attempts > 0 else 0
passing_yrds = st.number_input("Passing Yards:", min_value=0)
passing_tds = st.number_input("Passing TDs", min_value=0)
rushing_tds = st.number_input("Rushing TDs", min_value=0)
interceptions = st.number_input("Interceptions", min_value=0)
longest_td = st.number_input("Longest TD", min_value=0)
sacks_off = st.number_input("Sacks (on offense)", min_value=0)
carries = st.number_input("Carries", min_value=0)
rushing_yrds = st.number_input("Rushing Yards", min_value=0)
longest_rush = st.number_input("Longest Rush", min_value=0)
avg_rush = (rushing_yrds/carries)*100 if carries > 0 else 0
receptions = st.number_input("Number of Receptions", min_value=0)
receiving_yrds = st.number_input("Receiving Yards", min_value=0)
avg_receiving_yrds = (receiving_yrds/receptions)*100 if receptions > 0 else 0
flags_pulled = st.number_input("Number of Flags Pulled", min_value=0)
sacks_def = st.number_input("Sacks (on defense)", min_value=0)
conversion_points = st.number_input("Conversion Points", min_value=0)
total_points = (tds*6) + conversion_points
successful_def = st.number_input("Successful Defensive Plays", min_value=0)
int_yards = st.number_input("INT Yards", min_value=0)


# On submit button click, update the CSV
if st.button("Submit"):
    new_data = {
        'PLAYER': selected_player[0],
        'NUMBER': selected_player[1],
        'POSITION (OFF)': off_position,
        'POSITION (DEF)': def_position,
        'GAME': game,
        'WEEK': week,
        'RESULT': result,
        'COMPLETED PASSES': completions,
        'ATTEMPTED PASSES': attempts,
        'COMPLETION %': completion_pct,
        'PASSING YARDS': passing_yrds,
        'PASSING TDs': passing_tds,
        'RUSHING TDs': rushing_tds,
        'INT': interceptions,
        'LONGEST TD': longest_td,
        'SACKS (ON OFFENSE)': sacks_off,
        'CARRIES': carries,
        'RUSHING YARDS': rushing_yrds,
        'LONGEST RUSH': longest_rush,
        'AVERAGE RUSH': avg_rush,
        'RECEPTIONS': receptions,
        'RECEIVING YARDS': receiving_yrds,
        'AVERAGE RECEIVING YARDS': avg_receiving_yrds,
        'TOTAL TDs': tds,
        'FLAGS PULLED': flags_pulled,
        'SACKS (ON DEF)': sacks_def,
        'SUCCESSFUL DEFENSIVE PLAYS': successful_def,
        'TOTAL POINTS': total_points,
        'CONVERSION POINTS': conversion_points,
        'INT YARDS': int_yards
    }

    # Append the new data and save
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv('player_stats.csv', index=False)
    st.success(f"Stats for {selected_player[0]} added successfully!")