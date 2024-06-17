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
![773207_severity](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/43886585-1166-46a6-9e10-c3244f78521c)
![773303_severity](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/493d9a5e-15c4-449c-a357-d5560ee5304b)
![774150_severity](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/0eda2096-d23d-44f6-abbf-b96088154a93)

## 5 .Some Sample maps
![2024013100](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/7949ba92-ebd7-4cd9-8e70-0da236135ee5)
![2024020100](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/15141a1b-cc18-4a26-971d-0f6b7c90ab0c)
![2024020200](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/3a6b56b6-3222-4eec-974e-bd38ef6cc6a5)
![2024020300](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/0de3d63e-0694-4ac5-ac45-989e64f9ec41)
![2024020400](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/497eebbd-0cad-472b-9d1e-4d976101bcaa)
![2024020500](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/fe020b2f-e468-4e8d-90be-8c2ef2406da4)
![2024020600](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/6a68b42e-0a1f-45d6-b430-cf5c1a84e35d)
![2024020700](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/47473d60-8905-413c-aa0e-ed76b3160c7c)
![2024020800](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/f10222e2-e98d-4cfc-b03d-f8a6cdd643fa)

## 6. Animation
![my map](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/d0260434-1a42-4ecb-885b-84f03f2c1ad5)



