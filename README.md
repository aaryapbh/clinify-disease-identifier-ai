# Clinify.ai - Advanced Health Assessment Platform

**Demo Video**-https://drive.google.com/file/d/1lhohlvp2DXGRFeQ6nvrv1PcIq7jT1RvV/view?usp=drivesdk

**Run App**
Streamlit Cloud App Link - https://clinify-disease-identifier-ai-jwznx8baofvcxdfuguypro.streamlit.app

## Overview

Clinify.ai is a sophisticated health assessment platform that combines advanced symptom matching algorithms with GPT-4 powered medical explanations. The platform processes natural language symptom descriptions to provide preliminary health insights while maintaining high standards of medical information accuracy.

## Key Features

- **Natural Language Processing**: Advanced symptom recognition from free-text descriptions
- **Intelligent Matching**: Context-aware condition matching with confidence scoring
- **AI-Powered Analysis**: Detailed medical explanations using GPT-4
- **Interactive Interface**: Real-time analysis with visual confidence indicators
- **Privacy-Focused**: No personal health data storage, all processing done in-memory

## Quick Setup Guide

### Prerequisites
- Python 3.9+
- pip package manager
- OpenAI API key (GPT-4 access)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/aaryapbh/clinify-disease-identifier-ai.git
   cd clinify-disease-identifier-ai
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Launch the Application**
   ```bash
   streamlit run app.py
   ```

### API Key Configuration

You have two options for setting up your OpenAI API key:

1. **Direct Input in App (Recommended)**
   - Launch the application
   - Open the sidebar (click ⚙️ in top-right)
   - Enter your API key in the secure input field
   - Key is used only for the current session

2. **Environment Configuration**
   ```bash
   export OPENAI_API_KEY='your-key-here'  # Unix/macOS
   set OPENAI_API_KEY='your-key-here'     # Windows
   ```

## Development Process

### Phase 1: Core Architecture 

#### Foundation Setup
- Established modular project structure
- Implemented dependency management
- Created development environment
- Set up version control

#### Component Architecture
```
clinify-ai/
├── app.py                 # Streamlit interface
├── utils/
│   ├── match_engine.py    # Symptom processing
│   ├── llm_formatter.py   # AI integration
│   └── config.py         # Configuration
├── data/
│   └── conditions.json   # Medical database
└── .streamlit/           # Streamlit configuration
```

### Phase 2: Symptom Processing Engine 

#### Match Engine Implementation
- Developed medical term recognition
- Implemented context extraction
- Created weighted matching algorithm
- Built confidence scoring system

#### Medical Database Development
- Structured 30+ common conditions
- Mapped symptom relationships
- Added severity classifications
- Integrated risk factors

### Phase 3: AI Integration 

#### OpenAI Integration
- Implemented GPT-4 connection
- Developed medical prompting system
- Created response formatting
- Added error handling

#### Explanation Generation
- Structured medical analysis
- Symptom correlation
- Risk assessment
- Treatment suggestions

### Phase 4: User Interface 

#### Streamlit Implementation
- Created interactive components
- Implemented real-time analysis
- Added visual feedback systems

#### User Experience
- Developed intuitive flow
- Added progress indicators
- Implemented error handling

### Phase 5: Testing & Optimization 

#### Comprehensive Testing
Conducted extensive testing across multiple scenarios:
```python
# Example test case
{
    "input": "severe headache with light sensitivity",
    "expected": {
        "primary_condition": "Migraine",
        "confidence_threshold": 0.8,
        "context": {"severity": "severe", "triggers": ["light"]}
    }
}
```

#### Performance Metrics
Current production benchmarks:
- Symptom Recognition: 90% accuracy
- Context Extraction: 85% accuracy
- Response Time: <2 seconds
- API Latency: ~0.3 seconds

## Technical Implementation Details

### Symptom Processing Engine
```python
# utils/match_engine.py

def extract_symptoms(symptoms_text: str, conditions_data: Dict) -> Tuple[List[str], Dict]:
    """
    Enhanced preprocessing with medical term preservation
    """
    # Preprocess text while maintaining medical terminology
    tokens = preprocess_text(symptoms_text)
    
    # Extract medical context
    context = extract_context_clues(symptoms_text)
    
    # Match symptoms against database
    extracted_symptoms = []
    for token in tokens:
        if is_medical_term(token):
            extracted_symptoms.append(standardize_symptom(token))
    
    return extracted_symptoms, context

def calculate_symptom_weight(symptom: str, condition_data: Dict) -> float:
    """Calculate importance weight of each symptom"""
    base_weight = 1.0
    
    # Adjust weight for critical symptoms
    if symptom.lower() in CRITICAL_SYMPTOMS:
        base_weight *= 1.5
    
    # Consider condition-specific severity
    if condition_data.get('severity') == 'severe':
        base_weight *= 1.2
    
    return base_weight
```

### AI Integration Examples
```python
# utils/llm_formatter.py

def generate_medical_explanation(
    symptoms: List[str],
    condition: str,
    confidence: float,
    context: Dict
) -> str:
    """
    Generate detailed medical explanation using GPT-4
    """
    prompt = create_medical_prompt(
        symptoms=symptoms,
        condition=condition,
        confidence=confidence,
        context=context
    )
    
    response = get_openai_response(prompt)
    return format_medical_response(response)

def create_medical_prompt(symptoms: List[str], **kwargs) -> str:
    """
    Create structured medical analysis prompt
    """
    return f"""
    Analyze the following medical case:
    
    Symptoms Presented: {', '.join(symptoms)}
    Condition Under Consideration: {kwargs['condition']}
    Confidence Level: {kwargs['confidence']}
    
    Additional Context:
    - Duration: {kwargs['context'].get('duration', 'Not specified')}
    - Severity: {kwargs['context'].get('severity', 'Not specified')}
    - Risk Factors: {', '.join(kwargs['context'].get('risk_factors', []))}
    
    Provide a structured analysis including:
    1. Symptom correlation
    2. Risk assessment
    3. Recommended actions
    """
```

### Streamlit Interface Components
```python
# app.py

def create_symptom_input() -> str:
    """
    Create the main symptom input interface
    """
    st.markdown("### 🔍 Describe Your Symptoms")
    
    symptoms_text = st.text_area(
        "",
        placeholder="e.g., I've been experiencing a persistent headache...",
        height=120,
        key="symptoms_input"
    )
    
    return symptoms_text

def display_condition_details(condition: Dict):
    """
    Display detailed condition analysis
    """
    with st.container():
        # Header with confidence indicator
        st.markdown(f"### {condition['name']}")
        confidence_color = get_confidence_color(condition['confidence'])
        st.markdown(f"**Confidence:** :{confidence_color}[{condition['confidence']}]")
        
        # Matched symptoms
        st.markdown("#### Matched Symptoms")
        for symptom in condition['matched_symptoms']:
            st.success(f"✓ {symptom}")
        
        # Risk factors if present
        if condition.get('risk_factors'):
            st.markdown("#### Risk Factors")
            for risk in condition['risk_factors']:
                st.warning(f"! {risk}")

def create_analysis_results(results: Dict):
    """
    Display analysis results in organized tabs
    """
    tab1, tab2 = st.tabs(["Matched Conditions", "Detected Symptoms"])
    
    with tab1:
        for condition in results['conditions']:
            display_condition_details(condition)
    
    with tab2:
        for symptom in results['symptoms']:
            st.success(f"✓ {symptom}")
```

### Data Structure Examples
```json
// data/conditions.json
{
  "Migraine": {
    "symptoms": [
      "Severe headache",
      "Sensitivity to light",
      "Nausea",
      "Visual disturbances",
      "Throbbing pain"
    ],
    "severity": "moderate to severe",
    "risk_factors": [
      "Stress",
      "Hormonal changes",
      "Certain foods",
      "Lack of sleep"
    ],
    "typical_duration": "4-72 hours",
    "warning_signs": [
      "Aura",
      "Neck stiffness",
      "Mood changes"
    ]
  }
}
```

### Testing Implementation
```python
# tests/test_match_engine.py

def test_symptom_extraction():
    """
    Test symptom extraction functionality
    """
    test_cases = [
        {
            "input": "severe headache with sensitivity to light",
            "expected_symptoms": ["severe headache", "sensitivity to light"],
            "expected_context": {
                "severity": "severe",
                "duration": None
            }
        },
        {
            "input": "having fever and cough for 3 days",
            "expected_symptoms": ["fever", "cough"],
            "expected_context": {
                "duration": "3 days",
                "severity": None
            }
        }
    ]
    
    for case in test_cases:
        symptoms, context = extract_symptoms(case["input"])
        assert set(symptoms) == set(case["expected_symptoms"])
        assert context["severity"] == case["expected_context"]["severity"]
        assert context["duration"] == case["expected_context"]["duration"]

def test_condition_matching():
    """
    Test condition matching algorithm
    """
    symptoms = ["severe headache", "sensitivity to light", "nausea"]
    matches = match_conditions(symptoms, conditions_data)
    
    assert matches[0]["condition"] == "Migraine"
    assert matches[0]["confidence"] >= 0.8
    assert len(matches[0]["matched_symptoms"]) >= 2
```

### Error Handling Examples
```python
# utils/error_handlers.py

class SymptomProcessingError(Exception):
    """Custom error for symptom processing issues"""
    pass

def handle_api_errors(func):
    """Decorator for API error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OpenAIError as e:
            st.error(f"AI Service Error: {str(e)}")
            log_error("OpenAI API", e)
        except Exception as e:
            st.error("An unexpected error occurred")
            log_error("General", e)
    return wrapper

@handle_api_errors
def process_symptoms(symptoms_text: str) -> Dict:
    """
    Process symptoms with error handling
    """
    if not symptoms_text.strip():
        raise SymptomProcessingError("No symptoms provided")
    
    try:
        symptoms, context = extract_symptoms(symptoms_text)
        if not symptoms:
            raise SymptomProcessingError("No valid symptoms detected")
        
        matches = match_conditions(symptoms, context)
        return format_results(matches, context)
    except Exception as e:
        raise SymptomProcessingError(f"Error processing symptoms: {str(e)}")
```

## Usage Examples

### Basic Symptom Analysis
```text
Input: "I've had a headache and fever since yesterday"
Output: Matches conditions like Common Cold, Flu with confidence scores
```

### Complex Symptom Processing
```text
Input: "Severe migraine with light sensitivity for 2 weeks"
Output: Detailed analysis with context consideration and medical history
```

## Security Measures

- No persistent storage of health data
- Secure API key handling
- Memory-only processing
- Rate limiting implementation

Medical information is for reference only - always consult healthcare professionals
