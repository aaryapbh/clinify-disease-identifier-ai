import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

def get_openai_llm():
    """Initialize OpenAI LLM"""
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    try:
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    except Exception as e:
        raise Exception(f"Error initializing OpenAI model: {e}")

def get_explanation(symptoms, condition, matched_symptoms):
    """
    Generate an explanation for a diagnosis using LangChain and OpenAI
    
    Args:
        symptoms (str): User-provided symptoms text
        condition (str): The diagnosed condition
        matched_symptoms (str): Comma-separated list of matched symptoms
        
    Returns:
        str: Explanation text
    """
    try:
        # Create prompt template
        prompt_template = PromptTemplate(
            input_variables=["symptoms", "condition", "matched_symptoms"],
            template="""
            You are a friendly medical assistant.
            A user entered the following symptoms: {symptoms}
            The matched diagnosis is: {condition}
            Based on matched symptoms: {matched_symptoms}, explain why this might be the case.
            
            First, explain in clear, simple terms why this condition matches their symptoms.
            
            Then, provide a brief explanation of the condition in plain, non-technical language.
            
            Finally, suggest appropriate next steps in a polite, clear, and medically responsible way.
            
            Important: Always emphasize that this is not a definitive diagnosis and the user should
            consult with a healthcare professional for proper evaluation and treatment.
            
            Format your response with markdown headings and bullet points for readability.
            """
        )
        
        # Initialize LLM
        llm = get_openai_llm()
        
        # Create chain
        chain = LLMChain(llm=llm, prompt=prompt_template)
        
        # Run chain
        result = chain.run({
            "symptoms": symptoms,
            "condition": condition,
            "matched_symptoms": matched_symptoms
        })
        
        return result
    
    except Exception as e:
        return f"""
        ### Error Generating Explanation
        
        We were unable to generate a detailed explanation. Please ensure your OpenAI API key is valid.
        
        Error details: {str(e)}
        
        ### General Advice
        
        The condition '{condition}' may be related to your symptoms: {matched_symptoms}.
        Please consult with a healthcare professional for proper diagnosis and treatment.
        """
