import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="GlucoseGuard Dashboard", layout="wide")

# Configure Google Gemini AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
else:
    st.sidebar.error("API Key not found in Streamlit Secrets!")

# 2. SIDEBAR - USER PROFILE & DOCTOR PORTAL
st.sidebar.header("👤 User Profile")
age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=30)
weight = st.sidebar.number_input("Weight (kg)", min_value=10, max_value=200, value=70)
height = st.sidebar.number_input("Height (cm)", min_value=50, max_value=250, value=170)
has_diabetes = st.sidebar.selectbox("Diabetes Status", ["Non-Diabetic", "Type 1", "Type 2"])

st.sidebar.markdown("---")
st.sidebar.header("🩺 Doctor Portal")
doc_notes = st.sidebar.text_area("Doctor's Advice", "Keep daily carbs under 50g and walk daily.")

# 3. MAIN DASHBOARD
st.title("🩸 GlucoseGuard: AI Health Predictor")
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard & Predictor", "🤖 AI Chatbot", "🥗 Meal & Exercise", "🚨 Alerts"])

# TAB 1: DASHBOARD & PREDICTOR
with tab1:
    st.header("Health Predictor Dashboard")
    
    # Logic for calculating predicted blood sugar based on inputs
    predicted_sugar = 110 + (age * 0.2) + (weight * 0.1)
    if has_diabetes != "Non-Diabetic":
        predicted_sugar += 30

    # Displaying metrics using columns for an attractive UI
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Predicted Next Fasting Blood Sugar", value=f"{round(predicted_sugar, 1)} mg/dL")
    with col2:
        health_score = 85 if predicted_sugar < 140 else 60
        st.metric(label="Daily Health Score", value=f"{health_score}/100")

    st.subheader("Recent Blood Sugar Trend")
    # Generating dummy chart data for visualization
    chart_data = pd.DataFrame(np.random.randint(90, 150, size=(7, 1)), columns=['Blood Sugar (mg/dL)'])
    st.line_chart(chart_data)

# TAB 2: AI CHATBOT
with tab2:
    st.header("🤖 AI Health Assistant")
    st.write("Ask any question about health, diet, and exercise!")
    
    user_message = st.text_input("Ask your question:")
    # Triggering AI response on button click
    if st.button("Get AI Advice"):
        if user_message:
            try:
                response = model.generate_content(user_message)
                st.markdown(f"**AI Assistant:** {response.text}")
            except Exception as e:
                st.error("AI connection error. Please check your API key.")

# TAB 3: MEAL & EXERCISE
with tab3:
    st.header("🥗 Meal & Exercise Plan")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Recommended Meal Plan")
        st.markdown("* **Breakfast:** Oats with nuts.\n* **Lunch:** Dal, sabzi, salad, and 1 multigrain roti.\n* **Dinner:** Grilled paneer/chicken or boiled vegetables.")
    with col2:
        st.subheader("Daily Exercise Guide")
        st.markdown("* **Activity:** 20-30 minutes brisk walk after meals.\n* **Benefit:** Helps in natural sugar control.")

# TAB 4: ALERTS
with tab4:
    st.header("🚨 Live Smart Alerts")
    # Conditional logic for health alerts
    if predicted_sugar > 140:
        st.error(f"⚠️ **Alert:** Your predicted blood sugar ({round(predicted_sugar, 1)} mg/dL) is high. Please consult your doctor.")
    else:
        st.success("✅ **Status:** Your sugar level is stable. Good job!")