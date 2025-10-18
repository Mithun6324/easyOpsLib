from pydantic import BaseModel
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: str | None = None

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        orm_mode = True

class EBookBase(BaseModel):
    title: str
    author: str
    tags: str
    category_id: int

class EBookResponse(EBookBase):
    id: int
    file_url: str
    uploaded_at: datetime
    class Config:
        orm_mode = True

class FAQBase(BaseModel):
    question: str
    answer: str

class FAQResponse(FAQBase):
    id: int
    class Config:
        orm_mode = True
