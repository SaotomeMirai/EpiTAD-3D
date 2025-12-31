#!/usr/bin/env python
# 2025-11-29
# env:pastis
# dir: no restriction
# func: highlight locus atom list from .pdb file

import os
import argparse
import pandas as pd
import pyranges as pr

def parse_args():
    parser = argparse.ArgumentParser(description="Highlight locus atom list from .pdb file")
    parser.add_argument("-c", "--cell_type", required=True, help="Cell type")
    parser.add_argument("-a", "--atom-file", required=True, help="Atom file with bin ids")
    parser.add_argument("-r", "--resolution", type=int, required=True, default=10000, help="Resolution")
    parser.add_argument("-chr", "--chrom", required=True, help="Chromosome name")
    parser.add_argument("-o", "--out_dir", required=True, help="Output directory")
    parser.add_argument("--highlight_start",type=int,required=True,help="Highlight start position")
    parser.add_argument("--highlight_end",type=int,required=True, help="Highlight end position")
    return parser.parse_args()


def main():
    args = parse_args()
    
    cell_type = args.cell_type
    atom_file = args.atom_file
    out_dir = args.out_dir
    chrom = args.chrom
    resolution = args.resolution
    highlight_start = args.highlight_start
    highlight_end = args.highlight_end
    if highlight_start is None or highlight_end is None:
        raise ValueError("Highlight start and end positions must be provided.")
    # 1) read atom file
    atom = pd.read_csv(atom_file, sep="\t", header=None)
    atom_df = pd.DataFrame(atom)
    atom_df.columns = ["End", "atom_id"]
    # atom2bed
    atom_df["Start"] = atom_df["End"] - resolution
    atom_df["Chromosome"] = chrom
    atom_bed = atom_df.reindex(columns=["Chromosome", "Start", "End", "atom_id"])
    atom_bed = atom_bed.drop(index=0)

    atom_pr = pr.PyRanges(atom_bed)
    # 3) build PyRanges object for the query region
    df_query = pd.DataFrame({
    "Chromosome": [chrom],
    "Start": [min(highlight_start, highlight_end)],
    "End": [max(highlight_start, highlight_end)],
    })
    query_pr = pr.PyRanges(df_query)
    print(f"query: chr:{chrom}: {highlight_start}-{highlight_end}")
    # 4) overlap and get atom list
    overlap = atom_pr.join(query_pr)
    df_ov = overlap.df

    print("overlap.df columns:", df_ov.columns)

    if df_ov.empty:
        raise ValueError(
            f"No overlapping bins found for region {chrom}:{highlight_start}-{highlight_end}. "
            f"Please check if the highlight region is covered by mapping file."
    )

    atom_list = df_ov["atom_id"].unique().tolist()

    print(f"Query region: {chrom}:{highlight_start}-{highlight_end}")
    print(f"Found {len(atom_list)} atom(s):")
    print(atom_list)
    # 5) output atom list
    out_file = os.path.join(out_dir,
    "pdb", cell_type, chrom,
    f"{chrom}_{highlight_start}_{highlight_end}_{resolution}_highlight_atoms.txt"
    )

    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    with open(out_file, "w") as f:
        for atom_id in atom_list:
            f.write(f"{atom_id}\n")

    print(f"Saved atom list to: {out_file}")

if __name__ == "__main__":
    main()