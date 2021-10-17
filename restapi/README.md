# Model of Models Data API

## Data Products:
| Data | Resolution | Updated | Download Source |
| --- | --- | --- | --- |
| **HWRF** | 6km | Updated evey 6 hour for the forecasted tropical cyclone | https://www.emc.ncep.noaa.gov/gc_wmb/vxt/HWRF/about.php?branch=link|
| **DFO** | 250m | Updated daily, 1-day lag | https://floodmap.modaps.eosdis.nasa.gov/index.php |
| **VIIRS** | 375m | Updated daily, 1-day lag | https://www.ssec.wisc.edu/flood-map-demo/ftp-link |

## Basic API format:
```
https://momserver/api/v1/data?[parameters]
```

## Parameters:
| Parameter | Description | Possible Values
| --- | --- | --- |
| **product** | product type | HWRF, DFO, VIIRS
| **date** | date | for HWRF: YYYYMMDD00, YYYYMMDD06,YYYYMMDD12,YYYYMMDD18<br>for VIIRS: YYYYMMDD<br>for DFO: YYYYMMDD<br>**date=latest**: return the lastest data|
| **format** | output data format | csv, geojson, kml |

## Samples:
momsever need to be replaced with the real url

Get a CVS file
```
https://momserver/api/v1/data?product=HWRF&date=2021083118&format=csv
```
Output: HWRF_2021083118.csv
```
pfaf_id,FID,area_km2,ISO,Admin0,Admin1,rfr_score,cfr_score,Resilience_Index, NormalizedLackofResilience ,Alert
171000,3130.0,16410.89801,EGY,Egypt,Al Buhayrah,4.000368882,3.233220159,0.55,0.63,Warning
172111,3132.0,25391.76841,EGY,Egypt,Bani Suwayf,3.367829483,0.004255481,0.55,0.63,Warning
172115,3136.0,12900.15886,EGY,Egypt,Suhaj,3.693633873,0.0,0.55,0.63,Warning
172117,3138.0,37158.6911,EGY,Egypt,Aswan,4.012574421,0.0,0.55,0.63,Warning
172118,3139.0,21418.92802,EGY,Egypt,Al Bahr al Ahmar,4.166583258,0.0,0.55,0.63,Warning
172119,3140.0,19719.32651,EGY,Egypt,Aswan,4.230900174,0.0,0.55,0.63,Warning
162899,3104.0,12341.2055,SDN,Sudan,Central Darfur,4.019782449,0.0,0.28,1.0,Warning
162963,3120.0,161.5947307,SDN,Sudan,West Darfur,4.053413388,0.0,172170,3180.0,4682.198393,SDN,Sudan,Northern,4.127484219,0.0,0.28,1.0,Warning
...
```
Get a KML file:
```
https://momserver/api/v1/data?product=HWRF&date=2021083118&format=kml
```
Output: HWRF_2021083118.kml

KML file visualized on Google Earth

![googleearth](https://user-images.githubusercontent.com/6643873/134942937-e49fdf25-7332-48e8-9a01-5ba69017847d.png)

Get a GeoJSON file:
```
https://momserver/api/v1/data?product=HWRF&date=2021083118&format=geojson
```
Output: HWRF_2021083118.geojson

GeoJSON file visualized on ArcGIS online

![arcgisonline](https://user-images.githubusercontent.com/6643873/134942995-0494c5c2-41cc-4f50-938d-26df9781db5e.png)

