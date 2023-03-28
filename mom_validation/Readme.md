# MoM output
* **research_watersheds.csv**       
list of watersheds
* **research_watersheds.geojson**   
watersheds boundaries in geojson
* **[name]_boundary.geojson**  
Amin boundary to select the watersheds  

## MoM outputs
* **momoutput_Severity.csv**  
Severity value of each watershed based on Hazard_Score and maximum of Scaled_Riverine_Risk and Scaled_Coastal_Risk
* **momoutput_Alert.csv**  
Flood alert generated for the watershed based on the severity value

    0.00 ~ 0.35: Information  
    0.35 ~ 0.60: Advisory  
    0.60 ~ 0.80: Watch  
    0.80 ~ 1.00: Warning  

* **momoutput_Flag.csv**  
Flag (1 2 and 3) for the updated hazard score due to HWRF DFO and VIIRS respectively

## SubFolders:
* **severityplot**  
Plot of the severity value vs date for each watersheds 
* **geojson**  
Daily outputs for watersheds marked as Warning or Watch: YYYYMMDD00_Warning.geojson, YYYYMMDD00_Watch.geojson
* **mapimage**  
Map plots generated with daily warning and watch geojsons.


