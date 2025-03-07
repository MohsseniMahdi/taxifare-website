import streamlit as st
import requests
import datetime
import pandas as pd
import pydeck as pdk

# Mapbox token
MAPBOX_TOKEN = "pk.eyJ1IjoibW9oc3NlbmkiLCJhIjoiY203eW1tNjV2MGFxazJyc2Flbnpjd3k4YiJ9.CkSaCrnkfiA9lhRMRwWYTg"  # Replace with your actual Mapbox token

# Streamlit UI
st.title("Taxi Fare Prediction")

# --- Inject CSS for background color and button style ---
st.markdown(
    """
    <style>
    body {
        background-color: #f0f0f5; /* Change this to your desired color */
    }
    div.stButton > button:first-child {
        background-color: #0099ff;
        color: white;
        width: 200px;
        height: 50px;
        font-size: 20px;
    }
    </style>""",
    unsafe_allow_html=True,
)
# --- End of CSS injection ---

# Create two columns
col1, col2 = st.columns(2)

# Address Autocomplete Function
def get_coordinates_from_address(address):
    """
    Uses Mapbox Geocoding API to get coordinates for a given address.
    """
    if not MAPBOX_TOKEN:
        st.error("Mapbox token not provided. Please add it to the script.")
        return None, None

    geocoding_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {"access_token": MAPBOX_TOKEN}

    try:
        response = requests.get(geocoding_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data["features"]:
            longitude, latitude = data["features"][0]["center"]
            return longitude, latitude
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Error during geocoding: {e}")
        return None, None
    except (KeyError, IndexError):
        st.error("Invalid response from geocoding service.")
        return None, None

# Map Visualization Function
def display_map(pickup_lon=None, pickup_lat=None, dropoff_lon=None, dropoff_lat=None, focus_on_newyork=True):
    """
    Displays a map with pickup and dropoff markers using Pydeck.
    """
    if not MAPBOX_TOKEN:
        st.error("Mapbox token not provided. Please add it to the script.")
        return

    if focus_on_newyork:
        initial_view_state = pdk.ViewState(
            latitude=40.7128,  # New York latitude
            longitude=-74.0060,  # New York longitude
            zoom=10,
            pitch=50,
        )
    elif pickup_lon is not None and pickup_lat is not None and dropoff_lon is not None and dropoff_lat is not None:
        initial_view_state = pdk.ViewState(
            latitude=(pickup_lat + dropoff_lat) / 2,
            longitude=(pickup_lon + dropoff_lon) / 2,
            zoom=11,
            pitch=50,
        )
    else:
        st.error("please inter a valid address")
        return

    layers = []
    if pickup_lon is not None and pickup_lat is not None and dropoff_lon is not None and dropoff_lat is not None:
        data = [
            {"lon": pickup_lon, "lat": pickup_lat, "type": "Pickup"},
            {"lon": dropoff_lon, "lat": dropoff_lat, "type": "Dropoff"},
        ]

        layer = pdk.Layer(
            "ScatterplotLayer",
            data,
            get_position=["lon", "lat"],
            get_color="[200, 30, 0, 160]",
            get_radius=100,
        )
        layers.append(layer)

    tool_tip = {"html": "Location: <b>{type}</b>"}

    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v11",
        initial_view_state=initial_view_state,
        layers=layers,
        tooltip=tool_tip,
        api_keys={"mapbox": MAPBOX_TOKEN},
    )
    return deck

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

# Initialize map in session state
if "map_deck" not in st.session_state:
    st.session_state.map_deck = display_map(focus_on_newyork=True)

# Convert date and time inputs to a proper datetime string
def format_datetime(date, time):
    if date and time:
      return datetime.datetime.combine(date, time).strftime("%Y-%m-%d %H:%M:%S")
    return None

# User inputs in Column 1
with col1:
    d = st.date_input("When do you want to go?", value=None)
    t = st.time_input("Set a time for the ride", value=None)

    pickup_address = st.text_input("Enter Pickup Address:", key="pickup")
    if pickup_address:
        plong, plat = get_coordinates_from_address(pickup_address)
        plong, plat = abs(plong), abs(plat)
        if plong and plat:
            st.write(f"Pickup Coordinates: Longitude: {plong:.6f}, Latitude: {plat:.6f}")
        else:
            plong = None
            plat = None
    else:
      plong = None
      plat = None

    dropoff_address = st.text_input("Enter Dropoff Address:", key="dropoff")
    if dropoff_address:
        dlong, dlat = get_coordinates_from_address(dropoff_address)
        dlong, dlat = abs(dlong), abs(dlat)
        if dlong and dlat:
            st.write(f"Dropoff Coordinates: Longitude: {dlong:.6f}, Latitude: {dlat:.6f}")
        else:
            dlong = None
            dlat = None
    else:
      dlong = None
      dlat = None

    passenger_count = st.number_input(
        "Number of Passengers:", min_value=1, max_value=8, step=1, value=2
    )

# User inputs in Column 2
with col2:
    # Logo
    st.image("taxi_image.png")

    # Display the map
    st.pydeck_chart(st.session_state.map_deck)

    # Predict button
    if st.button("Predict Fare"):
        pickup_datetime=format_datetime(d,t)
        if pickup_datetime and plong and plat and dlong and dlat:
            fare = predict(
                pickup_datetime=pickup_datetime,
                pickup_longitude=plong,
                pickup_latitude=plat,
                dropoff_longitude=dlong,
                dropoff_latitude=dlat,
                passenger_count=passenger_count,
            )
            st.write(f"Your Estimated Fare is: ${fare}")
            st.session_state.map_deck = display_map(plong, plat, dlong, dlat, focus_on_newyork=False)
            #st.experimental_rerun()  # Remove this line

            # Update the map
            st.pydeck_chart(st.session_state.map_deck)

        else:
            st.write("Please enter a valid date, time, pickup and dropoff location.")
            st.session_state.map_deck = display_map(focus_on_newyork=True)
            #st.experimental_rerun()# Remove this line

            # Update the map
            st.pydeck_chart(st.session_state.map_deck)
