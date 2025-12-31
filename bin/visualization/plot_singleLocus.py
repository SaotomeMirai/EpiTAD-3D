#!/usr/bin/env python
# 2025-11-29
# env:pastis
# dir: no restriction
# func:automatically transfer .mcool to .pdb for visualization

import os
import glob
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Plot single locus 3D structure from .mcool file")
    parser.add_argument("-c", "--cell_type", required=True, help="Cell type")
    parser.add_argument("-o", "--out_dir", required=True, help="Output directory")
    parser.add_argument("-r", "--resolution", type=int, default=10000, help="Resolution")
    parser.add_argument("-chr", "--chrom", required=True, help="Chromosome to process,e.g.chr1 chr2")
    parser.add_argument("-s", "--start", type=int, required=True, help="Start position")
    parser.add_argument("-e", "--end", type=int, required=True, help="End position")
    parser.add_argument("--max_mem", type=int, default=100, help="Maximum mem in GB")
    parser.add_argument("--cores", type=int, default=5)
    parser.add_argument("cool_file", help=".mcool file path")
    parser.add_argument("--highlight_start",type=int,default=None,help="Highlight start position")
    parser.add_argument("--highlight_end",type=int,default=None,help="Highlight end position")
    return parser.parse_args()
args = parse_args()

cell_type = args.cell_type
out_dir = args.out_dir
resolution = args.resolution
chrom = args.chrom
start = args.start
end = args.end
max_mem = args.max_mem
cores = args.cores
cool_file = args.cool_file
highlight_start = args.highlight_start
highlight_end = args.highlight_end

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)

def mkdir(path):
	isExists=os.path.exists(path)
	if not isExists:
		os.makedirs(path)
		return True
	else:
		return False

def cool2mat(matrix_dir,chrom):
    cmd_cool2mat = f"python ./bin/visualization/01_cool2matrix_bed.py \
        -c {cell_type} -o {matrix_dir} -r {resolution} \
        -chr {chrom} -s {start} -e {end} --max-mem {max_mem} --cores {cores} {cool_file}"
    print(cmd_cool2mat)
    os.system(cmd_cool2mat)
    print(f"Cool2matrix_bed for {chrom} done.")

def var_mean_plot(matrix_dir,chrom):
    figs_dir = os.path.join(out_dir, "figs", cell_type, chrom)
    cmd_plot = f"python ./bin/visualization/02_var-mean_plot.py -i {matrix_dir} -o {figs_dir}"
    if not os.path.exists(figs_dir):
        os.makedirs(figs_dir)
    print(cmd_plot)
    os.system(cmd_plot)
    print(f"Var-mean plot for {chrom} done.")

def clear_matrix_dir(matrix_dir):
    for fname in os.listdir(matrix_dir):
        if not (fname.endswith(".matrix") or fname.endswith(".bed") or fname.endswith("_UNB02cst_structure.txt")):
            fpath = os.path.join(matrix_dir, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)
    print(f"matrix directory {matrix_dir} cleared.")

def run_pastis(matrix_dir,chrom):
    matrix_pattern = os.path.join(matrix_dir, "*.matrix")
    matrix_file = glob.glob(matrix_pattern)[0]
    cmd_nb = f"./bin/visualization/06_run_pastisnb.sh \
        -m {matrix_file} --cores {cores} --max-mem {max_mem}"
    os.system(cmd_nb)
    clear_matrix_dir(matrix_dir)
    print(f"PASTIS-nb for {chrom} done.")

def txt2pdb(chrom,start,end,resolution):
    matrix_dir = os.path.join(out_dir, "matrix", cell_type, chrom)
    pastis_out_dir = os.path.join(out_dir, "PASTIS_out", cell_type, chrom)
    prefix = f"{chrom}_{start}_{end}_{resolution}_UNB02cst_structure"
    bed_prefix = f"{chrom}_{start}_{end}_{resolution}"
    structure_file = os.path.join(matrix_dir, prefix+".txt")
    bed_file = os.path.join(matrix_dir, bed_prefix+".bed")
    pdb_dir = os.path.join(out_dir, "pdb", cell_type, chrom)
    # transfer the best nb file to pastis_out_dir
    if not os.path.exists(pastis_out_dir):
        os.makedirs(pastis_out_dir, exist_ok=True)
    if not os.path.exists(pdb_dir):
        os.makedirs(pdb_dir, exist_ok=True)
    os.system(f"ln {structure_file} {pastis_out_dir}/{prefix}.txt")
    os.system(f"ln {bed_file} {pastis_out_dir}/{prefix}_mapping.bed")
    cmd_txt2pdb = f"python ./bin/visualization/07_txt2pdb.py -i {pastis_out_dir} -o {pdb_dir} \
        -chr {chrom} -s {start} -e {end} -r {resolution}"
    os.system(cmd_txt2pdb)
    print(f"txt2pdb for {chrom} done.")

def get_highlight_atom_list(cell_type, highlight_start,highlight_end,resolution,chrom,out_dir,prefix):
    atom_file = os.path.join(out_dir, "pdb", cell_type, chrom, f"{prefix}_mapping.txt")
    cmd_gethighlight_atom = f"python ./bin/visualization/highlight_fromLOCUS.py \
        -c {cell_type} -a {atom_file} -r {resolution} -chr {chrom} -o {out_dir} \
        --highlight_start {highlight_start} --highlight_end {highlight_end}"
    print(cmd_gethighlight_atom)
    os.system(cmd_gethighlight_atom)
     

def main():
    print(f"=====================Processing locus: {chrom}:{start}-{end}=====================")
    # run cool2matrix
    matrix_dir = os.path.join(out_dir, "matrix", cell_type, chrom)
    cool2mat(matrix_dir, chrom)
    # run var-mean plot
    var_mean_plot(matrix_dir, chrom)
    # run PASTIS-nb
    run_pastis(matrix_dir, chrom)
    # run txt2pdb
    prefix = f"{chrom}_{start}_{end}_{resolution}_UNB02cst_structure"
    txt2pdb(chrom, start, end, resolution)

    # get highlight atom list
    get_highlight_atom_list(cell_type, highlight_start, highlight_end, resolution, chrom, out_dir, prefix)


if __name__ == '__main__':
    main()