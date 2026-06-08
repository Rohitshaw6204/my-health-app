import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np

# Configure Page Layout for a professional look
st.set_page_config(page_title="GlucoseGuard AI", layout="wide")

# Set up the API Key from Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key not found! Please set it in Streamlit Secrets.")

# --- SIDEBAR: USER INPUTS ---
st.sidebar.header("👤 User Profile")
age = st.sidebar.number_input("Age", min_value=0, max_value=120, value=30)
weight = st.sidebar.number_input("Weight (kg)", min_value=10, max_value=200, value=70)
height = st.sidebar.number_input("Height (cm)", min_value=50, max_value=250, value=170)
has_diabetes = st.sidebar.selectbox("Family History of Diabetes?", ["Yes", "No"])

st.sidebar.markdown("---")
doc_notes = st.sidebar.text_area("Add any doctor notes here:")

# --- MAIN DASHBOARD ---
st.title("📊 GlucoseGuard Dashboard")
tabs = st.tabs(["Prediction", "Chatbot", "Diet", "Settings"])

# TAB 1: PREDICTION
with tabs[0]:
    st.header("Health Predictor")
    
    # Simulating a prediction score for attractive UI
    if st.button("Predict My Health Score"):
        # Dummy calculation for demonstration
        risk_score = (age * 0.2) + (weight * 0.5) - (height * 0.1)
        risk_score = min(max(int(risk_score), 0), 100)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Predicted Health Risk Score", value=f"{risk_score}/100", delta="-5%" if risk_score < 50 else "+10%")
        with col2:
            st.info("Based on your provided metrics, this is your estimated risk score.")

# TAB 2: CHATBOT
with tabs[1]:
    st.header("🤖 AI Health Assistant")
    st.write("Ask any question about health, diet, and exercise!")
    
    user_query = st.text_input("Ask:")
    if user_query:
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(user_query)
            st.success(response.text)
        except Exception as e:
            st.error("Error communicating with AI. Please check your API Key.")