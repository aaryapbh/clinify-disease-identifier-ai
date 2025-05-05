import streamlit as st
import json
import os
from utils.match_engine import extract_symptoms, match_conditions
from utils.llm_formatter import get_explanation
from utils.config import check_api_key

# Initialize session states for modals
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False
if 'selected_condition' not in st.session_state:
    st.session_state.selected_condition = None
if 'selected_match' not in st.session_state:
    st.session_state.selected_match = None

def show_condition_details(condition, match):
    st.session_state.show_modal = True
    st.session_state.selected_condition = condition
    st.session_state.selected_match = match

def close_modal():
    st.session_state.show_modal = False
    st.session_state.selected_condition = None
    st.session_state.selected_match = None

# Modern UI Configuration
st.set_page_config(
    page_title="Clinify.ai - Smart Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom theme colors using st.markdown for CSS variables only
st.markdown("""
<style>
    :root {
        --primary-color: #2E3192;
        --secondary-color: #1E88E5;
        --accent-color: #00BFA6;
        --background-color: #F8F9FA;
        --text-color: #2C3E50;
    }
</style>
""", unsafe_allow_html=True)

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

# Create two main columns for layout
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    # Modern Header with gradient container
    header_container = st.container()
    with header_container:
        st.title("🩺 Clinify.ai")
        st.markdown("##### Your AI-Powered Health Assessment Assistant")
        st.divider()

    # Check API key status
    api_key_status = check_api_key()
    if not api_key_status:
        st.warning("⚠️ OpenAI API Key Required - Add your API key in the sidebar to enable AI-powered explanations.")

    # Initialize session state
    if 'diagnosis_results' not in st.session_state:
        st.session_state.diagnosis_results = None
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # Main content section with better spacing
    st.write("")  # Add spacing
    input_container = st.container()
    with input_container:
        st.markdown("### 🔍 Describe Your Symptoms")
        st.markdown("*Provide detailed information about your symptoms for more accurate analysis*")
        
        # Symptom input with better styling
        symptoms_text = st.text_area(
            "",
            placeholder="e.g., I've been experiencing a persistent headache for the past two days, accompanied by sensitivity to light...",
            height=120,
            key="symptoms_input",
            label_visibility="collapsed"
        )
        
        # Button layout with better spacing
        st.write("")  # Add spacing
        col1, col2, col3, col4 = st.columns([1, 1, 0.5, 1.5])
        with col1:
            submit_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
        with col2:
            clear_button = st.button("🔄 Clear", use_container_width=True)

with main_col2:
    # Information panel
    with st.container():
        st.markdown("### 📋 Quick Guide")
        st.info("""
        1. Enter your symptoms in detail
        2. Include duration and severity
        3. Mention any relevant history
        4. Add environmental factors
        """)

# Handle clear button
if clear_button:
    st.session_state.diagnosis_results = None
    st.session_state.submitted = False
    st.rerun()

# Process symptoms
if submit_button and symptoms_text:
    st.session_state.submitted = True
    
    with st.spinner("🔍 Analyzing your symptoms..."):
        extracted_symptoms, context = extract_symptoms(symptoms_text, conditions_data)
        
        if not extracted_symptoms:
            st.error("⚠️ No symptoms detected. Please provide more specific symptoms for accurate analysis.")
        else:
            matched_conditions = match_conditions(extracted_symptoms, conditions_data, context)
            st.session_state.diagnosis_results = {
                'symptoms_text': symptoms_text,
                'extracted_symptoms': extracted_symptoms,
                'top_matches': matched_conditions[:3] if matched_conditions else [],
                'context': context
            }

# Display results in a modern layout
if st.session_state.submitted and st.session_state.diagnosis_results:
    st.divider()
    
    # Results container
    results_container = st.container()
    with results_container:
        st.markdown("## 📊 Analysis Results")
        
        # Create tabs for different sections (removed Context tab)
        tab1, tab2 = st.tabs(["🎯 Matched Conditions", "🔍 Detected Symptoms"])
        
        with tab1:
            if st.session_state.diagnosis_results['top_matches']:
                # Create a grid layout for conditions
                for i in range(0, len(st.session_state.diagnosis_results['top_matches']), 2):
                    col1, col2 = st.columns(2)
                    
                    # First condition in row
                    with col1:
                        match = st.session_state.diagnosis_results['top_matches'][i]
                        with st.container():
                            # Header with condition name and confidence
                            st.markdown(f"### {match['condition']}")
                            confidence_color = {
                                "High": "green",
                                "Medium": "orange",
                                "Low": "red"
                            }[match['confidence']]
                            st.markdown(f"**Confidence:** :{confidence_color}[{match['confidence']}]")
                            
                            # Match statistics
                            st.metric(
                                "Matched Symptoms",
                                f"{match['match_count']}/{match['total_symptoms']}",
                                f"{(match['match_count']/match['total_symptoms']*100):.0f}% match"
                            )
                            
                            # View Details button
                            if st.button(f"🔍 View Details", key=f"view_{i}"):
                                show_condition_details(match['condition'], match)
                    
                    # Second condition in row (if exists)
                    if i + 1 < len(st.session_state.diagnosis_results['top_matches']):
                        with col2:
                            match = st.session_state.diagnosis_results['top_matches'][i + 1]
                            with st.container():
                                st.markdown(f"### {match['condition']}")
                                confidence_color = {
                                    "High": "green",
                                    "Medium": "orange",
                                    "Low": "red"
                                }[match['confidence']]
                                st.markdown(f"**Confidence:** :{confidence_color}[{match['confidence']}]")
                                
                                st.metric(
                                    "Matched Symptoms",
                                    f"{match['match_count']}/{match['total_symptoms']}",
                                    f"{(match['match_count']/match['total_symptoms']*100):.0f}% match"
                                )
                                
                                if st.button(f"🔍 View Details", key=f"view_{i+1}"):
                                    show_condition_details(match['condition'], match)
            
        with tab2:
            if st.session_state.diagnosis_results['extracted_symptoms']:
                # Create a more visual representation of symptoms
                st.markdown("### Detected Symptoms")
                symptoms_cols = st.columns(2)
                for idx, symptom in enumerate(st.session_state.diagnosis_results['extracted_symptoms']):
                    with symptoms_cols[idx % 2]:
                        st.success(f"✓ {symptom}")
            else:
                st.info("No specific symptoms were detected. Please try describing your symptoms in more detail.")

# Modal-like dialog for condition details
if st.session_state.show_modal:
    # Create a modal-like container
    modal_container = st.container()
    with modal_container:
        st.markdown("---")
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(f"## {st.session_state.selected_condition} - Detailed Analysis")
        with col2:
            if st.button("✕", help="Close"):
                close_modal()
        
        if api_key_status:
            with st.spinner("Generating detailed analysis..."):
                explanation = get_explanation(
                    symptoms=st.session_state.diagnosis_results['symptoms_text'],
                    condition=st.session_state.selected_condition,
                    matched_symptoms=st.session_state.selected_match['matched_symptoms'],
                    context=st.session_state.diagnosis_results['context'],
                    match_data=st.session_state.selected_match
                )
                
                # Display explanation in a structured way
                st.markdown(explanation)
        else:
            st.info(
                f"This condition matches the following symptoms:\n" +
                "\n".join([f"• {symptom}" for symptom in st.session_state.selected_match['matched_symptoms']]) +
                "\n\n*Add your OpenAI API key for detailed AI explanations.*"
            )
        st.markdown("---")

# Sidebar with improved layout
with st.sidebar:
    st.title("⚙️ Settings & Info")
    
    # API key section
    st.markdown("### 🔑 API Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Your key will not be stored permanently",
        placeholder="Enter your API key here..."
    )
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.success("✅ API key set successfully!")
        st.button("🔄 Refresh Analysis", on_click=st.rerun)
    
    st.divider()
    
    # About section
    st.markdown("### ℹ️ About Clinify.ai")
    st.markdown("""
    Clinify.ai combines advanced AI with medical knowledge to provide preliminary health assessments.
    
    **Key Features:**
    - 🤖 AI-powered analysis
    - 🔍 Symptom pattern matching
    - 📊 Confidence scoring
    - 📝 Detailed explanations
    """)
    
    st.divider()
    
    # Disclaimer
    st.caption("""
    ⚠️ **Medical Disclaimer**: This tool provides general information only and is not a substitute for professional medical advice. 
    Always consult with a healthcare professional for medical concerns.
    """)
