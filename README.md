# CodeAligner AI  
**Execution-Aware Code Diagnostics**

CodeAligner AI is an analysis framework designed to evaluate code by executing it alongside verified “Golden Solutions”. Instead of relying solely on static analysis or pattern matching, CodeAligner focuses on **observable execution behavior**, surfacing issues that traditional linters or AI assistants typically miss.

---

## 1. Overview

Modern AI code assistants are excellent at generating code, but they struggle at verifying it. CodeAligner shifts the focus to correctness by examining:

- Behavioral differences between user code and reference implementations  
- Runtime failures and hidden edge cases  
- Pattern-level inefficiencies in logic and complexity  
- Variable and control-flow deviations uncovered via trace comparison  

The system integrates execution tracing, vector search, and AI-generated test cases into a single end-to-end analysis workflow.

---

## 2. Core Capabilities

### **Language & Structure Analysis**
- Automatic language detection (Python, C++, Java)
- Function signature extraction
- Dynamic test-case generation powered by Gemini models

### **Vector-Based Code Retrieval**
- Backed by ChromaDB  
- Compares your submission against a curated index of 2,500+ LeetCode reference solutions  
- Uses a hybrid scoring approach (structural logic + predicted problem name)

### **Execution Trace Engine (Python)**
- Instruments both implementations via `sys.settrace`
- Records variable snapshots, call stack, and branching events
- Produces a step-level diff to expose incorrect states

### **Performance Diagnostics**
- Identifies nested loops or patterns affecting complexity
- Highlights potentially slow constructs (e.g., repeated scans or redundant operations)
- Detects mismatches between expected and actual time/space behavior

### **Mentorship Layer**
- Provides targeted feedback grounded in trace evidence  
- Explains failures without rewriting your code by default  

---

## 3. Getting Started

### **Clone the Repository**
```bash
git clone https://github.com/ashokram004/code-aligner.git
cd CodeAligner
```

### **Create a Virtual Environment**
#### Windows
```bash
python -m venv venv
.env\Scriptsctivate
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### **Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## 4. API Configuration

CodeAligner requires a Gemini API key for test-case generation.

1. Open **Google AI Studio**  
2. Generate an API Key  
3. Provide the key inside the application UI when prompted  

No environment variables are required; the key is stored in-session only.

---

## 5. Database Initialization

The first run requires building a local ChromaDB index containing the LeetCode dataset.

```bash
python build_db.py
```

Successful completion prints:

```
SUCCESS! Database built.
```

The generated files will appear in:  
```
leetcodedb_data/
```

---

## 6. Running the Application

### Web Interface (recommended)
```bash
streamlit run app.py
```

After starting, navigate to:

```
http://localhost:8501
```

Paste your code → add Gemini key → Run Analysis.

### CLI Mode
The pipeline is also available via:

```
python cli_runner.py
```

---

## 7. Repository Layout

```
CodeAligner/
│
├── app.py                # Streamlit UI
├── cli_runner.py         # Command-line analysis flow
├── inspector.py          # Language + signature + test generator
├── tracer.py             # Execution trace instrumentation
├── search_engine.py      # Vector-based code retrieval
├── build_db.py           # Local ChromaDB builder
├── leetcodedb_data/      # Generated database directory
└── requirements.txt      # Python dependencies
```

---

## 8. Contributing

Contributions are welcome. To propose a change:

1. Fork the repository  
2. Create a feature branch  
3. Implement your changes  
4. Submit a pull request with a clear summary  

For major features, please open an issue beforehand.

---

## 9. License

This project is open-source and intended for research and educational usage.  
See the LICENSE file for details.
