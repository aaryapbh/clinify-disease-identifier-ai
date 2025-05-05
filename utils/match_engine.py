import re
import string

# We'll use a simpler tokenization approach to avoid NLTK dependency issues
def preprocess_text(text):
    """
    Preprocess text by converting to lowercase, removing punctuation, and simple word tokenization
    
    Args:
        text (str): Input text
        
    Returns:
        list: List of preprocessed tokens
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Simple tokenization by splitting on whitespace
    tokens = text.split()
    
    return tokens

def extract_symptoms(symptoms_text, conditions_data):
    """
    Extract symptoms from user input text by matching against known symptoms
    
    Args:
        symptoms_text (str): User-provided symptoms text
        conditions_data (dict): Dictionary of conditions and their symptoms
        
    Returns:
        list: List of extracted symptoms
    """
    if not symptoms_text:
        return []
    
    # Preprocess input text
    tokens = preprocess_text(symptoms_text)
    text_lower = symptoms_text.lower()
    
    # Create a list of all symptoms
    all_symptoms = set()
    for condition_data in conditions_data.values():
        all_symptoms.update(condition_data['symptoms'])
    
    # Extract symptoms that match the input text
    extracted_symptoms = []
    
    # First try exact matches
    for symptom in all_symptoms:
        if symptom.lower() in text_lower:
            extracted_symptoms.append(symptom)
    
    # Then try token-based matching for symptoms that weren't caught by exact matching
    if len(extracted_symptoms) < 2:  # Only do this if we found fewer than 2 symptoms
        for symptom in all_symptoms:
            if symptom not in extracted_symptoms:
                # Preprocess symptom
                symptom_tokens = preprocess_text(symptom)
                
                # Check if all tokens in the symptom are in the input text
                token_match_count = sum(1 for token in symptom_tokens if token in tokens)
                
                # If most of the tokens match, consider it a match
                if token_match_count >= max(1, len(symptom_tokens) * 0.6):
                    extracted_symptoms.append(symptom)
    
    return extracted_symptoms

def match_conditions(symptoms, conditions_data):
    """
    Match conditions based on extracted symptoms
    
    Args:
        symptoms (list): List of extracted symptoms
        conditions_data (dict): Dictionary of conditions and their symptoms
        
    Returns:
        list: List of matched conditions with confidence scores
    """
    if not symptoms:
        return []
    
    matches = []
    
    for condition_name, condition_data in conditions_data.items():
        condition_symptoms = condition_data['symptoms']
        
        # Find matching symptoms
        matched_symptoms = [s for s in symptoms if s in condition_symptoms]
        match_count = len(matched_symptoms)
        
        # Skip if no matches
        if match_count == 0:
            continue
        
        # Calculate match percentage
        match_percentage = match_count / len(condition_symptoms)
        
        # Determine confidence level
        confidence = "Low"
        if match_percentage >= 0.7:
            confidence = "High"
        elif match_percentage >= 0.4:
            confidence = "Medium"
        
        # Add to matches
        matches.append({
            'condition': condition_name,
            'match_count': match_count,
            'total_symptoms': len(condition_symptoms),
            'match_percentage': match_percentage,
            'confidence': confidence,
            'matched_symptoms': matched_symptoms
        })
    
    # Sort by match percentage (descending)
    matches.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return matches
