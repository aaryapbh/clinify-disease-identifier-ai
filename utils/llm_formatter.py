import os
from typing import Dict, Optional, List
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

def get_openai_llm():
    """Initialize OpenAI LLM with optimal settings for medical analysis"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OpenAI API key not found. Please ensure the API key is properly configured.")
    
    try:
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=api_key
        )
    except Exception as e:
        raise Exception(f"Error initializing OpenAI model: {str(e)}")

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
            Base Match: {match_data.get('match_percentage', 0):.2%}
            """
        
        # Enhanced medical analysis prompt
        prompt_template = PromptTemplate(
            input_variables=["symptoms", "condition", "matched_symptoms", "context", "confidence_info"],
            template="""
            You are an experienced medical analysis system. Analyze the following case:

            PATIENT SYMPTOMS:
            {symptoms}

            CONDITION: {condition}
            MATCHED SYMPTOMS: {matched_symptoms}

            CONTEXT:
            {context}

            ANALYSIS METRICS:
            {confidence_info}

            Please provide a detailed analysis including:
            1. How the reported symptoms relate to {condition}
            2. Typical progression and severity
            3. Common risk factors
            4. Recommended actions
            5. When to seek immediate medical attention

            Format your response in markdown with clear sections.
            """
        )
        
        # Initialize LLM and chain
        llm = get_openai_llm()
        chain = LLMChain(llm=llm, prompt=prompt_template)
        
        # Generate analysis
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
        ### ⚠️ AI Analysis Temporarily Unavailable
        
        We're experiencing technical difficulties with our AI analysis system.
        However, we've identified that your symptoms may be related to {condition}.
        
        **Matched Symptoms:**
        {"".join([f"- {symptom}\\n" for symptom in matched_symptoms])}
        
        Please consult with a healthcare provider for proper diagnosis and treatment.
        
        Technical Details: {str(e)}
        """
