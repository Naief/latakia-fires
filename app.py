from flask import Flask, jsonify, request, Response, send_from_directory
import pandas as pd
from flask_cors import CORS
import json
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any
import webbrowser
import threading

app = Flask(__name__)
CORS(app)

API_LOG_FILE = "api.log"
FETCHER_LOG_FILE = "fetcher.log"
LOG_LINES = 200

MODEL_FILES = {
    "viirs": "hotspots_viirs.csv",
    "modis": "hotspots_modis.csv"
}

def setup_logger() -> logging.Logger:
    """Set up a rotating logger for API events."""
    logger = logging.getLogger("api")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(API_LOG_FILE, maxBytes=500_000, backupCount=3)
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

@app.route("/hotspots")
def hotspots():
    """Serve fire hotspots as GeoJSON for the requested model."""
    model = request.args.get("model", "viirs").lower()
    csv_file = MODEL_FILES.get(model, MODEL_FILES["viirs"])
    try:
        df = pd.read_csv(csv_file, comment="#")
    except Exception as e:
        logger.error(f"Failed to read {csv_file}: {e}")
        return jsonify({"error": f"Could not read data for model {model}"}), 500
    features = []
    for _, row in df.iterrows():
        # Use correct brightness column for each model
        if model == "viirs":
            brightness = getattr(row, "bright_ti4", None)
        else:  # modis
            brightness = getattr(row, "brightness", None)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row.longitude, row.latitude]
            },
            "properties": {
                "acq_date": row.acq_date,
                "acq_time": row.acq_time,
                "brightness": brightness,
                "frp": getattr(row, "frp", None),
                "confidence": getattr(row, "confidence", None),
                "daynight": getattr(row, "daynight", None),
                "wind_direction": getattr(row, "wind_direction", None)
            }
        })
    logger.info(f"Served {len(features)} features for model {model}")
    return jsonify({"type": "FeatureCollection", "features": features})

@app.route("/fetch_status")
def fetch_status():
    """Serve the latest fetch status as JSON."""
    if os.path.exists("fetch_status.json"):
        with open("fetch_status.json") as f:
            logger.info("Served fetch_status.json")
            return jsonify(json.load(f))
    else:
        logger.warning("fetch_status.json not found")
        return jsonify({"status": "unknown", "timestamp": None, "message": "No status file found."}), 404

@app.route("/logs")
def logs() -> Response:
    """Stream the last N lines of both fetcher and API logs as plain text."""
    def tail(filename: str, n: int) -> str:
        try:
            with open(filename, "r") as f:
                return ''.join(f.readlines()[-n:])
        except Exception:
            return f"(No log file: {filename})\n"
    api_log = tail(API_LOG_FILE, LOG_LINES)
    fetcher_log = tail(FETCHER_LOG_FILE, LOG_LINES)
    combined = f"--- API LOG ---\n{api_log}\n--- FETCHER LOG ---\n{fetcher_log}"
    return Response(combined, mimetype="text/plain")

# Serve index.html at the root URL
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

# Serve other static files (e.g., JS, CSS) from the project root
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 Internal Server Error: {e}")
    return jsonify({"error": "Internal server error"}), 500

def open_browser():
    webbrowser.open_new('http://localhost:5000/')

if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()
    app.run() 