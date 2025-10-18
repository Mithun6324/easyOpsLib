from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    ebooks = relationship("EBook", back_populates="category")


class EBook(Base):
    __tablename__ = "ebooks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100))
    tags = Column(String(100))
    file_url = Column(String(255))
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="ebooks")


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
