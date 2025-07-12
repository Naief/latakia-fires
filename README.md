# Latakia Wildfire Early-Warning & Mapping System

## Architecture Overview

```mermaid
graph TD
    A[NASA FIRMS API] -->|CSV Download| B[Data Fetcher (fetch_hotspots.py)]
    B -->|hotspots_viirs.csv| C[Flask API (app.py)]
    B -->|hotspots_modis.csv| C
    B -->|fetch_status.json| C
    B -->|fetcher.log| C
    C -->|GeoJSON, Status JSON| D[Leaflet Frontend (index.html)]
    C -->|/logs| D
    C -->|api.log| D
    D -->|AJAX| C
    D -->|Live Log Polling| C
    subgraph User
      D
    end
```

---

## System Components

### 1. **Data Pipeline** (`fetch_hotspots.py`)
- **Automated fetcher**: Downloads VIIRS and MODIS fire data every 15 minutes (cron or daemon)
- **Outputs**: `hotspots_viirs.csv`, `hotspots_modis.csv`, `fetch_status.json`, and `fetcher.log`
- **Logging**: All actions and errors are logged to `fetcher.log` (rotating file, also stdout)
- **Status**: Writes `fetch_status.json` with status, timestamp, and message after each run
- **Testing**: Modular, type-annotated, and ready for unit testing

### 2. **API Layer** (`app.py`)
- **Flask server**: Serves RESTful endpoints
    - `/hotspots?model=viirs|modis` (GeoJSON)
    - `/fetch_status` (JSON)
    - `/logs` (plain text, last 200 lines of both logs)
- **Logging**: All API actions and errors are logged to `api.log` (rotating file, also stdout)
- **CORS**: Enabled for public access
- **Error Handling**: Robust 404/500 handlers
- **Testing**: Modular, type-annotated, and ready for unit testing

### 3. **Web Interface** (`index.html`)
- **Modern, accessible UI**: Apple/Netflix/Leaf-inspired, responsive, ARIA, keyboard nav
- **Map**: Leaflet.js with VIIRS/MODIS toggle, time slider, playback, provenance, etc.
- **Live Log Popup**: Floating button opens a modal showing live logs from `/logs` (polls every 5s)
- **All times in Syria time**
- **No unused code or overlays**

---

## Logging & Monitoring

- **Fetcher logs**: `fetcher.log` (rotating, in project root)
- **API logs**: `api.log` (rotating, in project root)
- **Live logs**: `/logs` endpoint streams last 200 lines of both logs
- **Frontend log popup**: Click the 📝 button (bottom right) to view live system logs in the browser
- **Status**: `/fetch_status` endpoint and sidebar card show last fetch status

---

## Getting Started

### 1. Prerequisites
- Python 3.8+
- NASA FIRMS API key (register at https://firms.modaps.eosdis.nasa.gov/api)
- Web browser with JavaScript enabled

### 2. Install Dependencies
```bash
pip install requests pandas flask flask-cors
```

### 3. Data Fetching
```bash
python fetch_hotspots.py
```
This will download the latest fire data and update logs/status.

### 4. Start the Web Server
```bash
python app.py
```
The web interface will be available at `http://localhost:5000`

### 5. Automation (Recommended)
Set up a cron job to run the fetcher every 15 minutes:
```
*/15 * * * * cd /path/to/project && /path/to/venv/bin/python fetch_hotspots.py >> fetch_cron.log 2>&1
```

---

## Usage

- **Map**: Open `index.html` in your browser. The map loads fire hotspots and updates automatically.
- **Toggle**: Switch between VIIRS and MODIS data with the sidebar toggle.
- **Playback**: Use the time slider and playback controls to explore fire spread.
- **Live Logs**: Click the 📝 button (bottom right) to view live logs (fetches, API calls, errors, etc.).
- **Status**: Sidebar shows last fetch status and errors.

---

## Best Practices

- **Type hints and docstrings** in all Python code
- **Rotating logs** for both fetcher and API
- **Error handling** for all file/network operations
- **Testing**: Add unit tests for fetcher and API endpoints
- **Accessibility**: ARIA, keyboard nav, high contrast, responsive
- **No unused code or files**
- **Clear documentation and diagrams**

---

## Troubleshooting

- **No data on map?** Check `fetch_status.json` and logs via the log popup or `/logs` endpoint.
- **API not responding?** Check `api.log` and ensure Flask is running on port 5000.
- **Cron not running?** Check `fetch_cron.log` and `fetcher.log` for errors.
- **Frontend errors?** Open browser dev tools and check network/log popup.

---

## Contributing

- Bug reports, feature requests, and improvements are welcome!
- Please follow code style and documentation standards.

---

## License

MIT License. See LICENSE file.

---

## Acknowledgments

- NASA FIRMS for satellite fire detection data
- Leaflet.js for interactive mapping
- OpenStreetMap for base map data
- The open-source community for tools and libraries