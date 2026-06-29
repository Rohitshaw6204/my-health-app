import streamlit as st
import pandas as pd
import numpy as np
import pickle
import google.generativeai as genai
import sqlite3
import time
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from fpdf import FPDF

from database import create_database, get_user_history
from database import (
    create_database,
    get_user_history,
    save_profile,
    get_profile
)

def generate_pdf_report(
    username,
    age,
    weight,
    diabetes,
    predicted_sugar,
    future_prediction,
    hba1c
):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt="Health Report", ln=True)

    pdf.ln(10)

    pdf.cell(200, 10, txt=f"User: {username}", ln=True)
    pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
    pdf.cell(200, 10, txt=f"Weight: {weight}", ln=True)
    pdf.cell(200, 10, txt=f"Diabetes: {diabetes}", ln=True)

    pdf.ln(5)

    pdf.cell(200, 10, txt=f"Predicted Sugar: {predicted_sugar}", ln=True)
    pdf.cell(200, 10, txt=f"Future Prediction: {future_prediction}", ln=True)
    pdf.cell(200, 10, txt=f"HbA1c: {hba1c}", ln=True)

    filename = f"{username}_report.pdf"

    pdf.output(filename)

    return filename
st.set_page_config(
    page_title="GlucoseGuard Dashboard",
    layout="wide"
    
)
st.markdown("""
<style>
...
</style>
""", unsafe_allow_html=True)

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
                st.session_state.username = username
                st.rerun()

            else:
                st.error(
                    "Invalid Username or Password"
                )

    st.stop()
    profile = get_profile(
    st.session_state.user_id
)
profile = get_profile(st.session_state.user_id)

if profile is None:

    st.title("👤 Complete Your Profile")

    name = st.text_input("Full Name")

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=20,
        max_value=200,
    )

    diabetes_type = st.selectbox(
        "Diabetes Type",
        ["Type 1", "Type 2", "Non-Diabetic"]
    )

    email = st.text_input("Email")

    if st.button("Save Profile"):

        save_profile(
            st.session_state.user_id,
            name,
            age,
            weight,
            diabetes_type,
            email
        )

        st.success("Profile Saved Successfully")
        st.rerun()

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
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/2966/2966486.png",
    width=120
)

st.sidebar.title("GlucoseGuard")
profile = get_profile(
    st.session_state.user_id
)

name = profile[0]
age = profile[1]
weight = profile[2]
has_diabetes = profile[3]
email = profile[4]
st.sidebar.markdown("---")

st.sidebar.markdown("""
<div style="
background:rgba(255,255,255,0.08);
padding:15px;
border-radius:15px;
border:1px solid rgba(255,255,255,0.2);
text-align:center;
">
<h3>👨‍💻 Developer</h3>
<h4>Rohit Kumar</h4>
<p>AI & Python Developer</p>
<p>Creator of GlucoseGuard</p>
<p>🚀 Building Healthcare AI Solutions</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

st.sidebar.header("👤 User Profile")

st.sidebar.write(f"Name: {name}")
st.sidebar.write(f"Age: {age}")
st.sidebar.write(f"Weight: {weight} kg")
st.sidebar.write(f"Diabetes: {has_diabetes}")
st.sidebar.write(f"Email: {email}")
st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False

    if "user_id" in st.session_state:
        del st.session_state["user_id"]

    if "username" in st.session_state:
        del st.session_state["username"]

    st.rerun()
    st.success("Logged out successfully")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Blood Sugar History")



st.sidebar.markdown("---")
st.sidebar.header("🩺 Doctor Portal")
doc_notes = st.sidebar.text_area("Doctor's Advice", "Keep daily carbs under 50g and walk daily.")

# 3. MAIN DASHBOARD - TABS
st.title("🩸 GlucoseGuard: AI Health Predictor")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Dashboard",
    "📜 History",
    "🤖 AI Chatbot",
    "🥗 Meal & Exercise",
    "⚠️ Alerts",
    "🩺 Doctor Appointment"
])

# Session State Initialization
if "history" not in st.session_state:
    st.session_state.history = []

if "last_sugar" not in st.session_state:
    st.session_state.last_sugar = 140
 

# TAB 1: DASHBOARD & ML PREDICTION

with tab1:
    if st.session_state.last_sugar > 200:
        st.error(
        f"🚨 CRITICAL ALERT! Blood Sugar is {st.session_state.last_sugar} mg/dL"
    )
    

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
    medicine_name = st.text_input(
    "💊 Medicine Taken",
    placeholder="e.g. Metformin 500mg"
    )
    st.metric("🩸 Diabetes", has_diabetes)
    medicine_taken = bool(medicine_name)

    current_weight = st.number_input(
    "Current Weight (kg)",
    min_value=20.0,
    max_value=200.0,
    value=float(weight)
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
        
        
        score = 100
        if predicted_sugar > 180:
            score -= 30

        if not exercise_followed:
            score -= 20

        if not diet_followed:
            score -= 20

        if not medicine_taken:
            score -= 30
            st.metric("🏆 Health Score", f"{score}/100")
        if predicted_sugar > 200:
            st.error(
        f"🚨 CRITICAL ALERT! Blood Sugar is {predicted_sugar} mg/dL"
    )

        future_prediction = predicted_sugar
        
        if diet_followed:
            future_prediction *= 0.95
            
        if exercise_followed:
            future_prediction *= 0.95
            
        if medicine_taken:
            future_prediction *= 0.90
            
        future_prediction = round(future_prediction)
       
        now = datetime.now()
        past_time = (
            now - pd.Timedelta(hours=2)
            ).strftime(
                "%A, %d-%m-%Y %I:%M %p"
)
        current_time = now.strftime(
            "%A, %d-%m-%Y %I:%M %p"
)
        future_time = (
            now + pd.Timedelta(hours=2)
            ).strftime(
                "%A, %d-%m-%Y %I:%M %p"
)

        st.success(
            f"Prediction Generated On: {current_time}"
        )
        st.info(
            f"Predicted Time: {future_time}"
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



        time.sleep(1)
        st.subheader("🎯 Blood Sugar Risk Meter")
        gauge_fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=predicted_sugar,
                title={"text": "Predicted Blood Sugar"},
                gauge={
                    "axis": {"range": [70, 300]},
                    "steps": [
                        {"range": [70, 140], "color": "lightgreen"},
                        {"range": [140, 180], "color": "yellow"},
                        {"range": [180, 300], "color": "red"}
            ]
        }
    )
)
        hba1c = round(
            (predicted_sugar + 46.7) / 28.7,
            2
)
        st.markdown("## 📊 Health Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "🩸 Blood Sugar",
            f"{predicted_sugar} mg/dL"
)
        c2.metric(
            "📉 Future Sugar",
            f"{future_prediction} mg/dL"
)
        c3.metric(
            "🧪 HbA1c",
            hba1c
)
        c4.metric(
            "⚖️ Weight",
            f"{current_weight} kg"
)
        pdf_file = generate_pdf_report(
    st.session_state.username,
    age,
    current_weight,
    has_diabetes,
    predicted_sugar,
    future_prediction,
    hba1c
)
        with open(pdf_file, "rb") as file:
            st.download_button(
        "📄 Download Health Report",
        file,
        file_name=pdf_file,
        mime="application/pdf"
    )
     
        
           
        st.plotly_chart(
        gauge_fig,
        use_container_width=True
)
        
        st.subheader("🥧 Health Status Analysis")
        pie_df = pd.DataFrame({
            "Category": [
            "Sugar",
            "Diet",
            "Exercise",
            "Medicine"
    ],
    "Value": [
        predicted_sugar,
        1 if diet_followed else 0,
        1 if exercise_followed else 0,
        1 if medicine_taken else 0
    ]
})
        pie_fig = px.pie(
        pie_df,
        names="Category",
        values="Value",
        hole=0.4
)
        st.plotly_chart(
        pie_fig,
        use_container_width=True
)
        conn = sqlite3.connect("medical_data.db")
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO health_records (
             user_id,
             record_date,
             blood_sugar,
             activity
        )
        VALUES (?, ?, ?, ?)
        """, (
            st.session_state.user_id,
            current_time,
            predicted_sugar,
            food_input
))
        conn.commit()
        conn.close()
        st.balloons()
        st.markdown("---")
        st.markdown("## 📈 Health Analytics")
        st.markdown("""
 <h1 style='text-align:center;color:#00B4D8;'>
🩸 GlucoseGuard AI Predictor
 </h1>

 <p style='text-align:center;font-size:20px;'>
 Smart Diabetes Monitoring & Prediction System
 </p>
 """, unsafe_allow_html=True)

#Tab2: History
with tab2:

    st.header("📜 Blood Sugar History")

    history = get_user_history(
        st.session_state.user_id
    )

    if history:

        history_df = pd.DataFrame(
            history,
            columns=[
                "Date",
                "Blood Sugar",
                "Activity"
            ]
        )

        st.dataframe(
            history_df,
            use_container_width=True
        )
        history_df["Date"] = pd.to_datetime(
        history_df["Date"],
        format="%A, %d-%m-%Y %I:%M %p",
         errors="coerce"
)



        fig = px.area(
            history_df,
            x="Date",
            y="Blood Sugar",
            line_shape="spline"
)
        fig.update_traces(
            line=dict(width=4)
)
        fig.update_layout(
            height=400,
            xaxis_title="Date & Time",
            yaxis_title="Blood Sugar (mg/dL)",
            margin=dict(l=20, r=20, t=20, b=20)
)
        fig.update_layout(
            hovermode="x unified",
            height=450
)
        st.plotly_chart(
            fig,
            use_container_width=True
            
)
        st.subheader("🥧 Sugar Records Distribution")
        healthy_count = len(
            history_df[history_df["Blood Sugar"] < 140]
)
        high_count = len(
            history_df[history_df["Blood Sugar"] >= 140]
)
        pie_df = pd.DataFrame({
            "Status": ["Normal", "High"],
            "Count": [healthy_count, high_count]
})
        pie_fig = px.pie(
        pie_df,
        names="Status",
        values="Count",
        hole=0.4
)
        st.plotly_chart(
            pie_fig,
            use_container_width=True
)
        

    else:
        st.info(
            "No history available"
        )   

# TAB 3: AI CHATBOT INTEGRATION
with tab3:

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


with tab4:
    if st.session_state.last_sugar > 200:
     st.error(
        f"🚨 CRITICAL ALERT! Blood Sugar is {st.session_state.last_sugar} mg/dL"
    )
    

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
        
        
        

with tab5:

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
with tab6:

    st.header("🩺 Book Doctor Appointment")

    patient_name = st.text_input("Patient Name")
    doctors = {
    "Dr. A. Chandra": {
        "specialization": "Diabetologist & Endocrinologist",
        "rating": "4.8 ⭐ (294 Reviews)",
        "experience": "13+ Years",
        "location": "Laxmi's Clinic, Harmu Road, Near Imli Chowk, Ranchi",
        
        "link": "https://drachandraranchi.wixsite.com/mysite"
    },

    "Dr. Ajay Chhabra": {
        "specialization": "Diabetologist",
        "rating": "4.3 ⭐ (269 Reviews)",
        "experience": "23+ Years",
        "location": "Chhabra Diabetes Centre, Ratu Road, Ranchi",
        
        "link": "https://www.chhabradiabetescentre.com"
    },

    "Dr. Avinash Kumar": {
        "specialization": "Diabetologist & Family Physician",
        "rating": "4.6 ⭐ (94 Reviews)",
        "experience": "18+ Years",
        "location": "Uday Complex, Hazaribagh Road, Tharpakhna, Ranchi",
        
        "link": "https://www.practo.com/ranchi"
    },

    "Dr. P. Mukherjee": {
        "specialization": "Diabetologist",
        "rating": "4.9 ⭐ (60 Reviews)",
        "experience": "Senior Consultant",
        "location": "Cheshire Home Road, Deepatoli, Ranchi",
        
        "link": "https://www.practo.com/ranchi"
    },

    "Dr. Rakesh Mishra": {
        "specialization": "Diabetologist",
        "rating": "4.8 ⭐ (830 Reviews)",
        "experience": "19+ Years",
        "location": "Kanke Road, Near Rock Garden, Ranchi",
        
        "link": "https://www.practo.com/ranchi"
    },

    "Dr. Vinay K. Dhandhania": {
        "specialization": "Diabetologist",
        "rating": "4.9 ⭐ (89 Reviews)",
        "experience": "25+ Years",
        "location": "Orchid Medical Centre, H.B. Road, Ranchi",
        
        "link": "https://www.hexahealth.com/ranchi/doctor/dr-vinay-k-dhandhania-diabetologist"
    }
}
    

    selected_doctor = st.selectbox(
    "👨‍⚕️ Select Doctor",
    list(doctors.keys()),
    key="doctor_select"
)   

    date = st.date_input("Appointment Date")

    time_slot = st.selectbox(
        "Time",
        [
            "10:00 AM",
            "12:00 PM",
            "03:00 PM",
            "05:00 PM"
        ]
)
    doc = doctors[selected_doctor]
    col1, col2 = st.columns([1,2])
    with col1:
        with col2:
            st.markdown(f"## {selected_doctor}")
            st.write(f"🩺 Specialization: {doc['specialization']}")
            st.write(f"⭐ Rating: {doc['rating']}")
            st.write(f"💼 Experience: {doc['experience']}")
            st.write(f"📍 Location: {doc['location']}")
            maps_url = (
    "https://www.google.com/maps/search/?api=1&query="
    + urllib.parse.quote(doc["location"])
)
            st.link_button(
                "🗺️ View Clinic Location",
                maps_url
)
            st.link_button(
    "📅 Book Appointment",
    doc["link"]
)

    