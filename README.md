# Mutual Fund Facts Assistant

A facts-only FAQ assistant for mutual fund scheme information, built as an educational prototype using official public sources.

## Product

Groww

## AMC in Scope

HDFC Mutual Fund

## Schemes Covered

1. HDFC Large Cap Fund - Direct Plan
2. HDFC Flexi Cap Fund - Direct Plan
3. HDFC ELSS Tax Saver Fund - Direct Plan

## What the Assistant Can Answer

The assistant answers factual questions such as:

- Expense ratio
- Exit load
- Minimum SIP
- ELSS lock-in period
- Riskometer
- Benchmark
- Scheme-related charges
- How to access mutual fund statements

Every factual answer includes a link to an official source.

## What the Assistant Does Not Do

The assistant does not:

- Recommend whether a user should buy or sell a mutual fund
- Recommend how much money a user should invest
- Compare funds based on expected or historical returns
- Provide portfolio or financial advice
- Accept or store personal financial information

## Data Sources

Only official public sources are used:

- HDFC Mutual Fund
- SEBI
- AMFI

The complete source list is available in `sources.csv`.

## Sample Questions

Examples:

- What is the minimum SIP for HDFC Flexi Cap Fund?
- What is the exit load of HDFC Large Cap Fund?
- What is the lock-in period for HDFC ELSS Tax Saver Fund?
- What is the benchmark of HDFC Flexi Cap Fund?
- How can I download my mutual fund account statement?

Sample responses are available in `sample_qa.md`.

## Disclaimer

**Facts-only assistant:** This tool provides factual information from official AMC, SEBI and AMFI sources and does not provide investment advice or recommendations.

Do not enter PAN, Aadhaar, account numbers, OTPs, email addresses, phone numbers or any other personally identifiable information.

## Known Limitations

- The assistant covers only the selected HDFC Mutual Fund schemes.
- Information depends on the latest available official public documents.
- Mutual fund information such as expense ratios and scheme details may change over time.
- The assistant does not calculate or compare investment returns.
- The assistant does not provide personalised financial advice.

## Working Prototype

Live app:

https://groww-mf-faq-assistant-6c3fgonnfkzm685msffeiw.streamlit.app/

## Setup

To run the project locally:

1. Clone this repository.
2. Install the required Python packages:

   pip install -r requirements.txt

3. Run the Streamlit app:

   streamlit run app.py

The app reads factual scheme information from `knowledge_base.csv` and returns answers with official source links.

## Project Status

Working prototype completed.
