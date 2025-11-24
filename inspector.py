import google.generativeai as genai
import json
import re

def inspect_code_snippet(code_str, problem_desc, api_key):
    """
    Analyzes code/description to find the LeetCode URL SLUG.
    """
    if not api_key: return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    print(f"   [inspector] 🕵️ Analyzing for LeetCode Slug...")
    
    prompt = f"""
    You are a LeetCode Expert.
    
    USER PROBLEM DESCRIPTION:
    "{problem_desc}"
    
    USER CODE SNIPPET:
    {code_str}

    TASK:
    1. Identify the programming language.
    2. Identify the entry function name.
    3. COUNT the arguments in the user's function definition.
    4. Generate a valid test case tuple that matches the argument count EXACTLY.
       - If function is `def f(nums):` -> test_input must be `([1, 2, 3],)` (1 arg)
       - If function is `def f(nums, target):` -> test_input must be `([1, 2, 3], 5)` (2 args)
    5. DEDUCE the standard LeetCode URL SLUG.
       - Format: lowercase-with-dashes
       - Example: "Two Sum" -> "two-sum"
       - Example: "Best Time to Buy and Sell Stock" -> "best-time-to-buy-and-sell-stock"

    Return ONLY raw JSON:
    {{
        "language": "python",
        "user_function": "my_func",
        "predicted_slug": "two-sum",
        "test_input": "([1,2,3],)" 
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        clean_text = re.sub(r"```json|```", "", response.text).strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"❌ Inspection Failed: {e}")
        return None