import streamlit as st
import google.generativeai as genai
import sqlite3
import re
import os
from dotenv import load_dotenv

# ---------------------------------------------------------
# INITIALIZATION & ERGONOMIC DARK THEME OVERHAUL
# ---------------------------------------------------------
load_dotenv()
st.set_page_config(
    page_title="Be The Top One | Enterprise Placement Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Space Dark Theme Injector with High Contrast Elements
st.markdown("""
    <style>
        /* Global Reset and Dark Mode Canvas */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0b0f19 !important;
            color: #f1f5f9 !important;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        .stApp {
            background: linear-gradient(160deg, #090d16 0%, #111827 50%, #070a12 100%) !important;
        }
        
        /* Persistent Sidebar Structural Style */
        section[data-testid="stSidebar"] {
            background-color: #05070c !important;
            border-right: 1px solid #1e293b;
        }
        
        /* Typographic Styling and Gradient Headers */
        h1 {
            background: linear-gradient(90deg, #38bdf8 0%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            letter-spacing: -0.04em;
        }
        h2, h3, h4 {
            color: #f8fafc !important;
            font-weight: 600 !important;
        }
        
        /* Modern Glassmorphic Container Cards */
        div.stBox, div[data-testid="stExpander"], div.stForm {
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid #1e293b !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
        }
        
        /* Input & Dropdown Interfaces */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
            background-color: #030712 !important;
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: #4f46e5 !important;
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.3) !important;
        }
        
        /* Premium Navigation and Form Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #3b82f6 0%, #4f46e5 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.8rem !important;
            font-weight: 600 !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .stButton>button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4) !important;
        }
        
        /* Tailored Sidebar Solver Box Dimension Override */
        div[data-testid="stSidebar"] .stTextArea textarea {
            min-height: 160px !important;
            font-size: 14px !important;
        }
        
        /* Clean Utility Classes */
        .step-card {
            background: rgba(30, 41, 59, 0.4);
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 0 8px 8px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Fetch and Assert Gemini API Engine Access
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("Gemini Core Key Missing. Ensure your GEMINI_API_KEY parameter is declared in your system environment profile or local .env context.")

# ---------------------------------------------------------
# SECURITY ACCESS AND PERSISTENCE ENGINE
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def register_user(username, password):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    # FIXED: Removed the invalid 'VALUES' keyword from the SQL selection query string
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def validate_password(password):
    if len(password) < 12: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[0-9]", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_+\-\[\]\\\/~`=;']", password): return False
    return True

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.markdown("<div style='text-align: center; padding: 3rem 0;'><h1>Be The Top One</h1><h3>Unified Multi-Disciplinary Placement System</h3></div>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        auth_mode = st.radio("System Gateway Access", ["Sign In", "Sign Up"], horizontal=True)
        with st.form("system_auth_gate"):
            username = st.text_input("user name/email").strip()
            password = st.text_input("password", type="password")
            submit_btn = st.form_submit_button("submit")
            
            if submit_btn:
                if not username or not password:
                    st.error("Please fill in all requested connection inputs.")
                elif auth_mode == "Sign Up":
                    if not validate_password(password):
                        st.error("Complexity Standard Violated: Token length must be >= 12, with 1 uppercase character, 1 numeric, and 1 specialized delimiter.")
                    else:
                        if register_user(username, password):
                            st.success("Registration record created. Adjust select gateway profile to 'Sign In'.")
                        else:
                            st.error("Identity signature conflict detected.")
                elif auth_mode == "Sign In":
                    if authenticate_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid entry keys. Check parameters.")
    st.stop()

# ---------------------------------------------------------
# SIDEBAR CONTROL NAVIGATION & LOGOUT CONTEXT
# ---------------------------------------------------------
st.sidebar.markdown("<h2 style='font-size:22px; color:#38bdf8;'>Control Console</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"Profile Vector: **{st.session_state.username}**")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

st.sidebar.markdown("---")
navigation_dest = st.sidebar.selectbox(
    "Select Target Track",
    [
        "Subject-Wise Technical Interview Bank",
        "Coding Round Deep-Dive",
        "Infinite Aptitude Sandbox",
        "Advanced Communication Skills",
        "Interview Tips & Etiquette",
        "GitHub Project Presentation Analyzer"
    ]
)

# ---------------------------------------------------------
# TRACK 1: SUBJECT-WISE TECHNICAL INTERVIEW BANK
# ---------------------------------------------------------
if navigation_dest == "Subject-Wise Technical Interview Bank":
    st.header("Multi-Disciplinary Technical Subject Deep-Dive")
    st.write("Browse deep computer science, infrastructure, circuits, and core industrial engineering curricula.")
    
    dept = st.selectbox(
        "Target Academic Discipline",
        ["Computer Science (CS)", "Information Technology (IT)", "Artificial Intelligence & Data Science (AI&DS)", 
         "Artificial Intelligence & Machine Learning (AI&ML)", "Data Science (DS)", "Electronics & Communication (ECE)", 
         "Electrical & Electronics (EEE)", "Mechanical Engineering (MECH)", "Civil Engineering (CIVIL)"]
    )
    
    if dept in ["Computer Science (CS)", "Information Technology (IT)"]:
        subject = st.selectbox("Academic Specialization Subject", ["Database Management Systems", "Operating Systems", "Computer Networks", "Data Structures & Algorithms", "Compiler Design"])
    elif dept in ["Artificial Intelligence & Data Science (AI&DS)", "Data Science (DS)"]:
        subject = st.selectbox("Academic Specialization Subject", ["Applied Statistical Inference", "Data Mining & Warehouse Architecture", "Big Data Frameworks (Hadoop/Spark)", "Data Visualization Pipelines"])
    elif dept == "Artificial Intelligence & Machine Learning (AI&ML)":
        subject = st.selectbox("Academic Specialization Subject", ["Deep Learning & Neural Topologies", "Supervised/Unsupervised Algorithms", "Natural Language Processing Engine", "Computer Vision Matrices"])
    elif dept == "Electronics & Communication (ECE)":
        subject = st.selectbox("Academic Specialization Subject", ["Digital Signal Processing", "Embedded Systems Architecture", "Microprocessors & VLSI Design", "Antenna Wave Propagation"])
    elif dept == "Electrical & Electronics (EEE)":
        subject = st.selectbox("Academic Specialization Subject", ["Power Systems Engineering", "Electrical Control Matrix", "Synchronous Machinery", "Analog and Digital Power Electronics"])
    elif dept == "Mechanical Engineering (MECH)":
        subject = st.selectbox("Academic Specialization Subject", ["Thermodynamics & Heat Exchange", "Fluid Mechanics & Hydraulics", "Kinematics of Rigid Machineries", "CAD/CAM Production Automation"])
    else:
        subject = st.selectbox("Academic Specialization Subject", ["Structural Matrix Analysis", "Geotechnical Concrete Foundations", "Fluid Hydraulics Engineering", "Transportation & Highway Topologies"])

    sub_concept = st.text_input("Enter Focus Concept Parameter", placeholder="e.g., Transaction Isolation Levels, Backpropagation, Boundary Layer Theory")

    if "tech_q_idx" not in st.session_state:
        st.session_state.tech_q_idx = 1
        
    col_nav1, col_nav2 = st.columns([5, 1])
    with col_nav2:
        if st.button("Next Question Module"):
            st.session_state.tech_q_idx += 1
            
    st.markdown(f"#### Concept Framework Evaluation: Target Question {st.session_state.tech_q_idx} / 200")

    if st.button("Execute In-Depth Engineering Search"):
        if not api_key:
            st.error("API gateway credentials verification context failure.")
        else:
            with st.spinner(f"Compiling comprehensive engineering data frameworks for {subject}..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    subjective_prompt = f"""
                    You are a distinguished Distinguished Professor and Chief Enterprise Technical Interviewer.
                    Conduct an exhaustive in-depth breakdown for the department: '{dept}', subject domain: '{subject}', and specific concept: '{sub_concept}'.
                    
                    This profile maps to core interview framework reference context {st.session_state.tech_q_idx} out of a 200-question deep subject question matrix pool.
                    
                    Provide the following highly structured output:
                    1. High-Level Core Architectural Theory/Equation foundation framework.
                    2. Detailed Technical Interview Question (Advanced Scenario/Production Scale Issue).
                    3. The Definitive, Exemplary Technical Response (Include line-item explanations, structural data logs, or circuit topology formulas where relevant).
                    4. Edge-Case Scenarios and Trap/Follow-up paths an interviewer will utilize based on this specific explanation profile.
                    
                    Ensure presentation format is perfectly structured, highly mathematical where necessary using clean Markdown syntax, and contains zero emojis.
                    """
                    response = model.generate_content(subjective_prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error compiling engineering records: {str(e)}")

# ---------------------------------------------------------
# TRACK 2: CODING ROUND DEEP-DIVE
# ---------------------------------------------------------
elif navigation_dest == "Coding Round Deep-Dive":
    st.header("Coding Round Deep-Dive Problem Solver")
    st.write("Deep structural algorithm execution across multiple targets. Choose your technical language stack to review fully compiled solutions.")
    
    col1, col2 = st.columns(2)
    with col1:
        pattern_category = st.selectbox("Select Core Algorithm Domain", ["Linear Data Structures", "Non-Linear Data Structures", "General Problem Solving Patterns"])
    with col2:
        selected_lang = st.selectbox("Target Programming Language", ["C++", "Java", "Python"])
        
    if pattern_category == "Linear Data Structures":
        pattern = st.selectbox("Choose Structural Pattern Focus", ["Two Pointers", "Sliding Window", "Fast & Slow Pointers", "Prefix Sum", "Cyclic Sort"])
    elif pattern_category == "Non-Linear Data Structures":
        pattern = st.selectbox("Choose Structural Pattern Focus", ["Tree BFS", "Tree DFS", "Topological Sort", "Union-Find", "Trie (Prefix Tree)"])
    else:
        pattern = st.selectbox("Choose Structural Pattern Focus", ["Modified Binary Search", "Two Heaps", "Merge Intervals", "Top K Elements", "Backtracking", "Dynamic Programming"])

    st.markdown(f"### Current Parameters: **{pattern}** optimized in **{selected_lang}**")
    
    if st.button("Generate Deep Dive Analysis & Problem Set"):
        if not api_key:
            st.error("API configuration required to fetch technical query structures.")
        else:
            with st.spinner(f"Querying Gemini models to compile structural variations for {pattern}..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    coding_prompt = f"""
                    You are an elite competitive coding instructor. Provide an incredibly in-depth, comprehensive breakdown for the coding pattern: '{pattern}'.
                    The user has explicitly selected target execution language: '{selected_lang}'.
                    
                    Provide the following layout structure:
                    1. Core Paradigm Theory and structural breakdown.
                    2. Company Target Profiles (e.g., Google, Amazon, Meta tier).
                    3. A highly advanced, complex, production-ready coding question based on this pattern.
                    4. Clear, production-ready, fully-commented implementation code written exclusively in '{selected_lang}'.
                    5. Comprehensive Time Complexity Analysis and Space Complexity Analysis utilizing strict LaTeX mathematical notation (e.g., $O(N)$ or $O(\\log N)$).
                    6. Edge-cases breakdown and optimization tricks.
                    
                    Ensure the formatting is extremely clean and avoid using any visual emojis.
                    """
                    response = model.generate_content(coding_prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error accessing model parameters: {str(e)}")

# ---------------------------------------------------------
# TRACK 3: INFINITE APTITUDE SANDBOX
# ---------------------------------------------------------
elif navigation_dest == "Infinite Aptitude Sandbox":
    st.header("Infinite Aptitude Practice Engine")
    st.write("Dynamic practice modules configured to auto-generate over 100 to 200 concept variations on demand.")
    
    aptitude_topic = st.selectbox("Choose Core Aptitude Module", ["Quantitative Aptitude", "Logical Reasoning", "Verbal Ability"])
    
    if aptitude_topic == "Quantitative Aptitude":
        concept = st.selectbox("Select Target Concept", ["Time, Speed & Distance", "Work & Efficiency Matrices", "Permutations & Combinations", "Profit & Loss Mechanics", "Probability Distributions"])
    elif aptitude_topic == "Logical Reasoning":
        concept = st.selectbox("Select Target Concept", ["Number Series Configurations", "Syllogisms", "Blood Relations Mapping", "Seating Arrangement Matrices", "Data Sufficiency Complexities"])
    else:
        concept = st.selectbox("Select Target Concept", ["Contextual Synonyms", "Sentence Correction Protocols", "Reading Comprehension Analysis", "Idiomatic Usage Evaluation"])

    if "aptitude_count" not in st.session_state:
        st.session_state.aptitude_count = 1

    col_btn1, col_btn2 = st.columns([5, 1])
    with col_btn2:
        if st.button("Generate Next Variation"):
            st.session_state.aptitude_count += 1

    st.markdown(f"#### Concept Tracker: Generating Problem Variation #{st.session_state.aptitude_count} / 200")
    
    if not api_key:
        st.error("Gemini API key verification needed for automated logic generation.")
    else:
        with st.spinner("Generating unique, target-specific questions..."):
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                apt_prompt = f"""
                You are an expert technical placement evaluation system matching formats used by companies like AMCAT, eLitmus, and TCS iON.
                Generate a complex question based on the topic '{concept}' inside the broader category '{aptitude_topic}'.
                This is problem variation reference number {st.session_state.aptitude_count} out of a 200-question concept series. Ensure it is unique.
                
                Output requirements:
                1. Clearly state the problem scenario.
                2. Provide 4 distinct Multiple Choice Options (A, B, C, D).
                3. Provide a detailed, step-by-step mathematical explanation of the solution inside an expander structure.
                4. Use LaTeX format equations for all complex calculations.
                
                Do not use any emojis in your response.
                """
                response = model.generate_content(apt_prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error handling automated aptitude generation: {str(e)}")

# ---------------------------------------------------------
# TRACK 4: ADVANCED COMMUNICATION SKILLS
# ---------------------------------------------------------
elif navigation_dest == "Advanced Communication Skills":
    st.header("Executive Linguistic Agility & Behavioral Delivery Engine")
    st.write("Step-by-step framework to transition technical thoughts into flawless, high-impact English speech during professional evaluations.")
    
    comm_vector = st.selectbox(
        "Select Target Communication Framework Domain",
        [
            "Speech Pacing & Active Auditory Shadowing Protocols",
            "Real-Time Technical Concept Articulation & Thought Projection",
            "Elimination of Fillers, Code-Switching Flaws, and Speech Crutches",
            "Corporate Lexicon Integration & Domain Vocabulary Expansion",
            "Behavioral Assertiveness & Managing High-Pressure Interrogation"
        ]
    )
    
    if st.button("Generate High-Understandability Action Plan"):
        if not api_key:
            st.error("Linguistic processing requires stable active API engine context connectivity.")
        else:
            with st.spinner("Executing deep linguistic modeling analysis..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    comm_prompt = f"""
                    You are a Principal Corporate Communications Coach and Behavioral Linguistic Expert specializing in global tech placements.
                    Perform a comprehensive, deep-dive search and provide an incredibly high-understandability, efficient, step-by-step method for the domain: '{comm_vector}'.
                    
                    The presentation of your output must follow this rigorous architectural format:
                    1. CORE CHALLENGE MAP - Break down the exact anatomical or psychological reason why students falter in this area.
                    2. STEP-BY-STEP STRATEGIC ROADMAP - Provide a sequential, highly practical, chronologically actionable daily drill framework.
                    3. MOCK EXAMPLES & CONTRAST TABLES - Contrast bad/weak delivery expressions against elite corporate delivery formats.
                    4. MEASURABLE PERFORMANCE METRICS - Define how the user can audit their pacing, vocabulary diversity, and clarity without external help.
                    
                    Ensure the complete output is logical, linear, highly academic yet fully digestible, and contains zero emojis.
                    """
                    response = model.generate_content(comm_prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error running language synthesis modeling parameters: {str(e)}")

# ---------------------------------------------------------
# TRACK 5: INTERVIEW TIPS & ETIQUETTE
# ---------------------------------------------------------
elif navigation_dest == "Interview Tips & Etiquette":
    st.header("Executive Presentation & Field-Verified Interview Playbook")
    st.write("Comprehensive guide analyzing visual mechanics, mental preparation, and tactical feedback loops collected directly from placed seniors.")
    
    etiquette_domain = st.selectbox(
        "Select Etiquette Domain Vector",
        [
            "Virtual Interview Environments (Camera Angle, Audio Isolation, Lighting Arrays)",
            "In-Person Body Language (Postural Framing, Eye Metrics, Hand Micro-Movements)",
            "Strategic Behavioral Structuring (STAR Method Optimization, Handling Unknowable Questions)",
            "Post-Interview Follow-Up Lifecycle & Negotiation Etiquette"
        ]
    )
    
    if st.button("Extract In-Depth Playbook & Student Case Diaries"):
        if not api_key:
            st.error("API authorization token context error.")
        else:
            with st.spinner("Compiling anonymous student interview transcripts and experience logs..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    etiquette_prompt = f"""
                    You are a Chief Talent Officer and Senior Human Resources Architect.
                    Conduct a highly comprehensive search on current industry placement benchmarks for: '{etiquette_domain}'.
                    
                    To maximize real-world execution and clarity, divide your output into these precise core segments:
                    1. CORPORATE PROTOCOL PLAYBOOK - Detailed, actionable rules governing high-tier placement selection panels.
                    2. HISTORICAL STUDENT ARCHIVES (Case Diaries & Opinions) - Include at least three anonymous profiles of recently evaluated students from elite tech universities. Detail what went right, what curveballs they encountered (e.g., unexpected system architecture pressure, tricky psychological tests), and their direct opinions on how to bypass these traps.
                    3. CRITICAL MISTAKE AUDIT MATRIX - A clear table contrasting minor presentation flaws with fatal assessment pipeline errors.
                    
                    Do not use any visual emojis in the synthesized text layout.
                    """
                    response = model.generate_content(etiquette_prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error loading playbook databases: {str(e)}")

# ---------------------------------------------------------
# TRACK 6: GITHUB PROJECT PRESENTATION ANALYZER
# ---------------------------------------------------------
elif navigation_dest == "GitHub Project Presentation Analyzer":
    st.header("GitHub Repository & Technical Architectural Presentation Analyzer")
    st.write("Convert raw system design details, schemas, and source indicators into an optimized project pitch script.")
    
    with st.form("enhanced_project_analyzer_form"):
        p_title = st.text_input("Project Title Vector", value="Smart Campus Recruiter")
        p_idea = st.text_area("Core System Concept / Algorithmic Engine", value="An automated platform that coordinates campus hackathons and uses an optimization algorithm to match students into balanced teams based on their skills.")
        p_exist = st.text_area("Existing Legacy System Limitations", value="Students currently look for teammates manually, which often leads to unbalanced skill sets, unformed teams, and missed coordination across departments.")
        p_proposed = st.text_area("Proposed Innovation/ Architectural Benefits", value="An AI-powered matchmaking platform built on Streamlit and SQLite that uses profile metrics to pair frontend developers, backend developers, and data specialists automatically.")
        p_func = st.text_area("Functional System Requirements", value="The system must authenticate users via secure sign-up pages, allow profile building, parse skill keywords, and run team generation algorithms on demand.")
        p_nonfunc = st.text_area("Non-Functional Operational Constraints", value="Passwords must follow strict verification checks. The system should process matchmaking results within 2 seconds and keep database access secure.")
        p_components = st.text_area("Components, Dependencies & Library Drivers Used", value="Python 3.11, Streamlit UI, SQLite, SQLAlchemy, python-dotenv, Regex validations.")
        
        p_custom_features = st.text_area(
            "Prospective Features / Custom Scalability Extensions (User Defined Box)", 
            value="Incorporate OAuth2 GitHub commit-history frequency tracking to dynamically verify declared developer skill metrics.",
            placeholder="Add any additional feature modules, third-party API integrations, or roadmap extensions you want to evaluate here..."
        )
        
        p_scope = st.text_area("Future Evolution Scope", value="Adding real-time chat, integrating GitHub profile analysis via an API, and using machine learning models to predict how well teams will perform together.")
        
        analyze_btn = st.form_submit_button("Synthesize Executive Narrative Matrix")
        
        if analyze_btn:
            if not api_key:
                st.error("Please configure your Gemini API key inside the .env file to run this analysis.")
            else:
                analysis_prompt = f"""
                You are an elite Engineering Project Consultant and Technical Interview Panel Chair.
                Deconstruct this system architecture profile and compile a highly advanced presentation defense narrative:
                
                Architecture Specifications:
                - Project Title: {p_title}
                - Algorithmic Core: {p_idea}
                - Legacy System Deficiencies: {p_exist}
                - Architectural Solution: {p_proposed}
                - Functional Execution Paths: {p_func}
                - Guardrails/Constraints: {p_nonfunc}
                - Core Dependencies Stack: {p_components}
                - User-Defined Custom Extensions: {p_custom_features}
                - Extended Roadmap Scope: {p_scope}
                
                Output requirements: Provide an exhaustive breakdown structured across standard corporate presentation cycles (Elevator Pitch, Structural Problem Mapping, Engineering & Database Selection Trade-offs, Detailed Custom Extension Assessment, Future Scale Roadmap).
                
                Format without using any emojis.
                """
                with st.spinner("Analyzing project layout configurations and creating script matrices..."):
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        response = model.generate_content(analysis_prompt)
                        st.success("Project Presentation Matrix Successfully Compiled!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error mapping target code architectures: {str(e)}")

# ---------------------------------------------------------
# ERGONOMICALLY EXPANDED SIDEBAR GLOBAL DOUBT SOLVER
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("AI Doubt Solver Engine")

user_doubt = st.sidebar.text_area(
    "Stuck on an engineering concept or system error? Input criteria below:", 
    key="global_deep_doubt_canvas", 
    placeholder="Type any topic or stack trace here. The module will process and render an exhaustive step-by-step logic map.",
    help="This input box has been vertically expanded to handle complex query prompts or code blocks easily."
)

ask_ai_btn = st.sidebar.button("Execute Step-By-Step Logic Resolution")

if ask_ai_btn and user_doubt:
    if not api_key:
        st.sidebar.error("Gemini Core Engine authorization missing.")
    else:
        with st.sidebar.spinner("Running step-by-step trace analysis..."):
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(
                    f"You are a Senior Engineering Placement Mentor. Deconstruct the user query and generate a highly detailed, comprehensive response structured as a logical step-by-step trace solution. Do not include any emojis: {user_doubt}"
                )
                st.sidebar.info(response.text)
            except Exception as e:
                st.sidebar.error(f"Error handling tracing metrics: {str(e)}")