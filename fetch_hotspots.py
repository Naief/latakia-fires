import requests
import time
import pandas as pd
from datetime import datetime
import json
import traceback
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any

MAP_KEY = "3d47c7709150c515edb9beb54ac9832a"  # Use your MAP_KEY here
BBOX = "35.0,35.0,36.0,36.0"
DAY_RANGE = "10"

SOURCES = {
    "viirs": "VIIRS_SNPP_NRT",
    "modis": "MODIS_NRT"
}

BASE = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
INTERVAL_MINUTES = 10
LOG_FILE = "fetcher.log"

status: Dict[str, Any] = {
    "status": "unknown",
    "timestamp": None,
    "message": "Not yet run"
}

def setup_logger() -> logging.Logger:
    """Set up a rotating logger for fetcher events."""
    logger = logging.getLogger("fetcher")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=500_000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    # Also log to stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(stream_handler)
    return logger

logger = setup_logger()

def write_status(status: Dict[str, Any]) -> None:
    """Write the current fetch status to fetch_status.json."""
    status["timestamp"] = datetime.utcnow().isoformat() + "Z"
    with open("fetch_status.json", "w") as f:
        json.dump(status, f)

def fetch_and_report(model: str) -> bool:
    """Fetch data for a given model, log results, and update status."""
    source = SOURCES[model]
    url = f"{BASE}/{MAP_KEY}/{source}/{BBOX}/{DAY_RANGE}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        fname = f"hotspots_{model}.csv"
        with open(fname, "w") as f:
            f.write(resp.text)
        # Check for API error in the CSV
        if resp.text.startswith("Invalid") or resp.text.lower().startswith("error"):
            msg = f"API returned error: {resp.text.strip()}"
            logger.error(f"[{model.upper()}] {msg}")
            status["status"] = "error"
            status["message"] = f"{model.upper()}: {msg}"
            write_status(status)
            return False
        df = pd.read_csv(fname)
        if df.empty:
            # Overwrite with just the header if no data rows
            if model == "viirs":
                header = "latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight\n"
            else:
                header = "latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_t31,frp,daynight\n"
            with open(fname, "w") as f:
                f.write(header)
            logger.info(f"[{model.upper()}] No hotspots found. Overwrote {fname} with header only.")
            return True
        df['timestamp'] = pd.to_datetime(
            df['acq_date'].astype(str) + ' ' + df['acq_time'].astype(str).str.zfill(4),
            format='%Y-%m-%d %H%M'
        )
        newest = df['timestamp'].max()
        latency = datetime.utcnow() - newest.to_pydatetime()
        logger.info(f"[{model.upper()}] Retrieved {len(df)} records. Newest: {newest} UTC, Latency: {int(latency.total_seconds()//60)} min")
        return True
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[{model.upper()}] Error: {e}\n{tb}")
        status["status"] = "error"
        status["message"] = f"{model.upper()}: {e}\n{tb}"
        write_status(status)
        return False

def fetch_all() -> None:
    """Fetch all models and update status/logs."""
    all_success = True
    for model in SOURCES:
        ok = fetch_and_report(model)
        if not ok:
            all_success = False
    if all_success:
        status["status"] = "success"
        status["message"] = "All model fetches successful."
        write_status(status)
        logger.info("All model fetches successful.")

def main() -> None:
    """Main loop for scheduled fetching."""
    while True:
        logger.info(f"Fetching latest hotspots for all models at {datetime.utcnow():%Y-%m-%d %H:%M:%S} UTC …")
        fetch_all()
        logger.info(f"Sleeping {INTERVAL_MINUTES} minutes …")
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
