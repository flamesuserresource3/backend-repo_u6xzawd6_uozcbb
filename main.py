import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Cv, Project

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Portfolio/CV API running"}

# -----------------------------
# Health/DB Test
# -----------------------------

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# -----------------------------
# Helpers
# -----------------------------

def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


def serialize(doc: dict) -> dict:
    doc = dict(doc)
    if doc.get("_id"):
        doc["id"] = str(doc.pop("_id"))
    return doc

# -----------------------------
# CV Endpoints
# -----------------------------

@app.get("/api/cv", response_model=Optional[dict])
def get_cv():
    """Return the most recently created CV document if available"""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    docs = db.cv.find().sort("created_at", -1).limit(1)
    items = [serialize(d) for d in docs]
    return items[0] if items else None

@app.post("/api/cv")
def create_cv(payload: Cv):
    cv_id = create_document("cv", payload)
    created = db.cv.find_one({"_id": ObjectId(cv_id)})
    return serialize(created)

@app.put("/api/cv/{cv_id}")
def update_cv(cv_id: str, payload: Cv):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    oid = to_object_id(cv_id)
    result = db.cv.update_one({"_id": oid}, {"$set": payload.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="CV not found")
    updated = db.cv.find_one({"_id": oid})
    return serialize(updated)

@app.delete("/api/cv/{cv_id}")
def delete_cv(cv_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    oid = to_object_id(cv_id)
    result = db.cv.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="CV not found")
    return {"status": "deleted", "id": cv_id}

# -----------------------------
# Project Endpoints
# -----------------------------

@app.get("/api/projects")
def list_projects(limit: int = 50):
    docs = get_documents("project", {}, limit)
    return [serialize(d) for d in docs]

@app.post("/api/projects")
def create_project(payload: Project):
    proj_id = create_document("project", payload)
    created = db.project.find_one({"_id": ObjectId(proj_id)})
    return serialize(created)

@app.put("/api/projects/{project_id}")
def update_project(project_id: str, payload: Project):
    oid = to_object_id(project_id)
    result = db.project.update_one({"_id": oid}, {"$set": payload.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    updated = db.project.find_one({"_id": oid})
    return serialize(updated)

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    oid = to_object_id(project_id)
    result = db.project.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "deleted", "id": project_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
