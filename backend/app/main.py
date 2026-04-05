from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from services.qdrant_service import init_qdrant_collection, init_user_roadmaps_collection

from app.routers import (
    auth,
    user,
    recall_card,
    skill_scan,
    question,
    learning_session,
    confusion,
    knowledge_decay,
    learning_style,
    roadmap,
    youtube,
    pdf_generator,
    quiz,
    progress_card,
)

app = FastAPI(title="MindForge AI")

app.mount("/generated_pdfs", StaticFiles(directory="generated_pdfs"), name="generated_pdfs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    init_qdrant_collection()
    init_user_roadmaps_collection()


@app.get("/")
def read_root():
    return {"message": "MindForge AI Backend is Running!"}


app.include_router(auth.router)
app.include_router(user.router,             prefix="/users",             tags=["Users"])
app.include_router(skill_scan.router,       prefix="/skill-scan",        tags=["Skill Scan"])
app.include_router(learning_session.router, prefix="/learning-sessions", tags=["Learning Sessions"])
app.include_router(confusion.router,        prefix="/confusion-signals", tags=["Confusion Signals"])
app.include_router(knowledge_decay.router,  prefix="/knowledge-decay",   tags=["Knowledge Decay"])
app.include_router(recall_card.router,      prefix="/recall-cards",      tags=["Recall Cards"])
app.include_router(question.router,         prefix="/questions",         tags=["Questions"])
app.include_router(learning_style.router,   prefix="/learning-style",    tags=["Learning Style"])
app.include_router(roadmap.router,          prefix="/api",               tags=["Roadmap"])
app.include_router(youtube.router,          prefix="/api",               tags=["YouTube"])
app.include_router(pdf_generator.router,    prefix="/api",               tags=["PDF"])
app.include_router(quiz.router,             prefix="/api",               tags=["Quiz"])
app.include_router(progress_card.router,    prefix="/api",               tags=["Progress"])