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

# DENVIS v1.0 paper results reproduction
## 1. Download output scores

It is recommended that you run `download_extract_data.sh` to download and extract all output data/scores used in the Benchmark and the ablation studies.

Alternatively, you can manually download the following DUD-E output scores and extract into `data/outputs` folder:
* [DENVIS](https://storage.googleapis.com/denvis_v1_outputs/denvis_outputs.tar.gz) (945M)
* [DeepDTA](https://storage.googleapis.com/denvis_v1_outputs/deepdta_outputs.tar.gz) (109M)
* [AutoDock Vina](https://storage.googleapis.com/denvis_v1_outputs/vina_outputs.tar.gz) (141M)
* [GNINA](http://bits.csb.pitt.edu/files/defaultCNN_dude.tar.gz) (24M)
* [RF-score & NN-score](http://bits.csb.pitt.edu/files/rfnn_dude_scores.tgz) (189M)
* [Gold, Glide, Surflex, Flex](https://storage.googleapis.com/denvis_v1_outputs/docking_performance_scores.tar.gz) (11K - final performance scores only - see Note #3 below.)

Note #1: GNINA, RF-score and NN-score scoring outputs for DUD-E are provided by [David Koes Lab](http://bits.csb.pitt.edu/) (original links provided above).
If clicking any of those links does not initiate downloading, please copy the link address and paste it on a new tab or try using the `wget` command. 

Note #2: AutoDock Vina docking outputs for DUD-E are also provided in `.sdf` format from David Koes Lab. The results have been downloaded from the original [link](http://bits.csb.pitt.edu/files/docked_dude.tar) (5GB) and processed to extract the docking scores only, which are stored in `.csv` format in the link provided above. If you wish to extract the docking scores from the original `.sdf` files, download docked data from the original link, extract into `data/outputs/vina_outputs/` and run [`parse_autodock_outputs.py`](scripts/parse_autodock_outputs.py).

Note #3: Docking outputs with Gold, Glide, Surflex and Flex algorithms are, unfortunately, not publicly available. They have been kindly made available to us by [Dr. Liliane Mouawad](https://science.institut-curie.org/research/biology-chemistry-of-radiations-cell-signaling-and-cancer-axis/cmbc/chemistry-and-modelling-for-protein-recognition/team-members/?mbr=liliane-mouawad) and are from this [paper](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-016-0167-x). To enable reproduction of our paper results, we make available our computed performance metrics for each of these methods and each target protein in DUD-E.

Note #4: If you manually download and extract the data you might need to update the data paths in the notebooks.

The following files also need to be manually downloaded, if you don't use the provided `download_extract_data.sh` script. 
* [PDBBind v.2019 general set target data](https://storage.googleapis.com/denvis_v1_data/INDEX_general_PL_data.2019) (save into `data/pdbbdind`)
* [DENVIS inference times](https://storage.googleapis.com/denvis_v1_outputs/denvis_times.tar.gz) (extract into `data/times`)
* [DeepDTA inference times](https://storage.googleapis.com/denvis_v1_outputs/deepdta_times.tar.gz) (extract into `data/times`)

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
* [Benchmark](notebooks/01_Benchmark.ipynb): Virtual screening benchmark on DUD-E dataset (Figures 3, 4; Tables 3, 4, S1, S2, S3).
* [Ablation studies](notebooks/02_Ablation_studies.ipynb): Ablation studies for DENVIS model (Figures 5, 6; Tables 6, 7).
* [Performance metrics](notebooks/03_Performance_metrics.ipynb): Analysis of virtual screening performance metrics (Figure 7).
* [Ensemble tuning](notebooks/04_Ensemble_tuning.ipynb): Virtual screening performance vs. number of base models in multi-run ensembles (Figure S2).
* [PDBbind affinity distribution](notebooks/05_PDBbind_affinity_distribution.ipynb): Target distribution of PDBbind v.2019 general set for three binding affinity metrics (Kd, Ki, IC50) (Figure S1).
* [Inference times](notebooks/06_Inference_times.ipynb): Analysis of inference times with DENVIS and DeepDTA (Table 5).
