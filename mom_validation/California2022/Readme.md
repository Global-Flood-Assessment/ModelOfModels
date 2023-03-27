# California flood: 2022–2023
## 1. Research Area (watersheds)
The watersheds are selected by [the boundary of California](California_boundary.geojson) with 0.5 degree buffer zone.  
[research_watersheds.geojson](research_watersheds.geojson)  
[research_watersheds.csv](research_watersheds.csv)
## 2. Time Period 
[2022–2023 California floods](https://en.wikipedia.org/wiki/2022%E2%80%932023_California_floods):  a series of atmospheric rivers from 2022 December 31 to 2023 January 25.  
MoM outputs collected: **2022 December 15 ~ 2023 February 15**
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
![774300_severity](https://user-images.githubusercontent.com/6643873/227825556-f8a314ed-9bd7-4f8f-b91e-21e9709274e5.png)
![773309_severity](https://user-images.githubusercontent.com/6643873/227825859-034a45ec-ba91-4385-bc90-d0869474aec5.png)
## 5 .Some Sample maps
![2022122800](https://user-images.githubusercontent.com/6643873/227826042-f14de321-f5c1-46df-933c-fd2dd5f90df1.png)
![2023010300](https://user-images.githubusercontent.com/6643873/227826155-2f5b9901-8453-4b54-8727-02eaf1737ca3.png)
![2023010900](https://user-images.githubusercontent.com/6643873/227826195-794f9078-6587-43d1-b43f-3de7ffdfa93a.png)
![2023011100](https://user-images.githubusercontent.com/6643873/227826300-e200d192-cb41-4aec-ac7c-96b7f22429ce.png)

## 6. Animation
![mymap](https://user-images.githubusercontent.com/6643873/227825364-29da9d36-41ba-40f1-953b-cf2aa3866663.gif)



