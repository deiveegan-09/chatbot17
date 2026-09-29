import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from chatbot_config import MODEL_NAME, SYSTEM_PROMPT

load_dotenv()
app = Flask(__name__)
key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=key) if key else None

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    if client is None:
        return jsonify({"error": "GEMINI_API_KEY is missing. Add it to your .env file."}), 500
    try:
        response = client.models.generate_content(
            model=MODEL_NAME, contents=message,
            config={"system_instruction": SYSTEM_PROMPT},
        )
        return jsonify({"reply": (response.text or "").strip() or "Please try again."})
    except Exception:
        app.logger.exception("Gemini request failed")
        return jsonify({"error": "The chatbot is temporarily unavailable. Please try again."}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
