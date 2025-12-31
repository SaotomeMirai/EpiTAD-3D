# #!/usr/bin/env python
# 2025-12-04
# env: pastis
# get atoms-multiple colors vs states

import pandas as pd
import pyranges as pr
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="get states distribution per locus")
    parser.add_argument("-a", "--atom-file", required=True, help="Atom file with bin ids")
    parser.add_argument("-s", "--states-bed", required=True, help="Chromatin states bed file")
    parser.add_argument("-o", "--out-dir", required=True, help="Output directory")
    parser.add_argument("-r", "--resolution", type=int, required=True, help="Resolution")
    parser.add_argument("-chr", "--chrom", required=True, help="Chromosome name")
    return parser.parse_args()

args = parse_args()

atom_file = args.atom_file
state_bed = args.states_bed
out_dir = args.out_dir
resolution = args.resolution
chrom = args.chrom

def mkdir(path):
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False
    
def get_max_state_per_atom(atom_file, state_bed, resolution, chrom):
    atom = pd.read_csv(atom_file, sep="\t", header=None)
    atom_df = pd.DataFrame(atom)
    atom_df.columns = ["End", "atom_id"]
    # atom2bed
    atom_df["Start"] = atom_df["End"] - resolution
    atom_df["Chromosome"] = chrom
    atom_bed = atom_df.reindex(columns=["Chromosome", "Start", "End", "atom_id"])
    atom_bed = atom_bed.drop(index=0)
    # load states bed
    states_df = pr.read_bed(state_bed, as_df=True)
    states_df.columns = ["Chromosome", "Start", "End", "state"]

    # get pyranges
    atom_pr = pr.PyRanges(atom_bed)
    states_pr = pr.PyRanges(states_df)
    overlap_pr = states_pr.join(atom_pr, suffix="_atom")
    overlap_df = overlap_pr.df
    overlap_df["overlap_start"] = overlap_df[["Start", "Start_atom"]].max(axis=1)
    overlap_df["overlap_end"] = overlap_df[["End", "End_atom"]].min(axis=1)
    overlap_df["overlap_len"] = (overlap_df["overlap_end"] - overlap_df["overlap_start"]).clip(lower=0)

    # sum overlap length per atom per state
    len_per_atom_state = (
    overlap_df
    .groupby(["atom_id", "state"], as_index=False)["overlap_len"]
    .sum()
    )
    # get max overlap length state per atom
    max_state_per_atom = (
    len_per_atom_state
    .loc[len_per_atom_state.groupby("atom_id")["overlap_len"].idxmax()]
    .reset_index(drop=True)
)
    return max_state_per_atom

def get_dye_map():
    # get bin_ids for each state
    max_state_per_atom = get_max_state_per_atom(atom_file, state_bed, resolution, chrom)
    # states = len_per_atom_state['state'].unique()
    # print(states)
    atom_grouped_by_state = (max_state_per_atom.groupby("state")["atom_id"]
        .apply(list).reset_index())
    # Convert list of atom_ids to a '+'-joined string
    atom_grouped_by_state["atom_id_str"] = atom_grouped_by_state["atom_id"].apply(
        lambda x: "+".join(map(str, x))
    )

    atom_prefix = os.path.basename(atom_file).replace(".txt", "")
    dye_atom_state_map_file = os.path.join(out_dir, f"dye_atom_state_{atom_prefix}.txt")
    atom_grouped_by_state[["state", "atom_id_str"]].to_csv(dye_atom_state_map_file, sep="\t", index=False, header=False)

def main():
    mkdir(out_dir)
    get_dye_map()

if __name__ == '__main__':
    main()