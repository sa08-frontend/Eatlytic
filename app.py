from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API configuration
SITE_URL = os.getenv("SITE_URL", "http://localhost:5000")
SITE_NAME = os.getenv("SITE_NAME", "Eatlytic")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://api.openrouter.ai/api/v1/chat/completions"

# Removed test code and OpenRouter config

# Language mapping
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean"
}


@app.route("/api/analyze", methods=["POST"])
def analyze_food():

    api_key = OPENROUTER_API_KEY
    if not api_key:
        return jsonify({
            "success": False,
            "error": "api_key not found in .env file"
        }), 500

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        image_data = data.get("imageDataUrl")
        language_code = data.get("language", "en")

        if not image_data:
            return jsonify({"error": "Image not provided"}), 400

        language_name = LANGUAGE_NAMES.get(language_code, "English")

        headers = {
            "Authorization": f"Bearer { api_key}",
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": f"""
You are Eatlytic AI.

Analyze the food image and provide:

1. Estimated calories
2. Macronutrients (protein, fat, carbs)
3. Fiber if applicable
4. Impact on heart health
5. Impact on muscles
6. Energy impact
7. Smart eating tips

Use headings and bullet points.

Respond in {language_name}.
"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this food item"},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }
            ]
        }

        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload
        )

        if response.status_code == 401:
            return jsonify({
                "success": False,
                "error": "Invalid OpenRouter API key"
            }), 401

        if not response.ok:
            return jsonify({
                "success": False,
                "error": "OpenRouter API error",
                "details": response.text
            }), response.status_code

        result = response.json()

        analysis = result["choices"][0]["message"]["content"]

        return jsonify({
            "success": True,
            "analysis": analysis
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Server error",
            "details": str(e)
        }), 500


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Eatlytic AI backend running"
    })


@app.route("/")
def home():
    return jsonify({
        "name": "Eatlytic API",
        "version": "2.0",
        "status": "running"
    })


if __name__ == "__main__":

    if OPENROUTER_API_KEY:
        print("✅ API key loaded")
    else:
        print("⚠️ WARNING: api_key missing")

    print("🚀 Server running on http://localhost:5000")

    app.run(host="0.0.0.0", port=5000, debug=True)