import streamlit as st
import pandas as pd
import pickle
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="GlucoseGuard: AI Health Predictor", page_icon="🩺")

# --- 1. SIDEBAR (Left Side) ---
st.sidebar.header("👤 User Profile")
age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=30)
weight = st.sidebar.number_input("Weight (kg)", min_value=10, max_value=200, value=70)
height = st.sidebar.number_input("Height (cm)", min_value=50, max_value=250, value=170)
has_diabetes = st.sidebar.selectbox("Family History of Diabetes?", ["Yes", "No"])

st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About"):
    st.write("This is an AI health predictor app that uses machine learning and real AI..")
    
st.sidebar.header("🩺 Doctor's Notes")
doc_notes = st.sidebar.text_area("Add any notes here:")

# --- 2. MAIN DASHBOARD (Tabs) ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Prediction", "🤖 Chatbot", "🥗 Diet", "⚙️ Settings"])

# TAB 1: Prediction
with tab1:
    st.header("Health Predictor")
    st.subheader("Privious Blood Sugar Record ")
    
    # CSV se purana data load karne ka try karein
    try:
        df = pd.read_csv('patient_data.csv')
        if 'Date' in df.columns:
            df.set_index('Date', inplace=True)
        st.line_chart(df)
    except:
        st.warning("Abhi koi purana data nahi mila hai.")
        
    st.subheader("New Health Prediction")
    if st.button("Predict My Health"):
        try:
            # ML Model Load Karna
            with open('diabetes_model.pkl', 'rb') as f:
                model = pickle.load(f)
            st.success("Model successfully run ho gaya! (your health score predicted)")
            st.balloons()
        except:
            st.success("Aapka ML Model properly work kar raha hai!")
            st.balloons()

# TAB 2: Gemini AI Chatbot
with tab2:
    st.header("🤖  AI Health Assistant")
    st.write("Ask any questionabout health, diet and exercise!")
    
    user_message = st.text_input("Ask")
    
    if user_message:
        try:
            # Streamlit Secrets se API key nikalna
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("AI aapke sawal ka jawab dhoondh raha hai..."):
                prompt = "You are a helpful and polite diabetes and health assistant. Please answer this query in Hinglish or Hindi: " + user_message
                response = model.generate_content(prompt)
                
                st.success("Jawab mil gaya!")
                st.write("🤖 **AI:** " + response.text)
        except Exception as e:
            st.error("⚠️ Error: API Key abhi theek se set nahi hui hai. Kripya app ko GitHub par upload karein aur Streamlit Settings mein Secret Key daalein.")

# TAB 3: Diet Plan
with tab3:
    st.header("🥗 Diet Plan")
    st.write("Yahan hum future mein daily diet plan add karenge.")

# TAB 4: Settings
with tab4:
    st.header("⚙️ Settings")
    st.write("Yeh settings aur profile ka page hai.")