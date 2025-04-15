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

def get_groq_response(user_input, is_uml= False):
    """
    Sends the user input to the GROQ API and returns the response.
    """
    try:
        if is_uml:
            system_prompt ="""
                You are a professional UML diagram generator.

                Your job is to read the user-provided diagram type and system description, then return only a valid UML diagram written for correct PlantUML syntax.

                Output rules:
                - Use @startuml and @enduml to wrap the diagram.
                - Never include natural language text, explanations, or commentary.
                - Use meaningful class, actor, or method names based on the input.
                - Always match the diagram type requested by the user (e.g., class, sequence, use case, activity, component).
            """
        
        
        else:
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
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error while contacting the GROQ API: {e}")
        return "Sorry, I couldn't process that request."

user_input = st.text_input("Enter your project idea or diagram request:")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Generate Plan"):
        if user_input:
            st.session_state['messages'].append({"role": "user", "content": user_input})
            plan = get_groq_response(user_input)
            st.session_state['messages'].append({"role": "assistant", "content": plan})
        else:
            st.warning("Please enter a project idea to generate a plan.")

with col2:
    with st.expander("🔧 UML Diagram Options", expanded=True):
        diagram_type = st.selectbox("Diagram Type", ["Class", "Sequence", "Use Case", "Activity", "Component"])
        description = st.text_area("System / Component Description")
        # extra_context = st.text_area("Actors / Features (optional)")

        if st.button("Generate UML Diagram Code"):
            if description.strip():
                full_prompt = f"""
Diagram Type: {diagram_type}
Description: {description.strip()}
"""
                st.session_state['messages'].append({"role": "user", "content": full_prompt})
                uml_code = get_groq_response(full_prompt, is_uml=True)
                st.session_state['messages'].append({"role": "assistant", "content": uml_code})
            else:
                st.warning("Please provide a description for the UML diagram.")


# Display chat history
st.divider()
st.subheader("💬 Conversation History")
for message in st.session_state['messages']:
    role = "🧑 You" if message['role'] == 'user' else "🤖 Planner AI"

    if message['content'].strip().startswith("@startuml"):
        st.markdown(f"**{role}:**")
        st.code(message['content'], language="plantuml")
    else:
        st.markdown(f"**{role}:** {message['content']}")

# Clear Chat Button
if st.button("Clear Chat"):
    st.session_state['messages'] = []