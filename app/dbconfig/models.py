from sqlalchemy import Column, Integer, String, DateTime,Text
from datetime import datetime

from app.dbconfig.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    role = Column(
        String(20),
        nullable=False

    )
    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(String(255), nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class EssayMarking(Base):
    __tablename__ = "essay_markings"

    id = Column(Integer, primary_key=True, index=True)

    student_name = Column(String(150), nullable=False)
    course = Column(String(100), nullable=False)
    exam_title = Column(String(255), nullable=False)

    question = Column(Text, nullable=False)
    extracted_text = Column(Text, nullable=False)

    score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=False, default=100)
    percentage = Column(Integer, nullable=True)

    grade = Column(String(5), nullable=True)
    feedback = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    improvements = Column(Text, nullable=True)

    filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
