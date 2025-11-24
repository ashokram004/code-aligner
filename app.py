import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import time

# IMPORT YOUR BACKEND MODULES
from tracer import CodeTracer
from inspector import inspect_code_snippet
from search_engine import find_solution

# --- PAGE CONFIG ---
st.set_page_config(page_title="CodeAligner AI", page_icon="🧬", layout="wide")

# --- SIDEBAR: API KEY & SETTINGS ---
with st.sidebar:
    st.title("🧬 CodeAligner")
    st.markdown("The **Execution-Aware** Code Assistant.")
    
    # Securely input API Key here
    api_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    st.info("💡 Paste the problem description to help the AI find the exact reference solution in the database.")

# --- HELPER: AI FEEDBACK ---
def get_ui_feedback(model, user_code, lang, issue_type, context):
    prompt = f"""
    You are a Senior Software Engineer acting as a Mentor.
    USER CODE ({lang}):
    {user_code}
    CONTEXT: {issue_type} | {context}
    TASK: Explain the issue briefly, provide the fixed code, and mention Big-O complexity.
    FORMAT: Use Markdown.
    """

    try:
        with st.spinner("🤖 AI is typing..."):
            response = model.generate_content(prompt)
            return response.text
            
    except ResourceExhausted:
        return "⚠️ **AI Traffic Limit Reached.** I am using the free tier of Gemini. Please wait for a minute and try again!"
        
    except Exception as e:
        return f"❌ An unexpected error occurred: {str(e)}"

# --- MAIN APP ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1️⃣ Input Code")
    
    # NEW: Problem Description Input
    problem_desc = st.text_area("Problem Description (Optional but Recommended):", 
                               placeholder="e.g., Given an array of integers, find two numbers that add up to a specific target.",
                               height=100)

    # Default buggy code example
    default_code = """def find_max(arr):
    m = 0 # Bug: Should be arr[0] or -inf
    for x in arr:
        if x > m: m = x
    return m"""
    
    user_code = st.text_area("Paste your algorithm here:", value=default_code, height=300)
    
    run_btn = st.button("🚀 Run Analysis", type="primary")

# --- ANALYSIS LOGIC ---
if run_btn:
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
        st.stop()

    # Configure AI
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    with col2:
        st.subheader("2️⃣ Analysis Report")
        
        # PHASE 1: INSPECTION
        with st.status("🕵️ Inspecting Code...", expanded=True) as status:
            st.write("Using AI to analyze description and code structure...")
            
            # UPDATE: Pass description to inspector
            meta = inspect_code_snippet(user_code, problem_desc, api_key)
            
            if not meta:
                st.error("Could not analyze code. Please check your API Key.")
                st.stop()
                
            lang = meta.get('language', 'unknown')
            func_name = meta.get('user_function', 'unknown')
            # Inspector now returns 'predicted_slug' based on description
            slug = meta.get('predicted_slug', 'Unknown')
            inputs_str = meta.get('test_input', '()')
            
            st.write(f"**Language:** `{lang.upper()}`")
            st.write(f"**Function:** `{func_name}`")
            st.write(f"**Target Problem:** `{slug}`")
            status.update(label="Inspection Complete", state="complete", expanded=False)

        # PHASE 2: EXECUTION (Python Only)
        u_res = None
        u_log = []
        
        if lang.lower() == 'python':
            tracer = CodeTracer()
            
            # Parse Inputs
            try:
                real_args = eval(inputs_str)
                if not isinstance(real_args, tuple): real_args = (real_args,)
            except:
                real_args = ([1, 5, 2],)

            # Run Trace
            try:
                u_res, u_log = tracer.run(user_code, func_name, real_args, is_class=False)
                
                # Check Crash
                if isinstance(u_res, str) and "Error" in u_res:
                    st.error(f"💥 Runtime Crash: {u_res}")
                    fix = get_ui_feedback(model, user_code, lang, "RUNTIME ERROR", u_res)
                    st.markdown(fix)
                    st.stop()
                
                st.success(f"**User Output:** `{u_res}` (Steps: {len(u_log)})")
                
                # Show Trace Details
                with st.expander("📜 View User Execution Trace"):
                    st.json(u_log)

            except Exception as e:
                st.error(f"System Error: {e}")
                st.stop()
        
        else:
            st.info("Static Analysis Mode (Non-Python Language)")

        # PHASE 3: DATABASE SEARCH & COMPARISON
        st.divider()
        st.caption(f"Searching Knowledge Base for '{slug}'...")
        
        # UPDATE: Pass predicted slug to search engine
        golden_code, conf = find_solution(user_code, predicted_slug=slug)
        
        feedback_type = "INDEPENDENT REVIEW"
        context_msg = "No DB match. Analyzing complexity."
        
        # If confidence > 0.9, it means we found an EXACT slug match
        if conf > 0.9:
            st.success(f"✅ Reference Found! (Exact Match)")
            
            # Try to run golden code
            if lang.lower() == 'python':
                # Inspect golden code to find ITS function name
                gold_meta = inspect_code_snippet(golden_code, "", api_key)
                if gold_meta:
                    g_func = gold_meta.get('user_function') or "twoSum" # Fallback
                    g_res, g_log = tracer.run(golden_code, g_func, real_args, is_class=True)
                    
                    st.write(f"**Optimized Output:** `{g_res}` (Steps: {len(g_log)})")
                    
                    # Compare Logic
                    if str(u_res) != str(g_res):
                        feedback_type = "LOGIC BUG"
                        context_msg = f"User got {u_res}, Expected {g_res}"
                    elif len(u_log) > len(g_log) * 2:
                        feedback_type = "INEFFICIENT CODE"
                        context_msg = f"User took {len(u_log)} steps, Golden took {len(g_log)} steps."
                    else:
                        feedback_type = "GOOD CODE"
                        context_msg = "Code is efficient and correct."
                        st.balloons()

            with st.expander("📖 View Reference Solution"):
                st.code(golden_code, language=lang)
        else:
            st.warning(f"No exact match for '{slug}'. Using AI fallback.")

        # PHASE 4: FINAL AI FEEDBACK
        st.subheader("3️⃣ AI Mentor Feedback")
        response = get_ui_feedback(model, user_code, lang, feedback_type, context_msg)
        st.markdown(response)