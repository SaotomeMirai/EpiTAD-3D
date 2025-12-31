# EpiTAD-3d
---
v0.1.0
EpiTAD-3D is a tool to reconstruct and visualize 3D chromation structure from Hi-C data.

## Usage
---
Here introduce the workflow for plotting single locus in chromatin.
**Input**: HiC data in .cool/.mcool format
**Output**: Reconstructed structure files in certain directory level

## Installation (in linux)
---
```
git clone 
```
---
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
-c: cell type or a specific project id;
-r: expected resolution for visualization;
--chr: chromosome to visulization;
-s: start site;
-e: end site;
--max-mem: 

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
