import streamlit as st
import pandas as pd
import google.generativeai as genai
from google.api_core import exceptions
import time

# --- 1. DATA (CORE 2026 BENCHMARKS) ---
st.set_page_config(page_title="Universal Navigator v3.6", layout="wide")

CANCER_DATA = {
    "Brain": {
        "Stats": {"Incidence": "24,740 (US)", "5yr_Survival": "33%"},
        "Types": {
            "Astrocytoma": {"Grades": ["Grade 2", "Grade 3", "Grade 4"], "Mutations": ["IDH-mutant", "IDH-wildtype"]},
            "Oligodendroglioma": {"Grades": ["Grade 2", "Grade 3"], "Mutations": ["1p/19q Co-deleted", "IDH-mutant"]},
            "Other...": {}
        }
    },
    "Breast": {
        "Stats": {"Incidence": "324,580 (US)", "5yr_Survival": "91%"},
        "Types": {
            "Invasive Ductal": {"Grades": ["Grade 1", "Grade 2", "Grade 3"], "Mutations": ["HER2+", "Triple Negative", "ER/PR+"]},
            "Other...": {}
        }
    },
    "Other...": {"Stats": {"Incidence": "N/A", "5yr_Survival": "N/A"}, "Types": {"Other...": {}}}
}

# AI Setup
genai.configure(api_key=st.secrets["GEMINI_API_KEY"].strip())
model = genai.GenerativeModel('gemini-2.0-flash-lite')

def get_ai_stats(organ, c_type, grade):
    """Fallback for when 'Other' is selected"""
    prompt = f"Provide 2026 clinical statistics for {organ} {c_type} {grade}. Return in 3 bullets: 1. Incidence, 2. Median PFS, 3. 5-Year Survival."
    try:
        res = model.generate_content(prompt)
        return res.text
    except:
        return "Statistics currently unavailable for this rare type."

# --- 2. DYNAMIC SIDEBAR WITH 'OTHER' OVERRIDE ---
with st.sidebar:
    st.header("Step 1: Clinical Profile")
    
    # ORGAN SELECTION
    organ = st.selectbox("Select Organ", list(CANCER_DATA.keys()))
    if organ == "Other...":
        organ = st.text_input("Please specify Organ:", placeholder="e.g., Liver, Pancreas")
        c_type = st.text_input("Specify Type:", placeholder="e.g., Hepatocellular Carcinoma")
        grade = st.text_input("Specify Grade/Stage:", placeholder="e.g., Stage III")
        mutation = st.text_input("Specify Mutation (if known):", placeholder="e.g., TP53")
        is_other = True
    else:
        # TYPE SELECTION
        types_list = list(CANCER_DATA[organ]["Types"].keys())
        c_type = st.selectbox("Type", types_list)
        
        if c_type == "Other...":
            c_type = st.text_input("Specify Type:")
            grade = st.text_input("Specify Grade:")
            mutation = st.text_input("Specify Mutation:")
            is_other = True
        else:
            # NORMAL TIERED FLOW
            grade = st.selectbox("Grade", CANCER_DATA[organ]["Types"][c_type]["Grades"])
            mutation = st.selectbox("Mutation", CANCER_DATA[organ]["Types"][c_type]["Mutations"])
            is_other = False

# --- 3. DYNAMIC DASHBOARD ---
st.subheader(f"📊 {organ}: {c_type} {grade}")

col1, col2, col3 = st.columns(3)

if not is_other:
    # Use Hardcoded Data for Speed/Accuracy
    col1.metric("2026 Incidence", CANCER_DATA[organ]["Stats"]["Incidence"])
    col2.metric("5-Year Survival", CANCER_DATA[organ]["Stats"]["5yr_Survival"])
    col3.metric("Mutation Profile", mutation)
else:
    # Use AI for 'Other' selections
    with st.spinner("Consulting AI for rare cancer data..."):
        ai_data = get_ai_stats(organ, c_type, grade)
        st.info(ai_data)

# --- 4. CHAT CONCIERGE ---
st.divider()
st.subheader("💬 Clinical Chat")
if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if chat_in := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": chat_in})
    with st.chat_message("user"): st.markdown(chat_in)
    with st.chat_message("assistant"):
        res = model.generate_content(f"Context: {organ}, {c_type}, {grade}. User: {chat_in}")
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})
