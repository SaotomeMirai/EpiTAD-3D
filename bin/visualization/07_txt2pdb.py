#!/bin/python
# 2025-07-13
# 2025-11-30 updated adaption to specific prefix

import os
import numpy as np
import argparse
import pandas as pd

# 1. read file and add bin end info----------------
# terminal args set
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input-directory", help="input directory containing *_UNB02cst_structure.txt files and .bed file", required=True)
parser.add_argument("-o", "--output_directory", default=None, help="output directory to save the PDB and mapping files")
parser.add_argument("-chr", required=True)
parser.add_argument("-s", "--start", type=int, required=True)
parser.add_argument("-e", "--end", type=int, required=True)
parser.add_argument("-r", "--resolution", type=int, help="resolution used in PASTIS-nb")
args = parser.parse_args()

input_dir = args.input_directory
output_dir = args.output_directory
chrom = args.chr
start = args.start
end = args.end
resolution = args.resolution

# read .*_UNB02cst_structure.txt files and .bed file
prefix = f"{chrom}_{start}_{end}_{resolution}_UNB02cst_structure"
structure_file = os.path.join(input_dir, prefix+".txt")
bed_file = os.path.join(input_dir, prefix+"_mapping.bed")

if not structure_file:
    print(f"Error: No *_UNB02cst_structure.txt file found in {input_dir}")
if not bed_file:
    print(f"Error: No .bed file found in {input_dir}")


structure_df = pd.read_csv(structure_file, sep=" ", header=None)
bed_df = pd.read_csv(bed_file, sep="\t", header=None)

structure_df[3] = bed_df[2]

# 2. convert to pdb format----------------
# remove nan
structure_df = structure_df.dropna(axis=0, how='any')
# normalize
max_val = np.max(np.abs(structure_df.iloc[:, :3].values))
if max_val > 0:
    structure_df.iloc[:, :3] /= max_val
    structure_df.iloc[:, :3] *= 15

# keep original prefix
output_pdb = os.path.join(output_dir, f"{prefix}.pdb")
output_map = os.path.join(output_dir, f"{prefix}_mapping.txt")

bin_atom_list = []

with open(output_pdb, "w") as pdb:
    for idx, row in structure_df.iterrows():
        atom_id = idx + 1
        x, y, z, bin_end = row[0], row[1], row[2], row[3]
        pdb.write(f"ATOM  {atom_id:5d}  CA  ALA A{atom_id:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n")
        bin_atom_list.append((int(bin_end), atom_id))

    # write CONECT
    for i in range(1, len(structure_df)):
        pdb.write(f"CONECT{i:5d}{i+1:5d}\n")

# save bin_end - atom_id mapping
mapping_df = pd.DataFrame(bin_atom_list)
mapping_df.to_csv(output_map, sep="\t", index=False)

print(f"PDB written to: {output_pdb}")
print(f"Bin-end to atom mapping saved to: {output_map}")