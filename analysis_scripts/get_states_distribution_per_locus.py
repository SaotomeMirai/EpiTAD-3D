# #!/usr/bin/env python
# 2025-12-03
# env: pastis
# dyeing for chromation states

import pandas as pd
import pyranges as pr
import os
import argparse
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description="get states distribution per locus")
    parser.add_argument("-l", "--locus-bed", required=True, help="Locus bed file")
    parser.add_argument("-s", "--states-bed", required=True, help="Chromatin states bed file")
    parser.add_argument("-o", "--out-dir", required=True, help="Output directory")
    return parser.parse_args()

args = parse_args()

locus_bed = args.locus_bed
states_bed = args.states_bed
out_dir = args.out_dir

def mkdir(path):
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False
    
def get_states_distribution_per_locus(locus_bed, states_bed, out_dir):
    # 1. load bin bed
    locus_bin_df = pr.read_bed(locus_bed, as_df=True)
    locus_bin_df.columns = ["Chromosome", "Start", "End", "bin_id"]
    locus_prefix = os.path.basename(locus_bed).replace(".bed", "")

    # 2. load states bed
    states_df = pr.read_bed(states_bed, as_df=True)
    states_df.columns = ["Chromosome", "Start", "End", "state"]

    # 3. get pranges
    bin_pr = pr.PyRanges(locus_bin_df)
    states_pr = pr.PyRanges(states_df)

    # 4. intersect
    overlap_pr = states_pr.join(bin_pr, suffix="_bin")
    overlap_df = overlap_pr.df
    overlap_df["overlap_start"] = overlap_df[["Start", "Start_bin"]].max(axis=1)
    overlap_df["overlap_end"] = overlap_df[["End", "End_bin"]].min(axis=1)
    overlap_df["overlap_len"] = (overlap_df["overlap_end"] - overlap_df["overlap_start"]).clip(lower=0)

    # 5. sum overlap length per bin per state
    len_per_bin_state = (
    overlap_df
    .groupby(["bin_id", "state"], as_index=False)["overlap_len"]
    .sum()
    )

    max_state_per_bin = (
    len_per_bin_state
    .loc[len_per_bin_state.groupby("bin_id")["overlap_len"].idxmax()]
    .reset_index(drop=True)
    )

    # 6. state counts and plotting
    state_counts = (
    max_state_per_bin["state"]
    .value_counts()
    .sort_values()
    )
    print(state_counts)

    plt.figure(figsize=(8, 5))
    plt.bar(state_counts.index, state_counts.values)

    # Axis labels
    plt.xlabel("State")
    plt.ylabel("Bin Count")
    plt.title("Number of Bins Assigned to Each State")
    plt.xticks()

    plt.tight_layout()
    plot_file = os.path.join(out_dir, f"states_distribution_{locus_prefix}.pdf")
    plt.savefig(plot_file)

def main():
    mkdir(out_dir)
    get_states_distribution_per_locus(locus_bed, states_bed, out_dir)

if __name__ == "__main__":
    main()