# fetch the data from https://geoserver.cwfif.nrcan.gc.ca/geoserver/public/wfs?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0&TYPENAME=public:cwfif_national_activefires&PROPERTYNAME=(lat,lon,hectares,stage_of_control)&CQL_FILTER=NOT agency='ak' AND NOT agency='conus' AND NOT stage_of_control='OUT'&SRSNAME=urn:x-ogc:def:crs:EPSG:4326&OUTPUTFORMAT=csv and add a copy to the output directory
import pandas as pd
import os
# BASE SERVER URL HAS CHANGED TO  https://geoserver.cwfif.nrcan.gc.ca/
url = (
    "https://geoserver.cwfif.nrcan.gc.ca/geoserver/wfs?service=WFS&version=2.0.1&request=GetFeature&outputFormat=csv&typeNames=public:cwfif_national_activefires&sortBy=agency_code+A,record_start+D&CQL_FILTER=record_start%3C=now()%20AND%20record_end%3Enow()"
)

#fire data column headers: FID,id,agency_code,region_code,national_fire_id,agency_fire_id,national_fire_cause,fire_type_ics,severity_nearest_dsr,fire_was_prescribed,percent_contained,fire_size,response_type,stage_of_control_status,situation_report_date,status_date,latitude,longitude,geometry,fire_year,status_year,record_start,record_end
#agency codes would be one of the following from the province/territory codes: bc, ab, sk, mb, on, qc, nb, ns, pe, nl, yt, nt, nu
provinces = ["bc", "ab", "sk", "mb", "on", "qc", "nb", "ns", "pe", "nl", "yt", "nt", "nu"]
# first ensure the output directory exists
if not os.path.exists("output"):
    os.makedirs("output")

# try to read the CSV from the URL and save it
try:
    df = pd.read_csv(url)
    df.to_csv(os.path.join("output", "active_fires.csv"), index=False)
    print("Active fires data fetched and saved to output/active_fires.csv")

    # output a CSV per agency_code
    for code in df["agency_code"].dropna().unique():
        filtered = df[df["agency_code"] == code]
        filename = f"active_fires_{code.lower()}.csv"
        filtered.to_csv(os.path.join("output", filename), index=False)
        print(f"  Saved {len(filtered)} rows for agency '{code}' -> output/{filename}")
except Exception as e:
    print(f"Error fetching active fires data: {e}")