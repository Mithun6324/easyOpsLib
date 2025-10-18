from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import uuid
import os
import pandas as pd  # ✅ For Excel reading

# Local imports
from app.database import get_db
from app.models import EBook, Category, FAQ
from app.schemas import (
    EBookResponse,
    CategoryResponse,
    FAQResponse,
    CategoryBase,
    FAQBase
)

router = APIRouter()
UPLOAD_DIR = "uploads/"

# -----------------------------
# 📘 EBOOK ROUTES
# -----------------------------
@router.post("/ebooks", response_model=EBookResponse)
def upload_ebook(
    title: str = Form(...),
    author: str = Form(...),
    tags: str = Form(...),
    category_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a new eBook with metadata and file"""

    # ✅ Check if category_id exists
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail=f"Invalid category_id: {category_id} does not exist.")

    # ✅ Ensure uploads folder exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ✅ Save uploaded file
    file_path = f"{UPLOAD_DIR}{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ✅ Create new eBook record
    new_ebook = EBook(
        title=title,
        author=author,
        tags=tags,
        category_id=category_id,
        file_url=file_path
    )
    db.add(new_ebook)
    db.commit()
    db.refresh(new_ebook)

    return new_ebook
# -----------------------------
# 📊 BULK EBOOK UPLOAD (EXCEL)
# -----------------------------
@router.post("/ebooks/upload_excel")
def upload_ebooks_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    📘 Upload an Excel file to bulk add eBooks.
    - Creates missing categories automatically.
    - Returns detailed failure reasons for invalid rows.
    """

    # ✅ Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ✅ Save temporary Excel file
    temp_path = f"{UPLOAD_DIR}{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ✅ Read Excel file
    try:
        df = pd.read_excel(temp_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")

    # ✅ Validate required columns
    required_columns = {"title", "author", "tags", "category"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Excel file must contain columns: {', '.join(required_columns)}"
        )

    inserted_count = 0
    created_categories = 0
    failed_rows = []

    for index, row in df.iterrows():
        title = str(row["title"]).strip() if pd.notna(row["title"]) else ""
        author = str(row["author"]).strip() if pd.notna(row["author"]) else ""
        tags = str(row["tags"]).strip() if pd.notna(row["tags"]) else ""
        category_name = str(row["category"]).strip() if pd.notna(row["category"]) else ""

        # ✅ Check for missing required data
        if not title:
            failed_rows.append({"row": index + 2, "error": "Missing title"})
            continue
        if not author:
            failed_rows.append({"row": index + 2, "error": "Missing author"})
            continue
        if not category_name:
            failed_rows.append({"row": index + 2, "error": "Missing category"})
            continue

        try:
            # ✅ Create category if not exists
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name, description="Auto-created from Excel")
                db.add(category)
                db.commit()
                db.refresh(category)
                created_categories += 1

            # ✅ Insert eBook
            new_ebook = EBook(
                title=title,
                author=author,
                tags=tags,
                category_id=category.id,
                file_url=None
            )
            db.add(new_ebook)
            inserted_count += 1

        except Exception as e:
            db.rollback()
            failed_rows.append({"row": index + 2, "error": f"Database error: {str(e)}"})

    db.commit()

    # ✅ Build detailed response
    return {
        "message": "✅ Excel processed successfully",
        "summary": {
            "total_rows": len(df),
            "inserted_books": inserted_count,
            "created_categories": created_categories,
            "failed_rows_count": len(failed_rows)
        },
        "failed_rows": failed_rows
    }



@router.get("/ebooks", response_model=list[EBookResponse])
def list_ebooks(db: Session = Depends(get_db)):
    """Fetch all eBooks"""
    return db.query(EBook).all()


@router.delete("/ebooks/{ebook_id}")
def delete_ebook(ebook_id: int, db: Session = Depends(get_db)):
    """Delete an eBook by ID"""
    ebook = db.query(EBook).filter(EBook.id == ebook_id).first()
    if not ebook:
        raise HTTPException(status_code=404, detail="EBook not found")

    # Optional: Delete file from disk if exists
    if os.path.exists(ebook.file_url):
        os.remove(ebook.file_url)

    db.delete(ebook)
    db.commit()
    return {"message": "EBook deleted successfully"}


# -----------------------------
# 📊 BULK EBOOK UPLOAD (EXCEL)
# -----------------------------
@router.post("/ebooks/upload_excel")
def upload_ebooks_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an Excel file to bulk add eBooks (auto-creates categories)."""

    # ✅ Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ✅ Save temporary Excel file
    temp_path = f"{UPLOAD_DIR}{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ✅ Read Excel file using pandas
    try:
        df = pd.read_excel(temp_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")

    # ✅ Validate required columns
    required_columns = {"title", "author", "tags", "category"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Excel file must contain columns: {', '.join(required_columns)}"
        )

    inserted_count = 0
    for _, row in df.iterrows():
        # Auto-create category if missing
        category_name = str(row["category"]).strip()
        category = db.query(Category).filter(Category.name == category_name).first()

        if not category:
            category = Category(name=category_name, description=f"Auto-created: {category_name}")
            db.add(category)
            db.commit()
            db.refresh(category)

        # Create new eBook
        new_ebook = EBook(
            title=row["title"],
            author=row["author"],
            tags=row["tags"],
            category_id=category.id,
            file_url=None  # No file for Excel uploads
        )
        db.add(new_ebook)
        inserted_count += 1

    db.commit()
    return {"message": f"✅ Successfully added {inserted_count} eBooks from Excel."}


# -----------------------------
# 🗂 CATEGORY ROUTES
# -----------------------------
@router.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    """Create a new category (unique name enforced)"""
    # ✅ Prevent duplicate category names
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists.")

    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """List all categories"""
    return db.query(Category).all()


# -----------------------------
# 💬 FAQ ROUTES
# -----------------------------
@router.post("/faqs", response_model=FAQResponse)
def create_faq(faq: FAQBase, db: Session = Depends(get_db)):
    """Create a new FAQ"""
    new_faq = FAQ(**faq.dict())
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return new_faq


@router.get("/faqs", response_model=list[FAQResponse])
def list_faqs(db: Session = Depends(get_db)):
    """List all FAQs"""
    return db.query(FAQ).all()
