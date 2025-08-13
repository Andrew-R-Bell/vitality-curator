# test_run.py
import os
from dotenv import load_dotenv
from bot import run_once

# Load local environment variables
load_dotenv()

if __name__ == "__main__":
    print("[Test Run] Starting dry-run test of Health & Longevity Bot")
    run_once()
    print("[Test Run] Finished")
