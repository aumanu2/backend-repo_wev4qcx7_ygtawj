import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import create_document, get_documents, db
from schemas import ContactMessage, Testimonial, Experience

app = FastAPI(title="Girish Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Girish Portfolio API running"}

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
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Contact form endpoint
@app.post("/api/contact")
def submit_contact(msg: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", msg)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Read-only demo data endpoints for portfolio sections
@app.get("/api/testimonials", response_model=List[Testimonial])
def get_testimonials():
    # Could read from DB later; static seed for now
    return [
        Testimonial(name="Dr. A. N. Mentor", role="R&D Director, TechLabs", quote="Girish transforms ambiguous engineering challenges into elegant, manufacturable designs."),
        Testimonial(name="Priya S.", role="Program Manager, AeroWorks", quote="Rare balance of deep engineering rigor and product sense.")
    ]

@app.get("/api/experience", response_model=List[Experience])
def get_experience():
    return [
        Experience(company="InnovateX", title="Senior Design Engineer", start="2019", end="Present", highlights=["Led cross-functional design sprints for automation systems","Cut prototype cycles by 35% using modular CAD libraries","Filed 3 patents in mechatronic assemblies"]),
        Experience(company="AeroWorks", title="Mechanical Engineer", start="2016", end="2019", highlights=["Developed finite element models for composite structures","Implemented DFMA to reduce BOM by 18%","Mentored new grads on CAD best practices"])
    ]

# Schema endpoint for Flames database viewer
class SchemaItem(BaseModel):
    name: str
    fields: List[str]

@app.get("/schema")
def get_schema():
    # Basic reflection for viewer (manual list for clarity)
    return {
        "contactmessage": ["name", "email", "subject", "message", "source", "created_at", "updated_at"],
        "testimonial": ["name", "role", "quote", "avatar_url"],
        "experience": ["company", "title", "start", "end", "highlights", "logo_url"],
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
