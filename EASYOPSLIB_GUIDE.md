# EASYOPSLIB - E-Library Admin Backend Guide

## 🌟 Overview

EASYOPSLIB is a FastAPI-based backend system designed for managing an E-Library administration interface. It provides comprehensive functionality for managing eBooks, categories, and frequently asked questions (FAQs) with both individual and bulk upload capabilities.

## 🛠 Technology Stack

- **Framework**: FastAPI 0.115.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Python-JOSE (cryptography) & Passlib (bcrypt) for future implementation
- **File Handling**: Python-multipart for file uploads
- **Data Processing**: Pandas & OpenPyXL for Excel file processing
- **Server**: Uvicorn ASGI server
- **Migration**: Alembic for database migrations

## 📋 Requirements

All dependencies are listed in `requirements.txt`:

```
fastapi==0.115.0
uvicorn==0.31.0
SQLAlchemy==2.0.36
psycopg2-binary==2.9.10
alembic==1.13.3
python-dotenv==1.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic[email]==2.9.2
python-multipart==0.0.9
pandas==2.3.3
openpyxl==3.1.5
requests==2.32.3
```

## 🏗 Project Structure

```
easyOpsLib/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env                       # Environment configuration
├── uploads/                   # File upload directory
├── app/
│   ├── database.py           # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── admin_models.py   # Database models
│   ├── routes/
│   │   └── admin.py         # API routes
│   └── schemas/
│       ├── __init__.py
│       └── admin_schemas.py # Pydantic schemas
```

## 🗄 Database Models

### 1. Category Model
- **Table**: `categories`
- **Fields**:
  - `id`: Primary key (Integer)
  - `name`: Unique category name (String, max 100 chars)
  - `description`: Category description (Text, optional)
- **Relationships**: One-to-many with EBooks

### 2. EBook Model
- **Table**: `ebooks`
- **Fields**:
  - `id`: Primary key (Integer)
  - `title`: Book title (String, max 200 chars)
  - `author`: Author name (String, max 100 chars)
  - `tags`: Book tags/keywords (String, max 100 chars)
  - `file_url`: Path to uploaded file (String, max 255 chars)
  - `category_id`: Foreign key to Category (Integer)
  - `uploaded_at`: Upload timestamp (DateTime)
- **Relationships**: Many-to-one with Category

### 3. FAQ Model
- **Table**: `faqs`
- **Fields**:
  - `id`: Primary key (Integer)
  - `question`: FAQ question (Text)
  - `answer`: FAQ answer (Text)

## 🚀 API Functionality

### 📚 EBook Management

#### 1. Upload Single EBook
- **Endpoint**: `POST /ebooks`
- **Functionality**: Upload an eBook file with metadata
- **Required Parameters**:
  - `title` (Form data)
  - `author` (Form data)
  - `tags` (Form data)
  - `category_id` (Form data)
  - `file` (File upload)
- **Features**:
  - Validates category existence
  - Creates unique filename with UUID
  - Stores file in `uploads/` directory
  - Returns complete eBook information

#### 2. List All EBooks
- **Endpoint**: `GET /ebooks`
- **Functionality**: Retrieve all eBooks with metadata
- **Features**:
  - Handles null file URLs for Excel-imported books
  - Returns complete list with all fields

#### 3. Delete EBook
- **Endpoint**: `DELETE /ebooks/{ebook_id}`
- **Functionality**: Remove eBook and associated file
- **Features**:
  - Validates eBook existence
  - Safely removes file from disk
  - Handles missing files gracefully

#### 4. Bulk Upload from Excel
- **Endpoint**: `POST /ebooks/upload_excel`
- **Functionality**: Import multiple eBooks from Excel file
- **Required Excel Columns**:
  - `title`: Book title
  - `author`: Author name
  - `tags`: Book tags/keywords
  - `category`: Category name
- **Features**:
  - Auto-creates missing categories
  - Validates required fields
  - Handles missing/invalid data gracefully
  - Returns detailed success/failure report
  - Stores Excel file path for reference

### 🗂 Category Management

#### 1. Create Category
- **Endpoint**: `POST /categories`
- **Functionality**: Create new book category
- **Required Fields**:
  - `name`: Category name (unique)
  - `description`: Category description (optional)
- **Features**:
  - Enforces unique category names
  - Returns complete category information

#### 2. List Categories
- **Endpoint**: `GET /categories`
- **Functionality**: Retrieve all available categories
- **Features**:
  - Returns all categories with descriptions
  - Used for dropdown/selection interfaces

### 💬 FAQ Management

#### 1. Create FAQ
- **Endpoint**: `POST /faqs`
- **Functionality**: Add new frequently asked question
- **Required Fields**:
  - `question`: FAQ question text
  - `answer`: FAQ answer text
- **Features**:
  - Supports rich text content
  - Returns complete FAQ information

#### 2. List FAQs
- **Endpoint**: `GET /faqs`
- **Functionality**: Retrieve all FAQs
- **Features**:
  - Returns all questions and answers
  - Suitable for help/support sections

## ⚙️ Configuration

### Environment Variables (.env)
```
DATABASE_URL=postgresql://username:password@host:port/database_name
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
```

### Database Setup
The application uses PostgreSQL and automatically creates tables on startup through SQLAlchemy's `Base.metadata.create_all()`.

## 🚀 Getting Started

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd easyOpsLib

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration
```bash
# Create PostgreSQL database
createdb easyops-library

# Update .env file with your database credentials
```

### 3. Run Application
```bash
# Start the development server
uvicorn main:app --reload

# Access API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## 📖 Usage Examples

### Upload Single EBook
```bash
curl -X POST "http://localhost:8000/ebooks" \
  -H "Content-Type: multipart/form-data" \
  -F "title=Python Programming" \
  -F "author=John Doe" \
  -F "tags=programming,python,coding" \
  -F "category_id=1" \
  -F "file=@book.pdf"
```

### Create Category
```bash
curl -X POST "http://localhost:8000/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Programming",
    "description": "Books about programming and software development"
  }'
```

### Bulk Upload via Excel
Prepare an Excel file with columns: `title`, `author`, `tags`, `category`

```bash
curl -X POST "http://localhost:8000/ebooks/upload_excel" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@books.xlsx"
```

## 🔧 Key Features

### 1. File Management
- **UUID-based naming**: Prevents filename conflicts
- **Safe file handling**: Graceful error handling for missing files
- **Upload directory management**: Automatic directory creation

### 2. Data Validation
- **Pydantic schemas**: Strong typing and validation
- **Foreign key validation**: Ensures data integrity
- **Excel format validation**: Validates required columns

### 3. Bulk Operations
- **Excel import**: Support for .xlsx files
- **Auto-category creation**: Creates missing categories automatically
- **Detailed reporting**: Success/failure tracking for batch operations

### 4. Error Handling
- **HTTP status codes**: Proper REST API responses
- **Detailed error messages**: Clear feedback for API users
- **Graceful degradation**: Continues operation despite partial failures

## 🎯 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/ebooks` | POST | Upload single eBook |
| `/ebooks` | GET | List all eBooks |
| `/ebooks/{id}` | DELETE | Delete specific eBook |
| `/ebooks/upload_excel` | POST | Bulk upload from Excel |
| `/categories` | POST | Create new category |
| `/categories` | GET | List all categories |
| `/faqs` | POST | Create new FAQ |
| `/faqs` | GET | List all FAQs |

## 📚 Future Enhancements

The codebase includes preparation for:
- **Authentication system**: JWT tokens with python-jose
- **Password hashing**: bcrypt integration with passlib
- **Advanced search**: Text search across eBooks
- **File type validation**: Support for multiple formats
- **API rate limiting**: Request throttling
- **Logging system**: Comprehensive audit trails

## 🔍 Development Notes

- **Database migrations**: Use Alembic for schema changes
- **API documentation**: Automatic Swagger/ReDoc generation
- **Type safety**: Full Pydantic integration for request/response validation
- **Scalability**: Designed for horizontal scaling with stateless architecture

This guide provides comprehensive coverage of all functionality available in EASYOPSLIB. The system is designed to be maintainable, scalable, and user-friendly for managing e-library operations.