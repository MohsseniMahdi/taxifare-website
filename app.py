import streamlit as st
import requests
import datetime
import pandas as pd

# Streamlit UI
st.title("Taxi Fare Prediction")

# --- Inject CSS for button size ---
st.markdown(
    """
    <style>
    body {
        background-color: #0119ff; /* Change this to your desired color */
    }
    div.stButton > button:first-child {
        background-color: #0099ff;
        color: white;
        width: 200px; /* Adjust width as needed */
        height: 50px; /* Adjust height as needed */
        font-size: 20px; /* Adjust font size as needed */
    }
    </style>""",
    unsafe_allow_html=True,
)
# --- End of CSS injection ---

# Create two columns
col1, col2 = st.columns(2)

# User inputs in Column 1
with col1:
    d = st.date_input("When do you want to go?", value=None)
    t = st.time_input("Set a time for the ride", value=None)
    plong = st.number_input(
        "Insert your pickup longitude",
        value=0.0,
        placeholder="Type a pickup longitude...",
        format="%.6f",  # Set format to 4 decimal places
    )
    plat = st.number_input(
        "Insert your pickup latitude",
        value=0.0,
        placeholder="Type a pickup longitude...",
        format="%.6f",  # Set format to 4 decimal places
    )
    dlong = st.number_input(
        "Insert your dropoff longitude",
        value=0.0,
        placeholder="Type a pickup longitude...",
        format="%.6f",  # Set format to 4 decimal places
    )
    dlat = st.number_input(
        "Insert your dropoff latitude",
        value=0.0,
        placeholder="Type a pickup longitude...",
        format="%.6f",  # Set format to 4 decimal places
    )
    passenger_count = st.number_input(
        "Number of Passengers:", min_value=1, max_value=8, step=1, value=1
    )

# Function to call the API
def predict(
    pickup_datetime: str,
    pickup_longitude: float,
    pickup_latitude: float,
    dropoff_longitude: float,
    dropoff_latitude: float,
    passenger_count: int,
):
    url = "https://taxifare.lewagon.ai/predict"

    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
        "passenger_count": passenger_count,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json().get("fare", "Error: No fare returned")
    else:
        return f"Error: {response.status_code}"


# Convert date and time inputs to a proper datetime string
if d and t:
    pickup_datetime = f"{d} {t}"  # Format: YYYY-MM-DD HH:MM:SS
else:
    pickup_datetime = None

# User inputs in Column 2
with col2:
    # Logo
    st.image("taxi_image.png")
    # Predict button
    if st.button("Predict Fare"):
        if pickup_datetime:
            fare = predict(
                pickup_datetime=pickup_datetime,
                pickup_longitude=plong,
                pickup_latitude=plat,
                dropoff_longitude=dlong,
                dropoff_latitude=dlat,
                passenger_count=passenger_count,
            )
            st.write(f"Your Estimated Fare is: ${fare}")
        else:
            st.write("Please select a valid date and time.")
