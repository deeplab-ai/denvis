# Deep Neural Virtual Screening (DENVIS)

# Virtual screening inference REST API (Web service)

We provide a webservice that performs inference for a specified protein and a small colection of ligands (maximum of 100 ligands).
To extract the protein pocket that will be used for virtual screening, a protein and a crystal ligand structure must be specified.

## 1. Data

### 1.1 Instructions on how to set-up target data

The following data have been used for training and validation of DENVIS v1.0 models:
* [PDBBind v.2019 general set](https://storage.googleapis.com/denvis_v1_data/pdbbind_v2019_general.tar.gz) (1.8G)
* [PDBBind v.2019 refined set](https://storage.googleapis.com/denvis_v1_data/pdbbind_v2019_refined.tar.gz) (410M)
* [PDBBind v.2019 core set](https://storage.googleapis.com/denvis_v1_data/pdbbind_v2019_core.tar.gz) (28M)
* [TOUGH-M1](https://storage.googleapis.com/denvis_v1_data/tough_m1.tar.gz) (895M)
* [DUD-E](https://storage.googleapis.com/denvis_v1_data/dude.tar.gz) (10M)
* [Lit-PCBA](https://storage.googleapis.com/denvis_v1_data/Lit-PCBA.tar.gz) (47M)

These contain proteins, crystal ligands as well as the pockets extracted using the crystal ligand.
The protein `.pdb` files provided here can be directly used as input to the Web service.

#### Example: download DUD-E proteins
```bash
mkdir -p webservice_data/dude; cd webservice_data/dude
wget https://storage.googleapis.com/denvis_v1_data/dude.tar.gz
tar xzvf dude.tar.gz; rm dude.tar.gz
cd ../../
```
### 1.2 Instructions on how to set-up ligand data

You can use any `.sdf` file as input to the Web service, but only the first 100 ligands will be screened.
One source of such files is [dude.docking.org](http://dude.docking.org/).

Note: if you wish to exactly reproduce our results in DUD-E (see below), we recommend also running the deduplication script `drop_sdf_duplicates.py` on the `.sdf` file before making the request. This is done because the `.sdf` files provided in [dude.docking.org]('http://dude.docking.org') contain ligands with duplicate IDs, which we have removed.

#### Example: download a ligands file from DUD-E
```bash
wget http://dude.docking.org/targets/aa2ar/actives_final.sdf.gz
gzip -d actives_final.sdf.gz
mv actives_final.sdf webservice_data
```

##### Run the deduplication script to remove duplicates(ligands with the same ID) from the `.sdf` file
```bash
python scripts/drop_sdf_duplicates.py webservice_data/actives_final.sdf -o webservice_data/ligands_dedup.sdf
```

## 2. Inference via HTTP requests 

The Web service accepts the following inputs:
* protein: a protein file in a `.pdb` format. We suggest using the ones we have provided (see previous section), as we download all protein data from PDB using `moleculekit`. As a result, there might be slight differences between our provided data and the ones that are provided by various database portals (e.g. DUD-E, PDBbind etc.).
* crystal_ligand: a ligand in `.mol2` format. This should be taken from the protein-ligand complex and is used to specify the protein pocket. We do not calculate a screening score for this ligand.
* ligand: a library of ligands in `.sdf` format. If you wish to reproduce the results of our paper, you can download these from [dude.docking.org]('http://dude.docking.org') and use the [provided deduplication script](scripts/drop_sdf_duplicates.py) (see above).
Note: only the first 100 ligands in the file will be screened.

You also need to specify the model you wish to use for the virtual screening. The names represent the database that our models have been trained on, and we currently support the following options:
* `pdbbind_2019_refined`
* `pdbbind_2019_general`

For example, specify  `model=pdbbind_2019_refined` when making the request to run inference using the models trained on PDBbind v2019 refined set.

The output is a pandas `DataFrame` in `json` format and can be loaded using `pandas.read_json()`.

After the data has been prepared, we can make the request using the following API:
Note: the request can take ~1-2 minutes (depending on the size of the input protein) to complete due to the computationally expensive surface pre-processing step.
### Make the request and store the output in a json file
From a Unix-like terminal (e.g. Linux/Mac) execute:
```bash
curl --ipv4 -k -F model=pdbbind_2019_refined -F protein=@"webservice_data/dude/all/aa2ar/receptor.pdb" -F crystal_ligand=@"webservice_data/dude/all/aa2ar/crystal_ligand.mol2" -F ligand=@"webservice_data/ligands_dedup.sdf" -H "Content-Type: multipart/form-data" -X POST https://denvis.deeplab.ai/screen > webservice_data/aa2ar_denvis_webservice.json
```

## 3. Demo
We provide a [demo notebook](notebooks/07_Webservice_output_analysis.ipynb) that parses the output for a request on a specified target from the DUD-E database, and compares it to the inference scores we provide from to reproduce the results from our DENVIS v1.0 publication (see below).


# DENVIS v1.0 publication results reproduction
## 1. Download output scores

It is recommended that you run `download_extract_data.sh` to download and extract all output data/scores used in the Benchmark and the ablation studies.

Alternatively, you can manually download the following DUD-E output scores and extract into `data/outputs` folder:
* [DENVIS](https://storage.googleapis.com/denvis_v1_outputs/denvis_outputs.tar.gz) (3.2G)
* [DeepDTA](https://storage.googleapis.com/denvis_v1_outputs/deepdta_outputs.tar.gz) (939M)
* [AutoDock Vina](https://storage.googleapis.com/denvis_v1_outputs/vina_outputs.tar.gz) (142M)
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
It is recommended you create a `conda` environment using the provided file (tested on macOS only):
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
* `tensorboard`

The followng package is also required for running the optional `parse_autodock_outputs.py` script.
* `click`


Example using `conda`:
```bash
conda create -n denvis python=3.7 numpy scipy pandas scikit-learn rdkit matplotlib seaborn pingouin pyarrow click tqdm jupyter tensorboard -c conda-forge -c rdkit
```

## 3. Run notebooks
* [Benchmark DUD-E](notebooks/01_Benchmark_DUDE.ipynb): Virtual screening benchmark on DUD-E dataset (Figures 3, 4; Tables 3, 4, S1, S2, S3).
* [Ablation studies](notebooks/02_Ablation_studies.ipynb): Ablation studies for DENVIS model (Figures 5, 6; Tables 6, 7).
* [Performance metrics](notebooks/03_Performance_metrics.ipynb): Analysis of virtual screening performance metrics (Figure 7).
* [Ensemble tuning](notebooks/04_Ensemble_tuning.ipynb): Virtual screening performance vs. number of base models in multi-run ensembles (Figure S2).
* [PDBbind affinity distribution](notebooks/05_PDBbind_affinity_distribution.ipynb): Target distribution of PDBbind v.2019 general set for three binding affinity metrics (Kd, Ki, IC50) (Figure S1).
* [Inference times](notebooks/06_Inference_times.ipynb): Analysis of inference times with DENVIS and DeepDTA (Table 5).
* [Web service demo](notebooks/07_Webservice_output_analysis.ipynb): Demonstration of parsing output from the Web service (REST API) and comparison with the results from the DENVIS v1.0 publication.

## 4. Summary
To reproduce the DENVIS paper results, execute the following commands one at a time in a Unix-like terminal (e.g. Linux/Mac). 
```bash
git clone git@github.com:deeplab-ai/denvis.git  # Clone repo
cd denvis # Enter dir
chmod +x download_extract_data.sh && bash download_extract_data.sh  # Execute data download script
conda env create -f conda_env.yml # Create conda env
conda activate denvis  # Activate conda env
jupyter lab  # Launch Jupyter server to run notebooks
```

### Optional
In order to parse the AutoDock Vina results from scratch, execute the following commands, again one at a time (note that this step is not required as the parsed data are provided):
```bash
cd data/outputs/vina_outputs
mkdir docked_dude
wget http://bits.csb.pitt.edu/files/docked_dude.tar
tar -xvf docked_dude.tar -C docked_dude
rm docked_dude.tar
cd ../../../scripts
conda activate denvis
python parse_autodock_outputs.py 
```
