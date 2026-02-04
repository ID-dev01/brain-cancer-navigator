import streamlit as st
import requests
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Neuro-Onco Navigator", layout="wide")

# Connect to Google Gemini (Free Tier)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- UI HEADER ---
st.title("🧠 Neuro-Onco Navigator")
st.markdown("### Global Brain Cancer Intelligence Briefing")

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("Search Filters")
    
    # 1. Expanded Cancer Type Dropdown
    cancer_options = [
        "Glioblastoma (GBM)", 
        "Astrocytoma", 
        "Oligodendroglioma", 
        "Diffuse Midline Glioma (DIPG)", 
        "Meningioma", 
        "Ependymoma", 
        "Medulloblastoma", 
        "Brain Metastases (Secondary)", 
        "CNS Lymphoma",
        "Other"
    ]
    selected_cancer = st.selectbox("Cancer Type", cancer_options)
    
    # Show text input if "Other" is selected
    if selected_cancer == "Other":
        cancer_type = st.text_input("Please specify cancer type:")
    else:
        cancer_type = selected_cancer

    # 2. Expanded Mutation Dropdown
    mutation_options = [
        "IDH1/IDH2 Mutant", 
        "IDH-Wildtype", 
        "MGMT Methylated", 
        "MGMT Unmethylated", 
        "EGFRvIII / EGFR Amplification", 
        "H3K27M", 
        "1p/19q Codeleted", 
        "BRAF V600E", 
        "PTEN Loss",
        "Other"
    ]
    selected_mutation = st.selectbox("Genetic Mutation / Marker", mutation_options)
    
    # Show text input if "Other" is selected
    if selected_mutation == "Other":
        mutation = st.text_input("Please specify mutation (e.g., TERT, PIK3CA):")
    else:
        mutation = selected_mutation

    region = st.selectbox("Region", ["Global", "United States", "Europe", "Asia"])
    search_button = st.button("Generate Intelligence Report")

# --- DATA FETCHING & AI LOGIC ---
def fetch_trials(mutation_query, condition):
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.cond": condition,
        "query.term": mutation_query,
        "pageSize": 8
    }
    response = requests.get(url, params=params)
    return response.json()

if search_button:
    if not cancer_type or not mutation:
        st.warning("Please specify both a Cancer Type and a Mutation.")
    else:
        with st.spinner(f"Analyzing global data for {mutation} in {cancer_type}..."):
            raw_trials = fetch_trials(mutation, cancer_type)
            
            prompt = f"""
            Act as a medical research navigator. I have raw clinical trial data for {cancer_type} with {mutation} mutation.
            Summarize this into a clean, 'App-style' dashboard.
            
            Structure your response with:
            1. 🏥 **Top Specialty Centers**: List centers involved.
            2. 🧪 **Active Clinical Trials**: List trials with Phase, Goal, and a clickable link (https://clinicaltrials.gov/study/[NCTID]).
            3. 📞 **Contact Information**: Extract names/emails/phones.
            4. 💡 **Research Direction**: A 3-sentence summary of what's currently being studied for this specific profile.
            
            Raw Data: {raw_trials}
            """
            
            try:
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
                st.success("Report Generated. Links are live.")
            except Exception as e:
                st.error(f"AI Service Error: {e}")
else:
    st.info("👈 Use the sidebar to filter by diagnosis and mutation.")

# --- FOOTER ---
st.markdown("---")
st.caption("⚠️ **Disclaimer**: This tool is for informational purposes only. It does not provide medical advice. Managed by Neuro-Onco Navigator.")
