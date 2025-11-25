import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests
import datetime
import matplotlib
import matplotlib.pyplot as plt
import base64
import io
from pathlib import Path


############################## MODELS & STREAMLIT CONFIGURATION ##############################

# Function to load a model using pickle
def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

# Resolve paths relative to this file (App/app_football.py)
APP_DIR = Path(__file__).resolve().parent       # App/ folder
BASE_DIR = APP_DIR.parent                       # project root
MODELS_DIR = BASE_DIR / "Models"

# Load models
model_with_weather = load_model(MODELS_DIR / "finalized_model_with_weather (3).sav")
model_without_weather = load_model(MODELS_DIR / "finalized_model_without_weather (3).sav")

# Configure Streamlit page
st.set_page_config(
    page_title="Stadium Attendance Prediction For the Jupiler Pro League",  # Title of the app
    page_icon="🏟️",  # Icon for the app
    layout="wide"  # Use the entire width of the page
)


############################## CUSTOM STYLING (CSS) ##############################

# Add custom CSS for consistent and modern design
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
    }
    .stApp {
        background-color: #ffffff;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }
    [data-testid="stHeader"] {
        background-color: #ffffff;
    }

    .multicolor-title {
    text-align: center;
    font-size: 48px;
    font-weight: 800;
    margin-top: -60px;

    /* force black title (even in dark mode) */
    color: #000000 !important;
    background: none !important;
    -webkit-background-clip: initial !important;
    -webkit-text-fill-color: #000000 !important;

    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.12);
}


    .section-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin: 12px 0 24px 0;
    }
    
    .stSelectbox, .stSlider, .stRadio, .stExpander {
        margin-top: 10px;
        border-radius: 12px;
        background-color: #ffffff;
        padding: 14px 22px;
        font-size: 16px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    .stExpander details {
        border-color: #ffffff;
    }

    .stDateInput, .stTimeInput {
        margin-top: 5px;
        border-radius: 12px;
        background-color: #ffffff;
        padding: 14px 22px;
        font-size: 16px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    .stButton>button {
        background-color: #003366;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 12px 30px;
        border-radius: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: none;
        cursor: pointer;
        margin-bottom: 20px;
    }

    .stButton>button:hover {
        background-color: #0066cc;
        color: white;
        transition: all 0.3s ease;
    }

    /* force ALL widget labels to black (dark mode included) */
label,
[data-testid="stWidgetLabel"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label,
[data-testid="stDateInput"] label,
[data-testid="stTimeInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: #000000 !important;
}

/* force general text (markdown, captions, etc.) to black */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
.stMarkdown,
.stMarkdown p,
.stMarkdown span {
    color: #000000 !important;
}

    
    </style>
""", unsafe_allow_html=True)


############################## APP HEADER ##############################

# Display the app's main title and description
st.markdown("""
    <h1 class="multicolor-title">🏟️ Stadium Attendance Prediction App</h1>
    <div style="text-align: center; padding: 7px; padding-top:20px; background-color: #ffffff; border-radius: 15px; 
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom:20px">
        <p style="font-size: 20px; color: #555555;">🎉⚽ This app predicts stadium attendance based on various factors 
        such as the teams playing, weather conditions, and matchday info. Use the inputs below to get the prediction!</p>
    </div>
""", unsafe_allow_html=True)


############################## INPUT FIELDS ##############################

# Define available teams
available_home_teams = ["Club Brugge", "Cercle Brugge", "Genk", "RSC Anderlecht", "Union SG", "KAA Gent", "Royal Antwerp", "KVC Westerlo", "Standard Liège", "KV Mechelen", "R Charleroi SC", "OH Leuven", "Sint-Truiden", "FCV Dender EH", "Zulte Waregem", "La Louvière"]
available_away_teams = available_home_teams

# Fix competition to Super League (no dropdown shown to the user)
competition = "Jupiler Super League"

# Card-style container for match setup
st.markdown(
    """
    <div class="section-card">
        <h3 style="margin-bottom:0.5rem; color:#003366;">Match setup</h3>
        <p style="margin-top:0.2rem; font-size:14px; color:#777777;">
            Choose the home and away team, then set the matchday, date and kickoff time.
        </p>
    """,
    unsafe_allow_html=True,
)

# First row: teams
teams_col1, teams_col2 = st.columns([1.3, 1])
with teams_col1:
    home_team = st.selectbox("🏠 Home Team", available_home_teams)
with teams_col2:
    available_away_teams_dynamic = [team for team in available_home_teams if team != home_team]
    away_team = st.selectbox("🌍 Away Team", available_away_teams_dynamic)

# Second row: matchday, date & time
row2_col1, row2_col2 = st.columns([1, 1])
with row2_col1:
    matchday = st.slider("📅 Matchday", min_value=1, max_value=36, step=1)
with row2_col2:
    match_date = st.date_input(
        "📅 Match Date",
        min_value=datetime.date.today(),
        key="match_date_input",
    )
    match_time = st.time_input(
        "🕒 Match Time",
        value=datetime.time(15, 30),
        help="Select the match time in HH:MM format",
        key="match_time_input",
    )
    match_hour = match_time.hour
    weekday = match_date.strftime("%A")

# Close the card container
st.markdown("</div>", unsafe_allow_html=True)


############################## WEATHER DATA ##############################

# Function to fetch weather data from an API
def get_weather_data(latitude, longitude, match_date, match_hour):
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&start_date={match_date}&end_date={match_date}"
        f"&hourly=temperature_2m,weathercode"
        f"&timezone=auto"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        weather_data = response.json()
        hourly_data = weather_data['hourly']
        temperature_at_match = hourly_data['temperature_2m'][match_hour]
        weather_code_at_match = hourly_data['weathercode'][match_hour]
        # Map weather codes to human-readable conditions
        if weather_code_at_match in [0]:
            weather_condition = "Clear or mostly clear"
        elif weather_code_at_match in [1, 2, 3]:
            weather_condition = "Partly cloudy"
        elif weather_code_at_match in [61, 63, 65, 80, 81, 82]:
            weather_condition = "Rainy"
        elif weather_code_at_match in [51, 53, 55]:
            weather_condition = "Drizzle"
        elif weather_code_at_match in [71, 73, 75, 85, 86, 77]:
            weather_condition = "Snowy"
        else:
            weather_condition = "Unknown"

        return temperature_at_match, weather_condition
    except:
        return None, None

# Define stadium coordinates
stadium_coordinates = {
    "Club Brugge": {"lat": 51.19333, "lon": 3.18056},
    "Cercle Brugge": {"lat": 51.19333, "lon": 3.18056},
    "Genk": {"lat": 51.00500, "lon": 5.53333},
    "RSC Anderlecht": {"lat": 50.83417, "lon": 4.29833},
    "Union SG": {"lat": 50.81733, "lon": 4.32417},
    "KAA Gent": {"lat": 51.01611, "lon": 3.73417},
    "Royal Antwerp": {"lat": 51.22500, "lon": 4.46992},
    "KVC Westerlo": {"lat": 51.09482, "lon": 4.92881},
    "Standard Liège": {"lat": 50.60597, "lon": 5.53934},
    "KV Mechelen": {"lat": 51.03718, "lon": 4.48640},
    "R Charleroi SC": {"lat": 50.41461, "lon": 4.45379},
    "OH Leuven": {"lat": 50.86833, "lon": 4.69417},
    "Sint-Truiden": {"lat": 50.81347, "lon": 5.16626},
    "FCV Dender EH": {"lat": 50.88368, "lon": 4.07118},
    "Zulte Waregem": {"lat": 50.88306, "lon": 3.42889},
    "La Louvière": {"lat": 50.47750, "lon": 4.20131}
}

# Fetch weather data based on home team and match information
if home_team and match_date and match_time:
    coordinates = stadium_coordinates[home_team]
    latitude = coordinates['lat']
    longitude = coordinates['lon']
    temperature_at_match, weather_condition = get_weather_data(latitude, longitude, match_date, match_hour)

# Weather display and emoji mapping logic
def get_weather_emoji(weather_condition):
    weather_emoji = {
        "Clear or mostly clear": "☀️", 
        "Partly cloudy": "⛅", 
        "Rainy": "🌧️", 
        "Drizzle": "🌦️", 
        "Snowy": "❄️",  
        "Unknown": "🌫️",  
    }
    return weather_emoji.get(weather_condition, "🌫️")

# Display weather data in a styled container
if 'temperature_at_match' in locals() and temperature_at_match is not None and weather_condition is not None and weather_condition != "Unknown":
    weather_emoji = get_weather_emoji(weather_condition)
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom:25px; margin-top:10px">
            <h3 style="color: #003366;">Weather at the Match</h3>
            <p style="font-size: 18px; color: #333333;">
                The weather at the match will be <strong style="color: #007bff;">{weather_condition} {weather_emoji}</strong> 
                with a temperature of <strong style="color: #007bff;">{temperature_at_match}°C</strong> 🌡.
            </p>
        </div>
    """, unsafe_allow_html=True)
elif 'temperature_at_match' in locals() and temperature_at_match is not None:
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom:25px; margin-top:10px">
            <h3 style="color: #003366;">Weather at the Match</h3>
            <p style="font-size: 18px; color: #333333;">
                The temperature at the match will be <strong style="color: #007bff;">{temperature_at_match}°C</strong> 🌡.
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom:25px; margin-top:10px">
            <h3 style="color: #003366;">Weather at the Match</h3>
            <p style="font-size: 18px; color: #333333;">
                Unfortunately, the weather data is unavailable at the moment. 😞
            </p>
        </div>
    """, unsafe_allow_html=True)


################### Rankings and Team Data Processing ##############################

# user inputs for rankings and last 5 games (home + away)
form_col1, form_col2 = st.columns(2)

with form_col1:
    ranking_home_team = st.number_input(
        "Home team ranking (current league position)",
        min_value=1,
        max_value=20,
        value=5,
    )
    goals_scored_home_last5 = st.number_input(
        "Home team – goals scored in last 5 games",
        min_value=0,
        max_value=50,
        value=6,
    )
    goals_conceded_home_last5 = st.number_input(
        "Home team – goals conceded in last 5 games",
        min_value=0,
        max_value=50,
        value=5,
    )
    wins_home_last5 = st.number_input(
        "Home team – wins in last 5 games (last 5)",
        min_value=0,
        max_value=5,
        value=3,
    )

with form_col2:
    ranking_away_team = st.number_input(
        "Away team ranking (current league position)",
        min_value=1,
        max_value=20,
        value=8,
    )
    goals_scored_away_last5 = st.number_input(
        "Away team – goals scored in last 5 games",
        min_value=0,
        max_value=50,
        value=5,
    )


# Define team-specific data, including stadium capacity and attendance thresholds
team_data = {
    "Club Brugge": {
        "max_capacity": 29062,
        "attendance_30th_percentile": 19951.5,
        "attendance_70th_percentile": 24402.5,
    },
    "FCV Dender EH": {
        "max_capacity": 6200,
        "attendance_30th_percentile": 2459.4,
        "attendance_70th_percentile": 3561.5,
    },
    "Genk": {
        "max_capacity": 23500,
        "attendance_30th_percentile": 14907.0,
        "attendance_70th_percentile": 18352.6,
    },
    "KAA Gent": {
        "max_capacity": 20000,
        "attendance_30th_percentile": 12570.6,
        "attendance_70th_percentile": 16882.8,
    },
    "KV Mechelen": {
        "max_capacity": 16500,
        "attendance_30th_percentile": 11229.2,
        "attendance_70th_percentile": 14486.0,
    },
    "KVC Westerlo": {
        "max_capacity": 8000,
        "attendance_30th_percentile": 4848.3,
        "attendance_70th_percentile": 6133.9,
    },
    "OH Leuven": {
        "max_capacity": 10500,
        "attendance_30th_percentile": 5482.1,
        "attendance_70th_percentile": 7002.4,
    },
    "R Charleroi SC": {
        "max_capacity": 15000,
        "attendance_30th_percentile": 6000.0,
        "attendance_70th_percentile": 8533.0,
    },
    "RSC Anderlecht": {
        "max_capacity": 22500,
        "attendance_30th_percentile": 18000.0,
        "attendance_70th_percentile": 20100.0,
    },
    "Royal Antwerp": {
        "max_capacity": 16644,
        "attendance_30th_percentile": 12000.0,
        "attendance_70th_percentile": 14941.4,
    },
    "Sint-Truiden": {
        "max_capacity": 14600,
        "attendance_30th_percentile": 4345.0,
        "attendance_70th_percentile": 6000.0,
    },
    "Standard Liège": {
        "max_capacity": 27670,
        "attendance_30th_percentile": 16623.0,
        "attendance_70th_percentile": 21113.0,
    },
    "Union SG": {
        "max_capacity": 9400,
        "attendance_30th_percentile": 6173.4,
        "attendance_70th_percentile": 7256.0,
    },
    "Zulte Waregem": {
        "max_capacity": 12400,
        "attendance_30th_percentile": 6626.6,
        "attendance_70th_percentile": 7953.5,
    },
}


# --- stadium features for the model (uses your team_data dict) ---
home_team_info = team_data.get(home_team)
max_capacity_feature = home_team_info["max_capacity"] if home_team_info else 0

# mark which stadiums have (mostly) a full roof – adjust if needed
full_roof_map = {
    "Club Brugge": 0,
    "Cercle Brugge": 0,
    "Genk": 0,
    "RSC Anderlecht": 1,
    "Union SG": 0,
    "KAA Gent": 0,
    "Royal Antwerp": 0,
    "KVC Westerlo": 0,
    "Standard Liège": 0,
    "KV Mechelen": 0,
    "R Charleroi SC": 0,
    "OH Leuven": 0,
    "Sint-Truiden": 0,
    "FCV Dender EH": 0,
    "Zulte Waregem": 0,
    "La Louvière": 0,
}
full_roof_feature = float(full_roof_map.get(home_team, 0))

# --- simple derby flag between specific pairs ---
derby_pairs = {
    ("Club Brugge", "Cercle Brugge"),
    ("RSC Anderlecht", "Union SG"),
    # add more if you want
}

is_derby = int(
    (home_team, away_team) in derby_pairs
    or (away_team, home_team) in derby_pairs
)

# --- team categories from ranking (for the Home/Opposing team Category_* dummies) ---
def categorize_team(r):
    if r is None:
        return "Unknown"
    try:
        r = int(r)
    except ValueError:
        return "Unknown"

    if r <= 4:
        return "Top ranked"
    elif r <= 8:
        return "Medium ranked"
    elif r <= 16:
        return "Bottom ranked"
    else:
        return "Not ranked"

home_team_category = categorize_team(ranking_home_team)
opposing_team_category = categorize_team(ranking_away_team)

# --- game day (Weekday / Weekend) for Game day_* dummies ---
game_day = "Weekend" if match_date.weekday() >= 5 else "Weekday"

# --- time slot (Afternoon / Evening / Night) for Time slot_* dummies ---
if 12 <= match_hour < 17:
    time_slot = "Afternoon"
elif 17 <= match_hour < 22:
    time_slot = "Evening"
else:
    time_slot = "Night"

# --- Weather GoodBad (Good / Bad) based on your rule ---
good_conditions = ["Clear or mostly clear", "Partly cloudy"]
bad_conditions = ["Rainy", "Drizzle", "Snowy"]

if 'weather_condition' in locals() and weather_condition is not None:
    if weather_condition in good_conditions:
        weather_goodbad = "Good"
    elif weather_condition in bad_conditions:
        weather_goodbad = "Bad"
    else:
        weather_goodbad = "Good"  # neutral default, can set to "Bad" if you prefer
else:
    weather_goodbad = "Good"


################### Preparing Input Data for the Model ##############################

# Define the input features for the prediction model
input_features = {
    # basic match info
    'Matchday': matchday,
    'Time': match_hour,
    'Home Team': home_team,
    'Away Team': away_team,
    'Weekday': match_date.strftime("%A"),
    'Month': match_date.month,
    'Day': match_date.day,

    # rankings
    'Ranking Home Team': float(ranking_home_team),
    'Ranking Away Team': float(ranking_away_team),

    # recent form – home team, as in your training set
    'Goals Scored in Last 5 Games': float(goals_scored_home_last5),
    'Goals Conceded in Last 5 Games': float(goals_conceded_home_last5),
    'Number of Wins in Last 5 Games': float(wins_home_last5),

    # map last-5 goals into these features (so nothing stays at 0)
    'Home Team Goals Scored': float(goals_scored_home_last5),
    'Away Team Goals Scored': float(goals_scored_away_last5),

    # weather (raw condition + numeric temperature)
    'Weather': weather_condition if 'weather_condition' in locals() else 'Unknown',
    'Temperature (°C)': float(temperature_at_match) if 'temperature_at_match' in locals() and temperature_at_match is not None else 0.0,

    # stadium features
    'Derby': float(is_derby),
    'Max Capacity': float(max_capacity_feature),
    'Full Roof': float(full_roof_feature),

    # macro features – keep neutral for now unless you add extra inputs
    'GDP_Real_lagQ': 0.0,
    'CPI_QoQ_Growth_%_lagQ': 0.0,
    'Employment_Rate_%_lagQ': 0.0,

    # extra categorical vars for dummies
    'Home team Category': home_team_category,
    'Opposing team Category': opposing_team_category,
    'Game day': game_day,
    'Time slot': time_slot,
    'Weather GoodBad': weather_goodbad,
}

# Convert the input features into a DataFrame
input_df = pd.DataFrame([input_features])

# List of expected columns for the model
# List of expected columns for the models
expected_columns_with_weather = [
    'match_id',
    'Time',
    'Ranking Home Team',
    'Ranking Away Team',
    'Temperature (°C)',
    'Month',
    'Day',
    'Derby',
    'Max Capacity',
    'Full Roof',
    'GDP_Real_lagQ',
    'CPI_QoQ_Growth_%_lagQ',
    'Employment_Rate_%_lagQ',
    'Home Team Goals Scored',
    'Away Team Goals Scored',
    'Goals Scored in Last 5 Games',
    'Goals Conceded in Last 5 Games',
    'Number of Wins in Last 5 Games',
    'Matchday_10',
    'Matchday_11',
    'Matchday_12',
    'Matchday_13',
    'Matchday_14',
    'Matchday_15',
    'Matchday_16',
    'Matchday_17',
    'Matchday_18',
    'Matchday_19',
    'Matchday_2',
    'Matchday_20',
    'Matchday_21',
    'Matchday_22',
    'Matchday_23',
    'Matchday_24',
    'Matchday_25',
    'Matchday_26',
    'Matchday_27',
    'Matchday_28',
    'Matchday_29',
    'Matchday_3',
    'Matchday_30',
    'Matchday_31',
    'Matchday_32',
    'Matchday_33',
    'Matchday_34',
    'Matchday_3rd round 1st leg',
    'Matchday_3rd round 2nd leg',
    'Matchday_4',
    'Matchday_5',
    'Matchday_6',
    'Matchday_7',
    'Matchday_8',
    'Matchday_9',
    'Matchday_Final',
    'Matchday_Group A',
    'Matchday_Group B',
    'Matchday_Group D',
    'Matchday_Group E',
    'Matchday_Group F',
    'Matchday_Group H',
    'Matchday_Group Stage',
    'Matchday_Qualifying Round 1st leg',
    'Matchday_Qualifying Round 2nd leg',
    'Matchday_Quarter-Finals',
    'Matchday_Quarter-Finals 1st leg',
    'Matchday_Quarter-Finals 2nd leg',
    'Matchday_Round of 16',
    'Matchday_Second Round 1st leg',
    'Matchday_Second Round 2nd leg',
    'Matchday_Semi-Finals 1st Leg',
    'Matchday_Semi-Finals 2nd Leg',
    'Matchday_Seventh Round',
    'Matchday_Sixth Round',
    'Matchday_final 2nd leg',
    'Matchday_group I',
    'Matchday_intermediate stage 1st leg',
    'Matchday_intermediate stage 2nd leg',
    'Matchday_last 16 1st leg',
    'Matchday_last 16 2nd leg',
    'Home Team_Club Brugge',
    'Home Team_FCV Dender EH',
    'Home Team_Genk',
    'Home Team_KAA Gent',
    'Home Team_KV Mechelen',
    'Home Team_KVC Westerlo',
    'Home Team_La Louvière',
    'Home Team_OH Leuven',
    'Home Team_R Charleroi SC',
    'Home Team_RSC Anderlecht',
    'Home Team_Royal Antwerp',
    'Home Team_Sint-Truiden',
    'Home Team_Standard Liège',
    'Home Team_Union SG',
    'Home Team_Zulte Waregem',
    'Away Team_Club Brugge',
    'Away Team_FCV Dender EH',
    'Away Team_Genk',
    'Away Team_KAA Gent',
    'Away Team_KV Mechelen',
    'Away Team_KVC Westerlo',
    'Away Team_La Louvière',
    'Away Team_OH Leuven',
    'Away Team_R Charleroi SC',
    'Away Team_RSC Anderlecht',
    'Away Team_Royal Antwerp',
    'Away Team_Sint-Truiden',
    'Away Team_Standard Liège',
    'Away Team_Union SG',
    'Away Team_Unknown',
    'Away Team_Zulte Waregem',
    'Weekday_Monday',
    'Weekday_Saturday',
    'Weekday_Sunday',
    'Weekday_Thursday',
    'Weekday_Tuesday',
    'Weekday_Wednesday',
    'Opposing team Category_Bottom ranked',
    'Opposing team Category_Medium ranked',
    'Opposing team Category_Not ranked',
    'Opposing team Category_Top ranked',
    'Opposing team Category_Unknown',
    'Home team Category_Bottom ranked',
    'Home team Category_Medium ranked',
    'Home team Category_Not ranked',
    'Home team Category_Top ranked',
    'Home team Category_Unknown',
    'Game day_Weekday',
    'Game day_Weekend',
    'Time slot_Afternoon',
    'Time slot_Evening',
    'Time slot_Night',
    'Weather GoodBad_Bad',
    'Weather GoodBad_Good',
    'Weather_Clear or mostly clear',
    'Weather_Drizzle',
    'Weather_Partly cloudy',
    'Weather_Rainy',
    'Weather_Snowy',
]

expected_columns_without_weather = [
    'match_id',
    'Time',
    'Ranking Home Team',
    'Ranking Away Team',
    'Temperature (°C)',
    'Month',
    'Day',
    'Derby',
    'Max Capacity',
    'Full Roof',
    'GDP_Real_lagQ',
    'CPI_QoQ_Growth_%_lagQ',
    'Employment_Rate_%_lagQ',
    'Home Team Goals Scored',
    'Away Team Goals Scored',
    'Goals Scored in Last 5 Games',
    'Goals Conceded in Last 5 Games',
    'Number of Wins in Last 5 Games',
    'Matchday_10',
    'Matchday_11',
    'Matchday_12',
    'Matchday_13',
    'Matchday_14',
    'Matchday_15',
    'Matchday_16',
    'Matchday_17',
    'Matchday_18',
    'Matchday_19',
    'Matchday_2',
    'Matchday_20',
    'Matchday_21',
    'Matchday_22',
    'Matchday_23',
    'Matchday_24',
    'Matchday_25',
    'Matchday_26',
    'Matchday_27',
    'Matchday_28',
    'Matchday_29',
    'Matchday_3',
    'Matchday_30',
    'Matchday_31',
    'Matchday_32',
    'Matchday_33',
    'Matchday_34',
    'Matchday_3rd round 1st leg',
    'Matchday_3rd round 2nd leg',
    'Matchday_4',
    'Matchday_5',
    'Matchday_6',
    'Matchday_7',
    'Matchday_8',
    'Matchday_9',
    'Matchday_Final',
    'Matchday_Group A',
    'Matchday_Group B',
    'Matchday_Group D',
    'Matchday_Group E',
    'Matchday_Group F',
    'Matchday_Group H',
    'Matchday_Group Stage',
    'Matchday_Qualifying Round 1st leg',
    'Matchday_Qualifying Round 2nd leg',
    'Matchday_Quarter-Finals',
    'Matchday_Quarter-Finals 1st leg',
    'Matchday_Quarter-Finals 2nd leg',
    'Matchday_Round of 16',
    'Matchday_Second Round 1st leg',
    'Matchday_Second Round 2nd leg',
    'Matchday_Semi-Finals 1st Leg',
    'Matchday_Semi-Finals 2nd Leg',
    'Matchday_Seventh Round',
    'Matchday_Sixth Round',
    'Matchday_final 2nd leg',
    'Matchday_group I',
    'Matchday_intermediate stage 1st leg',
    'Matchday_intermediate stage 2nd leg',
    'Matchday_last 16 1st leg',
    'Matchday_last 16 2nd leg',
    'Home Team_Club Brugge',
    'Home Team_FCV Dender EH',
    'Home Team_Genk',
    'Home Team_KAA Gent',
    'Home Team_KV Mechelen',
    'Home Team_KVC Westerlo',
    'Home Team_La Louvière',
    'Home Team_OH Leuven',
    'Home Team_R Charleroi SC',
    'Home Team_RSC Anderlecht',
    'Home Team_Royal Antwerp',
    'Home Team_Sint-Truiden',
    'Home Team_Standard Liège',
    'Home Team_Union SG',
    'Home Team_Zulte Waregem',
    'Away Team_Club Brugge',
    'Away Team_FCV Dender EH',
    'Away Team_Genk',
    'Away Team_KAA Gent',
    'Away Team_KV Mechelen',
    'Away Team_KVC Westerlo',
    'Away Team_La Louvière',
    'Away Team_OH Leuven',
    'Away Team_R Charleroi SC',
    'Away Team_RSC Anderlecht',
    'Away Team_Royal Antwerp',
    'Away Team_Sint-Truiden',
    'Away Team_Standard Liège',
    'Away Team_Union SG',
    'Away Team_Unknown',
    'Away Team_Zulte Waregem',
    'Weekday_Monday',
    'Weekday_Saturday',
    'Weekday_Sunday',
    'Weekday_Thursday',
    'Weekday_Tuesday',
    'Weekday_Wednesday',
    'Opposing team Category_Bottom ranked',
    'Opposing team Category_Medium ranked',
    'Opposing team Category_Not ranked',
    'Opposing team Category_Top ranked',
    'Opposing team Category_Unknown',
    'Home team Category_Bottom ranked',
    'Home team Category_Medium ranked',
    'Home team Category_Not ranked',
    'Home team Category_Top ranked',
    'Home team Category_Unknown',
    'Game day_Weekday',
    'Game day_Weekend',
    'Time slot_Afternoon',
    'Time slot_Evening',
    'Time slot_Night',
]

# Perform one-hot encoding for categorical columns (we'll only keep what we need afterwards)
categorical_columns = [
    "Matchday",
    "Home Team",
    "Away Team",
    "Weather",
    "Weekday",
    "Home team Category",
    "Opposing team Category",
    "Game day",
    "Time slot",
    "Weather GoodBad",
]


encoded_df = pd.get_dummies(pd.DataFrame([input_features]), columns=categorical_columns, drop_first=False)

# Make sure all expected columns exist (for both models); if missing, fill with 0
all_expected = list(set(expected_columns_with_weather + expected_columns_without_weather))
for col in all_expected:
    if col not in encoded_df.columns:
        encoded_df[col] = 0

# Build the two final DataFrames with the correct column order and dtype
input_df_with_weather = encoded_df[expected_columns_with_weather].astype(float)
input_df_without_weather = encoded_df[expected_columns_without_weather].astype(float)



################### Predicting Attendance ##############################

# Predict attendance when the user clicks the button
if st.button("🎯 Predict Attendance"):

    # 1) Decide if we can reliably use the weather model
    use_weather_model = (
        'temperature_at_match' in locals()
        and temperature_at_match is not None
        and 'weather_condition' in locals()
        and weather_condition is not None
        and weather_condition != "Unknown"
    )

    if use_weather_model:
        prediction = model_with_weather.predict(input_df_with_weather)[0] * 100
        weather_status = "Weather data used for prediction."
    else:
        prediction = model_without_weather.predict(input_df_without_weather)[0] * 100
        weather_status = (
            "Weather data unavailable or unreliable. "
            "Prediction made without weather information."
        )

    # 2) Get stadium info for the home team
    home_team_name = home_team
    team_info = team_data.get(home_team_name, None)

    if not team_info:
        st.error("No stadium information found for this home team.")
        st.info(weather_status)
    else:
        max_capacity = team_info["max_capacity"]
        attendance_30th = team_info["attendance_30th_percentile"]
        attendance_70th = team_info["attendance_70th_percentile"]

        # 3) Convert predicted percentage into absolute attendance
        predicted_attendance = min(
            ((prediction / 100) * max_capacity).round(),
            max_capacity
        )

        if predicted_attendance < attendance_30th:
            attendance_status = "Low attendance 🚶‍♂️"
        elif predicted_attendance > attendance_70th:
            attendance_status = "High attendance 🏟️"
        else:
            attendance_status = "Normal attendance ⚖️"

        st.success(f"Attendance Status: {attendance_status}")

        # 4) Build horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 2.5))
        ax.barh(
            y=[0],
            width=[predicted_attendance / max_capacity],
            height=0.5,
            edgecolor="black",
            alpha=0.8,
        )

        # Threshold lines
        ax.axvline(x=attendance_30th / max_capacity, linestyle="--",
                   label="30th Percentile", linewidth=1.2)
        ax.axvline(x=attendance_70th / max_capacity, linestyle="--",
                   label="70th Percentile", linewidth=1.2)

        # Styling
        fig.patch.set_facecolor("#f8f9fa")
        ax.set_facecolor("#ffffff")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=12)
        ax.set_yticks([])

        ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, -0.4),
            ncol=2,
            fontsize=12,
            frameon=False,
        )

        ax.set_title(
            f"Predicted Attendance: {predicted_attendance:.0f} of {max_capacity} ({prediction:.2f}%)",
            fontsize=14,
            pad=15,
            color="#333333",
        )

        # 5) Render chart in Streamlit
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
        buf.seek(0)
        encoded_image = base64.b64encode(buf.read()).decode("utf-8")

        st.markdown(
            f"""
            <div style="background-color: #f9f9fa; padding: 20px; border-radius: 10px;
                        border: 1px solid #ddd; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h3 style="text-align: center; color: #003366;">Attendance Prediction Details</h3>
                <img src="data:image/png;base64,{encoded_image}" style="display: block; margin: auto;"/>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 6) Show whether weather was used or not
        st.info(weather_status)




