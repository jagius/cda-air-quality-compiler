# fetch the data from https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wfs?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0&TYPENAME=public:activefires_current&PROPERTYNAME=(lat,lon,hectares,stage_of_control)&CQL_FILTER=NOT agency='ak' AND NOT agency='conus' AND NOT stage_of_control='OUT'&SRSNAME=urn:x-ogc:def:crs:EPSG:4326&OUTPUTFORMAT=csv and add a copy to the output directory
import pandas as pd
import os
import time
import socket
from io import StringIO
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

url = (
    "https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wfs"
    "?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0"
    "&TYPENAME=public%3Aactivefires_current"
    "&PROPERTYNAME=lat%2Clon%2Chectares%2Cstage_of_control"
    "&CQL_FILTER=NOT%20agency%3D%27ak%27%20AND%20NOT%20agency%3D%27conus%27%20AND%20NOT%20stage_of_control%3D%27OUT%27"
    "&SRSNAME=urn%3Ax-ogc%3Adef%3Acrs%3AEPSG%3A4326"
    "&OUTPUTFORMAT=csv"
)

REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3

# first ensure the output directory exists
if not os.path.exists("output"):
    os.makedirs("output")

request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

for attempt in range(1, MAX_RETRIES + 1):
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            csv_text = response.read().decode("utf-8", errors="replace")
        df = pd.read_csv(StringIO(csv_text))
        df.to_csv(os.path.join("output", "active_fires.csv"), index=False)
        print("Active fires data fetched and saved to output/active_fires.csv", flush=True)
        break
    except (HTTPError, URLError, socket.timeout, TimeoutError, ValueError) as e:
        if attempt == MAX_RETRIES:
            raise RuntimeError(f"Error fetching active fires data after {MAX_RETRIES} attempts: {e}") from e
        print(
            f"Attempt {attempt}/{MAX_RETRIES} failed while fetching fire data: {e}. "
            f"Retrying in {RETRY_DELAY_SECONDS}s...",
            flush=True,
        )
        time.sleep(RETRY_DELAY_SECONDS)