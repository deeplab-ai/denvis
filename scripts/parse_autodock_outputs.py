import pandas as pd
from rdkit import Chem
import os
from tqdm import tqdm
import click
import gzip
import shutil

"""
Parses docked dude data downloaded from:
http://bits.csb.pitt.edu/files/docked_dude.tar used in the paper:
https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0220113
and saves them in a csv format.
"""


@click.command()
@click.option('--output_path',
                default='../data/outputs/vina_outputs/dude.csv')
@click.option('--docked_dude_path',
              default='../data/outputs/vina_outputs/docked_dude')
def parse_docked_dude_vina(output_path, docked_dude_path):

    # need to provide these two arguments but
    # their value is not important because we dont use the
    # actual molecule here
    remove_hs = True
    sanitize = False

    ligand_id = []
    target_id = []
    y_score = []
    y_true = []

    for target in tqdm(os.listdir(docked_dude_path)):
        for file in os.listdir(os.path.join(docked_dude_path, target)):
            abs_path = os.path.join(docked_dude_path, target, file)
            if file.startswith('actives'):
                y = 1
            elif file.startswith('decoys'):
                y = 0
            else:
                print(f'file {abs_path} not in correct form')
                continue

            # Unzip data and save into new file because SDMolSupplier takes
            # filepath as input argument only
            save_fn = abs_path[:-3]  # remove .gz file extension
            with gzip.open(abs_path, 'rb') as f_in:
                with open(save_fn, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            supplier = Chem.SDMolSupplier(save_fn, removeHs=remove_hs,
                                          sanitize=sanitize)
            for mol in supplier:
                vina_score = mol.GetProp('minimizedAffinity')
                ligand_name = mol.GetProp('_Name')

                ligand_id.append(ligand_name)
                target_id.append(target)
                y_score.append(vina_score)
                y_true.append(y)

            os.remove(save_fn)

    df_vina = pd.DataFrame()
    df_vina['target_list'] = target_id
    df_vina['ligand_list'] = ligand_id
    df_vina['score_list'] = y_score
    df_vina['y_list'] = y_true

    df_vina.to_csv(output_path, index=False)


if __name__ == '__main__':
    parse_docked_dude_vina()
