# EpiTAD-3D
*v0.1.0*
EpiTAD-3D is a tool to reconstruct and visualize 3D chromation structure from Hi-C data.

[TOC]

## Usage
Here introduce the workflow for plotting single locus in chromatin.
**Input**: HiC data in .cool/.mcool format
**Output**: Reconstructed structure files in certain directory level

## Notice
*Don't apply EpiTAD-3D to visualize regions that are too large (such as whole genome or whole chomosome)*

## Installation (in linux)
```
git clone git@github.com:SaotomeMirai/EpiTAD-3D.git
```
## Run example
### Prepare environment for EpiTAD-3D
```
conda env create -f environment.yml
```
### Plotting single locus in chromatin
The test .mcool file is from Hilliard et al, Biotechnol Bioeng
. 2021. And it is CHO-K1 cell line.
```
example/example_scripts/test.sh
```
or 
```
python ~/data_HD/projects/EpiTAD-3D-1230/bin/visualization/plot_singleLocus.py \
    -c cg1001 -o ~/data_HD/projects/EpiTAD-3D-1230/example/example_out \
    -r 40000 \
    --chr chr10 -s 27160000 -e 29100000 \
    --max_mem 100 --cores 20 \
    --highlight_start 28399963 --highlight_end 28410405 \
    ~/data_HD/projects/EpiTAD-3D-1230/example/example_data/CHO-K1_2020_rep1.mcool
```
### Params details
```
usage: plot_singleLocus.py [-h] -c CELL_TYPE -o OUT_DIR [-r RESOLUTION] -chr CHROM -s START -e END [--max_mem MAX_MEM] [--cores CORES] [--highlight_start HIGHLIGHT_START] [--highlight_end HIGHLIGHT_END] cool_file

Plot single locus 3D structure from .mcool file

positional arguments:
  cool_file             .mcool file path

optional arguments:
  -h, --help            show this help message and exit
  -c CELL_TYPE, --cell_type CELL_TYPE
                        Cell type
  -o OUT_DIR, --out_dir OUT_DIR
                        Output directory
  -r RESOLUTION, --resolution RESOLUTION
                        Resolution
  -chr CHROM, --chrom CHROM
                        Chromosome to process,e.g.chr1 chr2
  -s START, --start START
                        Start position
  -e END, --end END     End position
  --max_mem MAX_MEM     Maximum mem in GB
  --cores CORES
  --highlight_start HIGHLIGHT_START
                        Highlight start position
  --highlight_end HIGHLIGHT_END
                        Highlight end position
```

### Results
The output directory has following structure:
```
~/data_HD/projects/EpiTAD-3D-1230/example/example_out
├── figs
│   └── cg1001
│       └── chr10
│           └── mean_variance_plot.pdf
├── matrix
│   └── cg1001
│       └── chr10
│           ├── chr10_27160000_29100000_40000.bed
│           ├── chr10_27160000_29100000_40000.matrix
│           └── chr10_27160000_29100000_40000_UNB02cst_structure.txt
├── PASTIS_out
│   └── cg1001
│       └── chr10
│           ├── chr10_27160000_29100000_40000_UNB02cst_structure_mapping.bed
│           └── chr10_27160000_29100000_40000_UNB02cst_structure.txt
└── pdb
    └── cg1001
        └── chr10
            ├── chr10_27160000_29100000_40000_UNB02cst_structure_mapping.txt
            ├── chr10_27160000_29100000_40000_UNB02cst_structure.pdb
            └── chr10_28399963_28410405_40000_highlight_atoms.txt
```

**figs**: Var-Mean Plot to see if the data fits the negative binomial model better.
**matrix**: matrix file to reconstruct 3D coordinates.
**PASTIS_out**: coordinates reconstructed by pastis-nb.
**pdb**: output file for visualization.

### About highlight
You can highlight your interested sites with the function **highlight_fromLOCUS** or **highlight_fromBED** with a single locus/.bed file. The output of atom lists to highlight in pdb is saved in *_highlight_atoms.txt in pdb
```
31
32
```
Above are simulatied atoms to highlight.

## Contact

If you need test data ( `.mcool` files), please contact:  
**gy1.mirai2003@gmail.com**

---

© 2025 **4DGenome Lab, PUMC**. All rights reserved.