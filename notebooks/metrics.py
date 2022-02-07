import math
import numpy as np
from sklearn import metrics as skmetrics

from denvis.metrics import average_score_across_targets, bedroc_score, \
    ef_score, score_per_target

from rdkit.ML.Scoring.Scoring import CalcBEDROC


def ef_score(y_true, y_pred, alpha):
    """Enhancement factor score.

    EF-score is calculated as: EF_a  = NTB_a / (NTB_total x a), where NTB_a
    is the number of true binders observed among the a% top-ranked candidates
    selected by a given scoring function, NTB_total is the total number of
    true binders for a given target protein.

    See: https://doi.org/10.1021/acs.jcim.8b00545

    Args:
        y_true: 1d array-like
            Ground truth (correct) labels indicating whether the corresponding
            ligand binds to the target protein.

        y_pred: 1d array-like
            Predicted scores, one for each ligand, as returned by a scoring
            function.

        alpha: float, range (0, 1]
            Τop-ranking threshold (%). Set to ``0.01`` for EF1,
            ``0.1`` for EF10 and so on.

    Returns:
        score: float
            EF score for specified ``alpha``.
    """
    if not (0. < alpha <= 1.):
        raise ValueError("``alpha`` argument must be in range (0, 1] but {} "
                         "was provided.".format(alpha))

    # Sort in descending order and store indexes for labels sorting
    sort_ind = np.argsort(y_pred)[::-1]
    y_true, y_pred = y_true[sort_ind], y_pred[sort_ind]
    top_pred = y_true[0:math.ceil((len(y_true) * alpha))]
    return top_pred.sum() / (y_true.sum() * alpha)


def bedroc_score(y_true, y_pred, alpha):
    """Boltzmann-Enhanced Discrimination ROC score.

    Implementation of Boltzmann-Enhanced Discrimination ROC metric. This is a
    "weighted" ROC score assigning more weight on early recognition. Refer to
    paper below for details. This is  simply a wrapper function around the
    rdkit implementation.

    See: https://pubs.acs.org/doi/10.1021/ci600426e

    Args:
        y_true: 1d array-like
            Ground truth (correct) labels indicating whether the corresponding
            ligand binds to the target protein.

        y_pred: 1d array-like
            Predicted scores, one for each ligand, as returned by a scoring
            function.

        alpha: float
            Early recognition parameter.

    Returns:
        score: float
            BEDROC score for specified ``alpha``.
    """
    sort_ind = np.argsort(y_pred)[::-1]  # Descending order
    # BedROC only considers the ground truth vector sorted wrt predictions
    # but reshape to match the expected rdkit format (2D array)
    return CalcBEDROC(y_true[sort_ind].reshape(-1, 1), 0, alpha)


def average_score_across_targets(score, targets=None, avg_fun=np.mean):
    """Computes average score across specified target proteins. If target
    proteins are not specified the average will be computed across all targets.
    If `targets` is an empty iterable, `np.nan` will be returned.

    Args:
        score: dict
            Keys are target ids and values are corresponding scores.

        targets: list, optional (default: None)
            List with target ids to compute average on. If not provided,
            average will be computed across all targets.

        avg_fun: functional, optional (default: np.mean)
            Function that will be used to compute average score.

    Returns:
        score: float
            Mean score across target proteins.
    """
    if targets is None:
        return avg_fun(np.array([v for _, v in score.items()]))
    else:
        if len(targets) == 0:
            return np.nan
        else:
            return avg_fun(np.array([score[k] for k in targets]))


def score_per_target(y_true, y_score, y_target_id, scoring_fun, **kwargs):
    """Wrapper function that calculates a specified score for each target
    protein in a screening dataset.

    Args:
        y_true: 1d array-like
            Ground truth (correct) labels indicating whether the corresponding
            ligand binds to the target protein.

        y_score: 1d array-like
            Predicted scores, one for each ligand, as returned by a scoring
            function.

        y_target_id: 1d array-like
            Protein target id's.

        scoring_fun: callable
            Scoring function. It must follow the sklearn API, i.e., take as
            inputs a ``y_true`` and ``y_pred`` or ``y_score``
            array-like objects and return a single score value.

        **kwargs: key, value mappings
            These will be passed into the scoring function call to specify
            additional arguments.

    Returns:
        score: dict
            Keys are protein ids and values are corresponding scores. For
            targets for which a score cannot be computed (e.g.
            `sklearn.metrics.roc_auc_score` for which there are only positive/
            negative ground truth labels) a `nan` value is returned.
    """
    targets = set(y_target_id)
    score = dict()
    for target in targets:
        try:
            score[target] = scoring_fun(y_true[y_target_id == target],
                                        y_score[y_target_id == target],
                                        **kwargs)
        except ValueError:
            score[target] = np.nan

    return score


def compute_auroc_scores(results, avg_fun):
    """
    Computes AUROC metrics (per-target and micro-average).

    Args:
        results: pd.DataFrame
            Results DataFrame with one entry (row) per target-ligand pair.

        avg_fun: callable
            It will be passed to `average_score_across_targets`.

    Returns:
        auroc_per_target: dict
            One key-value pair target protein. Keys are target names and
            values are AUROC scores.

        auroc_micro: float
            Micro-AUROC score.
    """
    auroc_per_target = score_per_target(
        y_true=results['y_true'].values,
        y_score=results['y_score'].values,
        y_target_id=results['target_id'].values,
        scoring_fun=skmetrics.roc_auc_score)
    auroc_micro = average_score_across_targets(auroc_per_target,
                                               avg_fun=avg_fun)

    return auroc_per_target, auroc_micro


def compute_ef_scores(results, alpha, avg_fun):
    """
    Computes EF metrics (per-target and micro-average).

    Args:
        results: pd.DataFrame
            Results DataFrame with one entry (row) per target-ligand pair.

        alpha: float, range (0, 1]
            Τop-ranking threshold (%). Set to ``0.01`` for EF1,
            ``0.1`` for EF10 and so on.

        avg_fun: callable
            It will be passed to `average_score_across_targets`.

    Returns:
        ef_per_target: dict
            One key-value pair target protein. Keys are target names and
            values are AUROC scores.

        ef_micro: float
            Micro-EF score.
    """
    if not (0. < alpha <= 1.):
        raise ValueError("``alpha`` argument must be in range (0, 1] but {}"
                         "was provided.".format(alpha))

    ef_per_target = score_per_target(
        y_true=results['y_true'].values,
        y_score=results['y_score'].values,
        y_target_id=results['target_id'].values,
        scoring_fun=ef_score,
        alpha=alpha)
    ef_micro = average_score_across_targets(ef_per_target, avg_fun=avg_fun)

    return ef_per_target, ef_micro


def compute_pr_scores(results):
    """
    Computes precision-recall curve metrics (per-target and micro-average).

    Args:
        results: pd.DataFrame
            Results DataFrame with one entry (row) per target-ligand pair.

    Returns:
        pr_per_target: dict
            One key-value pair target protein. Keys are target names and
            values are precision-recall curve metrics.

        pr_macro: float
            Macro-precision-recall scores.
    """
    pr_per_target = score_per_target(
        y_true=results['y_true'].values,
        y_score=results['y_score'].values,
        y_target_id=results['target_id'].values,
        scoring_fun=skmetrics.precision_recall_curve)
    pr_macro = skmetrics.precision_recall_curve(
        y_true=results['y_true'].values,
        probas_pred=results['y_score'].values)

    return pr_per_target, pr_macro


def compute_bedroc_scores(results, alpha, avg_fun):
    """
    Computes BEDROC metrics (per-target and micro-average).

    Args:
        results: pd.DataFrame
            Results DataFrame with one entry (row) per target-ligand pair.

        alpha: float
            Early recognition parameter.

        avg_fun: callable
            It will be passed to `average_score_across_targets`.

    Returns:
        bedroc_per_target: dict
            One key-value pair target protein. Keys are target names and
            values are BEDROC scores.

        bedroc_micro: float
            Micro-BEDROC score.
    """

    bedroc_per_target = score_per_target(
        y_true=results['y_true'].values,
        y_score=results['y_score'].values,
        y_target_id=results['target_id'].values,
        scoring_fun=bedroc_score,
        alpha=alpha)
    bedroc_micro = average_score_across_targets(bedroc_per_target,
                                                avg_fun=avg_fun)

    return bedroc_per_target, bedroc_micro
