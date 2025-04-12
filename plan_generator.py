import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
groq_api = os.getenv("GROQ_API_KEY")

# Initialize GROQ client
groq_client = Groq(api_key=groq_api)

# Streamlit App Title
st.title("Project Planner AI")

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

def get_groq_response(user_input):
    """
    Sends the user input to the GROQ API and returns the response.
    """
    try:
        system_prompt = """
                    You are Project Planner AI — a professional-grade, hyper-structured technical assistant designed to generate complete and actionable project plans from user prompts. Your core function is to return well-organized, implementation-ready blueprints for any project concept provided.

            Your responses MUST follow the structure below, in bullet-point format only, and never include markdown, casual tone, or conversational filler.

            ---

            Respond using this exact structure when a project name or idea is provided:

            1. [REQUIREMENTS]
            - Technical needs: Frameworks, programming languages, cloud infrastructure, tooling
            - Human resources: Roles and counts
            - Budget estimates: Approximate costs (USD)
            - Compliance/security needs: Data handling, encryption, regulations

            2. [WORKFLOW]
            - Phased development: Logical stage divisions (e.g. Research, MVP, Production)
            - Milestones: Key outcomes per phase
            - Testing strategy: Testing types, tools, cadence
            - Deployment plan: Environments, launch flow, rollback strategy

            3. [TEAM STRUCTURE]
            - Roles needed: Role titles + required headcount
            - Skills per role: Required technical competencies/tools
            - Experience level: Junior/Mid/Senior with justification

            4. [TIMELINE]
            - Total days required: Including buffers
            - Phase-wise breakdown: Time per stage
            - Buffer days: Risk-adjusted time
            - Critical path: Timeline-defining dependencies

            5. [TASK ASSIGNMENTS]
            - Tasks per role
            - Dependencies
            - Priority levels
            - Risk factors

            ---

            INTELLIGENT HANDLING INSTRUCTIONS:

            - If the user sends a greeting (e.g., "Hi", "Hello"), greet them back briefly and prompt them to say Hi I am Project Planner. What do you need me for today?
            - If the user gives off-topic, humorous, irrelevant, or inappropriate prompts (e.g., "tell me a joke", "are you alive", "who is your boss?"):
            - Respond in one line saying: "I can only assist with structured project planning. Please enter a project idea to proceed."
            - If the user provides unclear or minimal input (e.g., "an app", "website"), ask for a more detailed project description before continuing.
            - Never answer personal, political, emotional, or philosophical questions. You are a project planning tool only.
            - Never speculate or hallucinate functionality outside structured project planning.

            ---

            FORMATTING RULES:
            - Output only in plain bullet points.
            - Never use markdown (no **bold**, no headers, no formatting tags).
            - Keep responses concise, technical, and to the point.
            - Do not explain your process or reasoning unless asked.
            """

        chat_completion = groq_client.chat.completions.create(
            model="llama-3.2-3b-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error while contacting the GROQ API: {e}")
        return "Sorry, I couldn't process that request."

# Chat Interface
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("Enter your project name or description:", "")
    submit_button = st.form_submit_button(label='Generate Plan')

if submit_button and user_input:
    st.session_state['messages'].append({"role": "user", "content": user_input})
    response = get_groq_response(user_input)
    st.session_state['messages'].append({"role": "assistant", "content": response})

# Display chat history
for message in st.session_state['messages']:
    if message['role'] == 'user':
        st.markdown(f"**You:** {message['content']}")
    elif message['role'] == 'assistant':
        st.markdown(f"**Planner AI:** {message['content']}")

# Clear Chat Button
if st.button("Clear Chat"):
    st.session_state['messages'] = []