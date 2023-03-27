# Philipines flood 2022
## 1. Research Area (watersheds)
The watersheds are selected by [the boundary of impacted provinces](impacted_provinces.geojson) with 0.1 degree buffer zone.  
[research_watersheds.geojson](research_watersheds.geojson)  
[research_watersheds.csv](research_watersheds.csv)  
Impacted provinces: Antique, Camarines Sur, Capiz, Cebu, Maguindanao del Norte, Negros Occidental, Southern Leyte
## 2. Time Period 
[Philippines – Floods and Landslides Triggered by Tropical Storm Nalgae](https://floodlist.com/asia/philippines-floods-storm-nalgae-october-2022)    
MoM outputs collected: **2022 October 15 ~ 2022 November 25**
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
![524028_severity](https://user-images.githubusercontent.com/6643873/228054392-b16c12e5-8c3b-4745-8ee9-cefd4a0fe206.png)
![524043_severity](https://user-images.githubusercontent.com/6643873/228054442-5483981a-9327-4b58-b198-22bc5aa18efa.png)
![524044_severity](https://user-images.githubusercontent.com/6643873/228054583-7aced294-a4c0-43e4-b218-a857acefc829.png)
![524047_severity](https://user-images.githubusercontent.com/6643873/228054604-87db77a8-c1d9-4b3c-9400-41f13537bd03.png)
## 5. Sample Maps
![2022102300](https://user-images.githubusercontent.com/6643873/228055070-49b9545e-d9f2-4b89-a91e-10e45c127125.png)
![2022102700](https://user-images.githubusercontent.com/6643873/228055122-0cb5bf93-d9a5-4c5a-8796-73a9378de885.png)
![2022103100](https://user-images.githubusercontent.com/6643873/228055195-56d058c3-941f-4936-ab62-7f0e5ef76518.png)
![2022110400](https://user-images.githubusercontent.com/6643873/228055369-f86290b4-68d6-445c-9eb4-bcef25ce4e57.png)

## 6. Animation
![mymap](https://user-images.githubusercontent.com/6643873/228054838-266a126a-426d-47c2-b9b7-fedf8ec35998.gif)



