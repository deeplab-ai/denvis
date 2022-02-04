# denvis
Deep Neural Virtual Screening (DENVIS) inference API, outputs scores and paper results reproduction.

# Instructions
## Inference API [TODO]
### Pre-processig data
### Use HTTP requests to run inference for a specified model and a provided protein pocket-ligand pair.

## Reproduce paper results [TODO]
### Denvis v1.0 paper
1. Download DUD-E output scores and extract into `data/outputs` folder.
* [DENVIS](https://storage.googleapis.com/denvis_v1_outputs/denvis_outputs.tar.gz)
* [DeepDTA](https://storage.googleapis.com/denvis_v1_outputs/deepdta_outputs.tar.gz)
* [AutoDock Vina](https://storage.googleapis.com/denvis_v1_outputs/vina_outputs.tar.gz)
* [GNINA](http://bits.csb.pitt.edu/files/defaultCNN_dude.tar.gz)
* [RF-score & NN-score](http://bits.csb.pitt.edu/files/rfnn_dude_scores.tgz)

Note #1: GNINA, RF-score and NN-score scoring outputs for DUD-E are provided by [David Koes Lab](http://bits.csb.pitt.edu/) (links to original files are provided above).

Note #2: AutoDock Vina docking outputs for DUD-E are also provided from David Koes Lab from this [link](http://bits.csb.pitt.edu/files/docked_dude.tar). The results have been downloaded from the original link (5GB) and processed to extract the docking scores only, which are stored in `.csv` format in the link provided above.
