# Deep Neural Virtual Screening (DENVIS)

# Inference API
## 1. Data pre-processing [TODO]
## 2. Inference via HTTP requests [TODO]

# DENVIS v1.0 paper results reproduction [WIP]
  1. Download the following DUD-E output scores and extract into `data/outputs` folder.
* [DENVIS](https://storage.googleapis.com/denvis_v1_outputs/denvis_outputs.tar.gz)
* [DeepDTA](https://storage.googleapis.com/denvis_v1_outputs/deepdta_outputs.tar.gz)
* [AutoDock Vina](https://storage.googleapis.com/denvis_v1_outputs/vina_outputs.tar.gz)
* [GNINA](http://bits.csb.pitt.edu/files/defaultCNN_dude.tar.gz)
* [RF-score & NN-score](http://bits.csb.pitt.edu/files/rfnn_dude_scores.tgz)
* [Gold, Glide, Surflex, Flex]() [TODO]

Note #1: GNINA, RF-score and NN-score scoring outputs for DUD-E are kindly provided by [David Koes Lab](http://bits.csb.pitt.edu/) (original links provided above).
In case clicking any of these links does not initiate downloading, please try via using the `wget` command. 

Note #2: AutoDock Vina docking outputs for DUD-E are also provided in `.sdf` format from David Koes Lab. The results have been downloaded from the original [link](http://bits.csb.pitt.edu/files/docked_dude.tar) (5GB) and processed to extract the docking scores only, which are stored in `.csv` format in the link provided above. If you wish to extract the docking scores from the original `.sdf` files, download docked data from the original link and run the `parse_autodock_outputs.py` script (for this you might need the following extra python packages: `rdkit`, `click`, `tqdm`).

Note #3: Docking outputs with Gold, Glide, Surflex and Flex algorithms are, unfortunately, not publicly available. They have been kindly made available to us by [Dr. Liliane Mouawad](https://science.institut-curie.org/research/biology-chemistry-of-radiations-cell-signaling-and-cancer-axis/cmbc/chemistry-and-modelling-for-protein-recognition/team-members/?mbr=liliane-mouawad) and are from this [paper](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-016-0167-x). To enable reproduction of our paper results, we make available our computed performance metrics for each of these methods and each target protein in DUD-E.

2. Environment instructions / package requirements [TODO]
3. Running notebook instructions [TODO]
