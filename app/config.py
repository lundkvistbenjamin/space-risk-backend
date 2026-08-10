import os
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

# NASA DONKI API configuration
NASA_API_KEY: str = os.getenv("NASA_API_KEY", "DEMO_KEY")
DONKI_BASE_URL = "https://api.nasa.gov/DONKI"

# Supabase configuration
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")