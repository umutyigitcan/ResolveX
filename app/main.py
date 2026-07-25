from fastapi import FastAPI
from app.models.user import User
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="ResolveX API",
    description="Customer support ticket management system",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"project_status":"running!"}

@app.get("/health")
def read_health():
    return {"status": "ok"}