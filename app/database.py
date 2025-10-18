from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Get database URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# ✅ Create session for DB transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Base class for models
Base = declarative_base()

# ✅ Dependency: Used inside FastAPI routes to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
print("DATABASE_URL:", DATABASE_URL)
