# Deep Neural Virtual Screening (DENVIS)

# Inference API
## 1. Data

### 1.1 Instructions on how to set-up target data [TODO --> Nick]
* Download from PDB
* PDB complexes together with crystal ligands

The following data have been used for training and validation of DENVIS v1.0 models:
* [PDBBind v.2019 general set](https://storage.googleapis.com/denvis_v1_data/pdbbind_v2019_general.tar.gz) (4.6G)
* [PDBBind v.2019 refined set](https://storage.googleapis.com/denvis_v1_data/pdbbind_v2019_refined.tar.gz) (1G)
* [PDBBind v.2019 core set](https://storage.googleapis.com/denvis_v1_data/pdbbind_v2019_core.tar.gz) (68M)
* [TOUGH-M1](https://storage.googleapis.com/denvis_v1_data/tough_m1.tar.gz) (895M)
* [DUD-E](https://storage.googleapis.com/denvis_v1_data/dude.tar.gz) (23M)

### 1.2 Instructions on how to set-up ligand data  [TODO --> Nick]

## 2. Inference via HTTP requests [TODO --> Nick]

# DENVIS v1.0 paper results reproduction [WIP]
## 1. Download output scores

Run `download_extract_data.sh` to download and extract all output data/scores used in the Benchmark.

Alternatively, you can manually download the following DUD-E output scores and extract into `data/outputs` folder:
* [DENVIS](https://storage.googleapis.com/denvis_v1_outputs/denvis_outputs.tar.gz) (1.1G)
* [DeepDTA](https://storage.googleapis.com/denvis_v1_outputs/deepdta_outputs.tar.gz) (109M)
* [AutoDock Vina](https://storage.googleapis.com/denvis_v1_outputs/vina_outputs.tar.gz) (141M)
* [GNINA](http://bits.csb.pitt.edu/files/defaultCNN_dude.tar.gz) (24M)
* [RF-score & NN-score](http://bits.csb.pitt.edu/files/rfnn_dude_scores.tgz) (189M)
* [Gold, Glide, Surflex, Flex](https://storage.googleapis.com/denvis_v1_outputs/docking_performance_scores.tar.gz) (11K - final performance scores only - see Note #3 below.)

The following needs to be downloaded and saved into `data/pdbbdind` folder:
* [PDBBind v.2019 general set target data](https://storage.googleapis.com/denvis_v1_data/INDEX_general_PL_data.2019)

Note #1: GNINA, RF-score and NN-score scoring outputs for DUD-E are provided by [David Koes Lab](http://bits.csb.pitt.edu/) (original links provided above).
If clicking any of those links does not initiate downloading, please copy the link address and paste it on a new tab or try using the `wget` command. 

Note #2: AutoDock Vina docking outputs for DUD-E are also provided in `.sdf` format from David Koes Lab. The results have been downloaded from the original [link](http://bits.csb.pitt.edu/files/docked_dude.tar) (5GB) and processed to extract the docking scores only, which are stored in `.csv` format in the link provided above. If you wish to extract the docking scores from the original `.sdf` files, download docked data from the original link and run the `parse_autodock_outputs.py` script. [TODO]

Note #3: Docking outputs with Gold, Glide, Surflex and Flex algorithms are, unfortunately, not publicly available. They have been kindly made available to us by [Dr. Liliane Mouawad](https://science.institut-curie.org/research/biology-chemistry-of-radiations-cell-signaling-and-cancer-axis/cmbc/chemistry-and-modelling-for-protein-recognition/team-members/?mbr=liliane-mouawad) and are from this [paper](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-016-0167-x). To enable reproduction of our paper results, we make available our computed performance metrics for each of these methods and each target protein in DUD-E.

Note #4: If you manually download and extract the data you might need to update the data paths in the notebooks.

## 2. Set-up environment
It is recommended you create a `conda` environment using the provided file:
```bash
conda env create -f conda_env.yml
```

Alternatively, if you can create your own environment, the following packages are required for running the noteboks: 
* `python>=3.6`
* `numpy`
* `scipy`
* `pandas`
* `sklearn`
* `rdkit`
* `matplotlib`
* `seaborn`
* `pingouin`
* `pyarrow`
* `tqdm`
* `jupyter`

The followng package is also required for running the optional `parse_autodock_outputs.py` script.
* `click`


Example using `conda`:
```bash
conda create -n denvis python=3.7 numpy scipy pandas scikit-learn rdkit matplotlib seaborn pingouin pyarrow click tqdm jupyter -c conda-forge -c rdkit
```

## 3. Run notebooks
