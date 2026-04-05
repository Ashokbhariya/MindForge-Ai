# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv

# # Explicit path for .env
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
# ENV_PATH = os.path.join(BASE_DIR, '..', '.env')        
# load_dotenv(dotenv_path=ENV_PATH)

# DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     raise ValueError("DATABASE_URL not found. Check your .env file path.")

# engine = create_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(bind=engine)
# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
"""add created_at to roadmaps

Revision ID: add_roadmap_created_at
Revises:
Create Date: 2026-03-30
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_roadmap_created_at'
down_revision = None   # set to your latest revision id if you have one
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'roadmaps',
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,   # nullable so existing rows don't break
        )
    )


def downgrade():
    op.drop_column('roadmaps', 'created_at')