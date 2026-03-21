# import os
# import re
# import time
# import requests
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from io import BytesIO
# from xhtml2pdf import pisa

# load_dotenv()

# router = APIRouter(tags=["PDF Generation"])

# class PDFRequest(BaseModel):
#     topic: str

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# PDF_OUTPUT_DIR = "generated_pdfs"
# os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# GEMINI_MODELS = [
#     "gemini-2.0-flash-lite",
#     "gemini-1.5-flash",
# ]

# GEMINI_URL = (
#     "https://generativelanguage.googleapis.com/v1beta/models/"
#     "{model}:generateContent?key={api_key}"
# )

# PROMPT_TEMPLATE = """You are a study guide generator. Write a study guide for: {topic}

# STRICT OUTPUT RULES:
# - Output ONLY raw HTML. Absolutely nothing before or after the HTML tags.
# - Do NOT use markdown, backticks, triple backticks, or code fences of any kind.
# - Your first character must be < and your last character must be >
# - Only use these HTML tags: h1, h2, p, ul, li, b, br
# - No div, no span, no table, no class, no style attributes anywhere.

# <h1>{topic}</h1>

# <h2>Introduction</h2>
# <p>Write 3-4 sentences giving a clear overview of what this topic is and why it matters.</p>

# <h2>Key Concepts</h2>
# <ul>
# <li><b>Concept Name:</b> 2-3 sentence explanation with a simple analogy.</li>
# <li><b>Concept Name:</b> 2-3 sentence explanation.</li>
# <li><b>Concept Name:</b> 2-3 sentence explanation.</li>
# <li><b>Concept Name:</b> 2-3 sentence explanation.</li>
# <li><b>Concept Name:</b> 2-3 sentence explanation.</li>
# </ul>

# <h2>How It Works</h2>
# <p>3-4 sentences explaining the core process or mechanism in simple terms.</p>

# <h2>Real World Applications</h2>
# <ul>
# <li><b>Application 1:</b> Explain specifically how this topic is applied here.</li>
# <li><b>Application 2:</b> Explain specifically how this topic is applied here.</li>
# <li><b>Application 3:</b> Explain specifically how this topic is applied here.</li>
# </ul>

# <h2>Common Mistakes to Avoid</h2>
# <ul>
# <li><b>Mistake 1:</b> Why it happens and how to avoid it.</li>
# <li><b>Mistake 2:</b> Why it happens and how to avoid it.</li>
# </ul>

# <h2>Summary</h2>
# <p>3-4 sentences summarizing the key takeaways from this guide.</p>"""


# def clean_llm_output(raw: str) -> str:
#     raw = re.sub(r"```(?:html)?\s*", "", raw)
#     raw = re.sub(r"```", "", raw)
#     match = re.search(r"<h1", raw, re.IGNORECASE)
#     if match:
#         raw = raw[match.start():]
#     return raw.strip()


# def generate_ai_content(topic: str) -> str:
#     if not GEMINI_API_KEY:
#         raise Exception("GEMINI_API_KEY is not set in your .env file.")

#     prompt = PROMPT_TEMPLATE.format(topic=topic)

#     for model in GEMINI_MODELS:
#         url = GEMINI_URL.format(model=model, api_key=GEMINI_API_KEY)
#         print(f"📤 Trying Gemini model: {model}")

#         for attempt in range(3):
#             try:
#                 response = requests.post(
#                     url,
#                     headers={"Content-Type": "application/json"},
#                     json={
#                         "contents": [{"parts": [{"text": prompt}]}],
#                         "generationConfig": {
#                             "temperature": 0.4,
#                             "maxOutputTokens": 2048,
#                         }
#                     },
#                     timeout=60
#                 )

#                 if response.status_code == 200:
#                     data = response.json()
#                     raw = data["candidates"][0]["content"]["parts"][0]["text"]
#                     cleaned = clean_llm_output(raw)
#                     print(f"✅ Gemini [{model}] responded successfully.")
#                     print(f"DEBUG HTML preview: {cleaned[:200]}")
#                     return cleaned

#                 elif response.status_code == 429:
#                     wait = [5, 8, 10][attempt]
#                     print(f"⚠️ [{model}] Rate limited (attempt {attempt + 1}/3). Waiting {wait}s...")
#                     time.sleep(wait)
#                     continue

#                 elif response.status_code == 404:
#                     print(f"⚠️ [{model}] not found, trying next model...")
#                     break

#                 else:
#                     print(f"❌ [{model}] error {response.status_code}: {response.text[:200]}")
#                     break

#             except requests.exceptions.RequestException as e:
#                 print(f"⚠️ Request error with [{model}]: {e}")
#                 break

#     print(print("❌ All Gemini models failed. Using rich static fallback content.")
#     return f"""<h1>{topic}</h1>

# <h2>Introduction</h2>
# <p>
# This study guide covers the topic of <b>{topic}</b>. Whether you are a beginner just
# starting out or an intermediate learner looking to consolidate your knowledge, this guide
# provides a structured overview of the key ideas, practical uses, and important concepts
# you need to understand.
# </p>
# <p>
# Note: AI-generated content was temporarily unavailable due to API rate limits.
# This guide contains foundational information. For deeper content, please try generating
# again in a minute.
# </p>

# <h2>What You Will Learn</h2>
# <ul>
# <li><b>Core Definitions:</b> Understand what {topic} means and where it fits in the broader landscape.</li>
# <li><b>Key Principles:</b> Learn the fundamental rules and ideas that govern this subject.</li>
# <li><b>Practical Applications:</b> Discover how {topic} is used in the real world.</li>
# <li><b>Common Pitfalls:</b> Identify mistakes beginners make and how to avoid them.</li>
# <li><b>Next Steps:</b> Know what to study after mastering the basics of {topic}.</li>
# </ul>

# <h2>Why This Topic Matters</h2>
# <p>
# Understanding <b>{topic}</b> is valuable because it builds foundational skills that apply
# across many domains. Professionals who master this area are better equipped to solve
# complex problems, communicate ideas clearly, and contribute meaningfully to their field.
# </p>
# <p>
# Whether you are studying for an exam, preparing for a job interview, or simply expanding
# your knowledge, a solid understanding of {topic} will give you a competitive edge.
# </p>

# <h2>How To Study This Topic Effectively</h2>
# <ul>
# <li><b>Start with the basics:</b> Make sure you understand the foundational definitions before moving on.</li>
# <li><b>Practice regularly:</b> Apply what you learn through exercises, projects, or real-world examples.</li>
# <li><b>Use multiple resources:</b> Combine textbooks, videos, and hands-on practice for best results.</li>
# <li><b>Test yourself:</b> Use quizzes and flashcards to reinforce memory and identify weak areas.</li>
# <li><b>Teach others:</b> Explaining a concept to someone else is one of the best ways to solidify your own understanding.</li>
# </ul>

# <h2>Recommended Next Steps</h2>
# <p>
# To go deeper on <b>{topic}</b>, consider exploring the following:
# </p>
# <ul>
# <li>Search for "{topic} tutorial" on YouTube for free video lessons.</li>
# <li>Look up "{topic}" on Wikipedia for a comprehensive overview and references.</li>
# <li>Find practice problems or projects related to {topic} on platforms like Coursera, Khan Academy, or freeCodeCamp.</li>
# <li>Join a community or forum where practitioners of {topic} share knowledge and answer questions.</li>
# </ul>

# <h2>Summary</h2>
# <p>
# <b>{topic}</b> is an important subject that rewards structured study and consistent practice.
# By understanding its core concepts, exploring its real-world applications, and avoiding
# common mistakes, you will be well on your way to mastering this area.
# </p>
# <p>
# Return to this guide after generating AI content for a richer, fully personalized
# study experience tailored specifically to <b>{topic}</b>.
# </p>""")
#     return f"""<h1>{topic}</h1>
# <h2>About This Topic</h2>
# <p>This study guide covers <b>{topic}</b>. AI content generation is temporarily unavailable due to API rate limits. Please try again in a few minutes.</p>
# <h2>What To Do Next</h2>
# <ul>
# <li><b>Try again shortly:</b> Gemini free tier allows 15 requests per minute. Wait 60 seconds and retry.</li>
# <li><b>Search online:</b> Look up "{topic}" on Wikipedia or YouTube for learning resources.</li>
# <li><b>Check your API quota:</b> Visit aistudio.google.com to monitor your usage.</li>
# </ul>"""


# def build_full_html(body_html: str) -> str:
#     return f"""<!DOCTYPE html>
# <html>
# <head>
# <meta charset="UTF-8"/>
# <style>
#   @page {{ margin: 2cm; }}
#   body {{
#     font-family: Helvetica, Arial, sans-serif;
#     font-size: 11pt;
#     color: #1a1a1a;
#     line-height: 1.7;
#   }}
#   h1 {{
#     font-size: 22pt;
#     color: #0d1b2a;
#     border-bottom: 2px solid #0d1b2a;
#     padding-bottom: 6px;
#     margin-bottom: 16px;
#   }}
#   h2 {{
#     font-size: 14pt;
#     color: #1b4332;
#     margin-top: 20px;
#     margin-bottom: 8px;
#     border-left: 4px solid #1b4332;
#     padding-left: 8px;
#   }}
#   p {{ margin: 6px 0 12px 0; }}
#   ul {{ margin: 6px 0 12px 18px; padding: 0; }}
#   li {{ margin-bottom: 6px; }}
#   b {{ font-weight: bold; color: #0d1b2a; }}
# </style>
# </head>
# <body>
# {body_html}
# </body>
# </html>"""


# def convert_html_to_pdf_in_memory(html: str) -> BytesIO:
#     pdf_buffer = BytesIO()
#     pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
#     if pisa_status.err:
#         raise Exception(f"xhtml2pdf failed with {pisa_status.err} error(s).")
#     pdf_buffer.seek(0)
#     size = len(pdf_buffer.getvalue())
#     print(f"DEBUG PDF size: {size} bytes")
#     if size < 500:
#         raise Exception(f"PDF appears empty ({size} bytes).")
#     return pdf_buffer


# def save_pdf_locally(pdf_buffer: BytesIO, topic: str) -> str:
#     safe_topic = topic.replace(' ', '_').replace('/', '-')
#     filename = f"{safe_topic}_{os.urandom(4).hex()}.pdf"
#     filepath = os.path.join(PDF_OUTPUT_DIR, filename)
#     with open(filepath, "wb") as f:
#         f.write(pdf_buffer.getvalue())
#     print(f"✅ PDF saved locally: {filepath}")
#     return f"/generated_pdfs/{filename}"


# def upload_to_supabase(pdf_buffer: BytesIO, topic: str):
#     try:
#         from supabase import create_client
#         if not SUPABASE_URL or not SUPABASE_KEY:
#             raise ValueError("Supabase credentials not configured")
#         supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
#         safe_topic = topic.replace(' ', '_')
#         storage_path = f"resources/{safe_topic}/{safe_topic}_{os.urandom(4).hex()}.pdf"
#         supabase.storage.from_("pdf-bucket").upload(
#             storage_path, pdf_buffer.getvalue(), {'content-type': 'application/pdf'}
#         )
#         return supabase.storage.from_("pdf-bucket").get_public_url(storage_path)
#     except Exception as e:
#         print(f"⚠️ Supabase upload failed: {e} — saving locally instead")
#         return None


# @router.post("/generate-pdf/")
# async def generate_resource_pdf(data: PDFRequest):
#     if not data.topic.strip():
#         raise HTTPException(status_code=400, detail="Topic cannot be empty.")
#     try:
#         body_html = generate_ai_content(data.topic)
#         full_html = build_full_html(body_html)
#         pdf_buffer = convert_html_to_pdf_in_memory(full_html)

#         pdf_url = upload_to_supabase(pdf_buffer, data.topic)
#         if not pdf_url:
#             pdf_buffer.seek(0)
#             pdf_url = save_pdf_locally(pdf_buffer, data.topic)

#         return {"topic": data.topic, "pdf_url": pdf_url}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
import os
import re
import time
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from io import BytesIO
from xhtml2pdf import pisa

load_dotenv()

router = APIRouter(tags=["PDF Generation"])

class PDFRequest(BaseModel):
    topic: str

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

PDF_OUTPUT_DIR = "generated_pdfs"
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

GEMINI_MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
]

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={api_key}"
)

PROMPT_TEMPLATE = """You are a study guide generator. Write a study guide for: {topic}

STRICT OUTPUT RULES:
- Output ONLY raw HTML. Absolutely nothing before or after the HTML tags.
- Do NOT use markdown, backticks, triple backticks, or code fences of any kind.
- Your first character must be < and your last character must be >
- Only use these HTML tags: h1, h2, p, ul, li, b, br
- No div, no span, no table, no class, no style attributes anywhere.

<h1>{topic}</h1>

<h2>Introduction</h2>
<p>Write 3-4 sentences giving a clear overview of what this topic is and why it matters.</p>

<h2>Key Concepts</h2>
<ul>
<li><b>Concept Name:</b> 2-3 sentence explanation with a simple analogy.</li>
<li><b>Concept Name:</b> 2-3 sentence explanation.</li>
<li><b>Concept Name:</b> 2-3 sentence explanation.</li>
<li><b>Concept Name:</b> 2-3 sentence explanation.</li>
<li><b>Concept Name:</b> 2-3 sentence explanation.</li>
</ul>

<h2>How It Works</h2>
<p>3-4 sentences explaining the core process or mechanism in simple terms.</p>

<h2>Real World Applications</h2>
<ul>
<li><b>Application 1:</b> Explain specifically how this topic is applied here.</li>
<li><b>Application 2:</b> Explain specifically how this topic is applied here.</li>
<li><b>Application 3:</b> Explain specifically how this topic is applied here.</li>
</ul>

<h2>Common Mistakes to Avoid</h2>
<ul>
<li><b>Mistake 1:</b> Why it happens and how to avoid it.</li>
<li><b>Mistake 2:</b> Why it happens and how to avoid it.</li>
</ul>

<h2>Summary</h2>
<p>3-4 sentences summarizing the key takeaways from this guide.</p>"""


def clean_llm_output(raw: str) -> str:
    raw = re.sub(r"```(?:html)?\s*", "", raw)
    raw = re.sub(r"```", "", raw)
    match = re.search(r"<h1", raw, re.IGNORECASE)
    if match:
        raw = raw[match.start():]
    return raw.strip()


def generate_ai_content(topic: str) -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY is not set in your .env file.")

    prompt = PROMPT_TEMPLATE.format(topic=topic)

    for model in GEMINI_MODELS:
        url = GEMINI_URL.format(model=model, api_key=GEMINI_API_KEY)
        print(f"📤 Trying Gemini model: {model}")

        for attempt in range(3):
            try:
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.4,
                            "maxOutputTokens": 2048,
                        }
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    raw = data["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned = clean_llm_output(raw)
                    print(f"✅ Gemini [{model}] responded successfully.")
                    print(f"DEBUG HTML preview: {cleaned[:200]}")
                    return cleaned

                elif response.status_code == 429:
                    wait = [3, 8, 15][attempt]
                    print(f"⚠️ [{model}] Rate limited (attempt {attempt + 1}/3). Waiting {wait}s...")
                    time.sleep(wait)
                    continue

                elif response.status_code == 404:
                    print(f"⚠️ [{model}] not found, trying next model...")
                    break

                else:
                    print(f"❌ [{model}] error {response.status_code}: {response.text[:200]}")
                    break

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Request error with [{model}]: {e}")
                break

    # ✅ Rich fallback — always produces a readable PDF even when Gemini is unavailable
    print("❌ All Gemini models failed. Using rich static fallback content.")
    return f"""<h1>{topic}</h1>

<h2>Introduction</h2>
<p>This study guide covers the topic of <b>{topic}</b>. Whether you are a beginner just
starting out or an intermediate learner looking to consolidate your knowledge, this guide
provides a structured overview of the key ideas, practical uses, and important concepts
you need to understand.</p>
<p>Note: AI-generated content was temporarily unavailable due to API rate limits.
This guide contains foundational information. For deeper AI-generated content, please
try generating again in a minute.</p>

<h2>What You Will Learn</h2>
<ul>
<li><b>Core Definitions:</b> Understand what {topic} means and where it fits in the broader landscape.</li>
<li><b>Key Principles:</b> Learn the fundamental rules and ideas that govern this subject.</li>
<li><b>Practical Applications:</b> Discover how {topic} is used in the real world.</li>
<li><b>Common Pitfalls:</b> Identify mistakes beginners make and how to avoid them.</li>
<li><b>Next Steps:</b> Know what to study after mastering the basics of {topic}.</li>
</ul>

<h2>Why This Topic Matters</h2>
<p>Understanding <b>{topic}</b> is valuable because it builds foundational skills that apply
across many domains. Professionals who master this area are better equipped to solve
complex problems, communicate ideas clearly, and contribute meaningfully to their field.</p>
<p>Whether you are studying for an exam, preparing for a job interview, or simply expanding
your knowledge, a solid grasp of {topic} will give you a competitive edge.</p>

<h2>How To Study This Topic Effectively</h2>
<ul>
<li><b>Start with the basics:</b> Make sure you understand foundational definitions before moving on.</li>
<li><b>Practice regularly:</b> Apply what you learn through exercises, projects, or real-world examples.</li>
<li><b>Use multiple resources:</b> Combine textbooks, videos, and hands-on practice for best results.</li>
<li><b>Test yourself:</b> Use quizzes and flashcards to reinforce memory and identify weak areas.</li>
<li><b>Teach others:</b> Explaining a concept to someone else is one of the best ways to solidify understanding.</li>
</ul>

<h2>Recommended Next Steps</h2>
<p>To go deeper on <b>{topic}</b>, consider exploring the following:</p>
<ul>
<li>Search for <b>{topic} tutorial</b> on YouTube for free video lessons.</li>
<li>Look up <b>{topic}</b> on Wikipedia for a comprehensive overview and references.</li>
<li>Find practice problems on platforms like Coursera, Khan Academy, or freeCodeCamp.</li>
<li>Join a community or forum where practitioners of {topic} share knowledge.</li>
</ul>

<h2>Summary</h2>
<p><b>{topic}</b> is an important subject that rewards structured study and consistent practice.
By understanding its core concepts, exploring its real-world applications, and avoiding
common mistakes, you will be well on your way to mastering this area.</p>
<p>Return to this guide after generating AI content for a richer, fully personalized
study experience tailored specifically to <b>{topic}</b>.</p>"""


def build_full_html(body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
  @page {{ margin: 2cm; }}
  body {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: 11pt;
    color: #1a1a1a;
    line-height: 1.7;
  }}
  h1 {{
    font-size: 22pt;
    color: #0d1b2a;
    border-bottom: 2px solid #0d1b2a;
    padding-bottom: 6px;
    margin-bottom: 16px;
  }}
  h2 {{
    font-size: 14pt;
    color: #1b4332;
    margin-top: 20px;
    margin-bottom: 8px;
    border-left: 4px solid #1b4332;
    padding-left: 8px;
  }}
  p {{ margin: 6px 0 12px 0; }}
  ul {{ margin: 6px 0 12px 18px; padding: 0; }}
  li {{ margin-bottom: 6px; }}
  b {{ font-weight: bold; color: #0d1b2a; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""


def convert_html_to_pdf_in_memory(html: str) -> BytesIO:
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
    if pisa_status.err:
        raise Exception(f"xhtml2pdf failed with {pisa_status.err} error(s).")
    pdf_buffer.seek(0)
    size = len(pdf_buffer.getvalue())
    print(f"DEBUG PDF size: {size} bytes")
    if size < 500:
        raise Exception(f"PDF appears empty ({size} bytes).")
    return pdf_buffer


def save_pdf_locally(pdf_buffer: BytesIO, topic: str) -> str:
    safe_topic = topic.replace(' ', '_').replace('/', '-')
    filename = f"{safe_topic}_{os.urandom(4).hex()}.pdf"
    filepath = os.path.join(PDF_OUTPUT_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(pdf_buffer.getvalue())
    print(f"✅ PDF saved locally: {filepath}")
    return f"/generated_pdfs/{filename}"


def upload_to_supabase(pdf_buffer: BytesIO, topic: str):
    try:
        from supabase import create_client
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        safe_topic = topic.replace(' ', '_')
        storage_path = f"resources/{safe_topic}/{safe_topic}_{os.urandom(4).hex()}.pdf"
        supabase.storage.from_("pdf-bucket").upload(
            storage_path, pdf_buffer.getvalue(), {'content-type': 'application/pdf'}
        )
        return supabase.storage.from_("pdf-bucket").get_public_url(storage_path)
    except Exception as e:
        print(f"⚠️ Supabase upload failed: {e} — saving locally instead")
        return None


@router.post("/generate-pdf/")
async def generate_resource_pdf(data: PDFRequest):
    if not data.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    try:
        body_html = generate_ai_content(data.topic)
        full_html = build_full_html(body_html)
        pdf_buffer = convert_html_to_pdf_in_memory(full_html)

        pdf_url = upload_to_supabase(pdf_buffer, data.topic)
        if not pdf_url:
            pdf_buffer.seek(0)
            pdf_url = save_pdf_locally(pdf_buffer, data.topic)

        return {"topic": data.topic, "pdf_url": pdf_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")