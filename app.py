import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

app = FastAPI(
    title="Space Weather Risk API",
    description="Provides real-time infrastructure risk assessment powered by NASA DONKI data.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase credentials missing on server."
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "space-risk-backend"}

@app.get("/api/v1/latest-assessment", tags=["Assessments"])
def get_latest_assessment():
    supabase = get_supabase_client()
    response = supabase.table("space_weather_assessments") \
        .select("*") \
        .order("generated_at", desc=True) \
        .limit(1) \
        .execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="No assessments found in database.")

    return response.data[0]

@app.get("/api/v1/trends", tags=["Assessments"])
def get_assessment_trends(limit: int = 7):
    supabase = get_supabase_client()
    response = supabase.table("space_weather_assessments") \
        .select("generated_at, scores, threat_level, flare_count, cme_count") \
        .order("generated_at", desc=True) \
        .limit(limit) \
        .execute()

    return response.data