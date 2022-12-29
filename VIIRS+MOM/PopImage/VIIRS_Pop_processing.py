"""
    VIIRS_Pop_processing.py
        -- VIIRS addon to process pop addons
        -- inputs:
            -- HWRF 
            -- VIIRS images
            static data:
            -- pop image (tiff)
            -- maskgeojson (geojson)
            -- popcount.csv (pfaf_id,totalpop)
        -- impacted poplation
            -- in csv format: pfaf_id,totalpop, viirs_impactpop, viirs_impactpop_percent
        
        -- workflow:
            -- extract impacted watersheds list
                -- "Alert" = "Warning"
                -- "Flag" = 3: 1-HWRF 2-DFO 3-VIIRS
            -- estimate impacted population from VIIRS image
            -- popimpact.csv: pfaf_id, totalpop, viirs_impactpop, viirs_impactpop_percent
            -- generate a HWRF output
        
        -- file name setup
            -- Final_Attributes_2022122606HWRF+20221225DFO+20221225VIIRSUpdated.csv
                |_ Final_Attributes_2022122606HWRF+20221225DFO+20221225VIIRS_PopCount.csv: temporary, popcount  
                |_ Final_Attributes_2022122606HWRF+20221225DFO+20221225VIIRS_PopUpdated.csv: update MoM output with popcount
                |_ VIIRS_20221225_PopCount.csv: temporary, popcount for all impacted watersheds from different MoM output
"""


import json
import os
import sys
from typing import List

import pandas as pd
import rasterio
import settings
from rasterio.mask import mask

PopCount_header = ["pfaf_id", "totalpop", "viirs_impactpop", "viirs_impactpop_percent"]


def get_impacted_watersheds(hwrfoutput: str) -> List:
    """get impacted watershed list"""
    # load csv file
    df = pd.read_csv(hwrfoutput)
    # force id as int
    df["pfaf_id"] = df["pfaf_id"].astype(int)
    # drop duplicates
    df = df.drop_duplicates(subset=["pfaf_id"])

    # find impacted watersheds
    df = df[(df.Alert == "Warning") & (df.Flag == 3)]

    impact_list = df["pfaf_id"].values.tolist()

    return impact_list


def get_VIIRS_image_location() -> str:
    """return VIIRS image location"""

    afolder = settings.VIIRS_IMG_DIR

    return afolder


def get_VIIRS_image_date(hwrfoutput: str) -> str:
    """get the date of VIIRS image"""

    if "VIIRS" not in hwrfoutput:
        return ""

    apos = hwrfoutput.index("VIIRS")
    adate = hwrfoutput[apos - 8 : apos]
    return adate


def get_VIIRS_image(adate: str) -> List:
    """get VIIRS images from Final_Attributes_2022122618HWRF+20221225DFO+20221225VIIRSUpdated"""

    # find images
    # VIIRS_1day_composite20221225_flood.tiff
    # VIIRS_1day_composite20221225_flood.tiff
    viirs_1day = f"VIIRS_1day_composite{adate}_flood.tiff"
    viirs_5day = f"VIIRS_5day_composite{adate}_flood.tiff"

    viirs_folder = get_VIIRS_image_location()
    viirs_1day = os.path.join(viirs_folder, viirs_1day)
    viirs_5day = os.path.join(viirs_folder, viirs_5day)
    if os.path.exists(viirs_1day) & os.path.exists(viirs_5day):
        return [viirs_1day, viirs_5day]
    else:
        return []


def clip_image_bymask(tiffimage: str, mask_json: str, clippedimage: str):
    """generate clipped image by a mask"""

    with rasterio.open(tiffimage) as src:
        try:
            out_image, out_transform = mask(
                src, [mask_json["features"][0]["geometry"]], crop=True
            )
            out_meta = src.meta.copy()
        except ValueError as e:
            #'Input shapes do not overlap raster.'
            src = None
            area = 0
            # return empty dataframe
            return area
    out_meta.update(
        {
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        }
    )
    with rasterio.open(clippedimage, "w", **out_meta) as dest:
        dest.write(out_image)

    return


def count_impact_pop(wastershed_id: int, floodimages: List, working_dir: str) -> List:
    """count impacted population for a wastershed"""

    # make sure id is as str
    id_str = str(wastershed_id)

    # load geojson mask
    maskgeojson = os.path.join(settings.MASK_GEOJSON_DIR, f"{id_str}.geojson")
    with open(maskgeojson, "r") as f:
        the_mask = json.load(f)
    for fimage in floodimages:
        if "1day" in fimage:
            fimage_clipped = f"1day_{id_str}.tiff"
        else:
            fimage_clipped = f"5day_{id_str}.tiff"
        fimage_clipped = os.path.join(working_dir, fimage_clipped)
        print(fimage_clipped)
        print(fimage)
        clip_image_bymask(fimage, the_mask, fimage_clipped)

    return


def VIIRS_pop(hwrfoutput: str):
    """Extract impacted population from VIIRS image"""

    # get of the list of watersheds
    impact_list = get_impacted_watersheds(hwrfoutput=hwrfoutput)

    # get VIIRS image
    viirs_date = get_VIIRS_image_date(hwrfoutput=hwrfoutput)
    viirs_images = get_VIIRS_image(adate=viirs_date)

    if len(viirs_images) != 2:
        print("viirs image is not found: ", viirs_images)
        sys.exit()

    # make a temporary working folder
    temp_dir = os.path.join(settings.VIIRS_PROC_DIR, viirs_date)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # count impacted population for each watershed
    impact_pop_count_list = []
    for pfaf_id in impact_list[:1]:
        print("prcessing: ", pfaf_id)
        count_impact_pop(pfaf_id, viirs_images, temp_dir)
        totalpop = 100
        viirs_impactpop = 1
        viirs_impactpop_percent = viirs_impactpop / totalpop * 100.0
        impact_pop_count_list.append(
            [pfaf_id, totalpop, viirs_impactpop, viirs_impactpop_percent]
        )
    df = pd.DataFrame(impact_pop_count_list, columns=PopCount_header)
    tmp_output = os.path.basename(hwrfoutput).replace("Updated", "PopCount")
    popcount_tmp_output = os.path.join(settings.VIIRS_PROC_DIR, tmp_output)
    df.to_csv(popcount_tmp_output)


def main():
    """test code"""
    testhwrf = os.path.join(
        settings.HWRF_MOM_DIR,
        "Final_Attributes_2022122606HWRF+20221225DFO+20221225VIIRSUpdated.csv",
    )
    VIIRS_pop(hwrfoutput=testhwrf)


if __name__ == "__main__":
    main()
