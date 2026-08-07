from fastapi import HTTPException
from supabase import Client, create_client
from app.config import SUPABASE_KEY, SUPABASE_URL


# Create and return a configured Supabase client
def get_supabase_client() -> Client:

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase credentials missing on server."
        )

    return create_client(SUPABASE_URL, SUPABASE_KEY)