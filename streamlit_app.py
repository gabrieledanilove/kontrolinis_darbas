import streamlit as st
import requests
import json

# Configure the page
st.set_page_config(
    page_title="AI Fitness Planner",
    page_icon="💪",
    layout="wide"
)

# Main app
def main():
    st.title("💪 AI Fitness Planner")
    st.write("Get a personalized weekly exercise plan using AI")
    
    # Sidebar for Ollama configuration
    with st.sidebar:
        st.header("AI Configuration")
        
        # Ollama server settings
        ollama_host = st.text_input("Ollama Host", value="http://localhost:11434")
        model_name = st.selectbox(
            "Model Name", 
            options=[
                "gemma3:4b",       # Current installed model
                "llama3.2:3b",     # Faster, smaller model
                "qwen2.5:7b",      # Medium size
                "qwen2.5:14b",     # Large model (as originally specified)
                "llama3.1:8b",     # Good balance
                "phi3:mini"        # Very fast, small model
            ],
            index=0,
            help="Select an available model. Smaller models (3b/4b) are faster but less detailed."
        )
        
        # Check model availability
        if st.button("Check Available Models"):
            try:
                response = requests.get(f"{ollama_host}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    if models:
                        st.success("Available models:")
                        for model in models:
                            st.write(f"- {model['name']}")
                    else:
                        st.warning("No models found. Install a model first.")
                else:
                    st.error("Cannot connect to Ollama")
            except:
                st.error("Ollama is not running or not accessible")
        
        st.info("Make sure Ollama is running and your selected model is installed")
    
    # Main form for user input
    st.header("Tell us about yourself")
    
    with st.form("fitness_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input(
                "Your age (years)", 
                min_value=13, 
                max_value=100, 
                value=25,
                help="Enter your age to get age-appropriate exercise recommendations"
            )
            
            exercise_time = st.number_input(
                "Available exercise time per day (minutes)", 
                min_value=10, 
                max_value=300, 
                value=30,
                help="How many minutes can you dedicate to exercise each day?"
            )
        
        with col2:
            health_problems = st.text_area(
                "Known health problems", 
                placeholder="e.g., back pain, knee issues, heart condition, diabetes, etc. (write 'none' if no issues)",
                help="List any health conditions that might affect your exercise routine"
            )
            
            goal = st.selectbox(
                "Your fitness goal",
                ["Lose weight", "Gain muscle"],
                help="Choose your primary fitness objective"
            )
        
        submitted = st.form_submit_button("Generate My Exercise Plan", type="primary")
    
    # Process form submission
    if submitted:
        if not health_problems.strip():
            st.error("Please fill in all fields. Write 'none' if you have no health problems.")
            return
            
        # Create prompt for AI
        prompt = f"""You are a professional fitness trainer and exercise physiologist. Create a personalized weekly exercise plan for a person with the following details:

Age: {age} years
Health problems: {health_problems}
Available exercise time per day: {exercise_time} minutes
Fitness goal: {goal.lower()}

Please provide:
1. A complete 7-day weekly exercise routine
2. Specific exercises for each day
3. Sets, reps, and duration for each exercise
4. Rest days and recovery recommendations
5. Safety considerations based on their health conditions
6. Tips for progression

Format your response clearly with each day of the week and the recommended exercises. Make sure the plan is safe and appropriate for their age, health conditions, and available time."""

        # Display loading message
        with st.spinner("Creating your personalized exercise plan..."):
            try:
                # First, check if the model is available
                models_response = requests.get(f"{ollama_host}/api/tags", timeout=10)
                if models_response.status_code == 200:
                    available_models = [model['name'] for model in models_response.json().get("models", [])]
                    if model_name not in available_models:
                        st.error(f"Model '{model_name}' is not installed!")
                        st.write("Available models:", available_models)
                        st.write(f"To install the model, run: `ollama pull {model_name}`")
                        return
                else:
                    st.error("Cannot connect to Ollama. Make sure it's running.")
                    return
                
                # Create a more focused prompt for faster processing
                focused_prompt = f"""Create a concise weekly exercise plan for:
- Age: {age} years
- Health: {health_problems}
- Daily time: {exercise_time} minutes
- Goal: {goal.lower()}

Provide a 7-day schedule with specific exercises, sets/reps, and safety notes. Keep it practical and brief."""

                # Try streaming first for faster response
                response = requests.post(
                    f"{ollama_host}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": focused_prompt,
                        "stream": True,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 1500  # Limit response length for faster generation
                        }
                    },
                    timeout=120,  # Increased timeout
                    stream=True
                )
                
                if response.status_code == 200:
                    # Handle streaming response
                    exercise_plan = ""
                    response_placeholder = st.empty()
                    
                    try:
                        for line in response.iter_lines():
                            if line:
                                chunk = line.decode('utf-8')
                                if chunk.strip():
                                    try:
                                        data = json.loads(chunk)
                                        if 'response' in data:
                                            exercise_plan += data['response']
                                            # Update the display in real-time
                                            response_placeholder.markdown(f"**Generating plan...**\n\n{exercise_plan}")
                                        if data.get('done', False):
                                            break
                                    except json.JSONDecodeError:
                                        continue
                    except Exception as stream_error:
                        st.warning(f"Streaming interrupted: {stream_error}")
                        # Fallback to non-streaming if streaming fails
                        if not exercise_plan.strip():
                            st.info("Trying non-streaming approach...")
                            response = requests.post(
                                f"{ollama_host}/api/generate",
                                json={
                                    "model": model_name,
                                    "prompt": focused_prompt,
                                    "stream": False,
                                    "options": {"num_predict": 1000}
                                },
                                timeout=180  # Even longer timeout for non-streaming
                            )
                            if response.status_code == 200:
                                result = response.json()
                                exercise_plan = result.get("response", "No response received")
                    
                    response_placeholder.empty()  # Clear the generating message
                    
                    if exercise_plan.strip():
                        # Display the exercise plan
                        st.success("Your personalized exercise plan is ready!")
                        
                        # Create a nice display for the plan
                        st.header("📋 Your Weekly Exercise Plan")
                        
                        # User summary
                        with st.expander("Your Profile Summary", expanded=False):
                            st.write(f"**Age:** {age} years")
                            st.write(f"**Health Considerations:** {health_problems}")
                            st.write(f"**Daily Exercise Time:** {exercise_time} minutes")
                            st.write(f"**Goal:** {goal}")
                        
                        # Exercise plan
                        st.markdown(exercise_plan)
                        
                        # Download option
                        st.download_button(
                            label="📥 Download Exercise Plan",
                            data=f"Personal Exercise Plan\n\nAge: {age} years\nHealth Considerations: {health_problems}\nDaily Exercise Time: {exercise_time} minutes\nGoal: {goal}\n\n{exercise_plan}",
                            file_name=f"exercise_plan_{goal.lower().replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("No response generated. The model might be overloaded.")
                        
                elif response.status_code == 404:
                    st.error(f"Model '{model_name}' not found!")
                    st.write(f"Please install the model first: `ollama pull {model_name}`")
                else:
                    st.error(f"Error: Unable to connect to Ollama (Status: {response.status_code})")
                    st.write("Make sure Ollama is running and the model is available.")
                    
            except requests.exceptions.ReadTimeout:
                st.error("⏱️ Request timed out!")
                st.write("The AI model is taking too long to respond. Try:")
                st.write("- Using a smaller/faster model (like llama3.2:3b)")
                st.write("- Reducing your prompt complexity")
                st.write("- Restarting Ollama: `ollama serve`")
                st.write("- Checking system resources (CPU/Memory)")
                
            except requests.RequestException as e:
                st.error(f"Connection Error: {str(e)}")
                st.write("Make sure Ollama is running on the specified host.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
    
    # Instructions section
    with st.expander("ℹ️ How to use this app", expanded=False):
        st.markdown("""
        1. **Fill out the form** with your personal information
        2. **Specify your health conditions** (be honest for safety)
        3. **Set your available exercise time** per day
        4. **Choose your primary goal** (lose weight or gain muscle)
        5. **Click Generate** to get your AI-powered exercise plan
        
        **Requirements:**
        - Ollama must be running on your system
        - Qwen2.5 14B model must be installed (`ollama pull qwen2.5:14b`)
        """)

if __name__ == "__main__":
    main()