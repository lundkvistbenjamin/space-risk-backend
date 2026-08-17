from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.database.supabase import get_supabase_client


app = FastAPI(
    title="Space Weather Risk API",
    description="Provides real-time infrastructure risk assessment powered by NASA DONKI data.",
    version="1.0.0",
)

# Allow local frontend development to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():

    return {
        "status": "ok",
        "service": "space-risk-backend",
    }


# Return the latest assessment
@app.get(
    "/api/v1/latest-assessment",
    tags=["Assessments"],
)
def get_latest_assessment():

    supabase = get_supabase_client()

    response = (
        supabase
        .table("space_weather_assessments")
        .select("*")
        .order("generated_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="No assessments found in database.",
        )

    return response.data[0]


# Return recent daily assessment history
@app.get(
    "/api/v1/trends",
    tags=["Assessments"],
)
def get_assessment_trends(
    limit: int = Query(7, ge=1, le=30),
):

    supabase = get_supabase_client()

    response = (
        supabase
        .table("space_weather_assessments")
        .select(
            "assessment_date, generated_at, scores, "
            "threat_level, flare_count, cme_count"
        )
        .order("assessment_date", desc=True)
        .limit(limit)
        .execute()
    )

    return {
        "count": len(response.data),
        "data": response.data,
    }