// ===================================================================
// Sentiment Readout — client-side interactivity
// Talks to the Flask /analyze endpoint and animates the gauge.
// ===================================================================

const textInput = document.getElementById("text-input");
const charCount = document.getElementById("char-count");
const analyzeBtn = document.getElementById("analyze-btn");
const errorText = document.getElementById("error-text");

const placeholderPanel = document.getElementById("placeholder");
const readoutPanel = document.getElementById("readout");

const sentimentBadge = document.getElementById("sentiment-badge");
const wordCountText = document.getElementById("word-count-text");
const needle = document.getElementById("needle");
const polarityValue = document.getElementById("polarity-value");
const subjectivityValue = document.getElementById("subjectivity-value");
const subjectivityFill = document.getElementById("subjectivity-fill");
const subjectivityNeedle = document.getElementById("subjectivity-needle");
const interpretationText = document.getElementById("interpretation-text");

const MAX_CHARS = 5000;

textInput.addEventListener("input", () => {
  charCount.textContent = `${textInput.value.length} / ${MAX_CHARS}`;
});

analyzeBtn.addEventListener("click", analyze);

// Allow Ctrl+Enter / Cmd+Enter inside the textarea to trigger analysis.
textInput.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    analyze();
  }
});

async function analyze() {
  const text = textInput.value.trim();
  hideError();

  if (!text) {
    showError("Please enter some text to analyze.");
    return;
  }

  setLoading(true);

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }

    renderResult(data);
  } catch (err) {
    showError("Could not reach the server. Is the Flask app running?");
  } finally {
    setLoading(false);
  }
}

function renderResult(data) {
  placeholderPanel.hidden = true;
  readoutPanel.hidden = false;

  // Badge
  sentimentBadge.textContent = data.sentiment.toUpperCase();
  sentimentBadge.className = `badge badge--${data.sentiment}`;

  // Word count
  wordCountText.textContent = `${data.word_count} word${data.word_count === 1 ? "" : "s"}`;

  // Polarity gauge: map [-1, 1] to a [-90deg, 90deg] needle rotation.
  const polarity = clamp(data.polarity, -1, 1);
  const rotation = polarity * 90;
  needle.style.transform = `rotate(${rotation}deg)`;
  polarityValue.textContent = polarity.toFixed(2);

  // Subjectivity bar: map [0, 1] to a 0%-100% fill/marker position.
  const subjectivity = clamp(data.subjectivity, 0, 1);
  const pct = subjectivity * 100;
  subjectivityFill.style.width = `${pct}%`;
  subjectivityNeedle.style.left = `calc(${pct}% - 1.5px)`;
  subjectivityValue.textContent = subjectivity.toFixed(2);

  interpretationText.textContent = data.interpretation;
}

function setLoading(isLoading) {
  analyzeBtn.disabled = isLoading;
  analyzeBtn.querySelector(".lever-label").textContent = isLoading ? "Reading…" : "Analyze";
}

function showError(message) {
  errorText.textContent = message;
  errorText.hidden = false;
}

function hideError() {
  errorText.hidden = true;
  errorText.textContent = "";
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}