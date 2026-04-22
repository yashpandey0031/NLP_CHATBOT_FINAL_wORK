from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from chatbot_engine import CoralChatbot


st.set_page_config(page_title="ReefMind: A Coral reef chatbot", page_icon=":ocean:", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    .block-container {
        max-width: min(1700px, 98vw);
        padding-top: 1.1rem;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
        padding-bottom: 2rem;
    }

    .stApp {
        background: linear-gradient(180deg, #f5fbff 0%, #ffffff 45%, #f8fdff 100%);
        color: #12303d;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #0f4a5a;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #3b6a78;
        text-align: center;
        margin-bottom: 1.2rem;
    }

    .stTabs {
        margin-top: 0.25rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 0.55rem;
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid #cfe9f4;
        border-radius: 999px;
        padding: 0.3rem;
        box-shadow: 0 10px 24px rgba(9, 63, 84, 0.08);
        width: fit-content;
        margin: 0 auto 1rem auto;
        position: sticky;
        top: 0.65rem;
        z-index: 30;
        backdrop-filter: blur(6px);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        color: #1e5a6f;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.45rem 1rem;
        height: auto;
        border: 1px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #1f9fc5 0%, #0f7ea1 100%);
        color: #ffffff !important;
        border: 1px solid #0d6f8e !important;
        box-shadow: 0 6px 18px rgba(15, 126, 161, 0.35);
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background: transparent;
    }

    .hero-card {
        border: 1px solid #d3ebf4;
        border-radius: 20px;
        padding: 1.25rem 1.35rem;
        background: #ffffff;
        box-shadow: 0 10px 28px rgba(13, 67, 87, 0.09);
    }

    .hero-kicker {
        font-size: 0.83rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #0f7ea1;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .hero-title {
        font-size: 2rem;
        line-height: 1.15;
        color: #0f4a5a;
        font-weight: 800;
        margin: 0 0 0.55rem 0;
    }

    .hero-text {
        color: #2d6372;
        font-size: 1rem;
        margin-bottom: 0.8rem;
    }

    .icon-label {
        font-size: 0.95rem;
        color: #1e5a6f;
        font-weight: 600;
    }

    .section-card {
        border: 1px solid #dceef5;
        border-radius: 12px;
        padding: 0.9rem 1rem;
        background: #fbfeff;
        margin-bottom: 0.7rem;
    }

    .pill {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        background: #e8f6fc;
        color: #15566c;
        font-size: 0.82rem;
        border: 1px solid #cbeaf5;
        margin-right: 0.35rem;
    }

    @media (max-width: 900px) {
        .main-title {
            font-size: 1.95rem;
        }

        .subtitle {
            font-size: 0.98rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            width: 100%;
            border-radius: 14px;
            justify-content: stretch;
        }

        .stTabs [data-baseweb="tab"] {
            flex: 1;
            text-align: center;
            padding: 0.5rem 0.35rem;
            font-size: 0.9rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">ReefMind: A Coral reef chatbot</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">An NLP-powered learning and conservation assistant to explore coral species, habitats, bleaching, and reef protection.</div>',
    unsafe_allow_html=True,
)

ASSET_DIR = Path(__file__).resolve().parent / "assets"
HERO_IMAGE = ASSET_DIR / "coral_reef_hero.svg"
ICON_IMAGE = ASSET_DIR / "reef_icons.svg"


def stream_text(text: str, delay: float = 0.02):
    words = text.split(" ")
    for i, word in enumerate(words):
        if i < len(words) - 1:
            yield word + " "
        else:
            yield word
        time.sleep(delay)


@st.cache_resource
def get_bot() -> CoralChatbot:
    return CoralChatbot()


bot = get_bot()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I'm your coral reef chatbot. Ask me anything about corals.",
            "score": None,
            "animate": False,
        }
    ]

tab_overview, tab_learn, tab_chat = st.tabs(["Why This Matters", "Learn Corals", "Chat With Coral Bot"])

with tab_overview:
    left, right = st.columns([1.15, 1.0], gap="large")
    with left:
        st.markdown(
            """
            <div class="hero-card">
                <div class="hero-kicker">Ocean Intelligence Platform</div>
                <h2 class="hero-title">Understand Coral Reefs Faster, Before They Disappear</h2>
                <p class="hero-text">
                    This chatbot turns complex reef science into direct, conversational answers.
                    It helps learners and conservation advocates discover species traits, habitats,
                    bleaching impacts, and practical protection actions in seconds.
                </p>
                <span class="pill">Education</span>
                <span class="pill">Conservation</span>
                <span class="pill">Fast Access To Knowledge</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        if HERO_IMAGE.exists():
            st.image(str(HERO_IMAGE), use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Species Knowledge Base", "15k+ Q/A")
    c2.metric("Focus Region", "Indo-Pacific + Caribbean")
    c3.metric("Core Topics", "Species, Habitat, Bleaching")

    if ICON_IMAGE.exists():
        st.image(str(ICON_IMAGE), use_container_width=True)

    feature_cols = st.columns(3)
    feature_cols[0].markdown('<div class="icon-label">Coral ID and morphology insights</div>', unsafe_allow_html=True)
    feature_cols[1].markdown('<div class="icon-label">Habitat and location guidance</div>', unsafe_allow_html=True)
    feature_cols[2].markdown('<div class="icon-label">Bleaching awareness and action</div>', unsafe_allow_html=True)

    st.subheader("Who can use it")
    st.write("- Students learning marine biology")
    st.write("- Divers and snorkellers identifying coral types")
    st.write("- Reef educators and awareness campaigns")
    st.write("- Anyone curious about coral ecosystems")

with tab_learn:
    st.subheader("Quick Learning Modules")

    st.markdown(
        """
        <div class="section-card">
            <b>What are corals?</b><br>
            Corals are animals made of tiny polyps. Over time, reef-building corals create limestone skeletons that form coral reefs.
        </div>
        <div class="section-card">
            <b>What is coral bleaching?</b><br>
            Heat stress can force corals to expel symbiotic algae. Corals then turn white and become vulnerable to starvation and disease.
        </div>
        <div class="section-card">
            <b>Why reefs matter</b><br>
            Reefs support biodiversity, protect coasts from waves, and support tourism and fisheries.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Explore by topic")
    topic_col1, topic_col2 = st.columns(2)
    with topic_col1:
        st.info("Try asking: What corals are found in Australia?")
        st.info("Try asking: Difference between hard and soft corals")
    with topic_col2:
        st.info("Try asking: Why are coral reefs threatened?")
        st.info("Try asking: Where is the Great Barrier Reef?")

    with st.expander("Conservation actions you can take"):
        st.write("- Reduce carbon emissions and energy use")
        st.write("- Use reef-safe sunscreen")
        st.write("- Avoid touching corals while diving/snorkelling")
        st.write("- Support reef conservation organizations")

with tab_chat:
    st.subheader("Chat With Coral Bot")
    st.caption("Ask species, habitat, bleaching, distribution, or reef conservation questions.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("animate"):
                st.write_stream(stream_text(message["content"]))
                message["animate"] = False
            else:
                st.markdown(message["content"])
            if message.get("score") is not None:
                st.caption(f"Similarity score: {message['score']:.3f}")

    prompt = st.chat_input("Ask a coral question...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "score": None})
        response, score = bot.ask(prompt)
        st.session_state.messages.append(
            {"role": "assistant", "content": response, "score": score, "animate": True}
        )
        st.rerun()
