#!/usr/bin/env python3
# 2025-07-04
# transform .mcool file to .matrix

import argparse
import numpy as np
import cooler
import os
import resource

parser = argparse.ArgumentParser(
    description="Transform .mcool/.cool file to .matrix sparse format for 3D genome analysis."
)
parser.add_argument("filename", help=".mcool or .cool file path")
parser.add_argument("-c", "--do_celltype", required=True, help="cell type")
parser.add_argument("-o", "--out-dir", required=True, help="output file directory")
parser.add_argument("-r", "--resolution", type=int, required=True, help="hic matrix resolution")
parser.add_argument("-chr", "--chromosome", help="chromosome name (if not provided, use whole genome)")
parser.add_argument("-s", "--start", type=int, help="start position of the region")
parser.add_argument("-e", "--end", type=int, help="end position of the region")
parser.add_argument("--max-mem", type=int, default=None, help="Maximum memory usage (GB)")
parser.add_argument("--cores", type=int, default=None, help="Max cores to use")


args = parser.parse_args()

if args.cores:
    os.environ["OMP_NUM_THREADS"] = str(args.cores)
    os.environ["MKL_NUM_THREADS"] = str(args.cores)
    print(f"Maximum cores: {args.cores}")

# max memory
if args.max_mem:
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (args.max_mem * 1024**3, hard))
    print(f"Max memory: {args.max_mem} GB")

# Assign parsed arguments to concise variable names
filename = args.filename
resolution = args.resolution
chromosome = args.chromosome
start = args.start
end = args.end
do_celltype = args.do_celltype

if not filename.endswith((".mcool", ".cool")):
    parser.error("input file must be a .mcool or .cool file")

output_dir = args.out_dir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

if start is None or end is None:
    clr = cooler.Cooler(f"{filename}::resolutions/{resolution}")
    if chromosome:
        bins = clr.bins().fetch(chromosome)
    else:
        bins = clr.bins()[:]
    min_start = bins["start"].min()
    max_end = bins["end"].max()
    if start is None:
        start = min_start
    if end is None:
        end = max_end

output_matrix = os.path.join(output_dir, f"{chromosome}_{start}_{end}_{resolution}.matrix")

# load mcool file

def cool2matrix_bed(filename, chrom, resolution, start, end,
                    output_matrix, output_bed):
    clr = cooler.Cooler(f"{filename}::resolutions/{resolution}")

    if chrom is None:
        raise ValueError("Chromosome must be provided for regional extraction.")

    region = f"{chrom}:{start}-{end}"

    bins_region = clr.bins().fetch(region)
    if len(bins_region) == 0:
        raise ValueError(f"No bins found in region {region}. "
                         "Check chromosome name and coordinates.")

    chroms = bins_region["chrom"].values \
        if "chrom" in bins_region else np.array([chrom] * len(bins_region))
    bin_starts = bins_region["start"].values
    bin_ends = bins_region["end"].values

    matrix = clr.matrix(balance="KR").fetch(region)
    matrix = np.asarray(matrix, dtype=float)

    n_bins = len(bins_region)
    if matrix.shape[0] != n_bins or matrix.shape[1] != n_bins:
        raise ValueError(
            f"Matrix shape {matrix.shape} does not match number of bins {n_bins} "
            f"in region {region}."
        )

    with open(output_matrix, "w") as f_mat:
        for i in range(n_bins):
            for j in range(i, n_bins):
                val = matrix[i, j]
                if not np.isnan(val) and val > 0:
                    f_mat.write(f"{i}\t{j}\t{val}\n")

    with open(output_bed, "w") as f_bed:
        for idx, (c, start, end) in enumerate(zip(chroms, bin_starts, bin_ends)):
            f_bed.write(f"{c}\t{start}\t{end}\t{idx}\n")

output_bed = os.path.join(output_dir, f"{chromosome}_{start}_{end}_{resolution}.bed")
cool2matrix_bed(filename, chromosome, resolution, start, end, output_matrix, output_bed)

