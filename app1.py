import streamlit as st
import requests
import json
from streamlit_lottie import st_lottie

# ==============================================================================
# --- Page Configuration ---
# ==============================================================================
st.set_page_config(
    page_title="MachineInsight AI Interface",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# --- Custom CSS for the Advanced, Fortune 500-Level UI ---
# ==============================================================================
st.markdown("""
<style>
    /* --- Import Google Font: Inter & Poppins --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', 'Poppins', sans-serif;
    }
    .stApp {
        background: linear-gradient(120deg, #0f2027 0%, #2c5364 100%);
        background-attachment: fixed;
        color: #e0e0e0;
        min-height: 100vh;
    }
    /* --- Animated Aurora Background --- */
    .stApp:before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 0;
        pointer-events: none;
        background: radial-gradient(at 27% 37%, hsla(215, 98%, 61%, 0.13) 0px, transparent 50%),
                    radial-gradient(at 97% 21%, hsla(125, 98%, 72%, 0.11) 0px, transparent 50%),
                    radial-gradient(at 52% 99%, hsla(355, 98%, 76%, 0.10) 0px, transparent 50%),
                    radial-gradient(at 10% 29%, hsla(256, 96%, 68%, 0.13) 0px, transparent 50%),
                    radial-gradient(at 97% 96%, hsla(38, 60%, 74%, 0.10) 0px, transparent 50%),
                    radial-gradient(at 33% 50%, hsla(222, 67%, 73%, 0.10) 0px, transparent 50%),
                    radial-gradient(at 79% 53%, hsla(343, 68%, 79%, 0.10) 0px, transparent 50%);
        animation: auroraMove 16s linear infinite alternate;
    }
    @keyframes auroraMove {
        0% { filter: blur(0px); }
        100% { filter: blur(8px); }
    }
    /* --- Glassmorphism Panel Styling --- */
    .glass-panel {
        background: rgba(20, 20, 40, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1.5px solid rgba(255, 255, 255, 0.13);
        border-radius: 20px;
        padding: 2.2rem 2rem 2rem 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
        position: relative;
        z-index: 1;
    }
    /* --- Card Hover Effects --- */
    .glass-panel:hover {
        box-shadow: 0 16px 48px 0 rgba(130, 87, 230, 0.25), 0 1.5px 8px 0 rgba(0,0,0,0.12);
        transform: translateY(-4px) scale(1.012);
        border-color: #8257E6;
    }
    /* --- Custom Button Styling --- */
    .stButton>button {
        border-radius: 12px;
        border: none;
        background-image: linear-gradient(90deg, #5028D5 0%, #8257E6 100%);
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.85rem 2.2rem;
        transition: all 0.25s cubic-bezier(.25,.8,.25,1);
        box-shadow: 0 4px 15px 0 rgba(116, 79, 168, 0.75);
        letter-spacing: 0.5px;
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 8px 25px 0 rgba(116, 79, 168, 0.9);
        background-image: linear-gradient(90deg, #8257E6 0%, #5028D5 100%);
    }
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 2px 10px 0 rgba(116, 79, 168, 0.75);
    }
    /* --- Result Animation & Styling --- */
    .result-container {
        opacity: 0;
        transform: scale(0.95);
        animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    @keyframes popIn {
        to { opacity: 1; transform: scale(1); }
    }
    .status-success { color: #34D399; }
    .status-warn { color: #FBBF24; }
    .status-fail { color: #F87171; }
    /* --- Section Divider --- */
    hr {
        background-color: rgba(255, 255, 255, 0.13);
        margin: 2rem 0;
        border: none;
        height: 1.5px;
        border-radius: 2px;
    }
    /* --- Typography --- */
    h1, h2, h3, p {
        text-shadow: 0 1px 3px rgba(0,0,0,0.18);
    }
    /* --- Responsive Design --- */
    @media (max-width: 900px) {
        .glass-panel { padding: 1.2rem 0.7rem; }
        h1 { font-size: 2.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- Lottie Animation Data ---
# ==============================================================================
LOTTIE_ANIMATION_DATA = {
    "v": "5.8.1", "fr": 60, "ip": 0, "op": 180, "w": 400, "h": 400, "nm": "AI_Analysis",
    "ddd": 0, "assets": [],
    "layers": [
        {
            "ddd": 0, "ind": 1, "ty": 4, "nm": "outer_ring", "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 80, "ix": 11},
                "r": {"a": 1, "k": [
                    {"i": {"x": [0.833], "y": [0.833]}, "o": {"x": [0.167], "y": [0.167]}, "t": 0, "s": [0]},
                    {"t": 180, "s": [720]}
                ], "ix": 10},
                "p": {"a": 0, "k": [200, 200, 0], "ix": 2},
                "s": {"a": 0, "k": [100, 100, 100], "ix": 6}
            },
            "shapes": [{"ty": "gr", "it": [{"ty": "el", "p": {"a": 0, "k": [0, 0], "ix": 2}, "s": {"a": 0, "k": [150, 150], "ix": 2}}, {"ty": "st", "c": {"a": 0, "k": [0.28, 0.69, 0.99, 1], "ix": 3}, "o": {"a": 0, "k": 100, "ix": 4}, "w": {"a": 0, "k": 3, "ix": 5}}, {"ty": "tr", "p": {"a": 0, "k": [0, 0], "ix": 2}, "s": {"a": 0, "k": [100, 100], "ix": 6}}]}]
        },
        {
            "ddd": 0, "ind": 2, "ty": 4, "nm": "inner_ring", "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100, "ix": 11},
                "r": {"a": 1, "k": [
                    {"i": {"x": [0.833], "y": [0.833]}, "o": {"x": [0.167], "y": [0.167]}, "t": 0, "s": [0]},
                    {"t": 180, "s": [-540]}
                ], "ix": 10},
                "p": {"a": 0, "k": [200, 200, 0], "ix": 2},
                "s": {"a": 0, "k": [100, 100, 100], "ix": 6}
            },
            "shapes": [{"ty": "gr", "it": [{"ty": "el", "p": {"a": 0, "k": [0, 0], "ix": 2}, "s": {"a": 0, "k": [80, 80], "ix": 2}}, {"ty": "st", "c": {"a": 0, "k": [1, 1, 1, 1], "ix": 3}, "o": {"a": 0, "k": 100, "ix": 4}, "w": {"a": 0, "k": 2, "ix": 5}}, {"ty": "tr", "p": {"a": 0, "k": [0, 0], "ix": 2}, "s": {"a": 0, "k": [100, 100], "ix": 6}}]}]
        }
    ]
}

# ==============================================================================
# --- API Call and Decoding Logic ---
# ==============================================================================
WML_API_KEY = "9rTun65cAZVA-Rx1K0Lb29EjGe5CDr89OcGI9GhV7jq1"
WML_ENDPOINT_URL = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/failure_prediction_service/predictions?version=2021-05-01"

LABEL_MAPPING = {
    0: {"text": "Heat Dissipation Failure", "type": "warn", "icon": "🔥"},
    1: {"text": "System Nominal", "type": "success", "icon": "✅"},
    2: {"text": "Overstrain Failure", "type": "warn", "icon": "⚡"},
    3: {"text": "Power Failure", "type": "fail", "icon": "🔌"},
    4: {"text": "Random Failure", "type": "warn", "icon": "❓"},
    5: {"text": "Tool Wear Failure", "type": "fail", "icon": "🔧"}
}

@st.cache_data(ttl=3600)
def get_wml_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}"
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def call_prediction_api(endpoint_url, token, input_data):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    payload = {
        "input_data": [{
            "fields": ["Type", "Air temperature [K]", "Process temperature [K]", "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"],
            "values": [input_data]
        }]
    }
    response = requests.post(endpoint_url, headers=headers, json=payload)
    response.raise_for_status()
    prediction = response.json()['predictions'][0]['values'][0][0]
    return prediction

# ==============================================================================
# --- User Interface (UI) ---
# ==============================================================================

# --- Header ---
st.markdown('<h1 style="text-align: center; font-weight: 800; font-size: 3.5rem; letter-spacing: -2px; margin-bottom: 0.2em;">Machine<span style="color: #8257E6;">Insight</span></h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #a0aec0; margin-bottom: 2.5em;">The pinnacle of AI-driven Predictive Maintenance</p>', unsafe_allow_html=True)

# --- Main Layout ---
col1, col2 = st.columns([0.55, 0.45], gap="large")

with col1:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.subheader("⦾ Machine Telemetry Input")
    c1, c2 = st.columns(2)
    with c1:
        air_temp = st.slider("Air Temperature [K]", 295.0, 305.0, 300.5, 0.1)
        rot_speed = st.slider("Rotational Speed [rpm]", 1100, 2900, 1500, 10)
        machine_type = st.selectbox("Machine Type", ("L", "M", "H"), help="L: Low, M: Medium, H: High quality variant")
    with c2:
        process_temp = st.slider("Process Temperature [K]", 305.0, 315.0, 309.8, 0.1)
        torque = st.slider("Torque [Nm]", 3.0, 80.0, 45.3, 0.1)
        tool_wear = st.slider("Tool Wear [min]", 0, 260, 120, 1)
    predict_button = st.button("Analyze Machine Status", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-panel" style="height: 100%;">', unsafe_allow_html=True)
    st.subheader("⦿ System Status Dashboard")
    st.write("Live Telemetry Readings:")
    st.progress((torque - 3.0) / (80.0 - 3.0), text=f"Torque: {torque:.1f} Nm")
    st.progress((rot_speed - 1100) / (2900 - 1100), text=f"Speed: {rot_speed} rpm")
    st.progress(tool_wear / 260, text=f"Tool Wear: {tool_wear} min")
    st.markdown("<hr>", unsafe_allow_html=True)
    result_placeholder = st.empty()
    if 'prediction_result' not in st.session_state:
        st.session_state.prediction_result = None
    if predict_button:
        input_values = [machine_type, air_temp, process_temp, float(rot_speed), torque, float(tool_wear)]
        with result_placeholder.container():
            st_lottie(LOTTIE_ANIMATION_DATA, speed=1.5, height=150, key="loading")
            st.write("Contacting AI Core... Analyzing patterns...")
        try:
            if WML_API_KEY.startswith("PASTE") or WML_ENDPOINT_URL.startswith("PASTE"):
                st.error("API Error: Credentials not configured in the script.")
                st.session_state.prediction_result = None
            else:
                token = get_wml_token(WML_API_KEY)
                prediction_code = call_prediction_api(WML_ENDPOINT_URL, token, input_values)
                st.session_state.prediction_result = LABEL_MAPPING.get(prediction_code)
                st.rerun()
        except Exception as e:
            st.session_state.prediction_result = None
            st.error(f"API Call Failed: {e}")
            st.rerun()
    if st.session_state.prediction_result:
        result = st.session_state.prediction_result
        with result_placeholder.container():
            st.markdown(f"""
            <div class="result-container" style="text-align: center;">
                <p style="font-size: 1rem; color: #a0aec0;">AI Prediction:</p>
                <p style="font-size: 5rem; line-height: 1; margin-top: 1rem;">{result['icon']}</p>
                <h2 class="status-{result['type']}" style="font-size: 2.2rem; font-weight: 700; margin-top: 1rem;">{result['text']}</h2>
            </div>
            """, unsafe_allow_html=True)
    else:
        with result_placeholder.container():
            st.info("System is awaiting telemetry data for analysis.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Animated Diagnostic Cards ---
st.markdown('<div class="glass-panel" style="margin-top: 2.5rem; display: flex; gap: 2rem; justify-content: center; align-items: stretch; flex-wrap: wrap;">', unsafe_allow_html=True)
card_data = [
    {"title": "Nominal Operation", "icon": "✅", "desc": "All systems stable. No anomalies detected.", "color": "#34D399", "lottie": None},
    {"title": "Tool Wear Alert", "icon": "🔧", "desc": "Tool wear approaching threshold. Maintenance advised soon.", "color": "#F87171", "lottie": None},
    {"title": "Heat Dissipation", "icon": "🔥", "desc": "Elevated heat detected. Check cooling systems.", "color": "#FBBF24", "lottie": None},
]
for card in card_data:
    st.markdown(f"""
    <div class="glass-panel" style="min-width: 260px; max-width: 340px; margin: 0.5rem; display: inline-block; vertical-align: top; box-shadow: 0 4px 24px 0 rgba(0,0,0,0.13); border-left: 5px solid {card['color']};">
        <div style="text-align: center; font-size: 2.5rem; margin-bottom: 0.5rem;">{card['icon']}</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: {card['color']}; text-align: center;">{card['title']}</div>
        <div style="font-size: 1rem; color: #a0aec0; text-align: center; margin-top: 0.5rem;">{card['desc']}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Upload Section ---
st.markdown('<div class="glass-panel" style="margin-top: 2.5rem;">', unsafe_allow_html=True)
st.subheader("⦾ Upload Machine Data File")
file = st.file_uploader("Upload CSV or Excel file for batch analysis", type=["csv", "xlsx"])
if file:
    st.success("File uploaded! (Batch analysis feature coming soon.)")
st.markdown('</div>', unsafe_allow_html=True)

# --- Documentation Expander ---
st.markdown('<div class="glass-panel" style="margin-top: 3rem;">', unsafe_allow_html=True)
with st.expander("View Project Documentation & Technical Briefing"):
    st.markdown("""
    ### Project Overview
    This project addresses the challenge of predictive maintenance for industrial machinery. The goal is to anticipate equipment failures before they occur by analyzing real-time sensor data. This AI model can predict the type of failure, enabling proactive maintenance and reducing costly downtime.
    
    ### Technology & Architecture
    - **Frontend Interface:** A bespoke, interactive dashboard built with Streamlit and custom CSS for a premium user experience.
    - **Machine Learning Model:** An XGBoost classification model developed in Python, utilizing the Scikit-learn library for robust data preprocessing.
    - **API & Deployment:** The trained model is deployed as a scalable web service on IBM Cloud via the Watson Machine Learning service, providing a secure and reliable API endpoint for real-time predictions.
    
    ### Model Limitations & Considerations
    - **High Performance on Common Failures:** The model demonstrates excellent accuracy (over 98%) in predicting common operational states, such as "No Failure" or "Heat Dissipation Failure."
    - **Challenges with Rare Events:** Due to insufficient data, the model's ability to predict rare events like "Random Failures" is limited. This is a known constraint and highlights the need for more diverse training data for a comprehensive real-world system.
    
    ### UI/UX Design Principles
    - **Glassmorphism:** All panels and cards use glassmorphism for a futuristic, premium look.
    - **Custom Fonts:** Google Fonts (Inter, Poppins) for a modern, clean feel.
    - **Lottie Animations:** Used for loading and visual feedback.
    - **Animated Gradients:** Aurora-style animated backgrounds for visual depth.
    - **Interactive Cards & Buttons:** Hover, click, and transition effects throughout.
    - **Responsive Layout:** Looks stunning on both desktop and mobile.
    - **Enterprise-Grade Polish:** Inspired by Apple, Tesla, IBM, and Adobe dashboards.
    """)
st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown('<p style="text-align: center; margin-top: 3rem; color: #a0aec0;">&copy; 2025 MachineInsight. Developed by Sai Abhinav Patel Sadineni.</p>', unsafe_allow_html=True)