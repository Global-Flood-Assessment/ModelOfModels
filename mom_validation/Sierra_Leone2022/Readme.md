# MoM Outputs for 2022 Sierra Leone Flood
[Sierra Leone: Flash Floods - Aug 2022](https://reliefweb.int/disaster/ff-2022-000309-sle)  
## 1. Research Area (watersheds) 
The watersheds are selected by [the boundary of Sierra Leone](Sierra_Leone_boundary.geojson) with 0.5 degree buffer zone.  
[research_watersheds.geojson](research_watersheds.geojson)  
[research_watersheds.csv](research_watersheds.csv)
## 2. Time Period 
MoM outputs collected: **Auguest 1 ~ September 31**
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
### Plots of Severity
![142988_severity](https://user-images.githubusercontent.com/6643873/224601956-a2dbe042-7d7b-4f6f-bf20-e3e1c94c8269.png)
![142989_severity](https://user-images.githubusercontent.com/6643873/224601959-0a74b96a-0612-4a0a-97e7-1d31ede84e24.png)
![145750_severity](https://user-images.githubusercontent.com/6643873/224601960-36b9207e-df2d-4337-803a-080441f6b473.png)
![145760_severity](https://user-images.githubusercontent.com/6643873/224601961-62ff5447-9848-4f3f-bf5e-97d1c2e27c98.png)
![145771_severity](https://user-images.githubusercontent.com/6643873/224601963-1fa2b0ca-b7e2-40b2-9c21-3cff45dcfe3f.png)
![145772_severity](https://user-images.githubusercontent.com/6643873/224601965-c5c1056b-d500-42b7-b460-f4a46be003b4.png)
![145773_severity](https://user-images.githubusercontent.com/6643873/224601967-57ca6180-45ea-4f2a-8ce8-ec56491fae5a.png)
![145774_severity](https://user-images.githubusercontent.com/6643873/224601972-e01894d3-c604-44df-b5c8-71267f9e5efc.png)
![145775_severity](https://user-images.githubusercontent.com/6643873/224601973-8c5c63d9-05df-45b1-95f5-3f0a9708bb67.png)
## 4. GeoJSON Outputs
For each date, two geojsons are generated: YYYYMMDDHH_Warning.geojson (Alert="Warning") and YYYYMMDDHH_Watch.geojson (Alert="Watch")  
Only "00" hours are uploaded to github.  
Example:  
[2022082800_Warning.geojson](geojson/2022082900_Warning.geojson)  
[2022082800_Watch.geojson](geojson/2022082900_Watch.geojson) 
### Maps

### Animation (every 5th day)
