from pydantic import BaseModel
from typing import Optional


# ============================================================
# 📘 EBOOK SCHEMAS
# ============================================================
class EBookBase(BaseModel):
    title: str
    author: str
    tags: str
    category_id: Optional[int] = None


class EBookResponse(EBookBase):
    id: int
    file_url: Optional[str] = None  # ✅ allow null for Excel-uploaded eBooks

    class Config:
        from_attributes = True  # ✅ replaces orm_mode=True (Pydantic v2 compatible)


# ============================================================
# 🗂 CATEGORY SCHEMAS
# ============================================================
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# ============================================================
# 💬 FAQ SCHEMAS
# ============================================================
class FAQBase(BaseModel):
    question: str
    answer: str


class FAQResponse(FAQBase):
    id: int

    class Config:
        from_attributes = True
