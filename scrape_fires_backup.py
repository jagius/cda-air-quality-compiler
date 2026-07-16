# fetch the data from https://geoserver.cwfif.nrcan.gc.ca/geoserver/public/wfs?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0&TYPENAME=public:cwfif_national_activefires&PROPERTYNAME=(lat,lon,hectares,stage_of_control)&CQL_FILTER=NOT agency='ak' AND NOT agency='conus' AND NOT stage_of_control='OUT'&SRSNAME=urn:x-ogc:def:crs:EPSG:4326&OUTPUTFORMAT=csv and add a copy to the output directory
import pandas as pd
import os
# BASE SERVER URL HAS CHANGED TO  https://geoserver.cwfif.nrcan.gc.ca/
url = (
    "https://geoserver.cwfif.nrcan.gc.ca/geoserver/wfs?service=WFS&version=2.0.1&request=GetFeature&outputFormat=csv&typeNames=public:cwfif_national_activefires&sortBy=agency_code+A,record_start+D&CQL_FILTER=record_start%3C=now()%20AND%20record_end%3Enow()"
)

# first ensure the output directory exists
if not os.path.exists("output"):
    os.makedirs("output")

# try to read the CSV from the URL and save it
try:
    df = pd.read_csv(url)
    df.to_csv(os.path.join("output", "active_fires.csv"), index=False)
    print("Active fires data fetched and saved to output/active_fires.csv")
except Exception as e:
    print(f"Error fetching active fires data: {e}")