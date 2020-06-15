Flood_Severity_Calculation.py calculates the flood severity of  watershed (with pfaf_id) based on the following data which is fed to the code using different csv files

1. GFMS data (Area of flooded watershed, percent of flooded area,  max depth of flood above threshold, mean depth of flood above threshold and duration of flooding)
The code reads csv file and the  Header must follow the following order of fields from (left to right)(please note "fieldname" doesn't matter but the order of field does as the code read data based on column index):
pfaf_id		GFMS_TotalArea_km 	GFMS_%Area 	GFMS_MeanDepth 	GFMS_MaxDepth 	GFMS_Duration

2.  GloFas data: The Header must follow the following order of fields from (left to right)(please note "fieldname" doesn't matter but the order of field does as the code read data based on column index):

Point_No 	Station 	Basin 		Country		Lat	Lon	Upstream_area	Forecast_Date 	max_EPS 	GloFAS_2yr	GloFAS_5yr	GloFAS_20y	Alert_level 	Days_until_peak 	pfaf_id

3. Attributes: This is the attribute table of the watershed shapefile used. Must contain the exact fieldname but order doesn't matter:

pfaf_id		ISO	Admin0	Admin1	rfr_score	cfr_score	

4. Copy of Resilience_index: This is the csv file with Countries' lack of Resilience Index, Normalized Lack of resilience , vulnerbility index and so on. For now, "NormalizedLackofResilience" is only used from this file and field name should be the same. This will be updated every year and is obtained from the PDC.

5. Weightage: This is the csv file provided with limit criteria/ initial weightage for attribute values and max and minimum score provided to GFMS and GloFas attributes.  

The code will gie us three Csv Files as result:
1. Final Attributes
2. Attributes_clean
3. GloFas_Error:  If any attributes of station from the GloFas have error in it. That data of that particular station data will be skipped and then, the number, the name of station, associated watershed id and the first encountered error will be listed row wise. 