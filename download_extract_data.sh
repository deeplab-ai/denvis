# Download data
wget -P data/outputs/ https://storage.googleapis.com/denvis_v1_outputs/denvis_outputs.tar.gz
wget -P data/outputs https://storage.googleapis.com/denvis_v1_outputs/deepdta_outputs.tar.gz
wget -P data/outputs https://storage.googleapis.com/denvis_v1_outputs/vina_outputs.tar.gz
wget -P data/outputs http://bits.csb.pitt.edu/files/rfnn_dude_scores.tgz
wget -P data/outputs https://storage.googleapis.com/denvis_v1_outputs/docking_performance_scores.tar.gz

# Extract data
cd data/outputs
for file in *.tar.gz; do tar xzvf "${file}" && rm "${file}"; done

# Extract RF/NN-score .tgz file into new dir and remove
mkdir rfnn_dude_scores && tar zxvf rfnn_dude_scores.tgz -C rfnn_dude_scores/ && rm rfnn_dude_scores.tgz
