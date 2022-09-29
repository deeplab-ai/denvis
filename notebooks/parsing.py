import os
import re

import json
from tqdm import tqdm
import numpy as np
import pandas as pd


def parse_results_denvis(path, metadata_path=None, target_binary=True):
    """
    Parses screening results from (possibly) multiple runs/checkpoints into a
    single DataFrame and metadata into an additional DataFrame.

    Args:
        path: str
            Path of results saved in json format.

        metadata_path: str, optional (default: None)
            Metadata path. Does not apply to the case ``fmt == 'old'``.

        target_binary: bool, optional (default: True)
            Whether the target variable should be boolean.

    Returns:
        results: pd.DataFrame
            Results DataFrame with the following columns:
            `['target_id', 'ligand_id', 'y_true', 'y_score',
            'version', 'ckpt']`.

        metadata: pd.DataFrame
            Inference metadata, including checkpoint path, inference times etc.
            If ``metadata_path`` is not specified it will be ``None``.
    """

    results_df = pd.read_parquet(path)
    if metadata_path is not None:
        metadata = _read_format_metadata(metadata_path)
    else:
        metadata = None

    # Convert `y_true` to boolean if required
    if target_binary:
        results_df['y_true'] = results_df['y_true'].astype(bool)

    return results_df.reset_index(drop=True), metadata


def _read_metadata(path):
    """Reads and returns the metadata file (new format) into a nested dict. """
    with open(path) as f:
        metadata = json.load(f)

    return metadata


def _format_metadata(metadata):
    """Converts metadata from nested dict to pd.DataFrame format. This applies
    to both the old as well as new metadata formats. """
    metadata_df = pd.DataFrame.from_dict(
        {(i, j): metadata[i][j]
         for i in metadata.keys()
         for j in metadata[i].keys()},
        orient='index')
    # Provide MultiIndex names and re-index using single index
    metadata_df.index.names = ['version', 'ckpt']
    metadata_df = metadata_df.reset_index(level=[0, 1])
    # Get rid of prefixes in version and ckpt columns
    for col in ['version', 'ckpt']:
        metadata_df[col] = metadata_df[col].str.split('_').str[-1]

    return metadata_df


def _read_format_metadata(path):
    """Combines reading and formatting the metadata file (new format). """
    return _format_metadata(_read_metadata(path))


def parse_results_vina(path, reduce='max'):
    """
    Parses VINA screening results.

    Args:
        path: str
            Path of results saved in json format.

        reduce: str, {'max', 'mean', None}
            If `max`, the maximum score for each target-ligand pair
            will be returned only. If `mean`, the mean score  will
            be returned. If `None`, all scores (corresponding to all
            docking positions) will be returned.

    Returns:
        results_df: pd.DataFrame
            Results DataFrame with the following columns:
            `['target_id', 'ligand_id', 'y_true', 'y_score',
            'version', 'ckpt']`.
    """
    # First column is index --> discard
    results_df = pd.read_csv(path)
    # Compatible column names
    results_df = results_df.rename(columns={
        'target_list': 'target_id',
        'ligand_list': 'ligand_id',
        'y_list': 'y_true',
        'score_list': 'y_score'})

    results_df['y_score'] = -results_df[
        'y_score']  # Scores are stored as negative
    results_df = target_ligand_pair_reduction(results_df, reduce)
    return results_df[
        ['target_id', 'ligand_id', 'y_true', 'y_score']]  # Reorder columns


def parse_results_gnina(path):
    """
    Parses GNINA screening results.

    Args:
        path: str
            Path of results saved in json format.

    Returns:
        results_df: pd.DataFrame
            Results DataFrame with the following columns:
            `['target_id', 'ligand_id', 'y_true', 'y_score',
            'version', 'ckpt']`.
    """
    results_df = pd.read_csv(
        path,
        delimiter=' ',
        header=None,
        usecols=range(4),  # Discard last column --> model name
        names=['y_true', 'y_score', 'target_id', 'ligand_id'])

    return results_df[
        ['target_id', 'ligand_id', 'y_true', 'y_score']]  # Reorder columns


def parse_results_rf_score(path, reduce='max', prog_bar=False):
    """
    Parses RF-score screening results.

    Args:
        path: str
            Path of results saved in json format.

        reduce: str, {'max', 'mean', None}
            If `max`, the maximum score for each target-ligand pair
            will be returned only. If `mean`, the mean score  will
            be returned. If `None`, all scores (corresponding to all
            docking positions) will be returned.

        prog_bar: bool (default: False)
            Whether to display progress bar while parsing results.

    Returns:
        results_df: pd.DataFrame
            Results DataFrame with the following columns:
            `['target_id', 'ligand_id', 'y_true', 'y_score',
            'version', 'ckpt']`.
    """
    return _parse_results_rf_nn_score(
        path=path, reduce=reduce, method='rfscore',
        prog_bar=prog_bar)


def parse_results_nn_score(path, reduce='max', prog_bar=False):
    """
    Parses NN-score screening results.

    Args:
        path: str
            Path of results saved in json format.

        reduce: str, {'max', 'mean', None}
            If `max`, the maximum score for each target-ligand pair
            will be returned only. If `mean`, the mean score  will
            be returned. If `None`, all scores (corresponding to all
            docking positions) will be returned.

        prog_bar: bool (default: False)
            Whether to display progress bar while parsing results.

    Returns:
        results_df: pd.DataFrame
            Results DataFrame with the following columns:
            `['target_id', 'ligand_id', 'y_true', 'y_score',
            'version', 'ckpt']`.
    """
    return _parse_results_rf_nn_score(
        path=path, reduce=reduce, method='nnscore3',
        prog_bar=prog_bar)


def _parse_results_rf_nn_score(path, method, reduce, prog_bar):
    """Helper function implementing parsing for RF and NN score. """
    def process_row(row, target_id):
        """Implements logic for parsing results from a single row. """
        ligand = row['ligand_id']
        splitted = re.split('_|.pdbqt', ligand)
        if len(splitted) == 4:  # expected
            ligand_type, ligand_id, docking_id, _ = splitted
            y_true = 1 if ligand_type == 'active' else 0
            return target_id, ligand_id, int(y_true), row['y_score'], int(
                docking_id)
        elif len(splitted) == 1:  # return None for problematic entries
            return [None] * 5

    columns = ['target_id', 'ligand_id', 'y_true', 'y_score', 'docking_id']
    results_df = pd.DataFrame(columns=columns)
    targets = os.listdir(path)
    target_iter = tqdm(targets) if prog_bar else targets
    for target in target_iter:
        path_target = os.path.join(path, target, 'pdbqt', method)
        tmp = pd.read_csv(path_target, delimiter=' ', header=None,
                          names=['ligand_id', 'y_score'])
        results_df_tmp = pd.DataFrame(columns=columns)
        results_df_tmp[['target_id', 'ligand_id', 'y_true', 'y_score',
                        'docking_id']] = \
            tmp.apply(lambda row: process_row(row, target), axis=1,
                      result_type='expand')
        results_df = pd.concat((results_df, results_df_tmp), axis='index')

    results_df['y_true'] = pd.to_numeric(
        results_df['y_true'])  # Convert `y_true` to numeric (int)

    if method == 'rfscore':
        results_df = results_df.dropna()  # Discard invalid entries (null)

    results_df = target_ligand_pair_reduction(results_df, reduce)
    return results_df[
        ['target_id', 'ligand_id', 'y_true', 'y_score']]  # Reorder columns


def parse_results_deeppurpose(path, reduce='max'):
    """
    Parses screening results into a single DataFrame.

    Args:
        path: str
            Path of results saved in json format.

        reduce: functional (default: `max`)
            What function to use to process protein-ligand pairs with more than
            one scores (e.g., due to having more than one one chains in the
            protein amino-acid sequence).

    Returns:
        results_df: pd.DataFrame
            Results DataFrame with the following columns:
            `['target_id', 'ligand_id', 'y_true', 'y_score']`.

        paths: dict
            Hierarchical dict with model paths.
    """
    # Load data in json format
    with open(path) as f:
        results_json = json.load(f)

    results_df = pd.read_json(results_json)

    # Reduction for multiple chains
    results_df = target_ligand_pair_reduction(results_df, reduce)

    return results_df.reset_index(drop=True)


def target_ligand_pair_reduction(results_df, reduce):
    """Helper function implementing the target/ligand pair reduction logic. """
    # Reduction logic
    if reduce == 'max':
        results_df = results_df.groupby(by=['target_id', 'ligand_id']).max(
            numeric_only=True).reset_index(drop=False)
    elif reduce == 'mean':
        results_df = results_df.groupby(by=['target_id', 'ligand_id']).mean(
            numeric_only=True).reset_index(drop=False)
    else:
        raise ValueError(f"Unsupported reduce argument f{reduce}.")

    return results_df

def process_target_id(results_df, dataset):
    """Decouples the `target_id` column into two columns `target_id` and
    target_pdb`. This is required because LIT-PCBA targets are saved as:
    <lit_pcba_id>#<pdb_code>. For other datasets it just returns the input.

    Args:
        results_df: pd.DataFrame
            Results DataFrame with the following columns:
            `['target_id', 'ligand_id', 'y_true', 'y_score',
            'version', 'ckpt']`.

        dataset: str
            Dataset name.

    Returns:
        results_df: pd.DataFrame
            Results DataFrame with the following columns:
            `['target_id', 'target_pdb', ligand_id', 'y_true', 'y_score',
            'version', 'ckpt']`.
    """
    if dataset == 'LIT-PCBA':
        def process_row(row):
            target = row['target_id']
            target_id, target_pdb = target.split('#')
            return target_id, target_pdb

        results_df[['target_id', 'target_pdb']] = results_df.apply(
            lambda row: process_row(row), axis=1, result_type='expand')

    return results_df
