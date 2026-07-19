"""Configuration — loads from environment (.env). See README."""
import os
from pathlib import Path

# Load .env if python-dotenv is installed (optional).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- API keys ---
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

# --- Qualification model: set to your current Sonnet model string ---
QUALIFY_MODEL = os.getenv("QUALIFY_MODEL", "claude-sonnet-5")

# --- Paths (relative to _agent/) ---
AGENT_DIR = Path(__file__).resolve().parent.parent          # _agent/
DB_PATH = Path(os.getenv("SEEN_LEADS_DB", AGENT_DIR / "data" / "seen_leads.db"))
SCHEMA_PATH = AGENT_DIR / "data" / "schema.sql"
PROMPT_PATH = AGENT_DIR / "skills" / "leads" / "qualification-prompt.md"
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", AGENT_DIR / "orchestrator" / "output"))

# --- Run tuning ---
SLICES_PER_RUN = int(os.getenv("SLICES_PER_RUN", "6"))       # productive slices per run
MAX_PER_SLICE = int(os.getenv("MAX_PER_SLICE", "10"))        # Maps results per slice query
WORKED_OUT_RATIO = float(os.getenv("WORKED_OUT_RATIO", "0.8"))  # >= this share dupes/rejects -> worked-out
REVISIT_AFTER_DAYS = int(os.getenv("REVISIT_AFTER_DAYS", "180"))  # worked-out/empty slices become sweepable again after this

# --- Google Sheets (optional; a dated CSV is always written) ---
SHEETS_ENABLED = os.getenv("SHEETS_ENABLED", "false").lower() == "true"
SHEETS_SPREADSHEET_ID = os.getenv("SHEETS_SPREADSHEET_ID", "")
SHEETS_WORKSHEET = os.getenv("SHEETS_WORKSHEET", "Manufacturer Leads")
SHEETS_REVIEW_WORKSHEET = os.getenv("SHEETS_REVIEW_WORKSHEET", "Review")
GOOGLE_SA_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")  # path to service-account key file
