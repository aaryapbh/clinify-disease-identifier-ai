import os
from typing import Dict, Optional, List
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

def get_openai_llm():
    """Initialize OpenAI LLM with optimal settings for medical analysis"""
    try:
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    except Exception as e:
        raise Exception(f"Error initializing OpenAI model: {e}")

def format_medical_context(context: Dict) -> str:
    """Format medical context into a structured string"""
    context_parts = []
    
    if context.get('duration'):
        context_parts.append(f"Duration: {context['duration']}")
    
    if context.get('severity'):
        context_parts.append(f"Severity Level: {context['severity']}")
    
    if context.get('medical_history'):
        history = '; '.join(context['medical_history'])
        context_parts.append(f"Medical History: {history}")
    
    if context.get('lifestyle'):
        lifestyle = ', '.join(context['lifestyle'])
        context_parts.append(f"Lifestyle Factors: {lifestyle}")
    
    if context.get('risk_factors'):
        risks = '; '.join(f"{risk[0]}: {risk[1]}" for risk in context['risk_factors'])
        context_parts.append(f"Risk Factors: {risks}")
    
    return "\n".join(context_parts) if context_parts else "No additional context available"

def get_explanation(
    symptoms: str,
    condition: str,
    matched_symptoms: List[str],
    context: Optional[Dict] = None,
    match_data: Optional[Dict] = None
) -> str:
    """
    Generate a comprehensive medical explanation using advanced LLM prompting
    
    Args:
        symptoms: User-reported symptoms
        condition: Diagnosed condition
        matched_symptoms: List of matched symptoms
        context: Additional medical context
        match_data: Matching confidence and analysis data
    """
    try:
        context = context or {}
        match_data = match_data or {}
        
        # Format context information
        context_str = format_medical_context(context)
        
        # Create confidence information
        confidence_info = ""
        if match_data:
            confidence_info = f"""
            Match Confidence: {match_data.get('confidence', 'Unknown')}
            Base Match: {match_data.get('base_match_percentage', 0):.2%}
            Context Score: {match_data.get('context_score', 0):.2%}
            """
        
        # Enhanced medical analysis prompt
        prompt_template = PromptTemplate(
            input_variables=["symptoms", "condition", "matched_symptoms", "context", "confidence_info"],
            template="""
            You are an experienced medical analysis system with comprehensive knowledge of clinical diagnosis.
            Analyze the following case with careful attention to detail and medical accuracy:

            PATIENT PRESENTATION:
            {symptoms}

            MEDICAL CONTEXT:
            {context}

            ANALYSIS METRICS:
            {confidence_info}

            CONDITION UNDER CONSIDERATION: {condition}
            MATCHED SYMPTOMS: {matched_symptoms}

            Please provide a detailed medical analysis following this structure:

            ### Symptom Analysis
            - Evaluate each reported symptom's relevance to {condition}
            - Note symptom patterns and combinations
            - Identify any potential red flags or critical indicators
            - Consider symptom severity and progression

            ### Clinical Overview
            - Provide a clear, accurate description of {condition}
            - Explain typical disease progression and variations
            - Discuss common risk factors and triggers
            - Note typical demographic and environmental factors

            ### Diagnostic Reasoning
            - Explain the strength of symptom matching
            - Analyze contextual factors affecting likelihood
            - Consider alternative explanations
            - Evaluate the reliability of the diagnosis

            ### Risk Assessment
            - Identify immediate health risks
            - Note potential complications
            - Consider long-term health implications
            - Evaluate need for urgent care

            ### Recommended Actions
            1. Immediate steps for symptom management
            2. Criteria for seeking emergency care
            3. Recommended medical consultations
            4. Suggested diagnostic tests
            5. Preventive measures

            ### Important Considerations
            - Note any limitations in the analysis
            - Highlight key uncertainties
            - Mention similar conditions to consider
            - Address special population considerations

            ### Medical Disclaimer
            This analysis is for informational purposes only and does not constitute medical advice. It is based on pattern matching and should not replace professional medical evaluation. Always consult qualified healthcare providers for diagnosis and treatment.

            Guidelines for response:
            - Use clear, accessible language while maintaining medical accuracy
            - Prioritize patient safety in recommendations
            - Be specific about when to seek immediate medical attention
            - Consider the full context of the patient's situation
            - Maintain a professional, evidence-based approach
            """
        )
        
        # Initialize LLM and chain
        llm = get_openai_llm()
        chain = LLMChain(llm=llm, prompt=prompt_template)
        
        # Generate comprehensive analysis
        result = chain.run({
            "symptoms": symptoms,
            "condition": condition,
            "matched_symptoms": ", ".join(matched_symptoms),
            "context": context_str,
            "confidence_info": confidence_info
        })
        
        return result
    
    except Exception as e:
        return f"""
        ### Error in Medical Analysis Generation
        
        We encountered an error while generating the detailed medical analysis.
        Please ensure your OpenAI API key is valid and try again.
        
        Error details: {str(e)}
        
        ### Important Notice
        
        The condition '{condition}' has been matched to your symptoms ({", ".join(matched_symptoms)}).
        However, this is not a definitive diagnosis. Please consult with a qualified healthcare provider
        for proper medical evaluation and treatment.
        """
