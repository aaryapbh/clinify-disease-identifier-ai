import re
import string
from typing import Dict, List, Tuple, Set

# We'll use a simpler tokenization approach to avoid NLTK dependency issues
def preprocess_text(text: str) -> List[str]:
    """
    Enhanced preprocessing with medical term preservation
    """
    # Preserve hyphenated terms and numbers
    text = re.sub(r'(?<![\w-])-|-(?![\w-])', ' ', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation except hyphens in words
    text = ''.join(c for c in text if c.isalnum() or c.isspace() or (c == '-' and text[text.index(c)-1].isalnum()))
    
    # Split on whitespace
    tokens = text.split()
    
    return tokens

def extract_context_clues(text: str) -> Dict:
    """
    Enhanced context extraction with medical relevance
    """
    context = {
        'duration': None,
        'severity': None,
        'risk_factors': [],
        'environmental': [],
        'medical_history': [],
        'medications': [],
        'lifestyle': []
    }
    
    # Enhanced duration patterns
    duration_patterns = [
        r'(\d+)\s*(day|days|week|weeks|month|months|year|years)',
        r'since\s+(yesterday|last\s+\w+)',
        r'for\s+(\d+|\w+)\s+(day|days|week|weeks|month|months|year|years)',
        r'(acute|chronic|intermittent|constant|recurring)'
    ]
    
    # Enhanced severity patterns with medical terminology
    severity_patterns = {
        'mild': r'(mild|slight|minor|barely|occasionally)',
        'moderate': r'(moderate|considerable|significant|noticeable)',
        'severe': r'(severe|intense|extreme|excruciating|unbearable|debilitating)'
    }
    
    # Medical history patterns
    medical_history_patterns = [
        r'(diagnosed with|history of|previous|chronic|runs in family|family history)',
        r'(surgery|operation|procedure)',
        r'(medication|taking|prescribed)',
        r'(allergic|allergy|allergies)'
    ]
    
    # Lifestyle and environmental patterns
    lifestyle_patterns = {
        'diet': r'(diet|eating|food|meal|nutrition)',
        'exercise': r'(exercise|activity|workout|sports)',
        'sleep': r'(sleep|insomnia|rest|tired)',
        'stress': r'(stress|anxiety|worried|tension)',
        'substance': r'(smoking|alcohol|drugs)',
        'occupation': r'(work|job|occupation|professional)'
    }
    
    # Extract duration
    for pattern in duration_patterns:
        match = re.search(pattern, text.lower())
        if match:
            context['duration'] = match.group(0)
            break
    
    # Extract severity
    for level, pattern in severity_patterns.items():
        if re.search(pattern, text.lower()):
            context['severity'] = level
            break
    
    # Extract medical history
    for pattern in medical_history_patterns:
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context['medical_history'].append(text[start:end].strip())
    
    # Extract lifestyle factors
    for category, pattern in lifestyle_patterns.items():
        if re.search(pattern, text.lower()):
            context['lifestyle'].append(category)
    
    return context

def calculate_symptom_weight(symptom: str, condition_data: Dict) -> float:
    """
    Calculate symptom importance weight based on medical knowledge
    """
    base_weight = 1.0
    
    # Critical symptoms get higher weight
    critical_symptoms = {
        'difficulty breathing', 'chest pain', 'shortness of breath',
        'severe headache', 'loss of consciousness', 'seizure',
        'coughing up blood', 'severe abdominal pain'
    }
    if symptom.lower() in critical_symptoms:
        base_weight *= 1.5
    
    # Condition-specific weight adjustments
    if 'severity' in condition_data:
        if condition_data['severity'] == 'severe':
            base_weight *= 1.2
    
    return base_weight

def extract_symptoms(symptoms_text: str, conditions_data: Dict) -> Tuple[List[str], Dict]:
    """
    Enhanced symptom extraction with medical context and common symptom variations
    """
    if not symptoms_text:
        return [], {}
    
    # Get enhanced context
    context = extract_context_clues(symptoms_text)
    
    # Preprocess input text
    tokens = preprocess_text(symptoms_text)
    text_lower = symptoms_text.lower()
    
    # Common symptom variations and synonyms
    common_symptoms = {
        "cold": ["cold", "common cold", "chill", "chills", "feeling cold"],
        "headache": ["headache", "head pain", "head ache", "migraine", "head pressure"],
        "fever": ["fever", "high temperature", "feeling hot", "temperature", "feverish"],
        "cough": ["cough", "coughing", "dry cough", "wet cough", "persistent cough"],
        "sore throat": ["sore throat", "throat pain", "throat ache", "painful throat", "scratchy throat"],
        "runny nose": ["runny nose", "nasal discharge", "nose running", "rhinorrhea"],
        "congestion": ["congestion", "stuffy nose", "blocked nose", "nasal congestion", "sinus"],
        "fatigue": ["fatigue", "tired", "tiredness", "exhaustion", "exhausted", "low energy"],
        "body ache": ["body ache", "muscle ache", "pain", "aches", "muscle pain", "body pain"],
        "nausea": ["nausea", "feeling sick", "queasy", "sick to stomach"],
        "vomiting": ["vomiting", "throwing up", "vomit", "threw up"],
        "diarrhea": ["diarrhea", "loose stool", "watery stool", "frequent bowel"],
        "dizziness": ["dizzy", "dizziness", "vertigo", "lightheaded", "light headed"],
        "weakness": ["weak", "weakness", "feeling weak", "loss of strength"],
        "chest pain": ["chest pain", "chest tightness", "chest pressure", "chest discomfort"],
        "shortness of breath": ["shortness of breath", "breathless", "difficulty breathing", "hard to breathe"],
        "stomach pain": ["stomach pain", "abdominal pain", "belly pain", "tummy pain"],
        "joint pain": ["joint pain", "arthralgia", "painful joints", "joint ache"],
        "rash": ["rash", "skin rash", "itchy skin", "skin irritation"],
        "swelling": ["swelling", "swollen", "edema", "puffiness"],
        "loss of appetite": ["loss of appetite", "poor appetite", "not hungry", "decreased appetite"],
        "insomnia": ["insomnia", "can't sleep", "difficulty sleeping", "trouble sleeping", "sleeplessness"],
        "anxiety": ["anxiety", "anxious", "worried", "nervousness", "panic"],
        "depression": ["depression", "depressed", "feeling down", "low mood", "sadness"],
        "back pain": ["back pain", "backache", "back ache", "pain in back"],
        "stiff neck": ["stiff neck", "neck pain", "neck stiffness", "painful neck"],
        "ear pain": ["ear pain", "earache", "ear ache", "painful ear"],
        "eye pain": ["eye pain", "painful eye", "eye ache", "eye discomfort"],
        "blurred vision": ["blurred vision", "blurry vision", "vision problems", "trouble seeing"],
        "numbness": ["numbness", "numb", "tingling", "pins and needles"]
    }
    
    # Create symptom variations with medical terminology
    all_symptoms: Set[str] = set()
    symptom_variations: Dict[str, List[str]] = {}
    
    # Add common symptoms to the variations
    for main_symptom, variations in common_symptoms.items():
        all_symptoms.add(main_symptom)
        symptom_variations[main_symptom] = variations
    
    # Add conditions data symptoms
    for condition_data in conditions_data.values():
        for symptom in condition_data['symptoms']:
            all_symptoms.add(symptom)
            base_variations = [
                symptom.lower(),
                symptom.lower().replace(' ', ''),
                symptom.lower().replace('-', ' '),
                symptom.lower().replace(' ', '-'),
                symptom.lower().replace('pain', 'ache'),
                symptom.lower().replace('ache', 'pain'),
                symptom.lower().replace('difficulty', 'trouble'),
                symptom.lower().replace('trouble', 'difficulty')
            ]
            # Add to existing variations if it's a common symptom
            if symptom in common_symptoms:
                base_variations.extend(common_symptoms[symptom])
            symptom_variations[symptom] = list(set(base_variations))
    
    # Extract symptoms with context and confidence
    extracted_symptoms = []
    symptom_contexts = {}
    symptom_confidence = {}
    
    # First pass: Check for common symptoms and their variations
    for symptom, variations in symptom_variations.items():
        for variation in variations:
            if variation in text_lower:
                if symptom not in extracted_symptoms:
                    extracted_symptoms.append(symptom)
                    match_idx = text_lower.find(variation)
                    start = max(0, match_idx - 30)
                    end = min(len(text_lower), match_idx + len(variation) + 30)
                    symptom_contexts[symptom] = text_lower[start:end]
                    symptom_confidence[symptom] = 1.0
                break
    
    # Second pass: Token-based matching for remaining symptoms
    if len(extracted_symptoms) < 3:  # Only do partial matching if we haven't found many symptoms
        for symptom in all_symptoms:
            if symptom not in extracted_symptoms:
                symptom_tokens = preprocess_text(symptom)
                token_match_count = sum(1 for token in symptom_tokens if token in tokens)
                if token_match_count >= max(1, len(symptom_tokens) * 0.7):  # Increased threshold
                    extracted_symptoms.append(symptom)
                    symptom_contexts[symptom] = symptoms_text
                    symptom_confidence[symptom] = token_match_count / len(symptom_tokens)
    
    return extracted_symptoms, {
        'symptom_contexts': symptom_contexts,
        'context_clues': context,
        'symptom_confidence': symptom_confidence
    }

def match_conditions(symptoms: List[str], conditions_data: Dict, context: Dict = None) -> List[Dict]:
    """
    Enhanced condition matching with medical knowledge and context
    """
    if not symptoms:
        return []
    
    matches = []
    context = context or {}
    context_clues = context.get('context_clues', {})
    symptom_confidence = context.get('symptom_confidence', {})
    
    for condition_name, condition_data in conditions_data.items():
        condition_symptoms = condition_data['symptoms']
        matched_symptoms = [s for s in symptoms if s in condition_symptoms]
        
        if not matched_symptoms:
            continue
        
        # Calculate weighted match score
        total_weight = 0
        matched_weight = 0
        
        for symptom in condition_symptoms:
            weight = calculate_symptom_weight(symptom, condition_data)
            total_weight += weight
            if symptom in matched_symptoms:
                confidence = symptom_confidence.get(symptom, 1.0)
                matched_weight += weight * confidence
        
        base_match_percentage = matched_weight / total_weight if total_weight > 0 else 0
        
        # Context-based adjustments
        context_score = 0
        
        # Risk factor analysis
        if 'risk_factors' in condition_data:
            for risk_factor in condition_data['risk_factors']:
                risk_matches = [
                    factor for factor, _ in context_clues.get('risk_factors', [])
                    if risk_factor.lower() in factor.lower()
                ]
                if risk_matches:
                    context_score += 0.15  # Increased weight for risk factors
        
        # Medical history analysis
        for history_item in context_clues.get('medical_history', []):
            if condition_name.lower() in history_item.lower():
                context_score += 0.2
        
        # Severity alignment
        if context_clues.get('severity') and 'severity' in condition_data:
            if context_clues['severity'] == condition_data['severity']:
                context_score += 0.1
        
        # Duration consideration
        if context_clues.get('duration'):
            duration_text = context_clues['duration'].lower()
            if 'chronic' in condition_data.get('severity', '').lower() and 'chronic' in duration_text:
                context_score += 0.15
            elif 'acute' in condition_data.get('severity', '').lower() and any(word in duration_text for word in ['day', 'week', 'recent']):
                context_score += 0.15
        
        # Calculate final score
        adjusted_percentage = min(1.0, base_match_percentage + context_score)
        
        # Determine confidence level with original three levels
        if adjusted_percentage >= 0.7:
            confidence = "High"
        elif adjusted_percentage >= 0.4:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        matches.append({
            'condition': condition_name,
            'match_count': len(matched_symptoms),
            'total_symptoms': len(condition_symptoms),
            'match_percentage': adjusted_percentage,
            'confidence': confidence,
            'matched_symptoms': matched_symptoms,
            'context_factors': [factor for factor, _ in context_clues.get('risk_factors', [])],
            'base_match_percentage': base_match_percentage,
            'context_score': context_score
        })
    
    # Sort by adjusted match percentage
    matches.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return matches
