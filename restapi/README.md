# Model of Models Data API

## Basic call format:
```
https://momserver/api/v1/data?[parameters]
```
## Parameters
| Parameter | Description | Possible Values
| --- | --- | --- |
| **product** | product type | HWRF, VIIRS
| **date** | date | for HWRF: YYYYMMDD00, YYYYMMDD06,YYYYMMDD12,YYYYMMDD18<br>for VIIRS: YYYYMMDD |
| **format** | output data format | csv, geojson, kml |

## Sample call:
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

Get a GeoJSON file:
```
https://momserver/api/v1/data?product=HWRF&date=2021083118&format=geojson
```
Output: HWRF_2021083118.geojson

GeoJSON file visualized on ArcGIS online