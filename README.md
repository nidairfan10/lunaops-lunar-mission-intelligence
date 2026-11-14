
# LunaOps — Lunar Mission Intelligence

An interactive lunar south-pole terrain analysis and preliminary mission-planning prototype.

LunaOps is an independent educational research project that explores how terrain measurements, astronomical observations, and configurable decision models can support preliminary comparisons of lunar south-polar study regions.

The project combines lunar terrain analysis, NASA/JPL Horizons integration, and transparent decision-support tools in an interactive dashboard.

## Project Objectives

- Explore terrain characteristics of selected lunar south-polar regions.
- Analyze elevation and surface slope using lunar terrain datasets.
- Compare candidate regions through measurable terrain indicators.
- Demonstrate configurable and transparent mission decision-making.
- Explore how different mission priorities affect candidate-site comparisons.
- Examine astronomical observation geometry over configurable time windows.
- Communicate scientific assumptions, data provenance, and uncertainty.

## Implemented Features

### 1. Lunar Terrain Explorer
- Interactive exploration of two candidate regions.
- Terrain visualizations for both study areas.
- Site selection controls.

### 2. Elevation Analysis
- Mean elevation and elevation range.
- Elevation variability statistics.
- Terrain visualization and quantitative measurements.

### 3. Slope Intelligence
- Candidate-site slope maps.
- Mean and median slope measurements.
- Terrain percentages at or below 5° and 10°.
- Slope distribution analysis.

### 4. Candidate-Site Comparison
- Side-by-side comparison of selected regions.
- Automated comparison using available terrain measurements.
- Terrain risk indicators.

### 5. Mission Site Decision Engine
- Weighted comparison using four terrain indicators.
- Configurable criterion weights.
- Relative performance scoring.
- Decision methodology and scoring transparency.

### 6. Sensitivity and Scenario Analysis
- Interactive mission-weight simulator.
- Weight sensitivity analysis.
- Scenario comparison summary.
- Exploration of how different weighting choices affect results.

### 7. Horizon Intelligence
- Single-observation Sun and Earth apparent-position calculations.
- Integration with the NASA/JPL Horizons API.
- Observation-time selection.
- Provisional-coordinate warnings and scientific limitations.

### 8. Mission Environment Timeline
- Configurable observation date and start time.
- Observation durations from 1 to 72 hours.
- Configurable sampling intervals.
- Sun and Earth apparent-elevation comparisons across the observation window.
- Interactive timeline inspection.

### 9. Data Confidence and Scientific Limitations
- Data provenance documentation.
- Dataset resolution information.
- Spatial metadata considerations.
- Scientific assumptions and known limitations.

### 10. Mission Analysis Reports
- Downloadable TXT report.
- Printable PDF mission analysis report.
- Candidate-site measurements and decision-model results.
- Current simulator weights and scores in the reports.

## Candidate Regions

LunaOps currently compares two selected lunar south-polar study areas:

**Site 01 — Connecting Ridge**

**Site 04 — Shackleton Rim**

The comparison examines available elevation and slope measurements for each region.

The candidate-site results are relative comparisons under an experimental scoring model. They do not establish absolute landing suitability or operational safety.

## Data Sources

The project uses lunar terrain datasets reported as originating from NASA's Lunar Orbiter Laser Altimeter (LOLA) data products.

- **NASA Planetary Geodesy and Geophysics Data Archive — LOLA Products:**  
  https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/

- **NASA Lunar Reconnaissance Orbiter Data Products:**  
  https://science.nasa.gov/mission/lro/data-products/

Astronomical observations are requested through the NASA/JPL Horizons API:

- **NASA/JPL Horizons:**  
  https://ssd.jpl.nasa.gov/horizons/

Dataset provenance, spatial metadata, resolution, and known uncertainties are documented within the application.

## Technologies

### Application
- HTML
- CSS
- JavaScript

### Data Processing
- Python
- Rasterio
- GeoTIFF raster datasets

### Data Visualization
- Interactive browser-based visualizations.
- Terrain and slope map representations.
- Quantitative comparison indicators.
- Astronomical observation timelines.

## Project Architecture

LunaOps uses a lightweight browser-based architecture supported by preprocessed lunar terrain datasets and a Python server.

### Application Layer
- HTML structures the dashboard and its interactive components.
- CSS provides interface styling, layouts, and visual presentation.
- JavaScript manages user interactions, terrain comparisons, decision-model calculations, simulator updates, and report generation.

### Data Layer
- GeoTIFF raster datasets provide lunar elevation, slope, and regional roughness information.
- Python and Rasterio support geospatial data inspection and processing.
- JSON files provide precomputed terrain statistics used by the application.

### Analysis Layer
- Elevation and slope measurements are presented through dashboard visualizations.
- Candidate regions are compared using four configurable terrain indicators.
- A weighted decision model calculates relative comparison scores.
- Sensitivity analysis and the mission-weight simulator allow users to explore alternative weighting scenarios.

### Astronomical Observation Layer
- A Python HTTP server communicates with the NASA/JPL Horizons API.
- The application requests apparent Sun and Earth positions for selected observation times.
- The timeline endpoint supports configurable observation durations and sampling intervals.

### Reporting Layer
- The application generates downloadable TXT reports.
- A browser-based printable report supports PDF export.
- Reports document candidate-site measurements, model results, data provenance, and scientific limitations.

## Decision Model Methodology

The prototype evaluates candidate regions using four terrain indicators:

1. Mean slope — lower values are preferred by the model.
2. Percentage of terrain at or below 10° slope — higher values are preferred.
3. Percentage of terrain at or below 5° slope — higher values are preferred.
4. Elevation standard deviation — lower values are preferred.

Each indicator is normalized relative to the two candidate regions and combined using configurable weights.

The mission-weight simulator allows users to explore alternative weighting scenarios and observe their effect on the relative comparison.

**Important:** The scoring methodology and weights are experimental project design choices. They are not official NASA standards, validated landing-suitability models, or probabilities of mission success.

## Data Provenance and Scientific Limitations

LunaOps documents the following considerations:

- Candidate-site elevation and slope rasters have matching grid dimensions, pixel spacing, and affine transforms within each respective site.
- The candidate rasters use matching polar stereographic projection parameters, but their CRS metadata is unnamed and the datum is unspecified.
- The regional LOLA roughness dataset has a pixel resolution of approximately 1,000 m.
- Spatial alignment between the regional roughness dataset and candidate-site rasters has not been conclusively verified.
- The 5 m candidate-site datasets and 1 km roughness dataset represent substantially different spatial scales.
- An internal numerical consistency check found very close agreement between interior elevation-derived slope calculations and the corresponding supplied slope rasters. This does not independently establish source-data accuracy or processing provenance.

### Astronomical Observation Limitations

The coordinates used for the Horizons calculations are provisional because the original elevation raster coordinate reference system and projection parameters have not been conclusively verified.

Consequently:

- Horizons results must not be treated as validated site-specific illumination measurements.
- Apparent Sun and Earth elevations are not equivalent to visibility above the local terrain.
- The calculations do not establish terrain obstruction or operational communications availability.

### Scientific Limitations

Terrain comparison is not landing certification.

Elevation and slope measurements alone cannot establish landing safety.

Further investigation is required to assess:

- Surface illumination and lighting conditions.
- Thermal conditions.
- Boulder distribution and surface hazards.
- Communications and operational constraints.
- Subsurface properties.
- Spatial registration and georeferencing accuracy.

The application is intended for preliminary educational exploration and should not be used for real lunar landing decisions.

## Running the Application

LunaOps uses a Python server to host the application and provide the Horizon Intelligence and Mission Environment Timeline API endpoints.

### Requirements
- Python 3
- Internet connection for live NASA/JPL Horizons requests
- A modern web browser

The Horizons server uses Python standard-library modules. No additional Python packages are required to run the server.

### Start the server

From the project directory, run:

```bash
python3 horizons_server.py
```

The server listens on port `8001`.

**Local environment:** Open `http://localhost:8001` in your browser.

**GitHub Codespaces:** Open the Ports panel, locate port `8001`, and open its forwarded address. If the port is not listed, add port `8001`.

Keep the server running while using the application. Press `Ctrl+C` in the terminal to stop it.

The Horizon Intelligence and Mission Environment Timeline features require an internet connection and access to the NASA/JPL Horizons API.

## Project Status

**Working educational research and mission-planning prototype.**

The application includes interactive terrain analysis, candidate-site comparison, a configurable decision engine, sensitivity analysis, astronomical observation tools, scientific transparency documentation, and downloadable mission analysis reports.

## Future Development

Potential future improvements include:

- Improved coordinate reference system verification and geospatial registration.
- More detailed lunar illumination analysis.
- Additional lunar terrain and surface-hazard datasets.
- Further investigation of thermal and subsurface characteristics.
- Uncertainty-aware decision-model approaches.
- Expanded mission-planning indicators.

These are proposed research directions and are not yet implemented features.

## Disclaimer

LunaOps is an independent educational project developed for research, exploration, and demonstration purposes.

It is not an official NASA application, does not represent NASA endorsement, and does not certify lunar landing-site safety.

---

**LunaOps — Lunar Mission Intelligence**

*Exploring lunar terrain through data, analysis, and transparent decision-making.*
