import os
import re
from io import BytesIO
from fpdf import FPDF
import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(tags=["PDF Generation"])

class PDFRequest(BaseModel):
    topic: str

# Use the same Groq key that's already working for quiz/recall cards
GROQ_API_KEY = os.getenv("API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "meta-llama/llama-4-scout-17b-16e-instruct"

PDF_OUTPUT_DIR = "generated_pdfs"
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


# ── Step 1: Generate study guide text via Groq ────────────────────────────────
def generate_study_content(topic: str) -> str:
    key = GROQ_API_KEY or os.environ.get("API_KEY") or os.environ.get("GROQ_API_KEY")
    if not key:
        return _fallback_content(topic)

    prompt = (
        f"Write a comprehensive study guide for: {topic}\n\n"
        f"Structure it with these exact section headers (use === before each):\n"
        f"=== Introduction\n"
        f"=== Key Concepts\n"
        f"=== How It Works\n"
        f"=== Real-World Applications\n"
        f"=== Common Mistakes to Avoid\n"
        f"=== Summary\n\n"
        f"Rules:\n"
        f"- Plain text only. No markdown, no asterisks, no bullet dashes.\n"
        f"- Use numbered lists like: 1. item\n"
        f"- Keep each section 3-5 sentences or 4-6 list items.\n"
        f"- Be clear and beginner-friendly."
    )

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1200,
                "temperature": 0.6,
            },
            timeout=30,
        )
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"].strip()
            print(f"[Groq PDF] Content generated ({len(content)} chars)")
            return content
        else:
            print(f"[Groq PDF] Error {response.status_code}: {response.text[:200]}")
            return _fallback_content(topic)
    except Exception as e:
        print(f"[Groq PDF] Exception: {e}")
        return _fallback_content(topic)


def _fallback_content(topic: str) -> str:
    return (
        f"=== Introduction\n"
        f"This study guide covers {topic}. It is designed to give you a solid "
        f"foundational understanding of the subject, its core ideas, and practical uses.\n\n"
        f"=== Key Concepts\n"
        f"1. Definition: Understand what {topic} means.\n"
        f"2. Principles: Learn the fundamental rules that govern this subject.\n"
        f"3. Tools: Identify the main tools or frameworks used.\n"
        f"4. Best Practices: Follow proven approaches to work effectively.\n\n"
        f"=== How It Works\n"
        f"{topic} operates through a structured set of principles and processes. "
        f"Understanding the flow of these processes is key to mastering the subject.\n\n"
        f"=== Real-World Applications\n"
        f"1. Industry Use: {topic} is widely applied across many professional domains.\n"
        f"2. Problem Solving: It helps solve complex, real-world challenges efficiently.\n"
        f"3. Career Value: Mastery of {topic} is a valued skill in the job market.\n\n"
        f"=== Common Mistakes to Avoid\n"
        f"1. Skipping fundamentals before advanced topics.\n"
        f"2. Not practicing with real examples and projects.\n"
        f"3. Ignoring edge cases and exceptions in the subject.\n\n"
        f"=== Summary\n"
        f"{topic} is an important subject worth mastering. Start with the basics, "
        f"practice consistently, and build on your knowledge progressively."
    )


# ── Step 2: Build PDF using fpdf2 ─────────────────────────────────────────────
class StudyGuidePDF(FPDF):
    def __init__(self, topic: str):
        super().__init__()
        self.topic = topic

    def header(self):
        self.set_fill_color(16, 37, 249)   # Brand blue #1025f9
        self.rect(0, 0, 210, 18, 'F')
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(255, 255, 255)
        self.set_y(4)
        self.cell(0, 10, f"Study Guide: {self.topic}", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(14)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"MindForgeAI  |  Page {self.page_no()}", align="C")


def build_pdf(topic: str, content: str) -> str:
    pdf = StudyGuidePDF(topic)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    sections = re.split(r"===\s*", content)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.split("\n", 1)
        title = lines[0].strip()
        body  = lines[1].strip() if len(lines) > 1 else ""

        # Section header bar
        pdf.set_fill_color(230, 235, 255)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(16, 37, 249)
        pdf.cell(0, 9, title, fill=True, ln=True)
        pdf.ln(2)

        # Body text
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)

        for line in body.split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(3)
                continue

            # Numbered list item
            if re.match(r"^\d+\.\s", line):
                num, rest = line.split(".", 1)
                pdf.set_x(14)
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(6, 6, f"{num}.", ln=False)
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, rest.strip())
            else:
                pdf.multi_cell(0, 6, line)

        pdf.ln(5)

    safe_topic = topic.replace(" ", "_").replace("/", "-")
    filename   = f"{safe_topic}_{os.urandom(4).hex()}.pdf"
    filepath   = os.path.join(PDF_OUTPUT_DIR, filename)
    pdf.output(filepath)
    print(f"[PDF] Saved: {filepath} ({os.path.getsize(filepath)} bytes)")
    return filepath


# ── Route ─────────────────────────────────────────────────────────────────────
@router.post("/generate-pdf/")
async def generate_resource_pdf(data: PDFRequest):
    if not data.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    try:
        content  = generate_study_content(data.topic)
        filepath = build_pdf(data.topic, content)

        # Return a local URL the frontend can load in the iframe
        filename = os.path.basename(filepath)
        pdf_url  = f"https://mindforge-backend-gwj4.onrender.com/generated_pdfs/{filename}"
        return {"topic": data.topic, "pdf_url": pdf_url}

    except Exception as e:
        print(f"[PDF] Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
