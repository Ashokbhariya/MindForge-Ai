import os
import json
import requests
from sqlalchemy.orm import Session
from app.models.roadmap_models import Roadmap, SubTopic
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("your_secret_key")  
LLM_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_roadmap_from_prompt(prompt: str):
    """
    Calls the LLaMA model via Groq API and returns structured roadmap JSON.
    """
    system_msg = "You're a roadmap generator. Return JSON with topic, description, and subtopics."
    user_msg = (
        f"Generate a detailed learning roadmap for: {prompt}. "
        "Respond only with JSON like: "
        "{'topic': ..., 'description': ..., 'subtopics': ["
        "{'title': ..., 'description': ...}, ...]}"
    )

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Error calling LLM API: {e}")

    content = response.json()['choices'][0]['message']['content']

    # Fix cases where the model returns code block or extra characters
    content = content.strip().strip("`").replace("json", "").strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise Exception(f"The LLM response was not valid JSON:\n{content}")

def generate_and_save_roadmap(prompt: str, user_id: int, db: Session):
    """
    Calls the LLM to generate roadmap and saves it to the database.
    """
    roadmap_json = get_roadmap_from_prompt(prompt)

    roadmap = Roadmap(
        user_id=user_id,
        topic=roadmap_json.get('topic', 'Unknown Topic'),
        description=roadmap_json.get('description', '')
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    for sub in roadmap_json.get("subtopics", []):
        subtopic = SubTopic(
            roadmap_id=roadmap.id,
            title=sub.get('title', ''),
            description=sub.get('description', '')
        )
        db.add(subtopic)

    db.commit()

    return {
        "roadmap_id": roadmap.id,
        "topic": roadmap.topic,
        "description": roadmap.description,
        "subtopics": roadmap_json.get('subtopics', [])
    }
