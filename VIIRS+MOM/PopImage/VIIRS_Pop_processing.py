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
            -- in csv format: pfaf_id,Totalpop, VIIRS_impactpop, VIIRS_impactpop_percent
        
        -- workflow:
            -- extract impacted watersheds list
                -- "Alert" = "Warning"
                -- "Flag" = 3: 1-HWRF 2-DFO 3-VIIRS
            -- estimate impacted population from VIIRS image
            -- popimpact.csv: pfaf_id, Totalpop, VIIRS_impactpop, VIIRS_impactpop_percent
            -- generate a HWRF output
        
        -- file name setup
            -- Final_Attributes_2022122606HWRF+20221225DFO+20221225VIIRSUpdated.csv
                |_ Final_Attributes_2022122606HWRF+20221225DFO+20221225VIIRS_PopCount.csv: temporary, popcount  
                |_ Final_Attributes_2022122606HWRF+20221225DFO+20221225VIIRS_PopUpdated.csv: update MoM output with popcount
                |_ VIIRS_20221225_PopCount.csv: temporary, popcount for all impacted watersheds from different MoM output
"""


import glob
import json
import os
import shutil
import sys
from typing import List

import numpy as np
import pandas as pd
import rasterio
import settings
from rasterio.mask import mask

PopCount_header = ["pfaf_id", "Totalpop", "VIIRS_impactpop", "VIIRS_impactpop_percent"]


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


def generate_popcountimage(
    viirs_image: str, pop_image: str, popcount_image: str, image_size: List
):
    """generate popcount image"""

    # generate binary image

    binary_image = viirs_image.replace(".", "_binary.")
    cmd = f'gdal_calc.py -A {viirs_image} --calc="(A<=140)*0 + logical_and(A>140, A<201)*1 + (A>=201)*0" --outfile {binary_image} > /dev/null'
    os.system(cmd)
    # resize binary image
    resize_image = binary_image.replace(".", "_resize.")
    xsize, ysize = image_size
    cmd = f"gdal_translate -of GTiff -outsize {xsize} {ysize} {binary_image} {resize_image} > /dev/null"
    os.system(cmd)
    # calculate A*B
    cmd = f'gdal_calc.py -A {resize_image} -B {pop_image} --calc="A*B" --outfile {popcount_image}  > /dev/null'
    os.system(cmd)

    return


def count_impact_pop(wastershed_id: int, floodimages: List, working_dir: str) -> int:
    """count impacted population for a wastershed"""

    # make sure id is as str
    id_str = str(wastershed_id)

    # load geojson mask
    maskgeojson = os.path.join(settings.MASK_GEOJSON_DIR, f"{id_str}.geojson")
    with open(maskgeojson, "r") as f:
        the_mask = json.load(f)

    # find popimage size
    pop_image = os.path.join(settings.POP_IMAGE_DIR, f"{id_str}_pop.tiff")
    pop_raster = rasterio.open(pop_image)
    ysize, xsize = pop_raster.shape

    popcountimage_list = []
    for fimage in floodimages:
        if "1day" in fimage:
            fimage_clipped = f"1day_{id_str}.tiff"
        else:
            fimage_clipped = f"5day_{id_str}.tiff"
        fimage_clipped = os.path.join(working_dir, fimage_clipped)
        # clip viirs image with the mask
        clip_image_bymask(fimage, the_mask, fimage_clipped)
        # generate population count image
        popcount_image = fimage_clipped.replace(".tiff", "_popcount.tiff")
        generate_popcountimage(
            fimage_clipped, pop_image, popcount_image, [xsize, ysize]
        )
        popcountimage_list.append(popcount_image)

    tempcount_list = []
    for countimage in popcountimage_list:
        src = rasterio.open(countimage)
        data = src.read(1)
        impact_popcount = int(np.sum(data, where=(data != src.nodata)))
        tempcount_list.append(impact_popcount)
    finalcount = max(tempcount_list)

    # remove files immediatelly
    tmpimage_list = glob.glob(os.path.join(working_dir, f"*{id_str}*.tiff"))
    for tmptiff in tmpimage_list:
        try:
            os.remove(tmptiff)
        except:
            continue

    return finalcount


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

    # read total population
    pop_df = pd.read_csv(settings.POP_COUNT_CSV)

    # check if it is pre-calucated
    adate_popcount = f"{viirs_date}_popcount.csv"
    adate_popcount = os.path.join(settings.VIIRS_PROC_DIR, adate_popcount)
    if os.path.exists(adate_popcount):
        check_flag = True
        adate_df = pd.read_csv(adate_popcount)
    else:
        check_flag = False

    # make a temporary working folder
    temp_dir = os.path.join(settings.VIIRS_PROC_DIR, viirs_date)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # count impacted population for each watershed
    impact_pop_count_list = []
    for pfaf_id in impact_list:
        print("prcessing: ", pfaf_id)
        # first check if it is already caculated
        needcaculate_flag = False
        if check_flag:
            arow = adate_df.loc[adate_df["pfaf_id"] == pfaf_id]
            # if not caculated
            if arow.empty:
                needcaculate_flag = True
            else:
                (
                    pfaf_id,
                    totalpop,
                    viirs_impactpop,
                    viirs_impactpop_percent,
                ) = arow.values.tolist()[0]
        # need caculate
        if check_flag == False or needcaculate_flag:
            totalpop = pop_df.loc[pop_df["pfaf_id"] == pfaf_id]["totalpop"].values[0]
            # only check when totalpop > 0
            if totalpop > 0:
                viirs_impactpop = count_impact_pop(pfaf_id, viirs_images, temp_dir)
                viirs_impactpop_percent = viirs_impactpop / totalpop * 100.0
            else:
                viirs_impactpop = 0
                viirs_impactpop_percent = 0.0

        impact_pop_count_list.append(
            [
                int(pfaf_id),
                int(totalpop),
                int(viirs_impactpop),
                float(viirs_impactpop_percent),
            ]
        )

    df = pd.DataFrame(impact_pop_count_list, columns=PopCount_header)
    tmp_output = os.path.basename(hwrfoutput).replace("Updated", "PopCount")
    popcount_tmp_output = os.path.join(settings.VIIRS_PROC_DIR, tmp_output)
    df.to_csv(popcount_tmp_output, index=False, float_format="%.2f")

    # write to the count for a date
    if check_flag == False:
        df.to_csv(adate_popcount, index=False, float_format="%.2f")
    if check_flag:
        merged_df = pd.concat([adate_df, df], ignore_index=True)
        merged_df = merged_df.drop_duplicates()
        merged_df.to_csv(adate_popcount, index=False, float_format="%.2f")

    # need to merge the result back to MoM output
    # 1. first join df to pop_df (need to drop Totalpop column) -> joinedpop_df
    # 2. second join joinedpop_df to hwrf_df -> mergedhwrf_df
    # 3. reorder column positions in mergedhwrf_df
    # 4. save reordered to csv

    # remove temp directory
    shutil.rmtree(temp_dir)


def main():
    """test code"""
    testhwrf = os.path.join(
        settings.HWRF_MOM_DIR,
        "Final_Attributes_2022122606HWRF+20221225DFO+20221225VIIRSUpdated.csv",
    )
    VIIRS_pop(hwrfoutput=testhwrf)

    # test another day
    testhwrf = os.path.join(
        settings.HWRF_MOM_DIR,
        "Final_Attributes_2022122618HWRF+20221225DFO+20221225VIIRSUpdated.csv",
    )
    VIIRS_pop(hwrfoutput=testhwrf)
    # test another day
    testhwrf = os.path.join(
        settings.HWRF_MOM_DIR,
        "Final_Attributes_2022122706HWRF+20221226DFO+20221225VIIRSUpdated.csv",
    )
    VIIRS_pop(hwrfoutput=testhwrf)


if __name__ == "__main__":
    main()
