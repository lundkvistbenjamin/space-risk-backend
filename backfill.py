import logging

from app.pipeline.ingestion import run_pipeline, save_to_supabase


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main():
    for days_back in range(30, 0, -1):
        logging.info(
            "Backfilling assessment %d/30 (days_back=%d)",
            31 - days_back,
            days_back,
        )

        payload = run_pipeline(days_back=days_back)
        save_to_supabase(payload)


if __name__ == "__main__":
    main()