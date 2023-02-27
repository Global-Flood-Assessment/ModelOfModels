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
"""

import argparse
import os

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def plot_map(adate, abase, awatch, awarning, afolder):
    """plot map"""

    imagename = os.path.join(afolder, f"{adate}.png")

    base = gpd.read_file(abase)
    watch = gpd.read_file(awatch)
    warning = gpd.read_file(awarning)

    fig, ax = plt.subplots(figsize=(6, 4))
    base.plot(ax=ax, facecolor="none", edgecolor="grey", linewidth=0.5)
    watch.plot(ax=ax, facecolor="white", edgecolor="orange", linewidth=1, label="Watch")
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
    ax.legend(lines, labels, loc="lower right")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.ylim(22.0, 39.0)
    plt.xlim(55, 85)
    plt.savefig(imagename, bbox_inches="tight")
    # plt.show()
    plt.close()


def generate_mommap(basegeojson, momfolder, hours="00", skipd=5):
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