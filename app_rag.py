from __future__ import annotations

import time
import threading
from pathlib import Path

import streamlit as st

from rag_chatbot_engine import CoralRAGChatbot

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ReefMind RAG",
    page_icon="🪸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    html, body {
        background: #0b1a1f !important;
    }

    /* ── app shell ── */
    .stApp {
        background: #0b1a1f;
        color: #d4e8ef;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stVerticalBlock"] {
        background: #0b1a1f !important;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #0d2029;
        border-right: 1px solid #1a3a48;
    }

    /* ── sidebar labels ── */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #7fb8cc !important;
        font-size: 0.82rem;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #b8dbe8 !important;
        font-family: 'DM Serif Display', serif;
    }

    /* ── sidebar sliders & selects ── */
    [data-testid="stSlider"] > div > div > div {
        background: #1a4a5c !important;
    }
    [data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: #5bc8e8 !important;
    }

    /* ── main block ── */
    .block-container {
        max-width: 860px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        margin: 0 auto;
    }

    /* ── wordmark ── */
    .rm-wordmark {
        font-family: 'DM Serif Display', serif;
        font-size: 2.2rem;
        color: #5bc8e8;
        letter-spacing: -0.02em;
        line-height: 1;
    }
    .rm-wordmark span {
        color: #1e7a96;
        font-style: italic;
    }
    .rm-sub {
        font-size: 0.78rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #3d8fa8;
        margin-top: 2px;
        font-weight: 300;
    }

    /* ── status badge ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        font-weight: 500;
        padding: 3px 10px;
        border-radius: 999px;
        margin-top: 6px;
    }
    .status-badge.online {
        background: #0a2e1f;
        color: #3fcf8e;
        border: 1px solid #1a6645;
    }
    .status-badge.offline {
        background: #2e1010;
        color: #cf5050;
        border: 1px solid #662222;
    }
    .status-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: currentColor;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }

    /* ── divider ── */
    hr { border-color: #1a3a48 !important; margin: 0.5rem 0; }

    /* ── chat messages ── */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 0.2rem 0 !important;
    }

    /* user bubble */
    [data-testid="stChatMessage"][data-testid*="user"] .stMarkdown,
    .user-bubble {
        background: #112830;
        border: 1px solid #1e4a5a;
        border-radius: 16px 16px 4px 16px;
        padding: 0.7rem 1rem;
        max-width: 78%;
        margin-left: auto;
        color: #c8e8f4;
        font-size: 0.95rem;
    }

    /* assistant bubble */
    .assistant-bubble {
        background: #0e2530;
        border: 1px solid #1a3a4a;
        border-left: 3px solid #1e7a96;
        border-radius: 4px 16px 16px 16px;
        padding: 0.85rem 1.1rem;
        color: #c8e8f4;
        font-size: 0.95rem;
        line-height: 1.65;
    }

    /* ── context pills ── */
    .ctx-header {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #2e7a96;
        font-weight: 500;
        margin-bottom: 5px;
        margin-top: 10px;
    }
    .ctx-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-bottom: 8px;
    }
    .ctx-pill {
        font-size: 0.72rem;
        background: #0a2535;
        border: 1px solid #1a4a60;
        color: #4ea8c8;
        border-radius: 999px;
        padding: 2px 9px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 280px;
    }
    .ctx-score {
        font-size: 0.65rem;
        color: #2e6a82;
        margin-left: 4px;
    }

    /* ── thinking indicator ── */
    .thinking {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #2e7a96;
        font-size: 0.8rem;
        font-style: italic;
        padding: 6px 0;
    }
    .thinking-dots span {
        display: inline-block;
        width: 5px; height: 5px;
        background: #1e7a96;
        border-radius: 50%;
        animation: bounce 1.1s ease-in-out infinite;
    }
    .thinking-dots span:nth-child(2) { animation-delay: .18s; }
    .thinking-dots span:nth-child(3) { animation-delay: .36s; }
    @keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-6px)} }

    /* ── model info card in sidebar ── */
    .model-card {
        background: #0a1e28;
        border: 1px solid #1a3a48;
        border-radius: 10px;
        padding: 0.75rem 0.9rem;
        margin: 0.5rem 0;
    }
    .model-card .label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #2e7a96;
        margin-bottom: 2px;
    }
    .model-card .value {
        font-size: 0.9rem;
        color: #8dd4e8;
        font-weight: 500;
    }

    /* ── suggested prompts ── */
    .stButton button {
        background: #0d2535 !important;
        border: 1px solid #1e4a60 !important;
        color: #6abcd8 !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        padding: 0.45rem 0.8rem !important;
        width: 100% !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stButton button:hover {
        background: #112e40 !important;
        border-color: #2e7a96 !important;
        color: #8dd4e8 !important;
    }

    /* ── chat input ── */
    .stChatFloatingInputContainer,
    [data-testid="stBottom"],
    [data-testid="stChatInput"] {
        background: transparent !important;
    }
    .stChatFloatingInputContainer > div,
    [data-testid="stBottom"] > div,
    [data-testid="stChatInput"] > div {
        background: transparent !important;
    }
    [data-testid="stChatInput"] textarea {
        background: #0d2029 !important;
    }
    [data-testid="stChatInputTextArea"] {
        background: #0d2029 !important;
        color: #c8e8f4 !important;
        border: 1px solid #1e4a5a !important;
        border-radius: 12px !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    [data-testid="stBottom"] {
        background: transparent !important;
    }
    .main .block-container > div:last-child,
    .stChatFloatingInputContainer,
    .stChatFloatingInputContainer * {
        background: transparent !important;
    }
    [data-testid="stChatInputTextArea"]:focus {
        border-color: #1e7a96 !important;
        box-shadow: 0 0 0 2px rgba(30,122,150,0.15) !important;
    }

    /* ── metric cards ── */
    [data-testid="stMetric"] {
        background: #0a1e28;
        border: 1px solid #1a3a48;
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
    }
    [data-testid="stMetricLabel"] { color: #2e7a96 !important; font-size: 0.72rem !important; }
    [data-testid="stMetricValue"] { color: #5bc8e8 !important; font-size: 1.3rem !important; }

    /* ── expander ── */
    [data-testid="stExpander"] {
        background: #0a1e28 !important;
        border: 1px solid #1a3a48 !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary {
        color: #4ea8c8 !important;
        font-size: 0.8rem !important;
    }

    /* ── scrollbar ── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #0b1a1f; }
    ::-webkit-scrollbar-thumb { background: #1a3a48; border-radius: 2px; }

    /* ── warning / info boxes ── */
    [data-testid="stAlert"] {
        background: #0a1e28 !important;
        border: 1px solid #1a3a48 !important;
        color: #7fb8cc !important;
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Asset paths ────────────────────────────────────────────────────────────────
ASSET_DIR = Path(__file__).resolve().parent / "assets"
BOT_AVATAR = ASSET_DIR / "coral_bot_avatar.svg"


# ── Helpers ────────────────────────────────────────────────────────────────────
def check_ollama_server_status() -> bool:
    """Ping Ollama to see if the server is reachable."""
    import requests as _req
    try:
        r = _req.get("http://localhost:11434/api/tags", timeout=2)
        return bool(r.ok)
    except Exception:
        pass
    return False


def check_ollama_model_status(model: str) -> bool:
    """Check whether the selected Ollama model is installed."""
    import requests as _req
    try:
        r = _req.get("http://localhost:11434/api/tags", timeout=2)
        if r.ok:
            models = [m["name"] for m in r.json().get("models", [])]
            return any(model in m for m in models)
    except Exception:
        pass
    return False


def list_ollama_models() -> list[str]:
    """Return installed Ollama model names, or an empty list if unavailable."""
    import requests as _req
    try:
        r = _req.get("http://localhost:11434/api/tags", timeout=2)
        if r.ok:
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return []


@st.cache_resource
def get_bot(top_k: int, threshold: float, ollama_model: str) -> CoralRAGChatbot:
    return CoralRAGChatbot(top_k=top_k, score_threshold=threshold, ollama_model=ollama_model)


# ── Session defaults ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_context" not in st.session_state:
    st.session_state.show_context = True
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = ""

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="rm-wordmark">Reef<span>Mind</span></div>
        <div class="rm-sub">RAG Edition</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Model settings ──
    st.markdown("#### ⚙️ RAG Settings")

    available_models = list_ollama_models()
    default_models = available_models or ["llama3.2", "mistral", "gemma3:4b", "phi3", "llama3.1"]
    default_index = 0 if not available_models else 0

    ollama_model = st.selectbox(
        "Ollama model",
        default_models,
        index=default_index,
        help="Must be pulled via `ollama pull <model>`",
    )

    top_k = st.slider(
        "Context chunks (top-k)",
        min_value=1, max_value=6, value=3,
        help="How many Q&A pairs to inject as context.",
    )

    threshold = st.slider(
        "Similarity threshold",
        min_value=0.1, max_value=0.9, value=0.3, step=0.05,
        help="Minimum similarity score to include a chunk.",
    )

    show_ctx = st.toggle("Show retrieved context", value=True)
    st.session_state.show_context = show_ctx

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Ollama status ──
    st.markdown("#### 🔌 Ollama Status")
    server_online = check_ollama_server_status()
    model_available = check_ollama_model_status(ollama_model)
    if server_online:
        st.markdown(
            '<span class="status-badge online"><span class="status-dot"></span>Connected</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-badge offline"><span class="status-dot"></span>Offline</span>',
            unsafe_allow_html=True,
        )
        st.caption("Run `ollama serve` to start the local server.")

    if server_online and not model_available:
        st.caption(f"Model `{ollama_model}` is not listed in Ollama yet. Run `ollama pull {ollama_model}` or choose an installed model.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Stats ──
    st.markdown("#### 📊 Session Stats")
    col_a, col_b = st.columns(2)
    col_a.metric("Queries", st.session_state.total_queries)
    col_b.metric("Top-k", top_k)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Suggested prompts ──
    st.markdown("#### 💡 Try asking")
    suggested = [
        "What is coral bleaching?",
        "Corals found in the Great Barrier Reef",
        "Difference between hard and soft corals",
        "How do corals reproduce?",
        "What threatens coral reefs?",
        "What is symbiosis in corals?",
    ]
    for prompt_text in suggested:
        if st.button(prompt_text, key=f"sug_{prompt_text}"):
            st.session_state.suggested_prompt = prompt_text

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Clear ──
    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_queries = 0
        st.rerun()

# ── Main area header ───────────────────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown(
        """
        <div style="padding-bottom: 0.25rem;">
            <div class="rm-wordmark" style="font-size:1.8rem;">Reef<span>Mind</span></div>
            <div class="rm-sub" style="margin-bottom:0.4rem;">Retrieval-Augmented Generation · Coral Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_badge:
    st.markdown(
        f"""
        <div style="text-align:right; padding-top:0.6rem;">
            <span style="
                font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em;
                background:#0a2535; border:1px solid #1a4a60; color:#3d8fa8;
                border-radius:999px; padding:3px 10px; font-weight:500;
            ">🔍 {ollama_model}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ── How RAG works (collapsible) ────────────────────────────────────────────────
with st.expander("How this RAG pipeline works", expanded=False):
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        """
        **1. Retrieve**
        Your question is embedded and matched against the coral knowledge base using FAISS.
        The top-k most similar Q&A pairs are retrieved as context.
        """,
    )
    c2.markdown(
        """
        **2. Augment**
        The retrieved context is injected into a structured prompt together with your question.
        The LLM is instructed to answer *only* from this context.
        """,
    )
    c3.markdown(
        """
        **3. Generate**
        Ollama streams a freshly generated answer — not a canned response.
        This means the bot can synthesise across multiple chunks and answer naturally.
        """,
    )

# ── Load bot ───────────────────────────────────────────────────────────────────
bot = get_bot(top_k=top_k, threshold=threshold, ollama_model=ollama_model)

# ── Welcome message ─────────────────────────────────────────────────────────── 
if not st.session_state.messages:
    st.markdown(
        """
        <div style="
            background: #0d2535;
            border: 1px solid #1a4a60;
            border-left: 3px solid #1e7a96;
            border-radius: 4px 14px 14px 14px;
            padding: 1rem 1.2rem;
            color: #9dd4e4;
            font-size: 0.93rem;
            line-height: 1.65;
            margin-bottom: 1rem;
        ">
            🪸 &nbsp;Hi! I'm <strong style="color:#5bc8e8">ReefMind</strong>, a coral reef assistant powered by RAG.
            I retrieve relevant knowledge from my coral database, then generate a fresh answer using a local LLM.
            Ask me anything about coral species, bleaching, habitats, or reef conservation.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Render chat history ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    role = msg["role"]
    avatar = "🪸" if role == "assistant" else "🧑"
    with st.chat_message(role, avatar=avatar):
        if role == "assistant":
            # Show retrieved context pills
            if st.session_state.show_context and msg.get("contexts"):
                st.markdown('<div class="ctx-header">retrieved context</div>', unsafe_allow_html=True)
                pills_html = '<div class="ctx-pills">'
                for ctx_item in msg["contexts"]:
                    short = ctx_item["text"][:60].replace('"', "'") + ("…" if len(ctx_item["text"]) > 60 else "")
                    score = ctx_item.get("score", 0)
                    pills_html += (
                        f'<span class="ctx-pill" title="{short}">'
                        f'{short}<span class="ctx-score">{score:.2f}</span>'
                        f'</span>'
                    )
                pills_html += "</div>"
                st.markdown(pills_html, unsafe_allow_html=True)

            st.markdown(
                f'<div class="assistant-bubble">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="user-bubble">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

# ── Handle suggested prompt ────────────────────────────────────────────────────
if st.session_state.suggested_prompt:
    prompt = st.session_state.suggested_prompt
    st.session_state.suggested_prompt = ""
else:
    prompt = st.chat_input("Ask about corals…")

# ── Process new prompt ─────────────────────────────────────────────────────────
if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.total_queries += 1

    with st.chat_message("user", avatar="🧑"):
        st.markdown(
            f'<div class="user-bubble">{prompt}</div>',
            unsafe_allow_html=True,
        )

    with st.chat_message("assistant", avatar="🪸"):
        # Retrieve context first (to display pills before streaming)
        with st.spinner(""):
            st.markdown(
                '<div class="thinking">Searching coral knowledge base'
                '<span class="thinking-dots">'
                '<span></span><span></span><span></span>'
                '</span></div>',
                unsafe_allow_html=True,
            )
            contexts = bot.retrieve_contexts(prompt)

        # Show context pills
        if st.session_state.show_context and contexts:
            st.markdown('<div class="ctx-header">retrieved context</div>', unsafe_allow_html=True)
            pills_html = '<div class="ctx-pills">'
            for ctx_item in contexts:
                short = ctx_item["text"][:60].replace('"', "'") + ("…" if len(ctx_item["text"]) > 60 else "")
                score = ctx_item.get("score", 0)
                pills_html += (
                    f'<span class="ctx-pill" title="{short}">'
                    f'{short}<span class="ctx-score">{score:.2f}</span>'
                    f'</span>'
                )
            pills_html += "</div>"
            st.markdown(pills_html, unsafe_allow_html=True)

        # Stream the generated answer
        response_placeholder = st.empty()
        full_response = ""

        try:
            for token in bot.generate(prompt, contexts):
                full_response += token
                response_placeholder.markdown(
                    f'<div class="assistant-bubble">{full_response}▌</div>',
                    unsafe_allow_html=True,
                )
            response_placeholder.markdown(
                f'<div class="assistant-bubble">{full_response}</div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            full_response = (
                "⚠️ Could not reach Ollama. "
                "Make sure it's running (`ollama serve`) and the model is pulled."
            )
            response_placeholder.markdown(
                f'<div class="assistant-bubble">{full_response}</div>',
                unsafe_allow_html=True,
            )

    # Persist to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "contexts": contexts,
    })
    st.rerun()
