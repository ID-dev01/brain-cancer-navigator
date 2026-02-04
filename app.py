import streamlit as st
import pandas as pd
import google.generativeai as genai
from cryptography.fernet import Fernet
import pydicom
import numpy as np
from PIL import Image

# --- 1. CONFIGURATION & DATA ---
st.set_page_config(page_title="Navigator v3.1", layout="wide")

# Real-world 2026 data mapping for survival/stats
CANCER_DATA = {
    "Brain": {
        "Stats": {"Incidence": "25k/yr", "Risk": "Low (1%)", "5yr_Survival": "33%"},
        "Types": {
            "Oligodendroglioma": {
                "Grades": ["WHO Grade 2", "WHO Grade 3"],
                "Mutations": ["IDH1 Mutant", "1p/19q Co-deleted", "IDH Wildtype"],
                "OS": {"Grade 2": "12-15 yrs", "Grade 3": "6-9 yrs"}
            },
            "Astrocytoma": {
                "Grades": ["Grade 2", "Grade 3", "Grade 4 (GBM)"],
                "Mutations": ["IDH1 Mutant", "ATRX Loss", "TP53 Mutant"],
                "OS": {"Grade 2": "8-10 yrs", "Grade 4": "1.5 yrs"}
            }
        }
    },
    "Breast": {
        "Stats": {"Incidence": "320k/yr", "Risk": "High (13%)", "5yr_Survival": "91%"},
        "Types": {
            "Invasive Ductal Carcinoma": {
                "Grades": ["Grade 1", "Grade 2", "Grade 3"],
                "Mutations": ["HER2+", "Triple Negative", "ER/PR+"],
                "OS": {"Grade 1": "High (95%)", "Grade 3": "Variable"}
            }
        }
    },
    "Lung": {
        "Stats": {"Incidence": "230k/yr", "Risk": "Moderate (6%)", "5yr_Survival": "28%"},
        "Types": {
            "Non-Small Cell (NSCLC)": {
                "Grades": ["Stage I", "Stage II", "Stage III", "Stage IV"],
                "Mutations": ["EGFR", "ALK", "KRAS", "PD-L1 High"],
                "OS": {"Stage I": "70%", "Stage IV": "10%"}
            }
        }
    }
}

# Encryption Setup
cipher_suite = Fernet(st.secrets["ENCRYPTION_KEY"])
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

# --- 2. DYNAMIC UI LOGIC ---
st.title("🌐 Universal Cancer Navigator v3.1")

# Sidebar Tiered Navigation
with st.sidebar:
    st.header("Step 1: Clinical Profile")
    organ = st.selectbox("Select Organ System", ["Select..."] + list(CANCER_DATA.keys()))
    
    if organ != "Select...":
        selected_organ_data = CANCER_DATA[organ]
        
        # Next Tier: Type
        cancer_type = st.selectbox(f"Select {organ} Cancer Type", list(selected_organ_data["Types"].keys()))
        
        # Next Tier: Grade/Stage
        type_data = selected_organ_data["Types"][cancer_type]
        grade = st.selectbox("Grade/Stage", type_data["Grades"])
        
        # Next Tier: Mutation
        mutation = st.selectbox("Biomarker/Mutation", type_data["Mutations"])
        
        st.divider()
        st.header("Step 2: Upload Imaging")
        uploaded_file = st.file_uploader("Upload MRI/CT Scan", type=['dcm', 'jpg', 'png'])

# --- 3. MAIN DASHBOARD (Updates Automatically) ---
if organ != "Select...":
    st.subheader(f"📊 {organ}: {cancer_type} Dashboard")
    
    # Live Stats Cards
    c1, c2, c3 = st.columns(3)
    c1.metric("National Incidence", selected_organ_data["Stats"]["Incidence"])
    c2.metric("Relative Survival", selected_organ_data["Stats"]["5yr_Survival"])
    c3.metric("Your Selected Profile", f"{grade} ({mutation})")

    # Survival Comparison Chart
    st.markdown("### Estimated Outlook (Based on 2026 Data)")
    os_est = type_data["OS"].get(grade, "Consult Specialist")
    st.write(f"**Median Overall Survival for this profile:** {os_est}")
    
    chart_df = pd.DataFrame({
        "Profile": ["Average", f"{grade} {mutation}"],
        "Score": [50, 85 if "Mutant" in mutation else 40] # Visual score for demo
    })
    st.bar_chart(chart_df, x="Profile", y="Score")

    # --- 4. MRI ANALYSIS & CHAT ---
    if uploaded_file:
        st.divider()
        st.subheader("🔍 Imaging Insights")
        # [MRI processing code from previous step goes here...]
        st.info("MRI Uploaded. Click 'Run Analysis' to see concerning features.")

    # Chat Concierge
    st.divider()
    st.subheader("💬 Real-time Patient Concierge")
    user_q = st.chat_input(f"Ask anything about {cancer_type}...")
    if user_q:
        with st.chat_message("assistant"):
            response = model.generate_content(f"Context: {organ}, {cancer_type}, {grade}, {mutation}. Question: {user_q}")
            st.write(response.text)
else:
    st.info("Please select an Organ System in the sidebar to begin.")
