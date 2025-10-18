from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import uuid
import os
import pandas as pd  # ✅ For Excel import

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

# ==============================================================
# 📘 EBOOK ROUTES
# ==============================================================

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


@router.get("/ebooks", response_model=list[EBookResponse])
def list_ebooks(db: Session = Depends(get_db)):
    """Fetch all eBooks"""
    ebooks = db.query(EBook).all()

    # ✅ Replace None file_url with empty string (for Excel-uploaded books)
    for ebook in ebooks:
        if ebook.file_url is None:
            ebook.file_url = ""
    return ebooks


@router.delete("/ebooks/{ebook_id}")
def delete_ebook(ebook_id: int, db: Session = Depends(get_db)):
    """Delete an eBook by ID"""
    ebook = db.query(EBook).filter(EBook.id == ebook_id).first()
    if not ebook:
        raise HTTPException(status_code=404, detail="EBook not found")

    # ✅ Delete file from disk only if it exists
    if ebook.file_url and os.path.exists(ebook.file_url):
        try:
            os.remove(ebook.file_url)
        except Exception as e:
            print(f"⚠️ Warning: Could not delete file {ebook.file_url}: {e}")

    db.delete(ebook)
    db.commit()
    return {"message": f"EBook '{ebook.title}' deleted successfully"}


# ==============================================================
# 📊 BULK EBOOK UPLOAD (EXCEL)
# ==============================================================

@router.post("/ebooks/upload_excel")
def upload_ebooks_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an Excel file to bulk add eBooks.
    Required columns: title, author, tags, category.
    Auto-creates categories if not found.
    """
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

    required_columns = {"title", "author", "tags", "category"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Excel file must contain columns: {', '.join(required_columns)}"
        )

    inserted, failed = [], []
    for index, row in df.iterrows():
        try:
            # Handle missing values
            title = str(row["title"]).strip() if pd.notna(row["title"]) else None
            author = str(row["author"]).strip() if pd.notna(row["author"]) else None
            tags = str(row["tags"]).strip() if pd.notna(row["tags"]) else ""
            category_name = str(row["category"]).strip() if pd.notna(row["category"]) else None

            # Skip invalid rows
            if not title or not author or not category_name:
                failed.append({"row": index + 2, "reason": "Missing required fields"})
                continue

            # ✅ Auto-create category if missing
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name, description=f"Auto-created: {category_name}")
                db.add(category)
                db.commit()
                db.refresh(category)

            # ✅ Create new eBook with Excel file reference
            new_ebook = EBook(
                title=title,
                author=author,
                tags=tags,
                category_id=category.id,
                file_url=temp_path  # 👈 store path to Excel file here
            )
            db.add(new_ebook)
            db.commit()
            db.refresh(new_ebook)
            inserted.append(new_ebook.title)

        except Exception as e:
            failed.append({"row": index + 2, "reason": str(e)})

    return {
        "message": f"✅ Added {len(inserted)} eBooks, ❌ {len(failed)} failed.",
        "inserted_titles": inserted,
        "failed_rows": failed,
        "excel_file_path": temp_path  # 👈 return the path to Excel file too
    }



# ==============================================================
# 🗂 CATEGORY ROUTES
# ==============================================================

@router.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    """Create a new category (unique name enforced)"""
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


# ==============================================================
# 💬 FAQ ROUTES
# ==============================================================

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
