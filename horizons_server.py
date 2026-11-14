import csv
import io
import json
import os
from datetime import datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import urlopen

HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"

# IMPORTANT:
# These coordinates are provisional. They were calculated by
# assuming the source elevation rasters use IAU 30135.
SITES = {
    "site01": {
        "name": "Site 01 — Connecting Ridge",
        "longitude": -137.489552922,
        "latitude": -89.463162834,
    },
    "site04": {
        "name": "Site 04 — Shackleton Rim",
        "longitude": -171.869897646,
        "latitude": -89.766811452,
    },
}

COORDINATE_WARNING = (
    "Provisional coordinates: the original elevation raster CRS "
    "and projection parameters have not yet been conclusively verified. "
    "These results must not be treated as validated site-specific "
    "illumination or terrain visibility."
)


def get_horizons_position(target, site, observation_time):
    stop_time = observation_time + timedelta(minutes=2)

    params = {
        "COMMAND": f"'{target}'",
        "CENTER": "'coord@301'",
        "COORD_TYPE": "'GEODETIC'",
        "SITE_COORD": (
            f"'{site['longitude']},{site['latitude']},0'"
        ),
        "EPHEM_TYPE": "'OBSERVER'",
        "QUANTITIES": "'4'",
        "ANG_FORMAT": "'DEG'",
        "START_TIME": f"'{observation_time:%Y-%m-%d %H:%M}'",
        "STOP_TIME": f"'{stop_time:%Y-%m-%d %H:%M}'",
        "STEP_SIZE": "'1 m'",
        "TIME_TYPE": "'UT'",
        "MAKE_EPHEM": "'YES'",
        "OBJ_DATA": "'NO'",
        "CSV_FORMAT": "'YES'",
    }

    url = HORIZONS_URL + "?" + urlencode(params)

    with urlopen(url, timeout=40) as response:
        payload = json.loads(response.read().decode("utf-8"))

    result = payload.get("result", "")

    if "ERROR" in result.upper():
        raise ValueError(result[-1200:])

    if "$$SOE" not in result or "$$EOE" not in result:
        raise ValueError("JPL Horizons returned no ephemeris data.")

    before_data = result.split("$$SOE")[0]
    data_section = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]

    azimuth_index = None
    elevation_index = None

    for line in before_data.splitlines():
        if "Azi" in line and "Elev" in line:
            cells = next(csv.reader([line.strip()]))

            for index, cell in enumerate(cells):
                if "Azi" in cell:
                    azimuth_index = index
                if "Elev" in cell:
                    elevation_index = index

    rows = csv.reader(io.StringIO(data_section.strip()))

    for row in rows:
        if not row:
            continue

        if azimuth_index is None or elevation_index is None:
            azimuth_index, elevation_index = 3, 4

        try:
            azimuth = float(row[azimuth_index].strip())
            elevation = float(row[elevation_index].strip())

            return {
                "azimuth_deg": azimuth,
                "elevation_deg": elevation,
            }
        except (ValueError, IndexError):
            continue

    raise ValueError("Could not interpret the Horizons position data.")


def get_horizons_series(target, site, start_time,
                        duration_hours=24, interval_minutes=60):
    """Retrieve apparent positions at a configurable time cadence."""
    stop_time = start_time + timedelta(hours=duration_hours)

    if interval_minutes >= 60:
        step_size = f"{interval_minutes // 60} h"
    else:
        step_size = f"{interval_minutes} m"

    params = {
        "COMMAND": f"'{target}'",
        "CENTER": "'coord@301'",
        "COORD_TYPE": "'GEODETIC'",
        "SITE_COORD": f"'{site['longitude']},{site['latitude']},0'",
        "EPHEM_TYPE": "'OBSERVER'",
        "QUANTITIES": "'4'",
        "ANG_FORMAT": "'DEG'",
        "START_TIME": f"'{start_time:%Y-%m-%d %H:%M}'",
        "STOP_TIME": f"'{stop_time:%Y-%m-%d %H:%M}'",
        "STEP_SIZE": f"'{step_size}'",
        "TIME_TYPE": "'UT'",
        "MAKE_EPHEM": "'YES'",
        "OBJ_DATA": "'NO'",
        "CSV_FORMAT": "'YES'",
    }

    url = HORIZONS_URL + "?" + urlencode(params)

    with urlopen(url, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))

    result = payload.get("result", "")

    if "ERROR" in result.upper():
        raise ValueError(result[-1200:])

    if "$$SOE" not in result or "$$EOE" not in result:
        raise ValueError("JPL Horizons returned no timeline data.")

    before_data = result.split("$$SOE")[0]
    data_section = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]

    azimuth_index = None
    elevation_index = None

    for line in before_data.splitlines():
        if "Azi" in line and "Elev" in line:
            cells = next(csv.reader([line.strip()]))
            for index, cell in enumerate(cells):
                if "Azi" in cell:
                    azimuth_index = index
                if "Elev" in cell:
                    elevation_index = index

    if azimuth_index is None or elevation_index is None:
        azimuth_index, elevation_index = 3, 4

    points = []
    rows = csv.reader(io.StringIO(data_section.strip()))

    for row in rows:
        if not row:
            continue

        try:
            azimuth = float(row[azimuth_index].strip().replace("*", ""))
            elevation = float(row[elevation_index].strip().replace("*", ""))

            timestamp = start_time + timedelta(
                minutes=len(points) * interval_minutes
            )

            points.append({
                "timestamp_utc": timestamp.isoformat(),
                "azimuth_deg": azimuth,
                "elevation_deg": elevation,
            })
        except (ValueError, IndexError):
            continue

    if len(points) < 2:
        raise ValueError("JPL Horizons returned too few valid timeline samples.")

    return points


class LunaOpsHandler(SimpleHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path not in ("/api/horizon", "/api/horizon-series"):
            return super().do_GET()

        try:
            query = parse_qs(parsed.query)

            if parsed.path == "/api/horizon-series":
                date_string = query.get("date", [""])[0]

                if not date_string:
                    raise ValueError("A timeline start date and time are required.")

                start_time = datetime.fromisoformat(date_string)

                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                else:
                    start_time = start_time.astimezone(timezone.utc)

                duration_hours = int(query.get("duration_hours", ["24"])[0])
                interval_minutes = int(query.get("interval_minutes", ["60"])[0])

                if not 1 <= duration_hours <= 72:
                    raise ValueError("Duration must be between 1 and 72 hours.")

                if interval_minutes not in (15, 30, 60, 120):
                    raise ValueError("Sampling interval must be 15, 30, 60, or 120 minutes.")

                if duration_hours * 60 % interval_minutes != 0:
                    raise ValueError("Duration must be divisible by the selected sampling interval.")

                expected_samples = (duration_hours * 60 // interval_minutes) + 1

                if expected_samples > 289:
                    raise ValueError("The requested timeline contains too many samples.")

                timeline = {}

                for site_id, site in SITES.items():
                    timeline[site_id] = {
                        "name": site["name"],
                        "sun": get_horizons_series(
                            "10", site, start_time,
                            duration_hours, interval_minutes
                        ),
                        "earth": get_horizons_series(
                            "399", site, start_time,
                            duration_hours, interval_minutes
                        ),
                    }

                self.send_json({
                    "success": True,
                    "date_start_utc": start_time.isoformat(),
                    "duration_hours": duration_hours,
                    "interval_minutes": interval_minutes,
                    "expected_samples": expected_samples,
                    "source": "NASA/JPL Horizons API",
                    "coordinate_status": "PROVISIONAL",
                    "warning": COORDINATE_WARNING,
                    "interval": f"{interval_minutes} minutes",
                    "sites": timeline,
                })
                return

            site_id = query.get("site", [""])[0]
            time_string = query.get("datetime", [""])[0]

            if site_id not in SITES:
                raise ValueError("Choose site01 or site04.")

            if not time_string:
                raise ValueError("A UTC date and time are required.")

            observation_time = datetime.fromisoformat(time_string)

            if observation_time.tzinfo is None:
                observation_time = observation_time.replace(
                    tzinfo=timezone.utc
                )
            else:
                observation_time = observation_time.astimezone(
                    timezone.utc
                )

            site = SITES[site_id]

            sun = get_horizons_position(
                "10", site, observation_time
            )

            earth = get_horizons_position(
                "399", site, observation_time
            )

            self.send_json({
                "success": True,
                "site": site_id,
                "site_name": site["name"],
                "timestamp_utc": observation_time.isoformat(),
                "coordinates": {
                    "longitude_east_deg": site["longitude"],
                    "latitude_deg": site["latitude"],
                },
                "coordinate_status": "PROVISIONAL",
                "warning": COORDINATE_WARNING,
                "source": "NASA/JPL Horizons API",
                "sun": sun,
                "earth": earth,
            })

        except Exception as error:
            self.send_json({
                "success": False,
                "error": str(error),
            }, status=400)


if __name__ == "__main__":
    server = ThreadingHTTPServer(
        ("0.0.0.0", int(os.environ.get("PORT", "8001"))),
        LunaOpsHandler
    )

    print("LunaOps server running on port 8001")
    print("Open your Codespaces port 8001 in the browser.")
    print("Press Ctrl+C to stop the server.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLunaOps server stopped.")
        server.server_close()
