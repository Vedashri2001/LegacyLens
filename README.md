# 🔍 LegacyLens

AI-powered tool that transforms legacy mainframe code (RPGLE, COBOL, JCL, PL/I, Natural/ADABAS, CL) into plain-English documentation and modern Python — built with Streamlit and Google Gemini.

## Setup & Run Locally

### Prerequisites
- **Python 3.10+** installed ([download](https://www.python.org/downloads/))
- A **Gemini API Key** (free) — get one at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/Vedashri2001/LegacyLens.git
cd LegacyLens

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open in your browser at **http://localhost:8501**.

### First Use
1. Paste your **Gemini API Key** in the sidebar
2. Select a **Legacy Language** (COBOL, RPGLE, JCL, etc.)
3. Paste your code or click **Load Sample**
4. Click **Full Analysis** to get documentation + Python translation

### Troubleshooting

| Issue | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| Rate limit / quota error | Switch to **Gemini Flash (Latest)** in the sidebar dropdown |
| Output truncated | Use **Translate to Python** separately instead of Full Analysis |
