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


############################## MODELS & STREAMLIT CONFIGURATION ##############################

# Function to load a model using pickle
def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

# Load models
model_with_weather = load_model("./finalized_model_with_weather (1).sav")
model_without_weather = load_model("./finalized_model_without_weather.sav")

# Configure Streamlit page
st.set_page_config(
    page_title="Stadium Attendance Prediction",  # Title of the app
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
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #1dd1a1, #5f27cd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_away_teams = available_home_teams

# Fix competition to Super League (no dropdown shown to the user)
competition = "Super League"

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
    'FC

