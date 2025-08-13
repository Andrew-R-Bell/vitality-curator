# test_run.py
from dotenv import load_dotenv
load_dotenv()

from bot import run_once

if __name__ == "__main__":
    print("[Test Run] Starting dry-run test of Health & Longevity Bot")
    run_once()
    print("[Test Run] Finished")
