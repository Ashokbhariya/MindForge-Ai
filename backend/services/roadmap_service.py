import os
import json
import requests
import re
import uuid
from sqlalchemy.orm import Session
from app.models import Roadmap, SubTopic
from dotenv import load_dotenv
from services.qdrant_service import insert_roadmap, insert_user_roadmap, init_qdrant_collection, get_embedding
from urllib.parse import quote

load_dotenv()
API_KEY = os.getenv("your_secret_key")

LLM_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

init_qdrant_collection()

# ----------- TECHNICAL TOPIC DETECTOR -----------
TECH_KEYWORDS = [
    "python", "java", "javascript", "c++", "c#", "sql", "html", "css",
    "array", "linked list", "stack", "queue", "tree", "graph", "sorting",
    "dynamic programming", "recursion", "hashing", "binary", "algorithm",
    "data structure", "machine learning", "deep learning", "neural",
    "database", "dbms", "os", "operating system", "network", "system design",
    "react", "node", "express", "mongodb", "docker", "git", "cloud", "api",
    "oops", "object oriented", "compiler", "linux", "kubernetes"
]

def is_technical(title: str) -> bool:
    return any(kw in title.lower() for kw in TECH_KEYWORDS)


# ----------- SMART LINK GENERATOR -----------
def generate_link(title: str) -> str:
    """
    Returns the best resource link for a topic:
    - Technical topics → GFG search (always works)
    - Non-technical topics → Wikipedia search (always works)
    """
    if is_technical(title):
        return f"https://www.geeksforgeeks.org/search/?q={quote(title)}"
    else:
        return f"https://en.wikipedia.org/wiki/Special:Search?search={quote(title)}"


# ----------- JSON CLEANER -----------
def extract_clean_json(raw: str) -> str:
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

    json.loads(content)
    return content


# ----------- LLM CALL -----------
def get_roadmap_from_prompt(prompt: str):
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert learning roadmap generator. "
                    "Return ONLY valid JSON with this exact structure: "
                    '{"topic": string, "description": string, "subtopics": [{"title": string, "description": string}]}. '
                    "Each subtopic description must be 1-2 sentences, clear and educational. "
                    "Cover both theory and practical steps. "
                    "Do NOT include any links — they are auto-generated. "
                    "Do NOT include any text outside the JSON."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Generate a detailed step-by-step learning roadmap for: {prompt}. "
                    "Include 8-12 subtopics covering all key concepts from beginner to advanced. "
                    "Respond with JSON only."
                )
            }
        ],
        "temperature": 0.3
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    raw_content = response.json()['choices'][0]['message']['content']
    return json.loads(extract_clean_json(raw_content))


# ----------- MAIN FUNCTION -----------
def generate_and_save_roadmap(prompt: str, user_id: str, db: Session, level: str = "Beginner"):
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
        link = generate_link(title)

        db.add(SubTopic(roadmap_id=roadmap.id, title=title, description=desc))
        clean_subtopics.append({
            "title": title,
            "description": desc,
            "link": link
        })
    db.commit()

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