import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import datetime
import subprocess

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
if 'latest_plan' not in st.session_state:
    st.session_state['latest_plan'] = ""

# -------- System Prompts -------- #

BASIC_PLAN_PROMPT = """
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
"""

ADVANCED_PLAN_PROMPT = """
You are Project Planner AI — an advanced and detail-oriented assistant built to create end-to-end project blueprints, covering all technical, design, development, and operational phases from concept to production.

You must return a complete, actionable, and well-organized plan in plain text only. Your responses MUST include both structural sections and detailed content per section.

---

Respond using this structure for any given project idea:

1. PROJECT OVERVIEW
- Objective and scope
- Target users or stakeholders
- Core problem being solved

2. SYSTEM DESIGN & ARCHITECTURE
- Key modules or components with class/service names
- API design considerations
- Storage and database planning
- Design tools or diagrams to use (e.g., UML, ERD)

3. MVP ROADMAP
- MVP features: Only what's essential
- Tech stack for MVP
- Testing and feedback loop

4. FULL PRODUCT ROADMAP
- Additional features for v1.0 and v2.0
- Scalability and performance concerns
- Security/compliance additions

5. WORKFLOW & PHASES
- Timeline: Research → MVP → Iteration → Production
- Milestones with deliverables per stage
- Code review, CI/CD, and testing processes

6. TEAM & ROLES
- Required roles + skillsets
- Team structure (hierarchical/flat)
- Internal and external collaboration

7. TIMELINE ESTIMATES
- Total estimated duration
- Buffer days per phase
- Critical bottlenecks to watch

8. DEPLOYMENT & MONITORING
- Deployment strategy
- Tools for monitoring, alerts, and analytics
- Post-launch support

---

FORMATTING INSTRUCTIONS:
- Use clear section titles
- Use bullet points where helpful, but full sentences are allowed
- Avoid markdown syntax
- Maintain a formal, technical tone
"""

UML_PROMPT = """
You are a professional UML diagram generator.

Your job is to read the user-provided diagram type and system description, then return ONLY a valid UML diagram written in correct PlantUML syntax.

STRICT OUTPUT RULES:
- Start your output with @startuml and end it with @enduml.
- DO NOT include any explanations, comments, or extra text.
- DO NOT wrap the code in markdown or code block markers.
- Use appropriate PlantUML syntax based on the requested diagram type.
- Use meaningful and consistent names based on the input description.

EXAMPLES OF VALID OUTPUT:
@startuml
Class A
A --> B : calls
@enduml

@startuml
actor User
User --> System : Request
@enduml
"""


def get_groq_response(user_input, system_prompt):
    """
    Sends the user input to the GROQ API and returns the response.
    """
    try:
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