# Bangladesh flood: 2022–2023
## 1. Research Area (watersheds)
The watersheds are selected by [the boundary of Bangladesh](Bangladesh_boundary.geojson) with 0.5 degree buffer zone.  
[research_watersheds.geojson](research_watersheds.geojson)  
[research_watersheds.csv](research_watersheds.csv)
## 2. Time Period 
[Millions in Bangladesh impacted by floods](https://www.ifrc.org/press-release/millions-bangladesh-impacted-one-worst-floodings-ever-seen)     
MoM outputs collected: **2022 May 01 ~ 2022 July 31**
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
## 4. Some Sample plots of Severity
![451005_severity](https://user-images.githubusercontent.com/6643873/228069942-46239216-779f-42f8-bbcf-cf13fc94cd72.png)
![452530_severity](https://user-images.githubusercontent.com/6643873/228070128-cbef73ba-d763-4e69-89ef-a51743674c64.png)
![452203_severity](https://user-images.githubusercontent.com/6643873/228070333-14ce97ca-49a9-4945-b56e-4847ae116230.png)
![451009_severity](https://user-images.githubusercontent.com/6643873/228070468-fb178e6a-2f32-4c1c-8d8a-cd5614c3f85e.png)

## 5. Sample Maps

## 6. Animation
