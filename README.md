# 🧬 CodeAligner AI  
### **The Execution-Aware Coding Assistant**

CodeAligner goes beyond standard AI chat assistants. It is a **deep analysis engine** that executes your code side-by-side with verified *Golden Solutions* to detect:

- Logic bugs  
- Runtime crashes  
- Time & space inefficiencies (e.g., **O(n²)** vs **O(n)**)  
- Unexpected control-flow differences  

All using **real-time execution traces**.

---

## 🚀 Key Features

### 🕵️ **Universal Inspector**
- Detects programming language automatically (Python / C++ / Java)  
- Extracts function signatures  
- Generates valid test cases using **Google Gemini**

### 🧠 **Hybrid Vector Search**
- Built on **ChromaDB**  
- Matches your code against **2,500+ LeetCode solutions**  
- Uses both code logic and AI-predicted problem names for high-accuracy lookup

### ⚡ **Execution Tracing (Python)**
- Runs your code + the Golden Solution in a sandbox  
- Compares step-by-step execution with `sys.settrace`  
- Captures variable states and call graph

### 📉 **Complexity Analysis**
- Detects abnormally slow patterns  
- Example: Bubble Sort vs Quick Sort  
- Highlights loops, nested loops, and repeated operations

### 🎓 **AI Mentor Mode**
- Gives constructive, developer-friendly feedback  
- Points out root causes instead of just rewriting your code  

---

## 🛠️ Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/ashokram004/code-aligner.git
cd CodeAligner
```

### **2. Set up Virtual Environment** *(Recommended)*

#### Windows
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## 🔑 Get Your API Key

You need a **Google Gemini API Key** (Free tier available).

1. Go to **Google AI Studio**  
2. Create an API Key  
3. Enter this key inside the CodeAligner App UI when prompted

---

## ⚙️ Database Setup (First Run Only)

CodeAligner uses a custom LeetCode dataset embedded locally using ChromaDB.

Run:
```bash
python build_db.py
```

You will see:

```
SUCCESS! Database built.
```

---

## 🖥️ Usage

You can run CodeAligner in two modes:

---

## 🌟 Mode 1: Web Interface (Recommended)

```bash
streamlit run app.py
```

Open: **http://localhost:8501**

- Enter your **Gemini API Key**  
- Paste your code  
- Click **Run Analysis**

---

## 💻 Mode 2: CLI Mode (Terminal)

Add your API key in `main.py` and run:

```bash
python main.py
```

---

## 📂 Project Structure

| File / Folder          | Description |
|------------------------|-------------|
| `app.py`               | Streamlit UI |
| `main.py`              | CLI pipeline controller |
| `inspector.py`         | Language detection + test case generator |
| `tracer.py`            | Execution tracing engine |
| `search_engine.py`     | Vector search logic |
| `build_db.py`          | Script to build local ChromaDB |
| `leetcodedb_data/`     | Auto-generated vector database |
| `requirements.txt`     | Dependency list |

---

## 🤝 Contributing

1. Fork the repo  
2. Create a feature branch  
3. Commit changes  
4. Open a Pull Request  

---

## 📄 License

This project is **open-source** and intended for **educational purposes**.
