from search_engine import find_solution
from tracer import CodeTracer
from inspector import inspect_code_snippet
import google.generativeai as genai
import ast

# --- CONFIGURATION ---
# PASTE YOUR API KEY HERE
API_KEY = "YOUR_API_KEY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def get_ai_feedback(user_code, lang, issue_type, context):
    """
    Generates a structured, educational response using the Mentor Persona.
    """
    print(f"   [AI Mentor] Analyzing '{issue_type}'...")
    
    prompt = f"""
    You are a Senior Software Engineer acting as a Mentor.
    
    USER CODE ({lang}):
    {user_code}
    
    CONTEXT / DIAGNOSIS:
    Issue Type: {issue_type}
    Details: {context}
    
    TASK:
    1. EXPLAIN: Briefly explain the issue (or why the code is good) in plain English.
    2. FIX/OPTIMIZE: If the code needs changes, provide the corrected code block. 
       - If it's already perfect, just say so and don't reprint code.
    3. ANALYSIS: Mention the Time Complexity (Big O) if relevant.
    
    FORMAT:
    Use Markdown. Use bolding for key concepts. Keep it concise.
    """
    response = model.generate_content(prompt)
    return response.text

def run_universal_pipeline(user_code):
    print("\n" + "="*60)
    print("🚀 STARTING AI CODE ALIGNER")
    print("="*60)

    # --- PHASE 1: INSPECTION (The Detective) ---
    # We identify Language, Function Name, and Predict the LeetCode Problem
    user_meta = inspect_code_snippet(user_code, API_KEY)
    if not user_meta: 
        print("❌ Could not analyze code structure.")
        return
    
    lang = user_meta.get('language', 'unknown').lower()
    user_func = user_meta.get('user_function')
    predicted_problem = user_meta.get('predicted_problem')
    test_inputs_str = user_meta.get('test_input')
    
    print(f"🔹 Language: {lang.upper()}")
    print(f"🔹 User Function: '{user_func}'")
    print(f"🔹 AI Prediction: This looks like '{predicted_problem}'")

    # --- PHASE 2: PYTHON EXECUTION (User Side) ---
    u_res = None
    u_log = []
    real_args = ([1, 5, 2],) # Default fallback

    if lang == 'python':
        tracer = CodeTracer()
        
        # Prepare Arguments safely
        try:
            real_args = eval(test_inputs_str)
            if not isinstance(real_args, tuple): real_args = (real_args,)
        except:
            print("⚠️ Error parsing input string. Using default.")

        print(f"\n--- 1. RUNNING USER TRACE ---")
        try:
            # Run User Code
            u_res, u_log = tracer.run(user_code, user_func, real_args, is_class=False)
            
            # CHECK FOR CRASHES
            if isinstance(u_res, str) and "Error" in u_res:
                print(f"❌ Runtime Crash: {u_res}")
                print(get_ai_feedback(user_code, lang, "RUNTIME ERROR", f"Error message: {u_res}"))
                return # Stop if user code crashes

            print(f"✅ Result: {u_res} (Steps: {len(u_log)})")
            
        except Exception as e:
            print(f"❌ System Error: {e}")
            return
    else:
        print(f"ℹ️ Skipping execution (Language is {lang}). Proceeding to Static Analysis.")

    # --- PHASE 3: KNOWLEDGE BASE SEARCH ---
    print("\n--- 2. SEARCHING KNOWLEDGE BASE ---")
    
    # HYBRID SEARCH: Pass the AI's prediction to boost accuracy
    golden_code, conf = find_solution(user_code, predicted_name=predicted_problem)
    
    if conf > 0.4:
        print(f"Match Found! (Similarity: {conf:.2%})")
        
        if lang == 'python':
            # We need to find the function name inside the Golden Code (it might be 'twoSum' or 'solve')
            print("   [inspector] Scanning Golden Solution...")
            gold_meta = inspect_code_snippet(golden_code, API_KEY)
            
            if gold_meta:
                gold_func = gold_meta.get('user_function') or gold_meta.get('standard_function_name')
                
                print(f"   [tracer] Running Golden Code: '{gold_func}'")
                g_res, g_log = tracer.run(golden_code, gold_func, real_args, is_class=True)
                
                # --- PHASE 4: LOGIC COMPARISON ---
                print("\n--- 3. MENTOR FEEDBACK ---")
                
                # CASE A: WRONG ANSWER
                if str(u_res) != str(g_res):
                    print(get_ai_feedback(user_code, lang, "LOGIC BUG", 
                        f"User Result: {u_res} | Expected (Golden) Result: {g_res}"))
                
                # CASE B: SLOW CODE (Strict Check: 2x slower)
                elif len(u_log) > len(g_log) * 2:
                    print(get_ai_feedback(user_code, lang, "INEFFICIENT CODE", 
                        f"User Steps: {len(u_log)} | Optimized Steps: {len(g_log)}. The code is inefficient."))
                
                # CASE C: GOOD CODE
                else:
                    print(get_ai_feedback(user_code, lang, "GOOD CODE", 
                        "Your code is logically correct and performs efficiently compared to the reference solution."))
            else:
                # Match found, but couldn't parse golden code structure
                print("⚠️ Could not trace Golden Solution. Switching to Static Review.")
                print(get_ai_feedback(user_code, lang, "STATIC REVIEW", "Analyze correctness."))
        else:
            # Non-Python Match Found (Logic Comparison)
            print(get_ai_feedback(user_code, lang, "STATIC ANALYSIS", 
                f"Compare User Code against this Reference Logic: \n{golden_code}"))

    else:
        print(f"⚠️ No database match found for '{predicted_problem}'.")
        # Fallback: Independent AI Review
        print("\n--- 3. INDEPENDENT AI REVIEW ---")
        print(get_ai_feedback(user_code, lang, "INDEPENDENT REVIEW", 
            "No reference solution available. Analyze for Edge Cases and Time Complexity."))

# --- TEST EXECUTION ---
if __name__ == "__main__":
    
    # TEST 1: Weird Function Name, O(n^2) Logic (Should be detected as Two Sum)
    obscure_code = """
def magic_pair_finder(arr, target):
    # Trying to find pair...
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j:
                if arr[i] + arr[j] == target:
                    return [i, j]
    return []
"""
    
    run_universal_pipeline(obscure_code)