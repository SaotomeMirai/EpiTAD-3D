#!/usr/bin/env python
# 2025-12-24
# env: pastis
# map bed intervals to atom ids

import pandas as pd
import pyranges as pr
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="map bed intervals to atom ids")
    parser.add_argument("-a", "--atom-file", required=True, help="Atom file with bin ids")
    parser.add_argument("-b", "--bed-file", required=True, help="Bed file (chr start end)")
    parser.add_argument("-o", "--out-dir", required=True, help="Output directory")
    parser.add_argument("-r", "--resolution", type=int, required=True, help="Resolution")
    parser.add_argument("-chr", "--chrom", required=True, help="Chromosome name")
    parser.add_argument("-n", "--name",required=True, help="unique name for bed")
    return parser.parse_args()

args = parse_args()

atom_file = args.atom_file
bed_file = args.bed_file
out_dir = args.out_dir
resolution = args.resolution
chrom = args.chrom
name = args.name

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_atom_overlap(atom_file, bed_file, resolution, chrom):
    # load atom file
    atom_df = pd.read_csv(atom_file, sep="\t", header=None)
    # print("[DEBUG] atom_df head:\n", atom_df.head())
    atom_df.columns = ["End", "atom_id"]

    atom_df["Start"] = atom_df["End"] - resolution
    atom_df["Chromosome"] = chrom
    atom_bed = atom_df[["Chromosome", "Start", "End", "atom_id"]]
    atom_bed = atom_bed.drop(index=0)

    # load bed (chr, start, end)
    bed_df = pr.read_bed(bed_file, as_df=True)
    bed_df = bed_df[["Chromosome", "Start", "End"]]

    atom_pr = pr.PyRanges(atom_bed)
    bed_pr = pr.PyRanges(bed_df)

    # get overlaps
    overlap_df = bed_pr.join(atom_pr).df
    print("[DEBUG] overlap_df columns:", overlap_df.columns.tolist())
    print("[DEBUG] overlap_df head:\n", overlap_df.head())

    # keep necessary columns
    overlap_df = overlap_df[
        ["Chromosome", "Start", "End", "atom_id"]
    ]

    return overlap_df

# def get_atom_map():
#     overlap_df = get_atom_overlap(atom_file, bed_file, resolution, chrom)

#     # group by bed interval, collect atom_ids
#     bed_atom_map = (
#         overlap_df
#         .groupby(["Chromosome", "Start", "End"])["atom_id"]
#         .apply(list)
#         .reset_index()
#     )
#     print("DEBUG: overlap_df atom_id dtype =", overlap_df["atom_id"].dtype)
#     print("DEBUG: bed_atom_map atom_id element types:\n", bed_atom_map["atom_id"].apply(type).value_counts())
#     print("DEBUG: examples of non-list atom_id:\n", bed_atom_map.loc[bed_atom_map["atom_id"].apply(lambda v: not isinstance(v, list)), ["Chromosome","Start","End","atom_id"]].head(10))
#     # convert atom_id list to '+'-joined string
#     bed_atom_map["atom_id_str"] = bed_atom_map["atom_id"].apply(
#         lambda x: "+".join(map(str, sorted(set(x))))
#     )

#     atom_prefix = os.path.basename(atom_file).replace(".txt", "")
#     out_file = os.path.join(out_dir, f"bed_atom_map_{atom_prefix}_{name}.txt")

#     bed_atom_map[
#         ["Chromosome", "Start", "End", "atom_id_str"]
#     ].to_csv(out_file, sep="\t", index=False, header=False)
#     print("[INFO]: bed to atom_id map saved to", out_file)

def get_atom_map():
    overlap_df = get_atom_overlap(atom_file, bed_file, resolution, chrom)
    print("[DEBUG]:clean_overlap_df:","\n", overlap_df.head())
    atom_prefix = os.path.basename(atom_file).replace(".txt", "")
    out_file = os.path.join(out_dir, f"bed_atom_map_{atom_prefix}_{name}.txt")

    overlap_df.to_csv(out_file, sep="\t", index=False, header=False)
    print("[INFO]: bed to atom_id map saved to", out_file)
    
    # bed_atom_map = (
    #     overlap_df
    #     .groupby(["Chromosome", "Start", "End"])
    #     .agg(
    #         atom_id_list=("atom_id", lambda s: sorted(set(s.astype(int))))
    #     )
    # )
    # print("bed_atom_map successfully created. Sample:\n", bed_atom_map.head())
    # bed_atom_map["atom_id_str"] = bed_atom_map["atom_id_list"].apply(
    #     lambda x: "+".join(map(str, x))
    # )

    

    # bed_atom_map[
    #     ["Chromosome", "Start", "End", "atom_id_str"]
    # ].to_csv(out_file, sep="\t", index=False, header=False)
    
def main():
    mkdir(out_dir)
    get_atom_map()

if __name__ == "__main__":
    main()