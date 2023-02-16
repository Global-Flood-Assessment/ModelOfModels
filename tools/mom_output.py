"""
    mom_output.py
        -- extract output from mom
    paramters:
        -- pfafidlist: a csv file has pfaf_id column
        -- timeperiod: YYYYMMDD-YYYYMMDD
    output:
        -- wastersheds.geojson: wastersheds in the list
        -- two geojsons for each PDC_final output:
            -- Warning
            -- Watch
        -- CSV output:
            -- header: pfaf_id, [dates]
            -- value: pfaf_id, [Severity] 
"""
