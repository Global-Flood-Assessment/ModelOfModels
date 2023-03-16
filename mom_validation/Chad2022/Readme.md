# Chad 2022 Flood
## 1. Research Area (watersheds)
The watersheds are selected by [the boundary of Chad south region](Chad_south_boundary.geojson) with 0.5 degree buffer zone.  
[research_watersheds.geojson](research_watersheds.geojson)  
[research_watersheds.csv](research_watersheds.csv)

## 2. Time Period
[Chad Flood 2022](https://en.wikipedia.org/wiki/2022_Chad_floods)
**2022 July 1 ~ 2022 December 31**
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
## 6. Animation
![mymap](https://user-images.githubusercontent.com/6643873/225654167-adcdf51a-9027-4e2f-89e8-2c37dca3f65e.gif)
