import streamlit as st
import csv
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


st.set_page_config(
    page_title="Mutual Fund Facts Assistant",
    layout="centered"
)

LAST_UPDATED = "2 October 2026"

SEBI_EDUCATION_LINK = (
    "https://investor.sebi.gov.in/regular_and_direct_mutual_funds.html"
)

HDFC_FACTSHEET_LINK = (
    "https://www.hdfcfund.com/mutual-funds/factsheets"
)


# ---------------------------------
# Load knowledge base
# ---------------------------------
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


# ---------------------------------
# Load LLM
# ---------------------------------
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    return tokenizer, model


tokenizer, model = load_model()


# ---------------------------------
# Safety checks
# ---------------------------------
def contains_pii(text):
    text_lower = text.lower()

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

    if any(word in text_lower for word in pii_words):
        return True

    # PAN-like pattern
    if re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text.upper()):
        return True

    # Aadhaar-like 12 digit number
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


# ---------------------------------
# Retrieval
# ---------------------------------
def retrieve_fact(question):
    documents = [
        row["search_text"]
        for row in knowledge_base
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(
        documents + [question]
    )

    similarities = cosine_similarity(
        vectors[-1],
        vectors[:-1]
    ).flatten()

    best_index = similarities.argmax()
    best_score = similarities[best_index]

    if best_score < 0.18:
        return None

    return knowledge_base[best_index]


# ---------------------------------
# LLM answer generation
# ---------------------------------
def generate_answer(question, retrieved_fact):
    prompt = f"""
You are a facts-only mutual fund FAQ assistant.

Answer the user's question using ONLY the factual context provided below.

Rules:
- Do not give investment advice.
- Do not recommend buying or selling.
- Do not compare or predict returns.
- Do not invent facts.
- Keep the answer concise.
- Maximum 3 sentences.
- If the context does not answer the question, say that the fact is not available in the provided source.

User question:
{question}

Official source context:
{retrieved_fact['content']}

Answer:
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=80,
        do_sample=False
    )

    answer = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    ).strip()

    return answer

    prompt = f"""
You are a facts-only mutual fund FAQ assistant.

Answer the user's question using ONLY the factual context provided below.

Rules:
- Do not give investment advice.
- Do not recommend buying or selling.
- Do not compare or predict returns.
- Do not invent facts.
- Keep the answer concise.
- Maximum 3 sentences.
- If the context does not answer the question, say that the fact is not available in the provided source.

User question:
{question}

Official source context:
{retrieved_fact['content']}

Answer:
"""

   inputs = tokenizer(
    prompt,
    return_tensors="pt",
    truncation=True,
    max_length=512
)

outputs = model.generate(
    **inputs,
    max_new_tokens=80,
    do_sample=False
)

answer = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
).strip()

    return answer


# ---------------------------------
# Main answering logic
# ---------------------------------
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
            "You can refer to the official HDFC Mutual Fund factsheets "
            "for published scheme information.\n\n"
            f"Source: {HDFC_FACTSHEET_LINK}\n\n"
            f"Last updated from sources: {LAST_UPDATED}"
        )

    retrieved_fact = retrieve_fact(question)

    if retrieved_fact is None:
        return (
            "I could not find this fact in the selected source set. "
            "Please ask about the expense ratio, exit load, minimum SIP, "
            "lock-in, benchmark or riskometer of the covered schemes.\n\n"
            f"Source: {HDFC_FACTSHEET_LINK}\n\n"
            f"Last updated from sources: {LAST_UPDATED}"
        )

    generated_answer = generate_answer(
        question,
        retrieved_fact
    )

    return (
        f"{generated_answer}\n\n"
        f"Source: {retrieved_fact['source_url']}\n\n"
        f"Last updated from sources: {LAST_UPDATED}"
    )


# ---------------------------------
# UI
# ---------------------------------
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

question = st.chat_input(
    "Ask a mutual fund fact..."
)

if question:

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):

        with st.spinner("Checking official sources..."):
            response = answer_question(question)

        st.write(response)


st.divider()

st.caption(
    "Covers HDFC Large Cap Fund, HDFC Flexi Cap Fund and "
    "HDFC ELSS Tax Saver Fund. Official public sources only."
)
