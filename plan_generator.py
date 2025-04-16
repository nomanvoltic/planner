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
    if st.button("Generate Basic Plan"):
        if user_input:
            st.session_state['messages'].append({"role": "user", "content": user_input})
            plan = get_groq_response(user_input, BASIC_PLAN_PROMPT)
            st.session_state['messages'].append({"role": "assistant", "content": plan})
            st.session_state['latest_plan'] = plan
        else:
            st.warning("Please enter a project idea to generate a plan.")
        
    if st.button("Generate Advanced Plan"):
        if user_input:
            st.session_state['messages'].append({"role": "user", "content": user_input})
            plan = get_groq_response(user_input, ADVANCED_PLAN_PROMPT)
            st.session_state['messages'].append({"role": "assistant", "content": plan})
            st.session_state['latest_plan'] = plan
        else:
            st.warning("Please enter a project idea to generate a plan.")
            
with col2:
    with st.expander("🔧 UML Diagram Options", expanded=True):
        diagram_type = st.selectbox("Diagram Type", ["Class", "Sequence", "Use Case", "Activity", "Component"])

        if st.button("Generate UML Diagram Code"):
            if 'latest_plan' not in st.session_state or not st.session_state['latest_plan'].strip():
                st.warning("Please generate a plan first (Basic or Advanced) before creating a UML diagram.")
            else:
                base_description = st.session_state['latest_plan'].strip()
                full_prompt = f"""
Diagram Type: {diagram_type}
Description: {base_description}
"""
                st.session_state['messages'].append({"role": "user", "content": full_prompt})
                uml_code = get_groq_response(full_prompt, UML_PROMPT)
                st.session_state['messages'].append({"role": "assistant", "content": uml_code})

                # Save UML code to file
                now = datetime.datetime.now()
                date_folder = now.strftime("%Y-%m-%d")
                timestamp = now.strftime("%H%M%S")
                safe_type = diagram_type.lower().replace(" ", "_")

                output_dir = os.path.join("uml_outputs", date_folder)
                os.makedirs(output_dir, exist_ok=True)

                filename = f"{timestamp}_{safe_type}_diagram.txt"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(uml_code)

                st.download_button(
                    label="💾 Download UML Code",
                    data=uml_code,
                    file_name=filename,
                    mime="text/plain"
                )

                st.success(f"UML diagram saved to: `{filepath}`")

                # Trigger rendering
                st.session_state['last_uml_path'] = filepath
                st.session_state['uml_render_ready'] = True


if st.session_state.get('uml_render_ready') and st.session_state.get('last_uml_path'):
    st.subheader("📄 Render UML Diagram")
    if st.button("Render Diagram Image"):
        txt_path = st.session_state['last_uml_path']
        jar_path = "plantuml.jar"  # Make sure this JAR file exists in your root or set correct path

        try:
            subprocess.run(["java", "-jar", jar_path, txt_path], check=True)
            image_path = txt_path.replace(".txt", ".png")
            if os.path.exists(image_path):
                st.image(image_path, caption="Rendered UML Diagram", use_container_width=True)
                with open(image_path, "rb") as img_file:
                    st.download_button("⬇️ Download Diagram Image", data=img_file, file_name=os.path.basename(image_path), mime="image/png")
            else:
                st.error("❌ Failed to find the rendered image.")
        except subprocess.CalledProcessError as e:
            st.error(f"Error rendering UML diagram: {e}")

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
    st.session_state['latest_plan'] = ""