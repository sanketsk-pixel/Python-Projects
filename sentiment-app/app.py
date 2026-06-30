"""
=====================================================================
 SENTIMENT ANALYSIS WEB APP
 A Flask application that classifies user-entered text as positive,
 negative, or neutral using TextBlob, and reports the underlying
 polarity (-1 to +1) and subjectivity (0 to 1) scores.

 Run with:
   python app.py
 Then open:
   http://127.0.0.1:5000
=====================================================================
"""

import re

from flask import Flask, render_template, request, jsonify
from textblob import TextBlob

app = Flask(__name__)

# Texts with polarity above POS_THRESHOLD are "positive", below
# NEG_THRESHOLD are "negative", and anything in between is "neutral".
# A small dead-band around 0 avoids labeling near-neutral text as
# strongly one-sided just because of a tiny positive/negative nudge.
POS_THRESHOLD = 0.1
NEG_THRESHOLD = -0.1

MAX_CHARS = 5000


def classify_sentiment(polarity: float) -> str:
    """Map a TextBlob polarity score to a positive/negative/neutral label."""
    if polarity > POS_THRESHOLD:
        return "positive"
    if polarity < NEG_THRESHOLD:
        return "negative"
    return "neutral"


def build_interpretation(sentiment: str, subjectivity: float) -> str:
    """Produce a short, plain-English summary of the reading."""
    if sentiment == "positive":
        tone = "leans positive"
    elif sentiment == "negative":
        tone = "leans negative"
    else:
        tone = "reads as neutral"

    if subjectivity < 0.35:
        nature = "and is fairly factual, with little personal opinion"
    elif subjectivity < 0.65:
        nature = "with a mix of fact and personal opinion"
    else:
        nature = "and is highly subjective, driven by personal opinion"

    return f"This text {tone} {nature}."


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Please enter some text to analyze."}), 400

    if len(text) > MAX_CHARS:
        return jsonify({"error": f"Text is too long. Please keep it under {MAX_CHARS} characters."}), 400

    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 4)
    subjectivity = round(blob.sentiment.subjectivity, 4)
    sentiment = classify_sentiment(polarity)
    interpretation = build_interpretation(sentiment, subjectivity)

    return jsonify({
        "sentiment": sentiment,
        "polarity": polarity,
        "subjectivity": subjectivity,
        "interpretation": interpretation,
        "word_count": len(re.findall(r"\b[\w'-]+\b", text)),
    })


if __name__ == "__main__":
    app.run(debug=True)