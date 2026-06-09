import streamlit as st
import pandas as pd
import numpy as np
import pickle
import google.generativeai as genai
import database # Ye aapki nayi database.py file ko use karega

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="GlucoseGuard Dashboard", layout="wide")

# Initialize database
database.init_db()

# Setup Google Gemini AI configuration
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
else:
    st.sidebar.error("API Key not found in Streamlit Secrets!")

# 2. SIDEBAR - USER PROFILE
st.sidebar.header("👤 User Profile")
age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=30)
weight = st.sidebar.number_input("Weight (kg)", min_value=10, max_value=200, value=70)
has_diabetes = st.sidebar.selectbox("Diabetes Status", ["Non-Diabetic", "Type 1", "Type 2"])

# 3. MAIN DASHBOARD - TABS
st.title("🩸 GlucoseGuard: AI Health Predictor")
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard & Predictor", "🤖 AI Chatbot", "🥗 Meal & Exercise", "🚨 Live Alerts"])

# TAB 1: DASHBOARD
with tab1:
    st.header("Weekly Health Tracker")
    # Data Entry Form
    with st.form("health_form"):
        col1, col2 = st.columns(2)
        sugar = col1.number_input("Blood Sugar (mg/dL)", min_value=50, max_value=400)
        med_status = col2.radio("Did you take medicine?", ["Yes", "No"])
        if st.form_submit_button("Save Weekly Record"):
            database.add_record("User1", str(pd.Timestamp.now().date()), sugar, med_status)
            st.success("Record saved!")

    # Display Graph from Database
    st.subheader("Your Weekly Progress")
    conn = database.sqlite3.connect('medical_data.db')
    df = pd.read_sql_query("SELECT * FROM records", conn)
    conn.close()
    if not df.empty:
        st.line_chart(df.set_index('date')['sugar'])

# TAB 2: AI CHATBOT
with tab2:
    st.header("🤖 AI Health Assistant")
    user_query = st.text_input("Ask about diabetes management:")
    if st.button("Get AI Advice"):
        if user_query:
            try:
                response = model.generate_content(user_query)
                st.markdown(f"**AI:** {response.text}")
            except:
                st.error("AI connection error.")

# TAB 3: MEAL & EXERCISE
with tab3:
    st.header("🥗 Maintenance Guide")
    st.markdown("- **Diet:** High fiber, low carb.\n- **Exercise:** 30 min brisk walk.")

import sqlite3

def init_db():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    # Pipes hata di hain aur lines sahi kar di hain
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS records (username TEXT, date TEXT, sugar REAL, med_status TEXT)''')
    conn.commit()
    conn.close()

def add_record(username, date, sugar, med_status):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO records VALUES (?, ?, ?, ?)", (username, date, sugar, med_status))
    conn.commit()
    conn.close()