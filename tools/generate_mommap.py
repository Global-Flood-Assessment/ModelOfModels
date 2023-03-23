"""
    generate_mommap.py
        --- gemerate map output
    paramters:
        -- base geojson: geojson contains all watersheds
        -- mom output folder: assume genjsons is under geojson folder
    output:
        -- map (*.png) under folder mapimage
    example:
        python generate_mommap.py research_watersheds.geojson pakistan2022
    convert images to gif
    convert -delay 20 -loop 0 pakistan2022/mapimage/*.png mymap.gif
"""

import argparse
import os

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def plot_map(adate, abase, awatch, awarning, afolder):
    """plot map"""

    imagename = os.path.join(afolder, f"{adate}.png")
    # no need to redraw the image
    if os.path.exists(imagename):
        return
    base = gpd.read_file(abase)
    plotwatch, plotwarning = True, True
    if os.path.exists(awatch):
        watch = gpd.read_file(awatch)
    else:
        plotwatch = False
    if os.path.exists(awarning):
        warning = gpd.read_file(awarning)
    else:
        plotwarning = False
    # extract bounding box from base geojson
    # then use it to setup the plot limit
    [minx, miny, maxx, maxy] = base.total_bounds

    # 6, 4
    fig, ax = plt.subplots(figsize=(6, 4))
    base.plot(ax=ax, facecolor="none", edgecolor="grey", linewidth=0.5)
    if plotwatch:
        watch.plot(
            ax=ax, facecolor="white", edgecolor="orange", linewidth=1, label="Watch"
        )
    if plotwarning:
        warning.plot(
            ax=ax, facecolor="white", edgecolor="red", linewidth=1.5, label="Warning"
        )
    plt.title("Date: " + adate)

    lines = [
        Line2D(
            [0],
            [0],
            linestyle="none",
            marker="s",
            markersize=10,
            markeredgecolor=t.get_edgecolor(),
            markerfacecolor=t.get_facecolor(),
        )
        for t in ax.collections[1:]
    ]
    labels = [t.get_label() for t in ax.collections[1:]]
    # lower right or upper right
    ax.legend(lines, labels, loc="lower right")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.xlim(minx - 1, maxx + 1)
    plt.ylim(miny - 1, maxy + 1)
    # plt.savefig(imagename, bbox_inches="tight")
    plt.savefig(imagename)
    # plt.show()
    plt.close()


def generate_mommap(basegeojson, momfolder, hours="00", skipd=1):
    """generate momfolder"""

    # get list of geojsons
    geojson_folder = os.path.join(momfolder, "geojson")
    geojsonlist = os.listdir(geojson_folder)
    dates_list = [os.path.basename(x).split("_")[0] for x in geojsonlist]
    dates_list = list(set(dates_list))
    dates_list.sort()

    dates_list = [x for x in dates_list if x[-2:] == hours]

    # create the mapimage folder
    mapfolder = os.path.join(momfolder, "mapimage")
    if not os.path.exists(mapfolder):
        os.mkdir(mapfolder)

    for datestr in dates_list[::skipd]:
        watch_g = os.path.join(geojson_folder, f"{datestr}_Watch.geojson")
        warning_g = os.path.join(geojson_folder, f"{datestr}_Warning.geojson")
        plot_map(datestr, basegeojson, watch_g, warning_g, mapfolder)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("basegeojson", type=str, help="geojson for all watersheds")
    parser.add_argument("momoutputfolder", type=str, help="MoM output folder")
    args = parser.parse_args()
    generate_mommap(args.basegeojson, args.momoutputfolder)


if __name__ == "__main__":
    main()
