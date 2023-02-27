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
![2022060100](https://user-images.githubusercontent.com/6643873/221620098-7a4c60b8-aea2-4e37-81be-4f1000982e79.png)
![2022061600](https://user-images.githubusercontent.com/6643873/221620207-53765c6a-7f85-4e32-a0f4-e545e11cb29e.png)
![2022062600](https://user-images.githubusercontent.com/6643873/221620251-f1f437df-753f-4ff2-8f82-b17a8d1dd4a2.png)
![2022071100](https://user-images.githubusercontent.com/6643873/221620280-76aca426-beaf-4287-aa4b-8b6eced83aae.png)
![2022072600](https://user-images.githubusercontent.com/6643873/221620293-d44b22d7-f14d-4380-8753-b316edff11d9.png)
![2022081000](https://user-images.githubusercontent.com/6643873/221620322-7c5bd3f8-fc7e-45cf-9af5-2ada9e7d4f55.png)
![2022082500](https://user-images.githubusercontent.com/6643873/221620341-e9f18a05-4c4f-471b-b4e4-b04622822c1b.png)
![2022090900](https://user-images.githubusercontent.com/6643873/221620361-efbe00bd-f571-45b8-9628-efdba105fcb1.png)
![2022092400](https://user-images.githubusercontent.com/6643873/221620387-7f825919-9fda-4215-af0e-187b7cbfae19.png)
![2022100900](https://user-images.githubusercontent.com/6643873/221620429-ec02bc93-ac59-4d87-b5e4-9cce761341bd.png)
![2022101900](https://user-images.githubusercontent.com/6643873/221620449-04826ac1-0c6e-4280-92d8-a272ae243e9a.png)
![2022102900](https://user-images.githubusercontent.com/6643873/221620458-90d11cc3-1b6a-4f9b-905b-55d57ec0d3ac.png)
### Animation (every 5th day)
![map](https://user-images.githubusercontent.com/6643873/221635312-1169636e-fa0a-4ed6-a2b8-a0666e233f35.gif)
