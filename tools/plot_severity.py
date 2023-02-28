"""
    plot_severity.py
        -- plot severity vs time
"""
import os

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("pakistan2022/momoutput_Severity.csv")
df.set_index("pfaf_id", inplace=True)
num = len(list(df.columns))

index_list = list(df.index.values)

for aid in index_list[4:5]:
    imagename = os.path.join("pakistan2022", "severityplot", f"{aid}_severity.png")
    fig, ax = plt.subplots(figsize=(6, 4))
    (df.loc[[aid]].T).plot.line(
        xticks=[1, int(num * 0.25), int(num * 0.50), int(num * 0.75), int(num * 0.95)],
        ylabel="Severity",
        xlabel="Date YYYYMMDDHH",
    )
    plt.ylim(0.0, 1.0)
    plt.axhline(y=0.8, color="r", linestyle="-")
    plt.axhline(y=0.6, color="orange", linestyle="-")
    plt.axhline(y=0.35, color="y", linestyle="-")
    # plt.savefig(imagename, bbox_inches="tight")
    plt.show()
    plt.close("all")