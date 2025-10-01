import streamlit as st
import requests
from io import BytesIO
from PIL import Image

# --- Page config ---
st.set_page_config(page_title="🌱 Green Simplify", layout="wide")

# --- API Key input ---
together_api_key = st.text_input("Enter your Together.ai API key:", type="password")
if not together_api_key:
    st.warning("Please enter your API key to use Green Simplify.")
    st.stop()
    
# --- Thumbnail ---
thumbnail_url = "https://raw.githubusercontent.com/MeeraYasmin/Green-Simplify/main/asset/Green Simplify.jpg"
try:
    response = requests.get(thumbnail_url)
    thumbnail = BytesIO(response.content)
    st.image(thumbnail, use_container_width=True)
except:
    st.warning("Thumbnail could not be loaded.")

st.title("🌱 Green Simplify")
st.markdown("""
Track your carbon footprint and get AI-generated eco tips personalized to your daily activities!
""")

# --- Inputs for daily activities ---
st.header("Log Your Daily Activities")
car_km = st.number_input("Car travel (km)", min_value=0, value=0)
meat_meals = st.number_input("Meat meals today", min_value=0, value=0)
electricity_kwh = st.number_input("Electricity use (kWh)", min_value=0, value=0)

# --- Calculate CO2 footprint ---
total_co2 = car_km*0.2 + meat_meals*5 + electricity_kwh*0.5
st.metric("🌍 Total CO₂ Emitted (kg)", round(total_co2,2))

# --- Session state ---
if "eco_tip" not in st.session_state:
    st.session_state.eco_tip = ""
if "relevance_score" not in st.session_state:
    st.session_state.relevance_score = 0

import requests

def get_eco_tip(car_km, meat_meals, electricity_kwh, together_api_key):
    api_url = "https://api.together.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {together_api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a friendly, concise, and helpful AI named GreenSimplify.
The user did today:
- Car travel: {car_km} km
- Meat meals: {meat_meals}
- Electricity: {electricity_kwh} kWh

Provide ONE eco-friendly tip most relevant to their activities.
Also provide a relevance score from 0 to 100.

Format the response like:
Tip: <eco tip here>
Relevance score: <score here>
"""

    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "messages": [
            {"role": "system", "content": "You are a helpful AI giving eco-friendly tips."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        # Extract the text similar to SafeEmo function
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No response from model.")
    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh} - {response.text}"
    except requests.exceptions.ConnectionError as errc:
        return f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"Something went wrong with the request: {err}"

# --- Button to get AI tip ---
if st.button("Generate Eco Tip 🌱"):
    with st.spinner("Getting your AI eco tip..."):
        tip, score = get_eco_tip(car_km, meat_meals, electricity_kwh, together_api_key).split("Relevance score:")
        st.session_state.eco_tip = tip
        st.session_state.relevance_score = score

# --- Display AI tip with CSS like old app ---
if st.session_state.eco_tip:
    st.markdown(f"""
    <div style='background-color:#32CD32;
                padding:20px;
                border-radius:20px;
                text-align:center;
                animation: fadeIn 1s ease-in-out;
                color:white;'>
        <h2>💡 AI Eco Tip</h2>
        <p style='font-size:18px'>{st.session_state.eco_tip}</p>
        <h3>📊 Relevance Score: {st.session_state.relevance_score}</h3>
    </div>
    <style>
    @keyframes fadeIn {{
        0% {{opacity: 0; transform: translateY(-20px);}}
        100% {{opacity: 1; transform: translateY(0);}}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Mock Pro Features ---
st.header("Premium Features")
if "pro_unlocked" not in st.session_state:
    st.session_state.pro_unlocked = False

if st.button("Unlock Pro Features 🌟"):
    st.session_state.pro_unlocked = True

if st.session_state.pro_unlocked:
    st.success("🎉 Pro features unlocked! Advanced analytics enabled.")
    activities = ['Car travel', 'Meat meals', 'Electricity']
    values = [car_km*0.2, meat_meals*5, electricity_kwh*0.5]
    st.bar_chart({"Activity": activities, "CO₂ (kg)": values})
else:
    st.info("Upgrade to Pro to see advanced analytics!")

# --- Footer ---
st.markdown("---")
st.write("Made with ❤️ during RevenueCat Shipathon 2025")
