# MoM Outputs for 2022 Pakistan Flood
## 1. Research Area (watersheds)
The watersheds are selected by [the boundary of Pakistan](../Pakistan_boundary.geojson) with 0.5 degree buffer zone.  
[research_watersheds.geojson](research_watersheds.geojson)  
[research_watersheds.csv](research_watersheds.csv)
## 2. Time Period 
[Plaostam Floods 2022](https://en.wikipedia.org/wiki/2022_Pakistan_floods): From 14 June to October 2022   
MoM outputs collected: **June 1 ~ October 31**
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
### Some Sample plots of Severity
old plots for Aug 1 to Aug 31, need to be updated  
![plot1](https://user-images.githubusercontent.com/6643873/219760667-bc9944a9-a357-4bfb-b1e3-58ca77205d78.png)
![plot4](https://user-images.githubusercontent.com/6643873/219760748-edd4b7d2-6f73-43bb-bc35-8bee4e1d8013.png)
![plot2](https://user-images.githubusercontent.com/6643873/219760909-c2f90f15-c845-496f-8c06-aeb5b682dd2d.png)
![plot3](https://user-images.githubusercontent.com/6643873/219760952-4f0bcff3-291b-483e-a47e-445502b86280.png)

## 4. GeoJSON Outputs
For each date, two geojsons are generated: YYYYMMDDHH_Warning.geojson (Alert="Warning") and YYYYMMDDHH_Watch.geojson (Alert="Watch")  
Only "00" hours are uploaded to github.  
Example:  
[2022081000_Warning.geojson](geojson/2022081000_Warning.geojson)  
[2022081000_Watch.geojson](geojson/2022081000_Watch.geojson) 
### Maps
