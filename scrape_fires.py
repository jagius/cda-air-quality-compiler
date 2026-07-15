import os
import socket
import ssl
import time
from io import StringIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

BASE_WFS_URL = "https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wfs"
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3
SSL_CONTEXT = ssl._create_unverified_context()

# Try the legacy layer first, then fall back to a currently available layer.
QUERY_CANDIDATES = [
    {
        "TYPENAME": "public:activefires_current",
        "PROPERTYNAME": "lat,lon,hectares,stage_of_control",
        "CQL_FILTER": "NOT agency='ak' AND NOT agency='conus' AND NOT stage_of_control='OUT'",
    },
    {
        "TYPENAME": "public:hotspots_last24hrs",
        "PROPERTYNAME": "lat,lon,estarea,agency",
        "CQL_FILTER": "NOT agency='ak' AND NOT agency='conus'",
    },
]


def build_url(candidate):
    params = {
        "SERVICE": "WFS",
        "REQUEST": "GetFeature",
        "VERSION": "2.0.0",
        "OUTPUTFORMAT": "csv",
        "SRSNAME": "urn:x-ogc:def:crs:EPSG:4326",
        **candidate,
    }
    return f"{BASE_WFS_URL}?{urlencode(params)}"


def fetch_csv_text(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS, context=SSL_CONTEXT) as response:
                return response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, socket.timeout, TimeoutError) as err:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"Request failed for {url}: {err}") from err
            print(
                f"Attempt {attempt}/{MAX_RETRIES} failed: {err}. "
                f"Retrying in {RETRY_DELAY_SECONDS}s...",
                flush=True,
            )
            time.sleep(RETRY_DELAY_SECONDS)


def normalize_columns(df):
    if "hectares" not in df.columns and "estarea" in df.columns:
        df["hectares"] = df["estarea"]
    if "stage_of_control" not in df.columns:
        df["stage_of_control"] = "Unknown"

    required = ["lat", "lon", "hectares", "stage_of_control"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise RuntimeError(f"Missing required columns in fire data: {', '.join(missing)}")

    output = df[required].copy()
    output["hectares"] = pd.to_numeric(output["hectares"], errors="coerce")
    return output


os.makedirs("output", exist_ok=True)

last_error = None
for candidate in QUERY_CANDIDATES:
    url = build_url(candidate)
    print(f"Trying fire source: {candidate['TYPENAME']}", flush=True)
    try:
        csv_text = fetch_csv_text(url)
        raw_df = pd.read_csv(StringIO(csv_text))
        df = normalize_columns(raw_df)
        df.to_csv(os.path.join("output", "active_fires.csv"), index=False)
        print(
            f"Active fires data fetched using {candidate['TYPENAME']} and saved to output/active_fires.csv",
            flush=True,
        )
        last_error = None
        break
    except Exception as err:
        last_error = err
        print(f"Source {candidate['TYPENAME']} failed: {err}", flush=True)

if last_error is not None:
    raise RuntimeError(f"All fire sources failed. Last error: {last_error}")