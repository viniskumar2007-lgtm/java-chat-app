from __future__ import annotations

import os
import re
import uuid
from datetime import datetime
from typing import Any

import streamlit as st
from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "JavaChat"
REQUESTED_MODEL = os.getenv("GEMINI_MODEL", "").strip()
KB_FILE = "java.txt"

MAX_HISTORY_MESSAGES = 6
MAX_KB_CHUNKS = 2
MAX_KB_CHARS = 6000


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HTML HELPERS
# ============================================================

def html(markup: str) -> str:
    """Collapse HTML to one line so Markdown never treats
    indented HTML as a code block."""
    return "".join(line.strip() for line in markup.splitlines())


def render(markup: str) -> None:
    st.markdown(html(markup), unsafe_allow_html=True)


def feature_card(icon: str, title: str, description: str) -> None:
    render(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-text">{description}</div>
        </div>
        """
    )


def section_title(text: str) -> None:
    render(f'<div class="section-title">{text}</div>')


def hero(badge: str, title_html: str, description: str) -> None:
    render(
        f"""
        <div class="hero">
            <div class="hero-badge">{badge}</div>
            <div class="hero-title">{title_html}</div>
            <div class="hero-description">{description}</div>
        </div>
        """
    )


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    #MainMenu,
    footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    .stApp {
        background: #0b0d12;
        color: #e8eaf0;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 1rem;
        padding-bottom: 7rem;
    }

    [data-testid="stSidebar"] {
        background: #101218;
        border-right: 1px solid #292d36;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 42px;
        background: #171a21;
        color: #dfe1e8;
        border: 1px solid #2b2e37;
        border-radius: 10px;
        text-align: left;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: #211c16;
        border-color: #f89820;
        color: #f89820;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 4px 22px;
    }

    .brand-icon,
    .top-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f89820, #bd560d);
        box-shadow: 0 8px 25px rgba(248, 152, 32, 0.2);
    }

    .brand-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        font-size: 22px;
    }

    .brand-name {
        color: white;
        font-size: 1.1rem;
        font-weight: 750;
    }

    .brand-subtitle {
        color: #707581;
        font-size: 0.68rem;
        margin-top: 2px;
    }

    .side-label {
        color: #676c78;
        font-size: 0.67rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 22px 0 8px;
    }

    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0 16px;
        margin-bottom: 22px;
        border-bottom: 1px solid #242731;
    }

    .top-left {
        display: flex;
        align-items: center;
        gap: 11px;
    }

    .top-icon {
        width: 38px;
        height: 38px;
        border-radius: 11px;
        font-size: 20px;
    }

    .top-title {
        color: white;
        font-size: 1rem;
        font-weight: 700;
    }

    .top-subtitle {
        color: #6e7380;
        font-size: 0.68rem;
        margin-top: 2px;
    }

    .status {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #777d88;
        font-size: 0.7rem;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #52bd8c;
        box-shadow: 0 0 9px rgba(82, 189, 140, 0.7);
    }

    .hero {
        padding: 42px 32px;
        border-radius: 20px;
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(248, 152, 32, 0.13),
                transparent 32%
            ),
            radial-gradient(
                circle at 90% 100%,
                rgba(73, 180, 164, 0.08),
                transparent 30%
            ),
            #11141b;
        border: 1px solid #282c36;
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.22);
    }

    .hero-badge {
        display: inline-flex;
        padding: 6px 11px;
        border-radius: 30px;
        background: #1d1914;
        border: 1px solid #67451e;
        color: #f0a04b;
        font-size: 0.68rem;
        font-weight: 650;
    }

    .hero-title {
        margin-top: 18px;
        color: white;
        font-size: clamp(2rem, 5vw, 3.2rem);
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.04em;
    }

    .hero-title span {
        color: #f89820;
    }

    .hero-description {
        max-width: 680px;
        margin-top: 14px;
        color: #858b98;
        font-size: 0.94rem;
        line-height: 1.7;
    }

    .stats {
        display: flex;
        gap: 12px;
        margin-top: 28px;
        flex-wrap: wrap;
    }

    .stat {
        padding: 10px 14px;
        border-radius: 10px;
        background: #171a21;
        border: 1px solid #292d37;
    }

    .stat-number {
        color: #f3f4f7;
        font-weight: 750;
        font-size: 0.86rem;
    }

    .stat-label {
        color: #6c717d;
        font-size: 0.64rem;
        margin-top: 2px;
    }

    .section-title {
        color: #f1f2f5;
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 5px;
    }

    .section-description {
        color: #6c717d;
        font-size: 0.74rem;
        margin-bottom: 14px;
    }

    .feature-card {
        min-height: 145px;
        padding: 18px;
        border-radius: 14px;
        background: #12151c;
        border: 1px solid #272b34;
        margin-bottom: 8px;
    }

    .feature-icon {
        font-size: 1.35rem;
        margin-bottom: 12px;
    }

    .feature-title {
        color: #e8e9ee;
        font-size: 0.83rem;
        font-weight: 700;
    }

    .feature-text {
        color: #707581;
        font-size: 0.69rem;
        line-height: 1.5;
        margin-top: 6px;
    }

    .topic-list {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-top: 12px;
    }

    .topic {
        padding: 7px 11px;
        border-radius: 20px;
        background: #15181f;
        border: 1px solid #292d36;
        color: #aeb2bd;
        font-size: 0.68rem;
    }

    [data-testid="stChatMessage"] {
        border-radius: 14px;
        border: 1px solid #252934;
        padding: 0.85rem 1rem;
        margin-bottom: 9px;
    }

    [data-testid="stChatMessage"] pre {
        border-radius: 10px;
        border: 1px solid #2b2f39;
    }

    [data-testid="stChatInput"] > div {
        background: #171a22;
        border: 1px solid #343843;
        border-radius: 15px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.22);
    }

    [data-testid="stChatInput"] textarea {
        color: white;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #686e7b;
    }

    @media (max-width: 700px) {
        .main .block-container {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }

        .hero {
            padding: 28px 20px;
        }

        .hero-title {
            font-size: 2rem;
        }

        .status {
            display: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

def create_empty_chat() -> dict[str, Any]:
    return {
        "title": "New Java Chat",
        "created": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "messages": [],
    }


def initialize_state() -> None:
    if "chats" not in st.session_state:
        chat_id = str(uuid.uuid4())
        st.session_state.chats = {chat_id: create_empty_chat()}
        st.session_state.active_chat_id = chat_id

    if "active_chat_id" not in st.session_state:
        st.session_state.active_chat_id = next(
            iter(st.session_state.chats)
        )

    if "page" not in st.session_state:
        st.session_state.page = "Chat"

    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


def get_active_chat() -> dict[str, Any]:
    return st.session_state.chats[st.session_state.active_chat_id]


def create_new_chat() -> None:
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = create_empty_chat()
    st.session_state.active_chat_id = chat_id


def delete_all_chats() -> None:
    st.session_state.chats = {}
    create_new_chat()


def make_chat_title(question: str) -> str:
    title = " ".join(question.strip().split())

    if len(title) > 34:
        title = title[:34].rstrip() + "..."

    return title or "New Java Chat"


def request_question(question: str) -> None:
    st.session_state.page = "Chat"
    st.session_state.pending_question = question
    st.rerun()


initialize_state()


# ============================================================
# KNOWLEDGE BASE
# ============================================================

@st.cache_data
def load_knowledge_base() -> str:
    try:
        with open(KB_FILE, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""


@st.cache_data
def create_kb_chunks(text: str) -> list[str]:
    if not text.strip():
        return []

    sections = re.split(
        r"\n(?=(?:#{1,6}\s|[A-Z][A-Za-z ]{2,40}:))",
        text,
    )

    chunks = [
        section.strip()
        for section in sections
        if section.strip()
    ]

    if len(chunks) <= 1:
        paragraphs = re.split(r"\n\s*\n", text)
        chunks = [
            paragraph.strip()
            for paragraph in paragraphs
            if paragraph.strip()
        ]

    return chunks


STOP_WORDS = {
    "the", "is", "a", "an", "what", "why", "how",
    "to", "in", "of", "for", "and", "or", "with",
    "give", "me", "explain", "show", "tell", "java",
    "program", "please", "can", "you",
}


def find_relevant_knowledge(
    question: str,
    chunks: list[str],
    max_chunks: int = 3,
) -> str:
    if not chunks:
        return ""

    question_words = set(re.findall(r"[a-zA-Z0-9]+", question.lower()))
    question_words -= STOP_WORDS

    scored_chunks = []

    for chunk in chunks:
        chunk_words = set(re.findall(r"[a-zA-Z0-9]+", chunk.lower()))
        score = len(question_words.intersection(chunk_words))
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    selected = [
        chunk
        for score, chunk in scored_chunks
        if score > 0
    ][:max_chunks]

    if not selected:
        selected = chunks[:1]

    knowledge = "\n\n---\n\n".join(selected)
    return knowledge[:MAX_KB_CHARS]


kb = load_knowledge_base()
kb_chunks = create_kb_chunks(kb)


# ============================================================
# GEMINI
# ============================================================

def get_api_key() -> str | None:
    try:
        key = st.secrets.get("GEMINI_API_KEY")

        if key:
            return str(key)
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY")


@st.cache_resource
def create_gemini_client() -> genai.Client | None:
    api_key = get_api_key()

    if not api_key:
        return None

    try:
        return genai.Client(api_key=api_key)
    except Exception as error:
        st.error(f"Could not initialize Gemini: {error}")
        return None


client = create_gemini_client()


@st.cache_resource
def discover_models() -> list[str]:
    """Return usable text-generation models reported by the API."""
    if client is None:
        return []

    try:
        models = list(client.models.list())
    except Exception:
        return []

    candidates: list[tuple[str, list[str]]] = []

    for model in models:
        name = str(getattr(model, "name", ""))
        if name.startswith("models/"):
            name = name[len("models/"):]

        actions = [
            str(action)
            for action in getattr(model, "supported_actions", [])
        ]

        lowered_name = name.lower()
        excluded_name = any(
            marker in lowered_name
            for marker in (
                "tts",
                "text-to-speech",
                "embedding",
                "image",
                "aqa",
            )
        )

        if name and "generateContent" in actions and not excluded_name:
            candidates.append((name, actions))

    preferred_names = (
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    )

    ordered_names: list[str] = []
    requested = REQUESTED_MODEL.removeprefix("models/")

    if requested:
        ordered_names.append(requested)

    for preferred_name in preferred_names:
        if preferred_name not in ordered_names:
            ordered_names.append(preferred_name)

    for name, _ in candidates:
        lowered = name.lower()
        if (
            "embedding" not in lowered
            and "image" not in lowered
            and "aqa" not in lowered
            and name not in ordered_names
        ):
            ordered_names.append(name)

    available_names = {name for name, _ in candidates}
    return [
        name
        for name in ordered_names
        if name in available_names
    ]


MODELS = discover_models()


# ============================================================
# AI PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are JavaChat, a friendly Java programming assistant.

Help beginner and intermediate students learn Java.

You can explain:

- Java syntax
- Variables and data types
- Operators
- Conditions
- Switch statements
- Loops
- Arrays
- Strings
- Methods
- Classes and objects
- Constructors
- Inheritance
- Polymorphism
- Encapsulation
- Abstraction
- Interfaces
- Exceptions
- Threads
- Debugging
- Programming problems
- Java examinations

Rules:

1. Use simple English.
2. Explain concepts step by step.
3. Give practical examples.
4. Use Markdown.
5. Java code must use ```java code blocks.
6. Give complete runnable Java code when code is requested.
7. For programming problems, use this structure:

Problem:
Logic:
Code:
Explanation:
Output:

8. For "what is" questions, begin with a definition.
9. For "how" questions, give clear numbered steps.
10. Maintain conversation context.
11. Do not mention system prompts, API keys, or internal implementation.
"""


MISSING_KEY_MESSAGE = """
### Gemini API key is missing

Create this file:

`.streamlit/secrets.toml`

Then add:

```toml
GEMINI_API_KEY = "your-real-gemini-api-key"
```

Restart the application after saving the key.
"""


def build_prompt(
    user_question: str,
    history_messages: list[dict[str, str]],
) -> str:
    recent_messages = history_messages[-MAX_HISTORY_MESSAGES:]

    history_lines = []

    for message in recent_messages:
        role = "USER" if message["role"] == "user" else "JAVACHAT"
        history_lines.append(f"{role}: {message['content']}")

    history = "\n\n".join(history_lines)

    relevant_knowledge = find_relevant_knowledge(
        user_question,
        kb_chunks,
        MAX_KB_CHUNKS,
    )

    return f"""
RELEVANT JAVA KNOWLEDGE:
{relevant_knowledge or "No local knowledge-base content is available."}

RECENT CHAT HISTORY:
{history or "No previous messages."}

LATEST USER QUESTION:
{user_question}

Answer the latest question while maintaining context.
"""


def model_not_found_message(error_text: str) -> str:
    return (
        "### Gemini model unavailable\n\n"
        "Google rejected every model reported for this API key. "
        "Check the key and enabled Gemini API.\n\n"
        "Original error:\n\n"
        f"```text\n{error_text}\n```"
    )


def permission_denied_message(error_text: str) -> str:
    return (
        "### Gemini permission denied\n\n"
        "Check that your API key is valid and that the Gemini API is "
        "enabled for its Google Cloud project.\n\n"
        "Original error:\n\n"
        f"```text\n{error_text}\n```"
    )


def quota_message(error_text: str) -> str:
    retry_match = re.search(
        r"retry(?: in| after).*?(\d+(?:\.\d+)?)s",
        error_text,
        re.IGNORECASE,
    )
    retry_text = (
        f" Try again in about {retry_match.group(1)} seconds."
        if retry_match
        else " Wait briefly and try again."
    )

    return (
        "### Gemini quota exceeded\n\n"
        "Google has temporarily limited this API key's free-tier "
        "input-token usage."
        f"{retry_text}\n\n"
        "For higher limits, review your plan and billing here:\n"
        "https://ai.google.dev/gemini-api/docs/rate-limits\n\n"
        "JavaChat also limits local context to reduce token usage.\n\n"
        f"```text\n{error_text}\n```"
    )


def generate_answer(
    user_question: str,
    history_messages: list[dict[str, str]],
) -> str:
    if client is None:
        return MISSING_KEY_MESSAGE

    if not MODELS:
        return (
            "### No compatible Gemini model found\n\n"
            "This API key did not return a model that supports "
            "`generateContent`. Verify the key in "
            "`.streamlit/secrets.toml` and enable the Gemini API."
        )

    prompt = build_prompt(user_question, history_messages)

    errors: list[str] = []

    for model_name in MODELS:
        try:
            chat = client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.4,
                    max_output_tokens=2048,
                ),
            )

            response = chat.send_message(prompt)
            answer = getattr(response, "text", None)

            if answer:
                return answer

            errors.append(f"{model_name}: empty response")

        except Exception as error:
            error_text = str(error)
            errors.append(f"{model_name}: {error_text}")

            if "403" in error_text or "PERMISSION_DENIED" in error_text:
                return permission_denied_message(error_text)

            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "quota" in error_text.lower()
            ):
                return quota_message(error_text)

            retryable_error = (
                "NOT_FOUND" in error_text
                or "not found" in error_text.lower()
                or "INVALID_ARGUMENT" in error_text
                or "response modalities" in error_text.lower()
            )

            if not retryable_error:
                return (
                    "### Gemini request failed\n\n"
                    f"```text\n{error_text}\n```"
                )

    return model_not_found_message("\n".join(errors))


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    render(
        """
        <div class="brand">
            <div class="brand-icon">☕</div>
            <div>
                <div class="brand-name">JavaChat</div>
                <div class="brand-subtitle">Learn Java. Build confidence.</div>
            </div>
        </div>
        """
    )

    render('<div class="side-label">Workspace</div>')

    pages = [
        ("💬", "Chat"),
        ("📚", "Learn"),
        ("💻", "Code Lab"),
        ("📝", "Exam Practice"),
    ]

    for icon, page_name in pages:
        if st.button(
            f"{icon}  {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True,
        ):
            st.session_state.page = page_name
            st.rerun()

    render('<div class="side-label">Conversation</div>')

    if st.button(
        "＋  New Chat",
        key="new_chat",
        use_container_width=True,
    ):
        create_new_chat()
        st.session_state.page = "Chat"
        st.rerun()

    render('<div class="side-label">Recent Chats</div>')

    recent_chats = list(st.session_state.chats.items())
    recent_chats.reverse()

    for chat_id, chat in recent_chats[:8]:
        title = chat["title"]

        if len(title) > 25:
            title = title[:25] + "..."

        prefix = "●" if chat_id == st.session_state.active_chat_id else "○"

        if st.button(
            f"{prefix}  {title}",
            key=f"chat_{chat_id}",
            use_container_width=True,
        ):
            st.session_state.active_chat_id = chat_id
            st.session_state.page = "Chat"
            st.rerun()

    render('<div class="side-label">Settings</div>')

    if st.button(
        "🗑️  Clear all chats",
        key="clear_chats",
        use_container_width=True,
    ):
        delete_all_chats()
        st.rerun()


# ============================================================
# TOP NAVIGATION
# ============================================================

render(
    f"""
    <div class="top-nav">
        <div class="top-left">
            <div class="top-icon">☕</div>
            <div>
                <div class="top-title">JavaChat</div>
                <div class="top-subtitle">{st.session_state.page}</div>
            </div>
        </div>
        <div class="status">
            <span class="status-dot"></span>
            AI Java Assistant
        </div>
    </div>
    """
)

active_chat = get_active_chat()
messages = active_chat["messages"]


# ============================================================
# CHAT PAGE
# ============================================================

if st.session_state.page == "Chat":

    # Read input first so the welcome screen disappears as soon
    # as a question is submitted.
    user_question = st.chat_input("Ask JavaChat anything about Java...")

    if st.session_state.pending_question:
        user_question = st.session_state.pending_question
        st.session_state.pending_question = None

    if not messages and not user_question:
        hero(
            "☕ AI-powered Java learning",
            "Learn Java.<br><span>Build with confidence.</span>",
            "Ask questions, understand OOP, solve programming problems, "
            "debug code, and prepare for Java exams.",
        )

        render(
            """
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">12+</div>
                    <div class="stat-label">Java topics</div>
                </div>
                <div class="stat">
                    <div class="stat-number">AI</div>
                    <div class="stat-label">Explanations</div>
                </div>
                <div class="stat">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Learning assistant</div>
                </div>
            </div>
            """
        )

        section_title("Start learning")

        render(
            '<div class="section-description">'
            "Choose a topic or ask your own question."
            "</div>"
        )

        columns = st.columns(3)

        actions = [
            (
                "🧠",
                "Learn OOP",
                "Understand the four pillars of OOP.",
                "Explain OOP in Java in simple English with examples.",
            ),
            (
                "🧬",
                "Inheritance",
                "Learn inheritance with a practical example.",
                "Explain inheritance in Java with a simple example.",
            ),
            (
                "🏗️",
                "Constructors",
                "Understand constructors and object creation.",
                "What is a constructor in Java? Explain with an example.",
            ),
        ]

        for column, action in zip(columns, actions):
            icon, title, description, question = action

            with column:
                feature_card(icon, title, description)

                if st.button(
                    f"Explore {title} →",
                    key=f"action_{title}",
                    use_container_width=True,
                ):
                    request_question(question)

        section_title("Java topics")

        topics = [
            "Syntax", "Variables", "Conditions", "Loops", "Arrays",
            "Strings", "Methods", "Classes", "Objects", "Constructors",
            "Inheritance", "Polymorphism", "Encapsulation",
            "Abstraction", "Interfaces", "Exceptions", "Threads",
        ]

        topic_html = '<div class="topic-list">'
        for topic in topics:
            topic_html += f'<span class="topic">{topic}</span>'
        topic_html += "</div>"

        render(topic_html)

    # Show existing conversation
    for message in messages:
        role = message["role"]
        avatar = "🧑‍💻" if role == "user" else "☕"

        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])

    # Handle a new question
    if user_question:
        if not messages:
            active_chat["title"] = make_chat_title(user_question)

        # History = everything before this new question
        history_before = list(messages)

        messages.append({"role": "user", "content": user_question})

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_question)

        with st.chat_message("assistant", avatar="☕"):
            with st.spinner("JavaChat is thinking..."):
                answer = generate_answer(user_question, history_before)

            st.markdown(answer)

        messages.append({"role": "assistant", "content": answer})

        st.rerun()


# ============================================================
# LEARN PAGE
# ============================================================

elif st.session_state.page == "Learn":

    hero(
        "📚 Java Learning Hub",
        "Explore Java concepts",
        "Choose a topic and let JavaChat explain it with "
        "beginner-friendly examples.",
    )

    section_title("Core Java")

    learn_topics = [
        ("☕", "Java Basics", "Syntax, variables, data types and operators."),
        ("🔁", "Control Flow", "if/else, switch and loops."),
        ("📦", "Arrays & Strings", "Work with values and text."),
        ("🧩", "Methods", "Parameters, return values and method design."),
        ("🏛️", "Classes & Objects", "Understand Java's object-oriented structure."),
        ("🧬", "Inheritance", "Reuse and extend existing classes."),
        ("🎭", "Polymorphism", "Understand method overriding and dynamic behavior."),
        ("🔐", "Encapsulation", "Protect and organize object data."),
        ("🧱", "Abstraction", "Focus on essential behavior."),
        ("🔌", "Interfaces", "Define contracts between classes."),
        ("⚠️", "Exceptions", "Handle errors safely."),
        ("🧵", "Threads", "Understand concurrent Java programs."),
    ]

    for row in range(0, len(learn_topics), 3):
        columns = st.columns(3)

        for column, topic in zip(columns, learn_topics[row:row + 3]):
            icon, title, description = topic

            with column:
                feature_card(icon, title, description)

                if st.button(
                    f"Learn {title} →",
                    key=f"learn_{title}",
                    use_container_width=True,
                ):
                    request_question(
                        f"Teach me {title} in Java from beginner level "
                        "with examples."
                    )


# ============================================================
# CODE LAB PAGE
# ============================================================

elif st.session_state.page == "Code Lab":

    hero(
        "💻 Java Code Lab",
        "Practice Java by writing code",
        "Write Java code and ask JavaChat to explain, debug, "
        "improve or review it.",
    )

    section_title("Your Java code")

    default_code = """public class Main {
    public static void main(String[] args) {
        System.out.println("Hello Java!");
    }
}"""

    code = st.text_area(
        "Java code",
        value=default_code,
        height=320,
        key="java_code",
        label_visibility="collapsed",
    )

    columns = st.columns(3)

    prompts = [
        (
            "🐛 Debug code",
            "Debug this Java code and explain every problem clearly:",
        ),
        (
            "💡 Explain code",
            "Explain this Java code line by line:",
        ),
        (
            "✨ Improve code",
            "Improve this Java code and explain the improvements:",
        ),
    ]

    for column, (button_text, instruction) in zip(columns, prompts):
        with column:
            if st.button(
                button_text,
                key=f"code_action_{button_text}",
                use_container_width=True,
            ):
                request_question(
                    instruction + "\n\n```java\n" + code + "\n```"
                )


# ============================================================
# EXAM PRACTICE PAGE
# ============================================================

elif st.session_state.page == "Exam Practice":

    hero(
        "📝 Exam preparation",
        "Practice Java questions",
        "Prepare definitions, theory questions, programming "
        "problems and viva questions.",
    )

    section_title("Practice mode")

    columns = st.columns(2)

    with columns[0]:
        feature_card(
            "📖",
            "Theory Questions",
            "Practice Java definitions, OOP concepts and short answers.",
        )

        if st.button(
            "Start theory practice →",
            key="theory_practice",
            use_container_width=True,
        ):
            request_question(
                "Give me 5 important Java theory questions for an exam. "
                "Ask them one at a time and wait for my answer."
            )

    with columns[1]:
        feature_card(
            "💻",
            "Programming Problems",
            "Practice Java coding problems with increasing difficulty.",
        )

        if st.button(
            "Start coding practice →",
            key="coding_practice",
            use_container_width=True,
        ):
            request_question(
                "Give me a beginner Java programming problem. "
                "Do not show the solution until I try it."
            )