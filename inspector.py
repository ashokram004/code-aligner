import google.generativeai as genai
import json
import re

def inspect_code_snippet(code_str, api_key):
    """
    Analyzes code using Gemini. Requires API Key passed from Frontend.
    """
    if not api_key:
        print("❌ Error: API Key missing in inspector.")
        return None

    # 1. Configure AI dynamically using the user's key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    print("   [inspector] 🕵️ AI Detective is profiling the code...")
    
    prompt = f"""
    Analyze this code snippet deeply. 
    1. Identify the programming language.
    2. Identify the entry function name used by the user.
    3. Generate a valid test case input (tuple format).
    4. PREDICTION: Based on the logic, what is the MOST LIKELY standard LeetCode problem name?
       (e.g. "Two Sum", "Binary Search", "Merge Sort").

    CODE:
    {code_str}

    Return ONLY raw JSON. Format:
    {{
        "language": "python",
        "user_function": "my_algo_name",
        "predicted_problem": "Name of LeetCode Problem",
        "test_input": "([1,2,3], 5)"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        clean_text = re.sub(r"```json|```", "", response.text).strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"❌ Inspection Failed: {e}")
        return None