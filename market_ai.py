import streamlit as st
import os
import pandas as pd


def analyze_market_gaps(df, api_key=None):
    """
    Analyze low-rated competitor reviews using Google Gemini.
    """

    if df.empty:
        return "No reviews are available for analysis."

    if api_key is None:
            api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        return (
            "AI analysis is not configured yet. "
            "A Gemini API key is required."
        )

    # Focus on low-rated reviews (1 or 2 stars).
    complaints = df[df["rating"].isin([1, 2])].copy()

    if complaints.empty:
        return "No 1-star or 2-star reviews were found."

    # Keep the request manageable.
    review_lines = []

    for _, row in complaints.head(100).iterrows():
        app_name = str(row.get("app_name", "Unknown app"))
        review_text = str(row.get("review_text", "")).strip()

        if review_text:
            review_lines.append(
                f"App: {app_name} | Review: {review_text[:500]}"
            )

    if not review_lines:
        return "No readable complaint text was found."

    prompt = """
You are a mobile market research analyst.

Analyze the following low-rated Google Play reviews.

Write your report in clear English with these sections:
1. Most common complaints and bugs.
2. Features users appear to need.
3. Recommendations for a new competing application.

Base your conclusions only on the provided reviews.
Do not invent facts or claim that a complaint is frequent
unless the reviews support that conclusion.

Reviews:
""" + "\n".join(review_lines)

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return response.text or "Gemini returned an empty response."

    except Exception as error:
        return f"AI analysis failed: {error}"
