from app.pipeline.ingestion import (
    run_pipeline,
    save_to_supabase,
)


# Entry point used by GitHub Actions
if __name__ == "__main__":

    results = run_pipeline(days_back=30)

    save_to_supabase(results)