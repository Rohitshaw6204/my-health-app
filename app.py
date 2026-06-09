import streamlit as st
import pandas as pd
import numpy as np
import pickle
import google.generativeai as genai

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="GlucoseGuard Dashboard", layout="wide")

# Setup Google Gemini AI configuration
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

# 3. MAIN DASHBOARD - TABS
st.title("🩸 GlucoseGuard: AI Health Predictor")
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard & Predictor", "🤖 AI Chatbot", "🥗 Meal & Exercise", "⚠️ Alerts"])

# TAB 1: DASHBOARD & ML PREDICTION
with tab1:
    st.header("Health Predictor Dashboard")
    
    # Load patient history from CSV
    try:
        df = pd.read_csv("patient_data.csv")
        df.set_index('Date', inplace=True)
        st.line_chart(df)
    except FileNotFoundError:
        st.warning("Historical record not found (patient_data.csv missing).")
        
    st.subheader("🔮 AI Glucose Prediction")
    if st.button("Predict My Blood Sugar"):
        diabetes_mapping = {"Non-Diabetic": 0, "Type 1": 1, "Type 2": 2}
        status_num = diabetes_mapping[has_diabetes]
        
        try:
            with open('diabetes_model.pkl', 'rb') as file:
                model_ml = pickle.load(file)
            
            user_data = pd.DataFrame([[age, weight, height, status_num]], columns=model_ml.feature_names_in_)
            predicted_sugar = model_ml.predict(user_data)[0]
            
            # Attractive metric display
            col1, col2 = st.columns(2)
            col1.metric(label="Predicted Fasting Blood Sugar", value=f"{round(predicted_sugar, 1)} mg/dL")
            col2.metric(label="Health Risk Score", value="Low" if predicted_sugar < 140 else "High")
            st.balloons()
            
        except Exception as e:
            st.error(f"Prediction Error: {e}")

# TAB 2: AI CHATBOT INTEGRATION
with tab2:
    st.header("🤖 AI Health Assistant")
    st.write("Ask any question about diabetes management.")
    
    user_query = st.text_input("Ask your health question:")
    if st.button("Get AI Advice"):
        if user_query:
            try:
                response = model.generate_content(user_query)
                st.success(f"**AI Assistant:** {response.text}")
            except Exception as e:
                st.error("AI connection error. Please check your API Key.")

# TAB 3: MEAL & EXERCISE GUIDE
with tab3:
    st.header("🥗 Blood Sugar Maintenance Guide")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Recommended Meal Plan")
        st.markdown("* **Breakfast:** Oats with nuts.\n* **Lunch:** Dal, sabzi, salad, and multigrain roti.\n* **Dinner:** Grilled paneer or boiled vegetables.")
    with col2:
        st.subheader("Daily Exercise Guide")
        st.markdown("* **Activity:** 20-30 minutes brisk walk after meals.\n* **Benefit:** Helps in maintaining natural blood sugar levels.")

# TAB 4: ALERTS
with tab4:
    st.header("⚠️ Live Smart Alerts")
    st.info("Your daily health score: **85/100**. Keep it up!")
    st.warning("🔔 Reminder: Ensure you take your medication on time.")