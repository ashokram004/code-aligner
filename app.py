import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import time

# IMPORT BACKEND MODULES
from tracer import CodeTracer
from inspector import inspect_code_snippet
from search_engine import find_solution

# --- PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(
    page_title="CodeAligner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PROFESSIONAL UI (CSS) ---
st.markdown("""
<style>
    /* Typography & Base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Code Editors */
    .stTextArea textarea {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        background-color: #0E1117 !important;
        color: #E6E6E6 !important;
        border: 1px solid #262730 !important;
        border-radius: 6px;
        caret-color: #3B82F6 !important; /* Professional Blue Cursor */
    }
    .stTextArea textarea:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 1px #3B82F6;
    }

    /* Buttons */
    .stButton button {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background-color: #1D4ED8 !important;
        transform: translateY(-1px);
    }

    /* Metric Containers */
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
    }
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] {
        color: #A0A0A0 !important; /* Light Grey for Label */
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important; /* White for Value */
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 1px solid #333;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        font-weight: 600;
        color: #888;
        border: none;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #3B82F6;
        border-bottom: 2px solid #3B82F6;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## CodeAligner")
    st.caption("Enterprise Edition v2.2")
    st.divider()
    
    api_key = st.text_input("Gemini API Key", type="password")
    
    st.markdown("#### System Status")
    st.info("Database Connected: Local (ChromaDB)")
    st.info("Execution Engine: Active (Python)")

# --- HELPERS ---
def get_ui_feedback(model, user_code, lang, issue_type, context, reference_code=None):
    """Concise, Executive Summary Style Feedback"""
    
    ref_instruction = ""
    if reference_code:
        ref_instruction = f"\nREFERENCE SOLUTION (Use this as ground truth):\n{reference_code}\n"

    prompt = f"""
    You are a Principal Software Engineer conducting a code review.
    
    USER CODE ({lang}):
    {user_code}
    {ref_instruction}
    
    CONTEXT: {issue_type} | {context}
    
    TASK: Provide a structured code review using the exact headers below.
    
    ### 1. Diagnosis
    [Brief explanation of the logic error or inefficiency if there is any. Otherwise, appreciate the code]
    
    ### 2. Action Plan
    [Concrete steps to fix or optimize if needed]
    
    ### 3. Solution
    ```{lang}
    [The corrected code block]
    ```
    
    ### 4. Complexity Analysis
    [Time & Space Big O with brief reasoning]
    
    CONSTRAINT: Do not output 'undefined'. Keep it professional, structured, brief and direct. We can keep indepth analysis for later.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Service Error: {str(e)}"

def get_deep_dive_feedback(model, user_code, lang, issue_type, context):
    """Detailed Academic Breakdown"""
    prompt = f"""
    You are a Computer Science Professor.
    USER CODE ({lang}):
    {user_code}
    CONTEXT: {issue_type} | {context}
    
    TASK:
    1. **Algorithmic Concept:** Explain the pattern used (e.g., Two Pointers, Sliding Window).
    2. **Step-by-Step Diagnosis:** Walk through the execution trace to show exactly where it deviates.
    3. **Complexity Theory:** Prove mathematically why the solution is O(n) vs O(n^2).
    4. **Industry Standard:** How would this be written in a FAANG production environment?
    
    FORMAT: Use clear headers and bullet points.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Service Error: {str(e)}"

# --- SESSION STATE ---
if 'results' not in st.session_state:
    st.session_state.results = None
if 'deep_dive' not in st.session_state:
    st.session_state.deep_dive = None

# --- CALLBACKS ---
def generate_deep_dive():
    res = st.session_state.results
    if res and api_key:
        genai.configure(api_key=api_key)
        model_dd = genai.GenerativeModel('gemini-2.0-flash')
        with st.spinner("Generating comprehensive analysis..."):
            deep_fb = get_deep_dive_feedback(
                model_dd, res["u_code"], res["lang"], res["fb_type"], res["fb_msg"]
            )
            st.session_state.deep_dive = deep_fb

# --- MAIN LAYOUT ---
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("### Input Workspace")
    
    problem_desc = st.text_area("Problem Statement", 
                               height=100,
                               placeholder="Describe the problem requirements here (e.g., Find the longest substring without repeating characters).")

    default_code = """def find_max(arr):
    m = 0 
    for x in arr:
        if x > m: m = x
    return m"""
    
    user_code = st.text_area("Source Code", value=default_code, height=500)
    
    run_btn = st.button("ANALYZE CODE", use_container_width=True)

# --- EXECUTION LOGIC ---
if run_btn:
    if not api_key:
        st.toast("Missing API Key", icon="⚠️")
        st.stop()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    with col_right:
        st.markdown("### Diagnostics")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 1. INSPECTION
        status_text.markdown("**Phase 1: Static Analysis...**")
        meta = inspect_code_snippet(user_code, problem_desc, api_key)
        progress_bar.progress(33)
        
        if not meta:
            st.error("Analysis failed. Please check input.")
            st.stop()
            
        lang = meta.get('language', 'unknown')
        func = meta.get('user_function', 'unknown')
        slug = meta.get('predicted_slug', 'Unknown') 
        inputs = meta.get('test_input', '()')

        # 2. EXECUTION
        status_text.markdown(f"**Phase 2: Executing Trace (`{slug}`)...**")
        u_res = None
        u_log = []
        
        if lang.lower() == 'python':
            tracer = CodeTracer()
            try:
                real_args = eval(inputs)
                if not isinstance(real_args, tuple): real_args = (real_args,)
                u_res, u_log = tracer.run(user_code, func, real_args, is_class=False)
                
                if isinstance(u_res, str) and "Error" in u_res:
                    st.error(f"Runtime Exception: {u_res}")
                    fb = get_ui_feedback(model, user_code, lang, "RUNTIME CRASH", u_res)
                    st.session_state.results = {"error": True, "feedback": fb}
                    st.stop()
            except Exception as e:
                st.error(f"System Error: {e}")
                st.stop()
        progress_bar.progress(66)
        
        # 3. SEARCH & COMPARE
        status_text.markdown("**Phase 3: Verifying Solution...**")
        golden_code, conf = find_solution(user_code, predicted_slug=slug)
        progress_bar.progress(100)
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()

        # 4. GENERATE REPORT
        fb_type = "REVIEW"
        fb_msg = "Complexity Analysis"
        g_res = None
        g_log = []
        used_reference = None

        if conf > 0.9 and lang.lower() == 'python':
            gold_meta = inspect_code_snippet(golden_code, "", api_key)
            if gold_meta:
                g_func = gold_meta.get('user_function') or "twoSum"
                g_res, g_log = tracer.run(golden_code, g_func, real_args, is_class=True)
                used_reference = golden_code
                
                if str(u_res) != str(g_res):
                    fb_type = "LOGIC ERROR"
                    fb_msg = f"Expected {g_res}, Got {u_res}"
                elif len(u_log) > len(g_log) * 2:
                    fb_type = "OPTIMIZATION NEEDED"
                    fb_msg = f"Steps: {len(u_log)} vs Ref: {len(g_log)}"
                else:
                    fb_type = "OPTIMAL"
                    fb_msg = "Performance matches reference."

        concise_fb = get_ui_feedback(model, user_code, lang, fb_type, fb_msg, reference_code=used_reference)

        st.session_state.results = {
            "error": False,
            "lang": lang,
            "conf": conf,
            "u_log": u_log,
            "u_res": u_res,
            "u_code": user_code,
            "slug": slug,
            "golden_code": golden_code,
            "feedback": concise_fb,
            "fb_type": fb_type,
            "fb_msg": fb_msg
        }
        # Reset deep dive on new run
        st.session_state.deep_dive = None

# --- RENDER RESULTS ---
if st.session_state.results:
    res = st.session_state.results
    
    with col_right:
        if res.get("error"):
            st.error("Analysis Halted")
            st.markdown(res["feedback"])
        else:
            # TABS interface
            tab_overview, tab_trace, tab_code, tab_mentor = st.tabs(
                ["Overview", "Execution Trace", "Reference Code", "Mentor Review"]
            )
            
            with tab_overview:
                c1, c2, c3 = st.columns(3)
                c1.metric("Language", res["lang"].upper())
                c2.metric("Match Score", f"{res['conf']:.0%}")
                c3.metric("User Steps", len(res["u_log"]) if res["lang"]=='python' else "-")
                
                st.caption(f"Target Problem: **{res['slug']}**")
                
                if res["fb_type"] == "LOGIC ERROR":
                    st.error(f"Outcome: {res['fb_msg']}")
                elif res["fb_type"] == "OPTIMIZATION NEEDED":
                    st.warning(f"Outcome: {res['fb_msg']}")
                elif res["fb_type"] == "OPTIMAL":
                    st.success("Outcome: Optimal Solution")
                else:
                    st.info("Outcome: Static Analysis")

            with tab_trace:
                if res["lang"] == 'python':
                    st.markdown(f"**Final Output:** `{res['u_res']}`")
                    st.json(res["u_log"], expanded=False)
                else:
                    st.info("Tracing is available for Python only.")

            with tab_code:
                if res["conf"] > 0.9:
                    st.code(res["golden_code"], language=res["lang"])
                else:
                    st.warning("No exact reference found.")

            with tab_mentor:
                st.markdown("#### Executive Summary")
                st.markdown(res["feedback"])
                
                st.divider()
                
                # Deep Dive Button & Content
                col_btn, col_spacer = st.columns([1, 1])
                with col_btn:
                    st.button("📖 Detailed Deep Dive", on_click=generate_deep_dive, use_container_width=True)
                
                if st.session_state.deep_dive:
                    st.markdown("---")
                    st.markdown(st.session_state.deep_dive)