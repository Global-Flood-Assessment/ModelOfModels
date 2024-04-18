# Louisiana 2022 Flood
## 1. Research Area (watersheds)
The watersheds are selected by [the boundary of Louisiana State](Louisiana_State.geojson) with 0.2 degree buffer zone.  
[research_watersheds.geojson](research_watersheds.geojson)  
[research_watersheds.csv](research_watersheds.csv)

## 2. Time Period
**2024 April 7 ~ 2024 April 13**
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
## 4. Plots of Severity

## 5. Maps
![2024040600](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/6a0ef5f8-d08c-49df-ba71-feba6f645572)
![2024040700](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/aac87d44-e46d-42ad-8025-0f59b9bedc98)
![2024040800](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/467838ad-482f-4497-8b83-956648c4ce5b)
![2024040900](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/72c1d196-0a62-48d3-8372-cb8a36a4f98b)
![2024041000](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/73258d66-88f6-4d34-8b7d-338b134bf7cf)
![2024041100](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/be80ec73-d549-456c-be89-b6803ffbab07)
![2024041200](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/2b6feddf-4727-4f3b-8200-cb79d488cf84)
![2024041300](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/5ed8456a-f2dc-4945-b2b7-b45dd418dea3)

## 6. Animation
![mymap](https://github.com/Global-Flood-Assessment/ModelOfModels/assets/6643873/9f3262f9-31f7-4f99-b934-0deafa34e7a1)
