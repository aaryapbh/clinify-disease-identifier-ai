import streamlit as st
import json
import os
from utils.match_engine import extract_symptoms, match_conditions
from utils.llm_formatter import get_explanation
from utils.config import check_api_key

# Set page configuration
st.set_page_config(
    page_title="Clinify.ai - Symptom Checker",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load conditions data
@st.cache_data
def load_conditions():
    try:
        with open('data/conditions.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading conditions data: {e}")
        return {}

conditions_data = load_conditions()

# Header section
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/logo.svg", width=100)
with col2:
    st.title("Clinify.ai")
    st.subheader("Smart, AI-assisted health triage right from your symptoms")

st.markdown("---")

# Check if OpenAI API key is available
api_key_status = check_api_key()
if not api_key_status:
    st.warning("⚠️ OpenAI API key not found. Some features may be limited.")

# Initialize session state for storing results
if 'diagnosis_results' not in st.session_state:
    st.session_state.diagnosis_results = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Main content
st.markdown("### 🩺 Describe your symptoms")
st.markdown("Enter your symptoms in detail below, and our system will analyze them to suggest possible conditions.")

# Symptom input section
symptoms_text = st.text_area(
    "Describe your symptoms",
    placeholder="e.g. I've had chills, sore throat, and a mild fever since yesterday...",
    height=150
)

col1, col2 = st.columns([1, 5])
with col1:
    submit_button = st.button("Submit", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("Clear", use_container_width=True)

# Handle clear button
if clear_button:
    st.session_state.diagnosis_results = None
    st.session_state.submitted = False
    st.text_area(
        "Describe your symptoms",
        value="",
        placeholder="e.g. I've had chills, sore throat, and a mild fever since yesterday...",
        height=150,
        key="cleared_symptoms"
    )
    st.rerun()

# Process symptoms when submitted
if submit_button and symptoms_text:
    st.session_state.submitted = True
    
    with st.spinner("Analyzing your symptoms..."):
        # Extract symptoms from text
        extracted_symptoms = extract_symptoms(symptoms_text, conditions_data)
        
        if not extracted_symptoms:
            st.warning("No recognizable symptoms were found. Please try again with more specific symptoms.")
        else:
            # Match conditions based on symptoms
            matched_conditions = match_conditions(extracted_symptoms, conditions_data)
            
            # Store top 3 matches
            st.session_state.diagnosis_results = {
                'symptoms_text': symptoms_text,
                'extracted_symptoms': extracted_symptoms,
                'top_matches': matched_conditions[:3] if matched_conditions else []
            }

# Display results if available
if st.session_state.submitted and st.session_state.diagnosis_results:
    st.markdown("---")
    st.markdown("### 📋 Analysis Results")
    
    # Show extracted symptoms
    with st.expander("Symptoms Detected", expanded=True):
        if st.session_state.diagnosis_results['extracted_symptoms']:
            st.write(", ".join(st.session_state.diagnosis_results['extracted_symptoms']))
        else:
            st.write("No specific symptoms were detected. Please try describing your symptoms in more detail.")
    
    # Display top matches
    if st.session_state.diagnosis_results['top_matches']:
        st.markdown("### 🔍 Possible Diagnoses")
        st.markdown("Based on your symptoms, here are the most likely conditions:")
        
        # Create columns for the three cards
        cols = st.columns(3)
        
        # Display each condition in a card
        for i, match in enumerate(st.session_state.diagnosis_results['top_matches']):
            with cols[i]:
                confidence_color = "#28a745" if match['confidence'] == "High" else "#ffc107" if match['confidence'] == "Medium" else "#dc3545"
                
                st.markdown(f"""
                <div style="border: 1px solid #e6e6e6; border-radius: 5px; padding: 15px; height: 100%;">
                    <h3 style="color: #2c90cc;">{match['condition']}</h3>
                    <p>Confidence: <span style="color: {confidence_color}; font-weight: bold;">{match['confidence']}</span></p>
                    <p>Matched symptoms: {match['match_count']}/{match['total_symptoms']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add View Details expander
                with st.expander("View Details"):
                    st.markdown("##### Why this diagnosis was suggested:")
                    
                    if api_key_status:
                        # Get AI explanation using OpenAI
                        with st.spinner("Generating explanation..."):
                            explanation = get_explanation(
                                symptoms=st.session_state.diagnosis_results['symptoms_text'],
                                condition=match['condition'],
                                matched_symptoms=", ".join(match['matched_symptoms'])
                            )
                            st.markdown(explanation)
                    else:
                        st.markdown(f"""
                        This condition matches {match['match_count']} of your symptoms:
                        - {", ".join(match['matched_symptoms'])}
                        
                        For a detailed AI-powered explanation, please add your OpenAI API key.
                        """)
    else:
        st.warning("No conditions match your symptoms. Please try providing more detailed information about your symptoms.")

# Disclaimer
st.markdown("---")
st.markdown("""
### ⚠️ Medical Disclaimer
This tool provides general information only and is not a substitute for professional medical advice. 
Always consult with a healthcare professional for medical concerns.
""")

# App info in sidebar
with st.sidebar:
    st.markdown("## About Clinify.ai")
    st.markdown("""
    Clinify.ai is a rule-based symptom checker with AI-powered explanations.

    **How it works:**
    1. Enter your symptoms in natural language
    2. Our system analyzes your input
    3. View potential diagnoses with explanations
    4. Get recommendations for next steps
    
    **Note:** This application uses OpenAI's API for generating explanations.
    """)
    
    # Add OpenAI API key input in sidebar
    st.markdown("### OpenAI API Key")
    st.markdown("Add your OpenAI API key to enable AI-powered explanations.")
    
    api_key = st.text_input("OpenAI API Key", type="password", help="Your key will not be stored permanently")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.success("API key set successfully!")
        st.button("Refresh Analysis", on_click=st.rerun)
