import streamlit as st
import pandas as pd
import numpy as np
import pickle

# 1. APP TITLE & CONFIGURATION
st.set_page_config(page_title="GlucoseGuard Dashboard", layout="wide")
st.title("🩸 GlucoseGuard: AI Health Predictor")

# 2. SIDEBAR - USER PROFILE & DOCTOR PORTAL
st.sidebar.header("👤 User Profile (Aapki Details)")
age = st.sidebar.number_input("Age (Umar)", min_value=1, max_value=120, value=30)
weight = st.sidebar.number_input("Weight (Vazan - kg)", min_value=10, max_value=200, value=70)
height = st.sidebar.number_input("Height (Lambaee - cm)", min_value=50, max_value=250, value=170)
has_diabetes = st.sidebar.selectbox("Diabetes Status", ["Non-Diabetic", "Type 1", "Type 2"])

st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About"):
    st.write("This is an AI health predictor that uses machine learning.")
st.sidebar.header("🩺 Doctor Portal")
doc_notes = st.sidebar.text_area("Doctor's Advice", "Keep daily carbs under 50g aur roz walk karein.")

# 3. MAIN DASHBOARD - DIFFERENT TABS
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard & Predictor", "🤖 AI Chatbot", "🥗 Meal & Exercise", "⚠️ Alerts"])

with tab1:
    st.header("Health Predictor Dashboard")
    st.subheader("Previous Blood Sugar Record")
    
    # CSV se purana data read karna
    try:
        df = pd.read_csv("patient_data.csv")
        df.set_index('Date', inplace=True)
        st.line_chart(df)
    except FileNotFoundError:
        st.warning("Pichla record nahi mila. (patient_data.csv missing hai)")
        
    st.subheader("🔮 AI Glucose Prediction")
    st.write("Aapke profile ke hisab se agla blood sugar level:")
    
    # Asli AI Model (Machine Learning) ka use
    if st.button("Predict My Blood Sugar"):
        st.success("AI Model aapka data analyzing...")
        
        # Status ko numbers mein badalna
        diabetes_mapping = {"Non-Diabetic": 0, "Type 1": 1, "Type 2": 2}
        status_num = diabetes_mapping[has_diabetes]
        
        try:
            # Model load karna jo humne pichle step mein train kiya tha
            with open('diabetes_model.pkl', 'rb') as file:
                model = pickle.load(file)
            
            # 🔥 Fix: AI se column names auto-match karna taaki ValueError na aaye
            user_data = pd.DataFrame([[age, weight, height, status_num]], 
                                     columns=model.feature_names_in_)
            predicted_sugar = model.predict(user_data)[0]
            
            st.metric(label="🧠 AI Predicted Fasting Blood Sugar", value=f"{round(predicted_sugar, 1)} mg/dL")
            st.balloons()
            
        except FileNotFoundError:
            st.error("Model file nahi mili! Kripya pehle train_model.py run karein.")
        except Exception as e:
            st.error(f"Prediction ke dauran ek error aaya: {e}")

with tab2:
    st.header("🤖 AI Health Assistant")
    st.write("Diabetes management ke baare mein kuch bhi puchein.")
    user_message = st.text_input("Ask")
    if user_message:
        msg = user_message.lower()
        if "walk" in msg or "exercise" in msg or "kasrat" in msg:
            st.write("🤖 **Chatbot:** Exercise karne se muscles blood se sugar absorb karti hain.")
        elif "sugar" in msg or "food" in msg or "khana" in msg:
            st.write("🤖 **Chatbot:** Khane mein high-fiber chizein (jaise salad) shamil karein.")
        else:
            st.write("🤖 **Chatbot:** Main abhi aapke sawal ka jawab seekh raha hoon!")

with tab3:
    st.header("🥗 Blood Sugar Maintain Kaise Karein")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Recommended Meal Plan")
        st.markdown("- **Breakfast:** Oats ya daliya nuts ke saath.\n- **Lunch:** Dal, sabzi, salad aur 1 multigrain roti.\n- **Dinner:** Tandoori paneer/chicken ya ubali hui sabziyan.")
    with col2:
        st.subheader("Daily Exercise Guide")
        st.markdown("- **Activity:** Khane ke baad 10-15 minute ki normal walk.\n- **Benefit:** Isse subah ki fasting sugar control mein rehti hai.")

with tab4:
    st.header("⚠️ Live Smart Alerts")
    st.info("Aapka daily health score: **85/100**. Keep it up!")
    st.warning("🔔 Alert: Apni dawai samay par lena na bhoolein.")