import os
from dotenv import load_dotenv
from bot import run_once

# Load local environment variables
load_dotenv()

print("[Test] Running a single bot post simulation...")
run_once()
print("[Test] Done. Check output above for any errors.")
