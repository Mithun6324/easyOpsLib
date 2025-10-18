from fastapi import FastAPI
from app.routes import admin
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EaseOps E-Library Admin Backend",
    description="Admin-side API for managing eBooks, FAQs, and Categories.",
    version="1.0.0"
)

app.include_router(admin.router)

@app.get("/")
def home():
    return {"message": "Welcome to EaseOps E-Library Admin API"}
