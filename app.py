import streamlit as st
import json
import os
from utils.match_engine import extract_symptoms, match_conditions
from utils.llm_formatter import get_explanation
from utils.config import check_api_key

# Initialize API key from environment variable or secrets
if 'OPENAI_API_KEY' not in st.session_state:
    st.session_state.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Function to set API key
def set_api_key(api_key):
    st.session_state.OPENAI_API_KEY = api_key
    os.environ["OPENAI_API_KEY"] = api_key

# Initialize session states for modals
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False
if 'selected_condition' not in st.session_state:
    st.session_state.selected_condition = None
if 'selected_match' not in st.session_state:
    st.session_state.selected_match = None

# Initialize session states
if 'show_details' not in st.session_state:
    st.session_state.show_details = None
if 'generated_explanation' not in st.session_state:
    st.session_state.generated_explanation = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'diagnosis_results' not in st.session_state:
    st.session_state.diagnosis_results = None

def show_condition_details(condition_name, match_data):
    """Display detailed information about a matched condition."""
    with st.expander(f"Details for {condition_name}", expanded=True):
        # Basic condition information
        st.markdown(f"### {condition_name}")
        st.markdown(f"**Severity Level:** {match_data['severity']}")
        st.markdown(f"**Match Confidence:** {match_data['confidence']}")
        
        # Match statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Matched Symptoms", 
                     f"{match_data['match_count']}/{match_data['total_symptoms']}", 
                     f"{(match_data['match_percentage']*100):.0f}% match")
        
        # Display matched symptoms
        st.markdown("#### ✓ Matched Symptoms")
        for symptom in match_data['matched_symptoms']:
            st.success(symptom)
        
        # Display condition description if available
        if 'description' in conditions_data[condition_name]:
            st.markdown("#### 📝 Description")
            st.write(conditions_data[condition_name]['description'])
        
        # Display recommendations if available
        if 'recommendations' in conditions_data[condition_name]:
            st.markdown("#### 💡 Recommendations")
            for rec in conditions_data[condition_name]['recommendations']:
                st.info(rec)
        
        # Medical disclaimer
        st.warning("""
        ⚠️ **Medical Disclaimer**: This is a preliminary analysis based on reported symptoms. 
        Please consult with a qualified healthcare professional for proper diagnosis and treatment.
        """)

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

# Add custom CSS for card styling
st.markdown("""
<style>
    .condition-card {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 1.5rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }
    .condition-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 5px;
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
        
        # Remove debug information displays
        if not extracted_symptoms:
            st.error("⚠️ No symptoms detected. Please provide more specific symptoms for accurate analysis.")
        else:
            # Get all symptoms from conditions data for matching
            all_symptoms = set()
            for condition in conditions_data.values():
                all_symptoms.update([s.lower() for s in condition['symptoms']])
            
            # Match conditions
            matched_conditions = []
            for condition_name, condition_data in conditions_data.items():
                condition_symptoms = [s.lower() for s in condition_data['symptoms']]
                matched_symptoms = [s for s in extracted_symptoms if s.lower() in condition_symptoms]
                
                if matched_symptoms:
                    match_percentage = len(matched_symptoms) / len(condition_data['symptoms'])
                    
                    # Determine confidence level
                    if match_percentage >= 0.7:
                        confidence = "High"
                    elif match_percentage >= 0.4:
                        confidence = "Medium"
                    else:
                        confidence = "Low"
                    
                    matched_conditions.append({
                        'condition': condition_name,
                        'match_count': len(matched_symptoms),
                        'total_symptoms': len(condition_data['symptoms']),
                        'match_percentage': match_percentage,
                        'confidence': confidence,
                        'matched_symptoms': matched_symptoms,
                        'severity': condition_data.get('severity', 'Unknown')
                    })
            
            # Sort by match percentage
            matched_conditions.sort(key=lambda x: x['match_percentage'], reverse=True)
            
            # Store in session state
            st.session_state.diagnosis_results = {
                'symptoms_text': symptoms_text,
                'extracted_symptoms': extracted_symptoms,
                'top_matches': matched_conditions[:3] if matched_conditions else [],
                'context': context
            }
            
            # Remove debug information display

# Display results in a modern layout
if st.session_state.submitted and st.session_state.diagnosis_results:
    st.divider()
    
    # Results container
    results_container = st.container()
    with results_container:
        st.markdown("## 📊 Analysis Results")
        
        # Create tabs for different sections
        tab1, tab2 = st.tabs(["🎯 Matched Conditions", "🔍 Detected Symptoms"])
        
        with tab1:
            if st.session_state.diagnosis_results['top_matches']:
                # Create a single row for all three conditions
                cols = st.columns(3)
                
                for idx, match in enumerate(st.session_state.diagnosis_results['top_matches']):
                    with cols[idx]:
                        with st.container():
                            st.markdown('<div class="condition-card">', unsafe_allow_html=True)
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
                                f"{(match['match_percentage']*100):.0f}% match"
                            )
                            
                            # View Details button
                            if st.button(f"🔍 View Details", key=f"view_{idx}"):
                                st.session_state.show_details = match['condition']
                            st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No conditions matched your symptoms. Please provide more detailed symptoms for better matching.")
        
        with tab2:
            if st.session_state.diagnosis_results['extracted_symptoms']:
                st.markdown("### 🔍 Detected Symptoms")
                for symptom in st.session_state.diagnosis_results['extracted_symptoms']:
                    st.success(f"✓ {symptom}")
            else:
                st.info("No specific symptoms were detected. Please try describing your symptoms in more detail.")
    
    # Display detailed information in a full-screen section below
    if st.session_state.show_details:
        st.divider()
        details_container = st.container()
        with details_container:
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"## 📋 Detailed Analysis: {st.session_state.show_details}")
            with col2:
                if st.button("✕ Close"):
                    st.session_state.show_details = None
                    st.rerun()
            
            # Get the match data for the selected condition
            selected_match = next(
                match for match in st.session_state.diagnosis_results['top_matches'] 
                if match['condition'] == st.session_state.show_details
            )
            
            # Basic Information Column
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Description
                if 'description' in conditions_data[selected_match['condition']]:
                    st.markdown("### 📝 Description")
                    st.write(conditions_data[selected_match['condition']]['description'])
                
                # Matched Symptoms
                st.markdown("### ✓ Matched Symptoms")
                for symptom in selected_match['matched_symptoms']:
                    st.success(symptom)
                
                # AI Analysis (generated only when viewing details)
                if api_key_status:
                    st.markdown("### 🤖 AI Analysis")
                    # Check if we already have generated explanation for this condition
                    if selected_match['condition'] not in st.session_state.generated_explanation:
                        with st.spinner("Generating AI analysis..."):
                            explanation = get_explanation(
                                symptoms=st.session_state.diagnosis_results['symptoms_text'],
                                condition=selected_match['condition'],
                                matched_symptoms=selected_match['matched_symptoms'],
                                context=st.session_state.diagnosis_results['context'],
                                match_data=selected_match
                            )
                            st.session_state.generated_explanation[selected_match['condition']] = explanation
                    
                    st.markdown(st.session_state.generated_explanation[selected_match['condition']])
            
            with col2:
                # Severity Level
                st.markdown("### ⚠️ Severity Level")
                st.warning(f"This condition is considered: **{selected_match['severity']}**")
                
                # Treatment Options
                if 'treatment' in conditions_data[selected_match['condition']]:
                    st.markdown("### 💊 Treatment Options")
                    for treatment in conditions_data[selected_match['condition']]['treatment']:
                        st.info(treatment)
                
                # Prevention Tips
                if 'prevention' in conditions_data[selected_match['condition']]:
                    st.markdown("### 🛡️ Prevention Tips")
                    for tip in conditions_data[selected_match['condition']]['prevention']:
                        st.info(tip)
                
                # Recommendations
                if 'recommendations' in conditions_data[selected_match['condition']]:
                    st.markdown("### 💡 Key Recommendations")
                    for rec in conditions_data[selected_match['condition']]['recommendations']:
                        st.success(rec)
            
            # Medical disclaimer at the bottom
            st.warning("""
            ⚠️ **Medical Disclaimer**: This analysis is for informational purposes only. 
            Always consult with a qualified healthcare professional for proper diagnosis and treatment.
            """)

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
        placeholder="Enter your API key here...",
        value=st.session_state.OPENAI_API_KEY
    )
    
    if api_key:
        set_api_key(api_key)
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
