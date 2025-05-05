# Clinify.ai - Symptom Checker

Clinify.ai is a Streamlit-based symptom checker application that uses natural language processing and OpenAI to suggest possible diagnoses based on user-input symptoms.

## Project Objective

This web application allows users to:
1. Enter symptoms in free-text (natural language)
2. Get the top 3 most likely diagnoses based on the symptoms
3. Receive detailed AI-generated explanations and recommendations for each diagnosis

## How It Works

1. **Symptom Input**: Users describe their symptoms in a text area
2. **Symptom Extraction**: The app identifies known medical symptoms from the text
3. **Condition Matching**: A rule-based algorithm matches symptoms to potential conditions
4. **Diagnosis Display**: Top 3 most likely conditions are displayed as cards
5. **AI Explanation**: OpenAI (via LangChain) provides detailed explanations and next steps

## Installation and Setup

### Prerequisites
- Python 3.7+
- Streamlit
- LangChain
- OpenAI API key

### Running the App

1. Clone the repository:
```bash
git clone https://github.com/aaryapbh/clinify-ai-new.git
cd clinify-ai-new
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
streamlit run app.py
```

## Features

- 💬 Natural language symptom input
- 🔍 Intelligent symptom extraction
- 🩺 Rule-based diagnosis matching
- 📊 Confidence ratings for each diagnosis
- 🤖 AI-powered explanations and recommendations
- 📱 Responsive design for all devices

## Technologies Used

- **Streamlit**: Frontend interface
- **LangChain**: AI prompt engineering and integration
- **OpenAI GPT**: AI explanation generation
- **Python**: Backend processing

## Disclaimer

This application is for educational purposes only and is not intended to replace professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.
