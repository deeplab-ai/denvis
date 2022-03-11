import click
import pandas as pd

"""
Removes duplicate entries from an .sdf ligand library file.
Duplicate entries are ones that have the same ID in the file.
It keeps the last entry in the file.
"""


@click.command()
@click.argument('sdf_file', type=str)
@click.option('--output_file', '-o', type=str, default='ligands_dedup.sdf')
def drop_sdf_duplicates(sdf_file, output_file):
    assert sdf_file.endswith(".sdf")
    assert output_file.endswith(".sdf")

    # Read sdf file
    with open(sdf_file, "r") as f:
        contents = f.readlines()

    ids = []
    mols = []

    start_of_mol = 0
    end_of_mol = None
    for i, line in enumerate(contents):
        # mols are separated with $$$$ in the sdf file
        if line == "$$$$\n":
            end_of_mol = i
            ids.append(contents[start_of_mol])
            # joins all the lines that correspond to a single molecule
            # and saves them in the mols list
            mols.append("".join(contents[start_of_mol:end_of_mol + 1]))
            # re init for next
            start_of_mol = i + 1

    # save the ids into a DataFrame for easy deduplication
    id_df = pd.DataFrame({"ligand_id": ids})

    # drop duplicates, keeping last
    id_df = id_df.drop_duplicates(subset='ligand_id', keep="last")
    ligands_to_keep = list(id_df.index)
    # save to new sdf file
    with open(output_file, "w") as f:
        for i, mol in enumerate(mols):
            if i in ligands_to_keep:
                f.write(mols[i])


if __name__ == '__main__':
    drop_sdf_duplicates()
