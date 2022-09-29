# Download data
wget -P data/outputs/ https://storage.googleapis.com/denvis_v1_outputs/denvis_outputs.tar.gz
wget -P data/outputs https://storage.googleapis.com/denvis_v1_outputs/deepdta_outputs.tar.gz
wget -P data/outputs https://storage.googleapis.com/denvis_v1_outputs/vina_outputs.tar.gz
wget -P data/outputs/gnina_outputs/dude http://bits.csb.pitt.edu/files/defaultCNN_dude.tar.gz
wget -P data/outputs/gnina_outputs/litpcba http://bits.csb.pitt.edu/files/defaultCNN_litpcba.tar.gz
wget -P data/outputs http://bits.csb.pitt.edu/files/rfnn_dude_scores.tgz
wget -P data/outputs https://storage.googleapis.com/denvis_v1_outputs/docking_performance_scores.tar.gz
wget -P data/pdbbind https://storage.googleapis.com/denvis_v1_data/INDEX_general_PL_data.2019
wget -P data/litpcba https://storage.googleapis.com/denvis_v1_data/lit_pcba_pdb_correspondence.json
wget -P data/times https://storage.googleapis.com/denvis_v1_outputs/denvis_times.tar.gz
wget -P data/times https://storage.googleapis.com/denvis_v1_outputs/deepdta_times.tar.gz

# Extract data and remove compressed files
cd data/outputs
for file in *.tar.gz; do tar xzvf "${file}" && rm "${file}"; done

# Extract RF/NN-score .tgz file into new dedicated and remove compressed files
mkdir rfnn_dude_scores && tar zxvf rfnn_dude_scores.tgz -C rfnn_dude_scores/ && rm rfnn_dude_scores.tgz

# Extract GNINA outputs (separately for DUD-E and LIT-PCBA)
cd gnina_outputs/dude
for file in *.tar.gz; do tar xzvf "${file}" && rm "${file}"; done
cd ../litpcba
for file in *.tar.gz; do tar xzvf "${file}" && rm "${file}"; done

# Extract inference time data and remove compressed files
cd ../../times
for file in *.tar.gz; do tar xzvf "${file}" && rm "${file}"; done

