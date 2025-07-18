from fastapi import FastAPI
from app.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

# Routers
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
    roadmap  # ✅ include roadmap correctly
)

app = FastAPI()

# ✅ CORS Middleware – allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Or use ["*"] during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ DB tables auto-create on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "MindForage AI Backend is Running!"}

# ✅ Register all routers only once
app.include_router(auth.router, tags=["Auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(skill_scan.router, prefix="/skill-scan", tags=["Skill Scan"])
app.include_router(learning_session.router, prefix="/learning-sessions", tags=["Learning Sessions"])
app.include_router(confusion.router, prefix="/confusion-signals", tags=["Confusion Signals"])
app.include_router(knowledge_decay.router, prefix="/knowledge-decay", tags=["Knowledge Decay"])
app.include_router(recall_card.router, prefix="/recall-cards", tags=["Recall Cards"])
app.include_router(question.router, prefix="/questions", tags=["Questions"])
app.include_router(learning_style.router, prefix="/learning-style", tags=["Learning Style"])

# ✅ Your roadmap generation API
app.include_router(roadmap.router, prefix="/api", tags=["Roadmap Generator"])
