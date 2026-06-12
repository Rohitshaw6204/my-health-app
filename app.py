import streamlit as st
import pandas as pd
import numpy as np
import pickle
import google.generativeai as genai

import time
from datetime import datetime

st.set_page_config(
    page_title="GlucoseGuard Dashboard",
    layout="wide"
)

from database import create_database
from auth import register_user, login_user

create_database()

# ADD THIS BLOCK HERE

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 GlucoseGuard Login")

    option = st.selectbox(
        "Select Option",
        ["Login", "Register"]
    )

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if option == "Register":
        if st.button("Register"):
            success = register_user(
                username,
                password
            )

            if success:
                st.success(
                    "Registration Successful"
                )
            else:
                st.error(
                    "Username already exists"
                )

    if option == "Login":
        if st.button("Login"):

            user = login_user(
                username,
                password
            )

            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.rerun()

            else:
                st.error(
                    "Invalid Username or Password"
                )

    st.stop()


# Setup Google Gemini AI configuration

try:
    api_key = st.secrets["GEMINI_API_KEY"]

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )


except Exception:

    model = None

    st.sidebar.warning(
        "Gemini API Key not configured."
    )


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

    if "history" not in st.session_state:
        st.session_state.history = []

    if "last_sugar" not in st.session_state:
        st.session_state.last_sugar = 140

    st.header("Health Predictor Dashboard")

    
    st.subheader("🔮 AI Glucose Prediction")

    st.markdown("### 📝 Previous Health Information")

    previous_sugar = st.number_input(
        "Previous Blood Sugar (mg/dL)",
        min_value=50,
        max_value=500,
        value=st.session_state.last_sugar
        
    )

    food_input = st.text_area(
        "🍽️ What did you eat today?",
        placeholder="Example: 2 roti, dal, rice, salad, tea"
    )

    diet_followed = st.checkbox(
        "Followed Diet Plan"
    )
    exercise_followed = st.checkbox(
        "Completed Exercise"
    )


    medicine_taken = st.checkbox(
        "Took Medicines On Time"
    )

    current_weight = st.number_input(
        "Current Weight (kg)",
        min_value=20,
        max_value=200,
        value=weight
    )

    if st.button("Predict My Blood Sugar"):

        import time
        from datetime import datetime

        with st.spinner("🧠 AI is analyzing your health data..."):

            progress = st.progress(0)

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            progress.empty()

        predicted_sugar = previous_sugar

        food_score = 0
        food_text = food_input.lower()

        # High Sugar Foods
        if "rice" in food_text:
            food_score += 15

        if "burger" in food_text:
            food_score += 25

        if "pizza" in food_text:
            food_score += 25

        if "cake" in food_text:
            food_score += 35

        if "ice cream" in food_text:
            food_score += 30

        if "coke" in food_text:
            food_score += 40

        if "cold drink" in food_text:
            food_score += 40

        if "sweets" in food_text:
            food_score += 35

        # Healthy Foods
        if "salad" in food_text:
            food_score -= 10

        if "vegetable" in food_text:
            food_score -= 5

        if "dal" in food_text:
            food_score -= 5

        if "sprouts" in food_text:
            food_score -= 10

        predicted_sugar += food_score

        if diet_followed:
            predicted_sugar *= 0.95
            
        else:
            predicted_sugar *= 1.05
            
        if exercise_followed:
            predicted_sugar *= 0.90
            
        else:
            predicted_sugar *= 1.03
            
        if medicine_taken:
            predicted_sugar *= 0.85
            
        else:
            predicted_sugar *= 1.10

        predicted_sugar = round(max(70, predicted_sugar))
        
        st.session_state.last_sugar = int(predicted_sugar)

        future_prediction = predicted_sugar
        
        if diet_followed:
            future_prediction *= 0.95
            
        if exercise_followed:
            future_prediction *= 0.95
            
        if medicine_taken:
            future_prediction *= 0.90
            
        future_prediction = round(future_prediction)

        now = datetime.now()
        
        past_time = now.strftime("%d-%m %H:%M")
        
        current_time = (now).strftime("%d-%m %H:%M")
        
        future_time = (
            now + pd.Timedelta(hours=2)
        ).strftime("%d-%m %H:%M")

        st.success(
            f"Prediction Generated On: {current_time}"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Previous Sugar",
            f"{previous_sugar:.0f} mg/dL"
        )

        col2.metric(
            "Current Prediction",
            f"{predicted_sugar:.0f} mg/dL"
        )

        col3.metric(
            "Future Prediction",
            f"{future_prediction:.0f} mg/dL"
        )

        trend_df = pd.DataFrame(
            {
                "Stage": [
                    f"Past\n{past_time}",
                    f"Current\n{current_time}",
                    f"Future\n{future_time}"
                ],
                
                "Sugar Level": [
                    previous_sugar,
                    predicted_sugar,
                    future_prediction
                ]
            }
        )
        
        trend_df = trend_df.set_index("Stage")

        st.success(
            "📈 Generating Health Trend Graph..."
        )

        time.sleep(1)

        st.subheader("📈 Blood Sugar Timeline")

        st.line_chart(trend_df)

        st.balloons()

# TAB 2: AI CHATBOT INTEGRATION
with tab2:

    st.header("🤖 AI Health Assistant")
    st.write("Ask any question about diabetes management.")

    user_query = st.text_input(
        "Ask your health question:"
    )

    if st.button("Get AI Advice"):

        try:

            if model is None:
                st.error(
                    "Gemini API not configured."
                )

            elif user_query:

                with st.spinner(
                    "🤖 Gemini is thinking..."
                ):

                    response = model.generate_content(
                        f"""
                        You are a diabetes health assistant.

                        User Profile:
                        Age: {age}
                        Weight: {weight}
                        Height: {height}
                        Diabetes Type: {has_diabetes}

                        Doctor Advice:
                        {doc_notes}

                        User Question:
                        {user_query}

                        Give safe and simple health guidance.
                        """
                    )

                st.markdown(
                    f"### 🤖 Gemini Response\n\n{response.text}"
                )

        except Exception as e:

            st.error(
                f"AI connection error: {e}"
            )


with tab3:

    st.header("🥗 Weekly Diabetes Diet & Exercise Plan")

    days = {
        "Monday": {
            "Breakfast": "Oats + Almonds + Green Tea",
            "Lunch": "Dal + Brown Rice + Salad",
            "Dinner": "Grilled Paneer + Vegetables",
            "Exercise": "30 min Brisk Walk"
        },

        "Tuesday": {
            "Breakfast": "Boiled Eggs + Whole Wheat Toast",
            "Lunch": "Chapati + Mixed Vegetables",
            "Dinner": "Soup + Salad",
            "Exercise": "20 min Cycling"
        },

        "Wednesday": {
            "Breakfast": "Poha + Sprouts",
            "Lunch": "Rajma + Brown Rice",
            "Dinner": "Paneer Salad",
            "Exercise": "30 min Walking"
        },

        "Thursday": {
            "Breakfast": "Upma + Green Tea",
            "Lunch": "Dal + Chapati + Salad",
            "Dinner": "Vegetable Soup",
            "Exercise": "25 min Yoga"
        },

        "Friday": {
            "Breakfast": "Oats + Fruits",
            "Lunch": "Chickpeas + Salad",
            "Dinner": "Paneer + Vegetables",
            "Exercise": "30 min Walking"
        },

        "Saturday": {
            "Breakfast": "Idli + Sambar",
            "Lunch": "Brown Rice + Dal",
            "Dinner": "Salad + Soup",
            "Exercise": "20 min Jogging"
        },

        "Sunday": {
            "Breakfast": "Sprouts + Green Tea",
            "Lunch": "Healthy Homemade Meal",
            "Dinner": "Light Vegetable Dinner",
            "Exercise": "45 min Family Walk"
        }
    }

    selected_day = st.selectbox(
        "Select Day",
        list(days.keys())
    )

    st.subheader(f"📅 {selected_day}")

    col1, col2 = st.columns(2)

    with col1:
        st.success(
            f"""
            🍳 Breakfast:
            {days[selected_day]['Breakfast']}

            🍛 Lunch:
            {days[selected_day]['Lunch']}

            🍽 Dinner:
            {days[selected_day]['Dinner']}
            """
        )

    with col2:
        st.info(
            f"""
            🏃 Exercise Plan

            {days[selected_day]['Exercise']}
            """
        )

with tab4:

    st.header("⚠️ Smart Health Alerts")

    if has_diabetes == "Type 2":
        st.error(
            "Avoid sugary drinks today."
        )

    elif has_diabetes == "Type 1":
        st.warning(
            "Monitor insulin levels regularly."
        )

    else:
        st.success(
            "Maintain healthy lifestyle habits."
        )

    st.info(
        "🚶 Walk 10 minutes after every meal."
    )

    st.warning(
        "💧 Drink at least 2-3 liters of water daily."
    )

    st.success(
        "🥗 Include fiber-rich foods in every meal."
    )