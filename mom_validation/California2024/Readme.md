# California flood: 2024 February
## 1. Research Area (watersheds)
The watersheds are selected by [the boundary of California](California_boundary.geojson) with 0.5 degree buffer zone.  
[research_watersheds.geojson](research_watersheds.geojson)  
[research_watersheds.csv](research_watersheds.csv)
## 2. Time Period 
[2024 February California floods](https://www.weather.gov/mtr/AtmosphericRiver-February_3-5_2024):  Atmospheric River - February 3-5, 2024 Heavy Rains and Damaging Winds Impacted the Bay Area and the Central Coast.  
MoM outputs collected: **2024 January 30 ~ 2024 February 10**
## 3. MoM Outputs

```
|-----------------date-------------------
|
pfaf_id           value
|
```
[momoutput_Severity.csv](momoutput_Severity.csv): Severity value of the watershed based on Hazard_Score and maximum of Scaled_Riverine_Risk and Scaled_Coastal_Risk    
[momoutput_Flag.csv](momoutput_Flag.csv): Flag (1 2 and 3) for the updated hazard score due to HWRF DFO and VIIRS respectively   
[momoutput_Alert.csv](momoutput_Alert.csv): Flood alert generated for the watershed based on the Severity 
* 0.00 ~ 0.35: Information
* 0.35 ~ 0.60: Advisory
* 0.60 ~ 0.80: Watch
* 0.80 ~ 1.00: Warning 
## 4 .Some Sample plots of Severity
![774140_severity](https://user-images.githubusercontent.com/6643873/227825523-3d8f71b8-3feb-4130-8b64-b33db130f0c3.png)
![773303_severity](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/493d9a5e-15c4-449c-a357-d5560ee5304b)

## 5 .Some Sample maps
![2022122800](https://user-images.githubusercontent.com/6643873/227826042-f14de321-f5c1-46df-933c-fd2dd5f90df1.png)

## 6. Animation



