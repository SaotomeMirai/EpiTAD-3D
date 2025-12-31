#!/bin/bash

 # default to 20 iterations
niter=20
cores=""
max_mem=""

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--matrix)
            matrix_file="$2"
            shift 2
            ;;
        -n|--niter)
            niter="$2"
            shift 2
            ;;
        --cores)
            cores="$2"
            shift 2
            ;;
        --max-mem)
            max_mem="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 -m your.matrix [-n number_of_iterations] [--cores N] [--max-mem GB]"
            echo ""
            echo "Options:"
            echo "  -m, --matrix       Input .matrix file (required)"
            echo "  -n, --niter        Number of iterations (default: 20)"
            echo "  --cores            Max CPU cores / threads"
            echo "  --max-mem          Max virtual memory in GB"
            echo "  -h, --help         Show this help message and exit"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information."
            exit 1
            ;;
    esac
done

# check required matrix file
if [ -z "$matrix_file" ]; then
    echo "Usage: $0 -m your.matrix [-n number_of_iterations] [--cores N] [--max-mem GB]"
    exit 1
fi

# set cores num
if [ -n "$cores" ]; then
    export OMP_NUM_THREADS=$cores
    export MKL_NUM_THREADS=$cores
    echo ">>> Limited to maximum $cores threads"
fi

# set max memory
if [ -n "$max_mem" ]; then
    ulimit -v $((max_mem * 1024 * 1024))
    echo ">>> Limited to maximum $max_mem GB virtual memory"
fi

echo ">>> Running $niter iterations of MDS + NB optimization on: $matrix_file <<<"

for SEED in $(seq 1 $niter)
do
    echo "=== Iteration $SEED: MDS optimization ==="
    python ./bin/visualization/03_infer_structure-mds.py "$matrix_file" --seed $SEED
    echo "=== Iteration $SEED: NB optimization ==="
    python ./bin/visualization/04_infer_structure-nb.py -u -e "$matrix_file" --seed $SEED
done

echo "=== Selecting the best NB structure (minimum objective value) among $niter runs ==="
python ./bin/visualization/05_select_bestNB.py -u -e "$matrix_file"

echo ">>> Done! Best NB structure file saved <<<"