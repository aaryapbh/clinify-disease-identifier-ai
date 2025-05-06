# Clinify.ai - Your AI Health Assistant

Hey there! 👋 I'm excited to share Clinify.ai with you. This is a health assessment tool I built that helps people understand their symptoms using AI. Let me walk you through how it works and how you can set it up yourself.

## What Does It Do?

When you run Clinify.ai, you'll see a clean interface where you can:
1. Type in your symptoms in everyday language
2. Get instant analysis of possible conditions
3. See detailed explanations of why certain conditions might match
4. Get suggestions about what to do next

## Setting It Up

I'll guide you through setting this up on your machine. Don't worry if you're not super technical - I'll explain each step!

### What You'll Need First
- Python (version 3.9 or newer)
- An OpenAI API key (I'll show you how to get this)
- About 5-10 minutes of your time

### Step-by-Step Setup

1. **First, Get the Code**
   ```bash
   git clone https://github.com/aaryapbh/clinify-disease-identifier-ai.git
   cd clinify-disease-identifier-ai
   ```
   This downloads all the code to your computer and moves you into the right folder.

2. **Set Up Your Python Environment**
   ```bash
   # If you're on Mac/Linux:
   python3 -m venv venv
   source venv/bin/activate

   # If you're on Windows:
   python -m venv venv
   .\venv\Scripts\activate
   ```
   This creates a clean space for our app's dependencies.

3. **Install What We Need**
   ```bash
   pip install -r requirements.txt
   ```
   This gets all the libraries we use - Streamlit for the interface, OpenAI for AI features, and other helpers.

4. **Set Up Your OpenAI Key**
   
   You'll need an API key from OpenAI. Here's how to set it up:
   1. Go to [OpenAI's platform](https://platform.openai.com)
   2. Create an account or sign in
   3. Go to API keys section
   4. Create a new key
   5. Save it somewhere safe!

   Then, create a file named `.streamlit/secrets.toml` and add:
   ```toml
   OPENAI_API_KEY = "your-key-here"
   ```

5. **Start the App**
   ```bash
   streamlit run app.py
   ```
   The app should open in your browser at `http://localhost:8501`

## How I Built This

Let me walk you through how I put this together:

### The Interface (app.py)
I used Streamlit to create a clean, simple interface where:
- You type your symptoms in a text box
- The app processes them in real-time
- Results appear in an organized layout with confidence levels
- You can click for detailed explanations

Here's what the main interface looks like:
```python
# The main symptom input area
symptoms_text = st.text_area(
    "Describe Your Symptoms",
    placeholder="e.g., I've been having a headache and fever since yesterday..."
)

# When you click analyze
if st.button("Analyze Symptoms"):
    results = process_symptoms(symptoms_text)
    show_results(results)
```

### The Brain (utils/match_engine.py)
This is where the magic happens. The symptom matcher:
1. Takes your description
2. Identifies key symptoms
3. Matches them against known conditions
4. Calculates how confident it is about each match

For example, if you type "severe headache with sensitivity to light", it:
- Recognizes "severe headache" and "sensitivity to light" as symptoms
- Identifies these as common migraine indicators
- Checks for other conditions with similar symptoms
- Ranks them by how well they match

### The Knowledge Base (data/conditions.json)
I've included information about common conditions like:
- Cold and Flu
- Migraines
- COVID-19
- Allergies
- And many more...

Each condition has:
- Common symptoms
- Severity levels
- Risk factors

### The AI Explanation System
When you click for more details, the app:
1. Takes the symptoms you described
2. Looks at the matched condition
3. Uses GPT-4 to explain in plain language:
   - Why this condition matches your symptoms
   - What you might want to know about it
   - When you should consider seeing a doctor

## Testing It Out

Try these examples to see how it works:
1. "I have a headache and fever since yesterday"
2. "My throat is sore and I'm coughing a lot"
3. "Feeling very tired with muscle aches"

## Important Notes

- This is a helper tool, not a replacement for doctors
- Always seek professional medical advice for health concerns
- Your data isn't stored - everything is processed in memory only
- The OpenAI API key is used only for generating explanations

## Need Help?

If you run into any issues:
1. Check that your OpenAI API key is set up correctly
2. Make sure you have all the requirements installed
3. Create an issue on GitHub if you're stuck

## Want to Make It Better?

I'd love your help making this tool even better! Feel free to:
- Suggest new features
- Report bugs
- Contribute code
- Add more medical conditions to the database

## License

This project is under the MIT License - feel free to use it, modify it, share it!

---

Built by Aarya Bhardwaj with a focus on making health information more accessible and understandable.
