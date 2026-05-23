**NLP Chatbot Research Project**

This repository contains research code for building and experimenting with NLP chatbots, including retrieval-augmented generation (RAG) and baseline chatbot implementations. It includes small Streamlit demo apps, engine modules, and example data used during experiments.

**Key Files**

- **app.py / app_rag.py**: Streamlit demo applications for interacting with the chatbot.
- **chatbot_engine.py / rag_chatbot_engine.py / coral.py**: Core experiment code and model integration logic.
- **requirements.txt**: Python dependencies for the project.

**Quick Setup (Windows)**

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the Streamlit demo (choose the app file present):

```powershell
streamlit run app.py
# or
streamlit run app_rag.py

```

**Usage**

- Open the Streamlit URL shown in the terminal (usually http://localhost:8501).
- Interact with the UI to send queries to the chatbot and inspect responses.
