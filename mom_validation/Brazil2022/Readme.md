# Brazil 2022 Flash Flood
## 1. Research Area (watersheds)
The watersheds are selected by [the boundary of four states](Brazil_four_states.geojson) with 0.5 degree buffer zone.  
[research_watersheds.geojson](research_watersheds.geojson)  
[research_watersheds.csv](research_watersheds.csv)

Santa Catarina State, Rio de Janeiro State, Espirito Santo State, Parana State

## 2. Time Period 
[Brazil Flash Floods 2022](https://reliefweb.int/report/brazil/brazil-floods-and-landslides-inmet-civil-defense-santa-catarina-civil-defense-parana-floodlist-media-echo-daily-flash-6-december-2022) 
MoM outputs collected: **Nov 15 ~ Dec 15**
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
### 4. Some Sample plots of Severity
![641103_severity](https://user-images.githubusercontent.com/6643873/226226714-1c154f52-3b20-4b41-a06a-1784f1a97603.png)
![641106_severity](https://user-images.githubusercontent.com/6643873/226226821-34c0dd01-849a-4042-9aac-c5c5c43f475c.png)

### 5. Maps
![2022112700](https://user-images.githubusercontent.com/6643873/226227042-49a44c80-1006-484a-9ddf-03df07ffc9cd.png)
![2022121200](https://user-images.githubusercontent.com/6643873/226227802-52158b78-4380-48e0-bcea-7a4d529ea501.png)


### 6. Animation
![mymap](https://user-images.githubusercontent.com/6643873/226226499-f585af4b-94ce-4ff9-b77f-080333c37343.gif)
