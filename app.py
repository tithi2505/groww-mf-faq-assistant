import streamlit as st
import csv
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="Mutual Fund Facts Assistant",
    page_icon="📘",
    layout="centered"
)

LAST_UPDATED = "2 October 2026"

SEBI_EDUCATION_LINK = (
    "https://investor.sebi.gov.in/regular_and_direct_mutual_funds.html"
)

HDFC_FACTSHEET_LINK = (
    "https://www.hdfcfund.com/mutual-funds/factsheets"
)

# -----------------------------
# Load knowledge base
# -----------------------------
@st.cache_data
def load_knowledge_base():
    rows = []

    with open("knowledge_base.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["search_text"] = (
                f"{row['scheme']} {row['topic']} {row['content']}"
            )
            rows.append(row)

    return rows


knowledge_base = load_knowledge_base()


# -----------------------------
# Safety checks
# -----------------------------
def contains_pii(text):
    pii_words = [
        "pan number",
        "aadhaar",
        "aadhar",
        "account number",
        "otp",
        "phone number",
        "mobile number",
        "email address"
    ]

    text_lower = text.lower()

    if any(word in text_lower for word in pii_words):
        return True

    # PAN-like pattern
    if re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text.upper()):
        return True

    # Aadhaar-like 12-digit number
    digits = re.sub(r"\D", "", text)
    if len(digits) == 12:
        return True

    return False


def is_advice_question(text):
    text = text.lower()

    advice_phrases = [
        "should i invest",
        "should i buy",
        "should i sell",
        "is it good to invest",
        "is this a good fund",
        "best fund",
        "better fund",
        "which fund should",
        "recommend",
        "worth investing",
        "how much should i invest"
    ]

    return any(phrase in text for phrase in advice_phrases)


def is_performance_question(text):
    text = text.lower()

    phrases = [
        "highest return",
        "best return",
        "future return",
        "expected return",
        "which will perform better",
        "which performed better",
        "compare returns",
        "calculate return",
        "return comparison"
    ]

    return any(phrase in text for phrase in phrases)


# -----------------------------
# Retrieve factual answer
# -----------------------------
def retrieve_answer(question):
    documents = [row["search_text"] for row in knowledge_base]

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(documents + [question])

    similarities = cosine_similarity(
        vectors[-1],
        vectors[:-1]
    ).flatten()

    best_index = similarities.argmax()
    best_score = similarities[best_index]

    # Avoid guessing if retrieval confidence is too low
    if best_score < 0.18:
        return None

    return knowledge_base[best_index]


# -----------------------------
# Generate response
# -----------------------------
def answer_question(question):

    if contains_pii(question):
        return (
            "Please do not enter PAN, Aadhaar, account numbers, OTPs, "
            "email addresses, phone numbers or other personal information.\n\n"
            f"Source: {SEBI_EDUCATION_LINK}\n\n"
            f"Last updated from sources: {LAST_UPDATED}"
        )

    if is_advice_question(question):
        return (
            "I can provide factual information about the selected schemes, "
            "but I cannot recommend whether you should buy, sell or invest "
            "in a mutual fund.\n\n"
            f"Source: {SEBI_EDUCATION_LINK}\n\n"
            f"Last updated from sources: {LAST_UPDATED}"
        )

    if is_performance_question(question):
        return (
            "I do not calculate, predict or compare mutual fund returns. "
            "You can refer to the official HDFC Mutual Fund factsheets for "
            "published scheme information.\n\n"
            f"Source: {HDFC_FACTSHEET_LINK}\n\n"
            f"Last updated from sources: {LAST_UPDATED}"
        )

    result = retrieve_answer(question)

    if result is None:
        return (
            "I could not find this fact in the selected source set. "
            "Please ask about the expense ratio, exit load, minimum SIP, "
            "lock-in, benchmark or riskometer of the covered schemes.\n\n"
            f"Source: {HDFC_FACTSHEET_LINK}\n\n"
            f"Last updated from sources: {LAST_UPDATED}"
        )

    return (
        f"{result['content']}\n\n"
        f"Source: {result['source_url']}\n\n"
        f"Last updated from sources: {LAST_UPDATED}"
    )


# -----------------------------
# UI
# -----------------------------
st.title("Mutual Fund Facts Assistant")

st.write(
    "Ask factual questions about selected HDFC Mutual Fund schemes."
)

st.info(
    "Facts-only. No investment advice. "
    "Please do not enter PAN, Aadhaar, account numbers, OTPs, "
    "email addresses or phone numbers."
)

st.subheader("Example questions")

st.markdown(
    """
- What is the minimum SIP for HDFC Flexi Cap Fund?
- What is the exit load for HDFC Large Cap Fund?
- What is the lock-in period for HDFC ELSS Tax Saver Fund?
"""
)

question = st.chat_input("Ask a mutual fund fact...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        st.write(answer_question(question))

st.divider()

st.caption(
    "Covers HDFC Large Cap Fund, HDFC Flexi Cap Fund and "
    "HDFC ELSS Tax Saver Fund. Official public sources only."
)
