# AI Fitness Planner

A personalized fitness planning application that uses AI to create custom weekly exercise routines based on your profile and goals.

## Features
- Personalized exercise planning based on age, health conditions, and available time
- AI-powered recommendations using Ollama and Qwen2.5 14B model
- User-friendly Streamlit web interface
- Downloadable exercise plans
- Safety considerations for health conditions
- Support for two main fitness goals: weight loss and muscle gain

## User Input Requirements
The application asks for:
1. **Age** (in years) - for age-appropriate exercise recommendations
2. **Known health problems** - to ensure safe exercise recommendations
3. **Available exercise time per day** (in minutes) - to create realistic plans
4. **Fitness goal** - either "lose weight" or "gain muscle"

## Output
The application provides:
- A complete 7-day weekly exercise routine
- Specific exercises for each day with sets, reps, and duration
- Rest days and recovery recommendations
- Safety considerations based on health conditions
- Progression tips
- Downloadable text file of the exercise plan

## Prerequisites
- Python 3.10+ (currently tested with Python 3.14)
- Ollama running locally
- Qwen2.5 14B model installed in Ollama

## Environment Setup

The application supports environment variables for configuration. Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your settings
# .env file content:
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
API_KEY=your_api_key_here
```

**Supported Environment Variables:**
- `OLLAMA_HOST` - Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - Default AI model to use (default: gemma3:4b)
- `API_KEY` - API key for external services (optional)

## Setup
```bash
# Install Ollama and the required model
ollama pull qwen2.5:14b

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (see INSTALLATION.md for troubleshooting)
pip install -r requirements.txt
```

## Run
```bash
# Start Ollama (if not already running)
ollama serve

# Run the Streamlit app
streamlit run streamlit_app.py
```

Then open http://localhost:8501 in your browser.

## Usage
1. Fill out the personal information form
2. Provide details about your health conditions (be honest for safety)
3. Set your available daily exercise time
4. Choose your primary fitness goal
5. Click "Generate My Exercise Plan"
6. Review your personalized weekly routine
7. Download the plan for offline use

## Notes
- The app uses Ollama's API with the Qwen2.5 14B model for generating exercise plans
- All processing happens locally on your machine
- No personal data is stored or transmitted to external servers
- For deployment, ensure Ollama is accessible from the deployment environment

## Troubleshooting
- If installation fails, see `INSTALLATION.md` for detailed troubleshooting
- Ensure Ollama is running before using the app
- Make sure the Qwen2.5 14B model is installed: `ollama list`
