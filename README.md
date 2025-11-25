# CodeAligner AI – The Execution-Aware Coding Assistant

## Introduction
CodeAligner is designed to solve the biggest gap in modern AI coding tools: reliable and efficient code verification.
Instead of depending solely on AI-generated guesses—which can be inconsistent—CodeAligner runs your code against real, verified Golden Solutions sourced from a curated LeetCode dataset. This allows it to:
- Identify logical errors with trace-level precision
- Surface hidden runtime failures
- Flag inefficiencies in time and space complexity (e.g., O(n²) vs O(n))
- Detect control-flow deviations that AI alone often misses

By combining dataset-backed matching, execution tracing, and AI-assisted reasoning, CodeAligner ensures your code is not just correct — but optimized and aligned with proven, high-quality solutions.

---

## Screenshots

<img width="1920" height="964" alt="image" src="https://github.com/user-attachments/assets/a7a93e10-a8b1-4e94-8337-2a6d9f8cea98" />

---

## Key Features

### Universal Inspector
Detects programming language automatically (Python / C++ / Java), extracts function signatures, and generates valid test cases using Google Gemini.

### Hybrid Vector Search
Built on ChromaDB. Matches your code against 2,500+ LeetCode solutions using both code logic and AI-predicted problem names.

### Execution Tracing (Python)
Runs your code + Golden Solution in a sandbox and compares step-by-step execution using sys.settrace. Captures variable states and call graph.

### Complexity Analysis
Detects slow patterns, highlights loops, nested loops, repeated operations, and abnormal time complexities.

### AI Mentor Mode
Provides constructive developer-friendly feedback and points out root causes instead of just rewriting your code.

---

## Installation

### Clone the Repository
git clone https://github.com/ashokram004/code-aligner.git  
cd CodeAligner

### Set up Virtual Environment (Recommended)

#### Windows
python -m venv venv  
.\venv\Scripts\activate

#### Mac/Linux
python3 -m venv venv  
source venv/bin/activate

### Install Dependencies
pip install -r requirements.txt

---

## Get Your API Key

You need a Google Gemini API Key (Free tier available).  
1. Go to Google AI Studio  
2. Create an API Key  
3. Enter this key inside the CodeAligner App UI when prompted

---

## Database Setup (First Run Only)

CodeAligner uses a custom LeetCode dataset embedded locally using ChromaDB.  
Run: python build_db.py

You will see:  
SUCCESS! Database built.

---

## Usage

### Run Streamlit App
streamlit run app.py  
Open http://localhost:8501  
- Enter your Gemini API Key  
- Paste your code  
- Click Run Analysis

---

## Project Structure

| File / Folder          | Description |
|------------------------|-------------|
| `app.py`               | Streamlit UI |
| `cli_runner.py`        | CLI controller |
| `inspector.py`         | Language detection + test case generator |
| `tracer.py`            | Execution tracing engine |
| `search_engine.py`     | Vector search logic |
| `build_db.py`          | Script to build local ChromaDB |
| `leetcodedb_data/`     | Auto-generated vector database |
| `requirements.txt`     | Dependency list |

---

## Contributing
1. Fork the repo  
2. Create a feature branch  
3. Commit changes  
4. Open a Pull Request

---

## License
Open-source and intended for educational purposes.

