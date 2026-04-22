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

    .panel-shell {
        border: 1px solid #d7edf5;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.92);
        box-shadow: 0 10px 24px rgba(13, 67, 87, 0.06);
        padding: 1rem 1.05rem;
        height: 100%;
    }

    .panel-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0f4a5a;
        margin-bottom: 0.45rem;
    }

    .panel-copy {
        color: #2d6372;
        line-height: 1.7;
        margin-bottom: 0.5rem;
    }

    .menu-caption {
        color: #0f7ea1;
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.25rem;
    }

    .menu-card {
        border: 1px solid #cfe9f4;
        background: #ffffff;
        border-radius: 14px;
        padding: 0.65rem 0.75rem;
        box-shadow: 0 6px 16px rgba(13, 67, 87, 0.05);
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
HERO_IMAGE = Path(__file__).resolve().parent / "coral.jpeg"
ICON_IMAGE = ASSET_DIR / "reef_icons.svg"
BOT_AVATAR = ASSET_DIR / "coral_bot_avatar.svg"


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

if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = ""

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

    st.markdown('<div class="menu-caption">Interactive Menu</div>', unsafe_allow_html=True)
    overview_choice = st.radio(
        "Explore the mission",
        ["Why this matters", "Who can use it", "What the bot does", "Threats to reefs"],
        horizontal=True,
        label_visibility="collapsed",
    )

    overview_panels = {
        "Why this matters": (
            "Reefs cover less than 1% of the ocean floor but support an outsized share of marine biodiversity.\n\n"
            "ReefMind helps people learn quickly, make better decisions, and connect the science of coral reefs with the urgent need for conservation."
        ),
        "Who can use it": (
            "- Students learning marine biology\n"
            "- Divers and snorkellers identifying coral types\n"
            "- Reef educators and awareness campaigns\n"
            "- Anyone curious about coral ecosystems"
        ),
        "What the bot does": (
            "- Answers species identification questions\n"
            "- Explains habitats and distributions\n"
            "- Breaks down bleaching and reef threats\n"
            "- Suggests conservation actions in plain language"
        ),
        "Threats to reefs": (
            "Corals are under pressure from warming seas, pollution, destructive fishing, ocean acidification, and disease outbreaks.\n\n"
            "The more people can learn interactively, the more likely they are to care and act."
        ),
    }

    st.markdown(
        f'''
        <div class="panel-shell">
            <div class="panel-title">{overview_choice}</div>
            <div class="panel-copy">{overview_panels[overview_choice].replace(chr(10), '<br>')}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    with st.expander("Quick facts panel"):
        f1, f2, f3 = st.columns(3)
        f1.metric("Species Knowledge Base", "15k+ Q/A")
        f2.metric("Focus Region", "Indo-Pacific + Caribbean")
        f3.metric("Core Topics", "Species, Habitat, Bleaching")

with tab_learn:
    st.subheader("Quick Learning Modules")

    learning_choice = st.radio(
        "Choose a learning module",
        ["What are corals?", "Coral bleaching", "Hard vs soft corals", "Why reefs matter"],
        horizontal=True,
        label_visibility="collapsed",
    )

    learning_panels = {
        "What are corals?": (
            "Corals are animals made of tiny polyps. Over time, reef-building corals create limestone skeletons that form coral reefs.",
            ["What corals are found in Australia?", "Tell me about Acropora species"],
        ),
        "Coral bleaching": (
            "Heat stress can force corals to expel symbiotic algae. Corals then turn white and become vulnerable to starvation and disease.",
            ["What is coral bleaching?", "How do corals recover from bleaching?"],
        ),
        "Hard vs soft corals": (
            "Hard corals build reef structures using limestone skeletons. Soft corals are flexible, decorative, and sway with the current.",
            ["Difference between hard and soft corals", "What are reef-building corals?"],
        ),
        "Why reefs matter": (
            "Reefs support biodiversity, protect coasts from waves, and support tourism and fisheries.",
            ["Why are coral reefs threatened?", "What is the Great Barrier Reef?"],
        ),
    }

    module_text, module_prompts = learning_panels[learning_choice]

    lc1, lc2 = st.columns([1.25, 1.0], gap="large")
    with lc1:
        st.markdown(
            f'''
            <div class="panel-shell">
                <div class="menu-caption">Learning Panel</div>
                <div class="panel-title">{learning_choice}</div>
                <div class="panel-copy">{module_text}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    with lc2:
        st.markdown('<div class="menu-caption">Try asking the bot</div>', unsafe_allow_html=True)
        for i, prompt_text in enumerate(module_prompts):
            st.button(
                prompt_text,
                use_container_width=True,
                key=f"learn_prompt_{learning_choice}_{i}",
                on_click=lambda q=prompt_text: st.session_state.__setitem__("suggested_prompt", q),
            )

    with st.expander("More learning paths"):
        exp1, exp2 = st.columns(2)
        with exp1:
            st.markdown(
                """
                <div class="section-card">
                    <b>Why reefs matter</b><br>
                    Reefs support biodiversity, protect coasts from waves, and support tourism and fisheries.
                </div>
                <div class="section-card">
                    <b>Conservation actions</b><br>
                    Reduce emissions, use reef-safe sunscreen, avoid touching corals, and support reef organizations.
                </div>
                """,
                unsafe_allow_html=True,
            )
        with exp2:
            st.markdown(
                """
                <div class="section-card">
                    <b>Best starter questions</b><br>
                    What are corals? How do reefs form? Where are coral reefs found?
                </div>
                <div class="section-card">
                    <b>Field guide ideas</b><br>
                    Identify coral shape, color, habitat, abundance, and geographic range.
                </div>
                """,
                unsafe_allow_html=True,
            )

with tab_chat:
    st.subheader("Chat With Coral Bot")
    st.caption("Ask species, habitat, bleaching, distribution, or reef conservation questions.")

    if st.session_state.suggested_prompt:
        st.info(f"Suggested question from Learn Corals: {st.session_state.suggested_prompt}")

    for message in st.session_state.messages:
        avatar = BOT_AVATAR if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
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
