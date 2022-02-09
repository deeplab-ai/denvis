from tqdm import tqdm
import numpy as np
import pandas as pd

from metrics import compute_auroc_scores


def compute_ensemble_scores(results, ckpt=False, version=False,
                            pair_id_cols=None, exclude_cols=None):
    """
    Computes average scores using ensembling.

    Args:
        results: pd.DataFrame
            Results DataFrame with scores from multiple models/checkpoints.

        ckpt: bool, optional (default: False)
            Whether to perform ensembling across multiple checkpoints.

        version: bool, optional (default: False)
            Whether to perform ensembling across multiple versions/runs.

        pair_id_cols: tuple, optional (default: ['target_id', 'ligand_id'])
            The columns that specifies a unique protein-ligand pair. Can be
            a list of arbitrary length. If there are non-numeric columns in the
            DataFrame that are not included here they will be dropped from the
            output DataFrame.

        exclude_cols: tuple, optional (default: ['y_true']
            These columns will be excluded from averaging computations.

    Returns:
        results: pd.DataFrame
            Results DataFrame with average scores using model/checkpoint
            ensembling.
    """
    if pair_id_cols is None:
        pair_id_cols = ['target_id', 'ligand_id']

    if exclude_cols is None:
        exclude_cols = ['y_true']

    non_avg_cols = pair_id_cols + exclude_cols  # excluded from averaging
    drop_columns = ['version', 'ckpt']  # will be dropped after ensembling
    if not version:
        non_avg_cols = non_avg_cols + ['version']
        drop_columns.remove('version')

    if not ckpt:
        non_avg_cols = non_avg_cols + ['ckpt']
        drop_columns.remove('ckpt')

    results = results.drop(columns=drop_columns)
    return results.groupby(by=non_avg_cols).mean(
        numeric_only=True).reset_index(drop=False)


def compute_level_ensemble_scores(results_atom, results_surface, atom_weight,
                                  use_target_intersection=False,
                                  pair_id_cols=None, exclude_cols=None):
    """
    Computes weighted average scores from atom-level and surface-level scores.
    Averages will be computed across all columns that have are of float type.

    Args:
        results_atom: pd.DataFrame
            DataFrame with results from atom-level model.

        results_surface: pd.DataFrame
            DataFrame with results from surface-level model.

        atom_weight: float
            Weight for atom-level model. Must satisfy
            0.<=weight_atom<=1.

        use_target_intersection: bool, optional (default: False)
            If `True`, only the target intersection of the atom and
            surface model will be used. If `False` for targets missing
            from one model, the scores from the other model will be used.

        pair_id_cols: tuple, optional (default: ['target_id', 'ligand_id'])
            The columns that specifies a unique protein-ligand pair. Can be
            a list of arbitrary length. If there are non-numeric columns in the
            DataFrame that are not included here they will be dropped from the
            output DataFrame.

        exclude_cols: tuple, optional (default: ['y_true']
            These columns will be excluded from averaging computations.

    Returns:
        results: pd.DataFrame
            DataFrame with ensemble results.
    """
    if pair_id_cols is None:
        pair_id_cols = ['target_id', 'ligand_id']

    if exclude_cols is None:
        exclude_cols = ['y_true']

    non_avg_cols = pair_id_cols + exclude_cols  # excluded from averaging

    # Intersection of two DataFrames (protein-ligand pairs)
    pairs_inter = pd.merge(results_atom, results_surface, how='inner',
                           on=pair_id_cols)
    # Indexes of unique atom-/surface-level entries
    atom_only_index = pd.concat((results_atom[pair_id_cols], pairs_inter[
        pair_id_cols])).drop_duplicates(keep=False).index
    surface_only_index = pd.concat((results_surface[pair_id_cols], pairs_inter[
        pair_id_cols])).drop_duplicates(keep=False).index
    # Unique atom/surface-level slices
    atom_only = results_atom.loc[
        atom_only_index]
    surface_only = results_surface.loc[
        surface_only_index]

    # Common pairs atom/surface-level slices
    atom_inter = results_atom.drop(index=atom_only_index)
    surface_inter = results_surface.drop(index=surface_only_index)
    # Scale atom/surface-level numerical outputs by specified weights
    atom_inter_weighted = pd.concat((
        atom_inter[non_avg_cols],
        atom_weight * atom_inter.drop(columns=non_avg_cols)),
        axis='columns')
    surface_inter_weighted = pd.concat((
        surface_inter[non_avg_cols],
        (1 - atom_weight) * surface_inter.drop(columns=non_avg_cols)),
        axis='columns')
    # Common df with weighted scores (every common pair appears in two rows)
    atom_surface_inter_weighted = pd.concat(
        (atom_inter_weighted, surface_inter_weighted), axis='index')
    # Compute average across same protein-ligand pairs. Weights have already
    # been applied so we can just use groupby().sum().
    atom_surface_inter_weighted = atom_surface_inter_weighted.groupby(
        by=non_avg_cols).sum(numeric_only=True).reset_index(
        drop=False)

    if use_target_intersection:
        atom_surface_ensemble = atom_surface_inter_weighted.sort_values(
            by=pair_id_cols).reset_index(drop=True)
    else:
        atom_surface_ensemble = pd.concat(
            (atom_only, surface_only, atom_surface_inter_weighted),
            axis='index').sort_values(by=pair_id_cols).reset_index(drop=True)

    return atom_surface_ensemble


def level_ensemble_grid_search(results_atom, results_surface,
                               atom_weight_grid=None, metric_avg_fun=None,
                               prog_bar=False):
    """
    Performs grid search to identify optimal weights for atom-level/surface-
    level ensembling using the micro-AUROC score as a validation metric.

    Args:
        results_atom: pd.DataFrame
            DataFrame with results from atom-level model.

        results_surface: pd.DataFrame
            DataFrame with results from surface-level model.

        atom_weight_grid: list, optional (default: [0.00, 0.01, ..., 1.00])
            Atom-level weights that will be evaluated.

        metric_avg_fun: callable
            It will be passed to `compute_auroc_scores`.

        prog_bar: bool, optional (default: False)
            If `True` a progress bar will be printed on the console.

    Returns:
        ensemble_auroc_micro: pd.DataFrame
            DataFrame with search results in tidy format. Each row corresponds
            to one evaluation. Columns are `[atom-level weight, surface-level
            weight, micro-AUROC]`.

    """
    if atom_weight_grid is None:
        atom_weight_grid = np.linspace(0., 1., 101)

    ensemble_auroc_micro = dict()
    iter_weights = tqdm(atom_weight_grid) if prog_bar else atom_weight_grid
    for atom_weight in iter_weights:
        res_tmp = compute_level_ensemble_scores(
            results_atom=results_atom,
            results_surface=results_surface,
            atom_weight=atom_weight)
        _, microauroc = compute_auroc_scores(res_tmp, avg_fun=metric_avg_fun)
        ensemble_auroc_micro[atom_weight] = microauroc

    # Convert to DF with scores and weights as columns (tidy format)
    ensemble_auroc_micro = pd.DataFrame(
        ensemble_auroc_micro.items(),
        columns=['atom-level weight', 'micro-AUROC'])
    # Insert an extra column with surface-level weights after the atom-level
    # weight column
    ensemble_auroc_micro.insert(
        loc=1, column='surface-level weight',
        value=(1.0 - ensemble_auroc_micro['atom-level weight']))
    ensemble_auroc_micro = ensemble_auroc_micro.reset_index(drop=True)

    return ensemble_auroc_micro
