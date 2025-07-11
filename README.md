# Latakia Wildfire Early-Warning & Mapping Pilot

## Overview
This project provides a lightweight, open-source prototype to ingest near-real-time satellite “hotspot” (fire) data over the Latakia mountains, visualize it on a map, and expose it via a simple API. Within hours you can offer local firefighting teams live situational awareness to:

- **Detect** new ignitions within 15 minutes via NASA MODIS/VIIRS
- **Visualize** hotspots on an interactive map (Jupyter preview or Leaflet web map)
- **Share** GeoJSON endpoints to any front-end/dashboard or mobile app

By combining minimal infrastructure (Python, Flask, free-tier hosting) with official satellite feeds, you can dramatically improve response times and coordination—even before scaling to drones or advanced modeling.

---

## Components

1. **fetch_hotspots.py**  
   - Queries the NASA FIRMS API for Latakia bounding coordinates  
   - Saves the latest VIIRS (and/or MODIS) CSV of active fires  

2. **view.ipynb**  
   - Loads `hotspots.csv` into GeoPandas  
   - Overlays points on a basemap (via Contextily) for quick visual checks  

3. **app.py**  
   - Flask server exposing `/hotspots` returning GeoJSON  
   - Can be embedded in any web or mobile front end  

---

## Getting Started

### 1. Prerequisites
- Python 3.8+  
- A free NASA FIRMS API key (register at https://firms.modaps.eosdis.nasa.gov/api)

### 2. Install Dependencies
```bash
pip install requests pandas geopandas flask python-dotenv contextily
```