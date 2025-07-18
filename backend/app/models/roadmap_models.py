from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Roadmap(Base):
    __tablename__ = 'roadmaps'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    topic = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    subtopics = relationship("SubTopic", back_populates="roadmap", cascade="all, delete")

class SubTopic(Base):
    __tablename__ = 'subtopics'
    
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey('roadmaps.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    roadmap = relationship("Roadmap", back_populates="subtopics")
