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
    D -->|Legend/Info Modals| E[Legend Info Modals]
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
- **Modern, accessible UI**: Google/Material/Apple/Netflix-inspired, responsive, ARIA, keyboard nav
- **Map**: Leaflet.js with VIIRS/MODIS toggle, time slider, playback, provenance, etc.
- **Legend**: Fully interactive, Material-style legend with:
    - Clickable items to toggle map layers (current, recent, spread path, highest FRP, decreasing FRP, risk buffer)
    - Info icons (ℹ) for every legend item, opening detailed modals explaining each map symbol and its significance
    - Custom icons for each item, including a buffer+hotspot icon for risk buffer
- **Info Modals**: Each legend item has a dedicated, accessible modal with:
    - Clear definition, visual characteristics, data significance, and usage tips
    - Color-coded headers and sections
    - Emergency and operational guidance
    - Consistent, modern design
- **Risk Buffer**: 1km red translucent circle around each hotspot, with a new icon in the legend and a detailed info modal
- **Spread Path**: Directional arrows and color-coded lines show fire movement; toggled together from the legend
- **Decreasing FRP**: Green glow and down arrow for dying-out fires, with legend and info modal
- **Highest FRP**: Blue glow and star badge for the most intense fire, with legend and info modal
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

## Key NASA FIRMS Resources & API Endpoints

- [NASA FIRMS Fire Map (Latakia, 24hrs)](https://firms.modaps.eosdis.nasa.gov/map/#d:24hrs;@35.99,35.87,13.66z)
- [NASA FIRMS Area API Documentation](https://firms.modaps.eosdis.nasa.gov/api/area/)
- [Sample Area API Call (VIIRS, World, 2025-07-11)](https://firms.modaps.eosdis.nasa.gov/api/area/html/3d47c7709150c515edb9beb54ac9832a/VIIRS_SNPP_NRT/world/1/2025-07-11)

---

## Running the System: Required Endpoints & Automation

To run the full wildfire mapping system, ensure the following are running and accessible:

- **Flask API Endpoints:**
    - [http://localhost:5000/hotspots?model=viirs](http://localhost:5000/hotspots?model=viirs)  
      (GeoJSON for VIIRS fire hotspots)
    - [http://localhost:5000/hotspots?model=modis](http://localhost:5000/hotspots?model=modis)  
      (GeoJSON for MODIS fire hotspots)
    - [http://localhost:5000/fetch_status](http://localhost:5000/fetch_status)  
      (JSON status of last data fetch)
    - [http://localhost:5000/logs](http://localhost:5000/logs)  
      (Live logs)
- **Frontend:**
    - Open `index.html` in your browser (or access via the Flask server if served statically)
- **Backend (optional):**
    - [http://[::]:8000/](http://[::]:8000/)  
      (If running an additional backend service, e.g., for advanced analytics)
- **Automation:**
    - Set up a **cron job** to run `fetch_hotspots.py` every 15 minutes to keep the data fresh and the map up to date. See the 'Getting Started' section above for a sample cron entry.

> **Note:** The Flask API and the data fetcher must be running for the map and endpoints to function correctly. The cron job ensures the latest NASA FIRMS data is always available for the frontend and API.

---

## Usage

- **Map**: Open `