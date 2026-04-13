import os
import json
import requests
import re
import uuid
from sqlalchemy.orm import Session
from app.models import Roadmap, SubTopic
from dotenv import load_dotenv
from services.qdrant_service import insert_roadmap, insert_user_roadmap, init_qdrant_collection, get_embedding

load_dotenv()
API_KEY = os.getenv("your_secret_key")

LLM_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

init_qdrant_collection()

# ----------------- UTILITIES -----------------

def generate_link(title: str) -> str:
    """Generate a direct GFG URL from topic title."""
    slug = title.strip().lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)   # remove special chars
    slug = re.sub(r'\s+', '-', slug)             # spaces → hyphens
    slug = re.sub(r'-+', '-', slug)              # collapse multiple hyphens
    return f"https://www.geeksforgeeks.org/{slug}/"


def extract_clean_json(raw: str) -> str:
    """Extract and clean JSON content from LLM response."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise Exception("No JSON object found in LLM response.")

    content = match.group(0).strip()
    content = content.replace("\u201c", '"').replace("\u201d", '"')
    content = content.replace("\u2018", "'").replace("\u2019", "'")
    content = re.sub(r'\\(?!["\\/bfnrt])', r'\\\\', content)
    content = re.sub(r"\s+", " ", content)
    content = re.sub(r",\s*}", "}", content)
    content = re.sub(r",\s*]", "]", content)

    json.loads(content)  # Validate JSON
    return content


def get_roadmap_from_prompt(prompt: str):
    """Call LLM API to generate roadmap JSON."""
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a roadmap generator. "
                    "Return valid JSON with keys: topic, description, subtopics "
                    "(list of {title, description}). "
                    "Use standard computer science terminology for titles "
                    "so they match GeeksforGeeks article slugs exactly. "
                    "Do NOT include any links — they will be generated automatically."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Generate a detailed learning roadmap for: {prompt}. "
                    "Respond with JSON only, no extra text."
                )
            }
        ],
        "temperature": 0.2
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()

    raw_content = response.json()['choices'][0]['message']['content']
    return json.loads(extract_clean_json(raw_content))


# ----------------- MAIN FUNCTION -----------------

def generate_and_save_roadmap(prompt: str, user_id: str, db: Session, level: str = "Beginner"):
    """Generate roadmap, save to Postgres, Qdrant, and user_roadmaps."""

    print(f"🔑 API_KEY loaded: {API_KEY}")

    try:
        roadmap_json = get_roadmap_from_prompt(prompt)
    except Exception as e:
        print(f"⚠️ Groq API failed: {e}")
        roadmap_json = {
            "topic": prompt,
            "description": "Default roadmap due to API failure.",
            "subtopics": []
        }

    roadmap_json["level"] = roadmap_json.get("level", level)

    # Save in Postgres
    roadmap = Roadmap(
        user_id=user_id,
        topic=roadmap_json.get('topic', 'Unknown Topic'),
        description=roadmap_json.get('description', ''),
        level=roadmap_json["level"]
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    clean_subtopics = []
    for sub in roadmap_json.get("subtopics", []):
        title = sub.get('title', sub.get('topic', ''))
        desc = sub.get('description', '')
        link = generate_link(title)   # always generate fresh GFG direct link

        db.add(SubTopic(roadmap_id=roadmap.id, title=title, description=desc))
        clean_subtopics.append({
            "title": title,
            "description": desc,
            "link": link
        })
    db.commit()

    # Save in Qdrant
    try:
        roadmap_payload = {
            "roadmap_id": str(roadmap.id),
            "user_id": str(user_id),
            "topic": roadmap.topic,
            "level": roadmap.level,
            "description": roadmap.description,
            "subtopics": clean_subtopics
        }

        vector = get_embedding(json.dumps(roadmap_payload)).tolist()
        insert_roadmap(str(uuid.uuid4()), vector, roadmap_payload)
        insert_user_roadmap(str(user_id), str(roadmap.id), prompt)

        print(f"✅ Roadmap inserted for user_id={roadmap_payload['user_id']} (vector length={len(vector)})")
    except Exception as e:
        print(f"⚠️ Qdrant insertion skipped: {e}")

    return roadmap_payload