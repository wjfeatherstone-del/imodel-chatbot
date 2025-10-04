import streamlit as st
import openai

# ---------- CONFIG ----------
openai.api_key = openai.api_key = st.secrets["OPENAI_API_KEY"]  # Replace with your valid key
st.set_page_config(page_title="IModel Chatbot", page_icon="⚽", layout="centered")

# ---------- LOAD RULES ----------
@st.cache_data
def load_rules():
    try:
        with open("imodel_rules.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

DOCUMENT = load_rules()

# ---------- HELPER:  Local small-talk ----------
def local_response(text: str) -> str | None:
    t = text.lower().strip(" ?.!")
    if t in {"hi", "hello", "hey"}:
        return "👋 Hi there! How can I help you with the IModel Rules today?"
    if t in {"how are you", "how are you doing"}:
        return "😊 I’m doing great, thank you! What would you like to know about the IModel Rules?"
    return None

# ---------- UI HEADER ----------
st.title("🏆 IModel Rules Assistant")
st.caption(
    "Ask me questions about the 2025 Ontario Soccer IModel Rules (Central Region). "
    "If something breaks, contact [wjfeatherstone@gmail.com]"
    "(mailto:wjfeatherstone@gmail.com)."
)

# ---------- SUGGESTED PROMPTS ----------
suggested = [
    "When is the roster freeze deadline?",
    "How many games can a call-up play?",
    "What is the fine for missing a mandatory meeting?",
    "Tell me about player eligibility rules.",
    "Hi 👋",
]
with st.expander("💡 Suggested Questions"):
    for s in suggested:
        st.markdown(f"- {s}")

# ---------- INITIALIZE SESSION ----------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------- DISPLAY HISTORY ----------
for role, message in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(message)

# ---------- USER INPUT ----------
if prompt := st.chat_input("Type your question..."):
    # Add user message
    st.session_state.chat.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # First, check small talk
    reply = local_response(prompt)

    if not reply:
        # Compose prompt for the model
        context = (
            "You are a polite assistant that only answers using information "
            "from the following 2025 IModel Rules and Regulations document "
            "(Central Region). If the answer isn't in the document, say you do not know.\n\n"
            f"Document:\n{DOCUMENT[:150000]}\n\nQuestion: {prompt}\nAnswer:"
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": context}],
                temperature=0.2,
                max_tokens=400,
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = (
                f"❌ Sorry, an error occurred:\n> {e}\n\n"
                "If this continues, please email [wjfeatherstone@gmail.com]"
                "(mailto:wjfeatherstone@gmail.com)."
            )

    # Add assistant message
    st.session_state.chat.append(("assistant", reply))
    with st.chat_message("assistant"):

        st.markdown(reply)
