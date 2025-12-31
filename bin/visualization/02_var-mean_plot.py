#!/usr/bin/env python3
# 2025-07-06
# env: pastis

import sys
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN_DIR))
from _bootstrap import *



import argparse
import numpy as np
import matplotlib.pyplot as plt
from iced import io, filter, normalization
from pastis import dispersion
# import resource

parser = argparse.ArgumentParser(
    description="Plot mean vs variance from a directory containing exactly one .matrix and one .bed file"
)
parser.add_argument(
    "-i", "--input-dir",
    required=True,
    help="Directory containing exactly one .matrix and one .bed file"
)
parser.add_argument(
    "-o", "--output-dir",
    required=True,
    help="Directory to save the mean_variance_plot.pdf"
)
args = parser.parse_args()

import os
input_dir = args.input_dir
output_dir = args.output_dir
output_file = os.path.join(output_dir, "mean_variance_plot.pdf")

# validate directory
if not os.path.isdir(input_dir):
    raise ValueError(f"{input_dir} is not a valid directory.")

files = os.listdir(input_dir)
matrix_files = [f for f in files if f.endswith(".matrix")]
bed_files = [f for f in files if f.endswith(".bed")]

if len(matrix_files) != 1 or len(bed_files) != 1:
    raise ValueError(f"{input_dir} must contain exactly one .matrix and one .bed file.")

matrixfile = os.path.join(input_dir, matrix_files[0])
bedfile = os.path.join(input_dir, bed_files[0])

lengths = io.load_lengths(bedfile)
counts = io.load_counts(matrixfile, lengths=lengths)

# Remove diagonal and filter low counts
counts.setdiag(0)
counts = counts.tocsr()
counts.eliminate_zeros()
counts = filter.filter_low_counts(counts, percentage=0.06, sparsity=False)

# Normalize
normed_counts, biases = normalization.ICE_normalization(counts, output_bias=True)

_, mean, variance, _ = dispersion.compute_mean_variance(counts, lengths, bias=biases)

fig, ax = plt.subplots(figsize=(6,6))
ax.scatter(mean, variance, s=20, alpha=0.7)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Mean", fontweight="bold")
ax.set_ylabel("Variance", fontweight="bold")

x = np.logspace(-1, 7, 100)
ax.plot(x, x, "--", color="black", label="y=x (Poisson)")
ax.plot(x, 0.1*x, ":", color="red", label="y=0.1x (sparse threshold)")

ax.legend()
ax.set_title("Mean vs Variance (check sparsity)", fontweight="bold")
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.grid(True, which="both", linestyle="--", color="0.8")

plt.tight_layout()
plt.savefig(output_file)