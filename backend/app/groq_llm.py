import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "meta-llama/llama-4-scout-17b-16e-instruct"


def _call_groq(key: str, prompt: str, max_tokens: int = 800) -> str:
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    print(f"[Groq] Sending request...")
    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"[Groq] Error {response.status_code}: {response.text}")
        response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()
    print(f"[Groq] Response received ({len(content)} chars)")
    return content


def generate_summary_for_topic(topic: str) -> str:
    """
    For Summary & Diagram tab.
    Returns structured JSON string with rich summary data.
    """
    key = GROQ_API_KEY or os.environ.get("API_KEY") or os.environ.get("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ API key not found. Make sure API_KEY is set in your .env file.")
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty.")

    prompt = (
        f"Generate a rich educational summary for the topic '{topic}'. "
        f"Respond ONLY with a JSON object, no markdown, no extra text. "
        f"Use this exact structure:\n"
        f'{{'
        f'"analogy": "one vivid real-world analogy sentence (not a keyword)",'
        f'"overview": "2-3 sentence overview of what {topic} is and why it matters",'
        f'"points": ["detailed fact 1 (full sentence)", "detailed fact 2", "detailed fact 3", "detailed fact 4", "detailed fact 5", "detailed fact 6"],'
        f'"keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8"],'
        f'"use_cases": ["real use case 1", "real use case 2", "real use case 3"],'
        f'"tip": "one important beginner tip or common mistake to avoid"'
        f'}}'
    )

    raw = _call_groq(key, prompt, max_tokens=900)

    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        data = json.loads(clean)
        # Return the raw JSON string — the router will parse it
        return json.dumps(data)
    except Exception as e:
        print(f"[Groq] JSON parse failed for summary: {e}")
        # Fallback to plain text so old parsing still works
        return raw


def generate_flashcard_for_topic(topic: str) -> dict:
    """For Flashcard tab. Returns rich structured dict."""
    key = GROQ_API_KEY or os.environ.get("API_KEY") or os.environ.get("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ API key not found. Make sure API_KEY is set in your .env file.")
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty.")

    prompt = (
        f"Generate flashcard content for the topic '{topic}'. "
        f"Respond ONLY with a JSON object, no markdown, no extra text. "
        f"Use this exact structure:\n"
        f'{{"front_subtitle": "one-line teaser max 12 words","back_definition": "clear 2-sentence definition","back_points": ["key fact 1","key fact 2","key fact 3","key fact 4"],"back_analogy": "one memorable real-world analogy sentence","keywords": ["keyword1","keyword2","keyword3","keyword4","keyword5"]}}'
    )

    raw = _call_groq(key, prompt, max_tokens=600)

    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        data = json.loads(clean)
        data["front_title"] = topic
        return data
    except Exception as e:
        print(f"[Groq] JSON parse failed for flashcard: {e}")
        return {
            "front_title": topic,
            "front_subtitle": f"What do you know about {topic}?",
            "back_definition": raw[:200] if raw else f"A foundational concept: {topic}.",
            "back_points": [],
            "back_analogy": "",
            "keywords": [topic],
        }