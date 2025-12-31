# !/usr/bin/env python
# 2025-07-09

import sys
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN_DIR))
from _bootstrap import *

import os
import argparse

import numpy as np

from pastis.optimization import mds
import utils
import resource



"""
Launches the inference of the 3D model on .matrix/.bed files"""


parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("--seed", default=1, type=int)
parser.add_argument("--lengths", default=None, type=str)
parser.add_argument("--no-normalization", dest="normalize",
                    default=True, action="store_false")
parser.add_argument("--bias-vector", dest="bias", default=None)
parser.add_argument("--max-mem", type=int, default=None, help="Maximum memory usage (GB)")
parser.add_argument("--cores", type=int, default=None, help="Max cores to use")

args = parser.parse_args()

# print(f"[DEBUG] Input matrix: {args.filename}")
# print(f"[DEBUG] Normalize: {args.normalize}, Seed: {args.seed}")

normalize = args.normalize

_, counts, lengths, bias = utils.load(args.filename, bias=args.bias,
                                      normalize=normalize)

if args.cores:
    os.environ["OMP_NUM_THREADS"] = str(args.cores)
    os.environ["MKL_NUM_THREADS"] = str(args.cores)
    print(f"Maximum cores: {args.cores}")

# max memory
if args.max_mem:
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (args.max_mem * 1024**3, hard))
    print(f"Max memory: {args.max_mem} GB")


if args.filename.startswith("data"):
    filename = args.filename.replace("data", "results")
else:
    filename = args.filename

try:
    os.makedirs(os.path.dirname(filename))
except OSError:
    pass

outname = filename.replace(
    ".matrix", "_MDS_%02d_structure.txt" % (args.seed, ))

if os.path.exists(outname):
    # Simple caching mechanism
    print("File already exists")
    import sys
    sys.exit()

random_state = np.random.RandomState(args.seed)

X = mds.estimate_X(counts, random_state=random_state)
mask = (np.array(counts.sum(axis=0)).flatten() +
        np.array(counts.sum(axis=1)).flatten() == 0)
# print(f"[DEBUG] Estimated 3D coordinates shape: {X.shape}")
X[mask] = np.nan


np.savetxt(outname, X)

print("Finished", outname)
