# fetch the data from https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wfs?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0&TYPENAME=public:activefires_current&PROPERTYNAME=(lat,lon,hectares,stage_of_control)&CQL_FILTER=NOT agency='ak' AND NOT agency='conus' AND NOT stage_of_control='OUT'&SRSNAME=urn:x-ogc:def:crs:EPSG:4326&OUTPUTFORMAT=csv and add a copy to the output directory
import pandas as pd
import os

url = "https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wfs?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0&TYPENAME=public:activefires_current&PROPERTYNAME=(lat,lon,hectares,stage_of_control)&CQL_FILTER=NOT agency='ak' AND NOT agency='conus' AND NOT stage_of_control='OUT'&SRSNAME=urn:x-ogc:def:crs:EPSG:4326&OUTPUTFORMAT=csv"

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