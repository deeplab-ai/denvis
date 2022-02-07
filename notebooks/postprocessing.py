import warnings

import numpy as np
from scipy.special import expit as sigmoid


def combine_outputs(results, y_aff_weight=0.0, y_kd_weight=0.0,
                    y_ki_weight=0.0, y_ic50_weight=0.0, use_clf=False,
                    clf_strategy=None):
    """
    Combines potentially several network output predictions into a 1D final
    prediction.

    Args:
        results: pd.DataFrame
            Results DataFrame with scores for multiple outputs (e.g.
            `y_score_aff`, `y_score_Kd`, `y_score_Ki`, `y_score_IC50`,
            `y_score_clf`).

        y_aff_weight: float, optional (default: 0.0)
            Weight for `y_score_aff` output, corresponding to combined binding
            metric regression output. If this is set to a non-zero value, it is
            expected that all of {`y_kd_weight`, `y_ki_weight`,
            `y_ic50_weight`} will be `0.0`. Otherwise a warning will be issued.

        y_kd_weight: float, optional (default: 0.0)
            Weight for `y_score_aff` output, corresponding to combined binding
            metric regression output.

        y_ki_weight: float, optional (default: 0.0)
            Weight for `y_score_aff` output, corresponding to combined binding
            metric regression output.

        y_ic50_weight: float, optional (default: 0.0)
            Weight for `y_score_aff` output, corresponding to combined binding
            metric regression output.

        use_clf: boolean, optional (default: False)
            Whether to use the classification output if available. To use only
            the classification output , this should be set to `True` and all of
            {`y_aff_weight`, `y_Kd_weight`, `y_Ki_weight`, `y_IC50_weight`}
            should be set to `0.0`.

        clf_strategy: str {None, 'soft', 'hard'}, optional (default: None)
            When set to `soft`, the combined regression score for each protein-
            ligand pair will be scaled with the corresponding classification
            probability. When set to `hard`, the scores of protein ligand pairs
            with binding probability will be set to zero, and the rest will
            remain unchanged. If classification output is not used or if only
            the classification output is used (i.e., all regression weights are
            set to `0.0`), this should be set to `None`.

    Returns:
        results: pd.DataFrame
            Results DataFrame with final prediction (`y_score`).
    """

    # Argument checking: raise Exception in case of negative weights
    for weight, weight_name in zip(
            [y_aff_weight, y_kd_weight, y_ki_weight, y_ic50_weight],
            ['y_aff_weight', 'y_Kd_weight', 'y_Ki_weight', 'y_IC50_weight']):
        if weight < 0.0:
            raise ValueError(f'Non-zero weights are only supported, but '
                             f'``{weight_name}`` parameter was set to'
                             f'{weight}.')

    # Argument checking: raise Exception if output specified but not available
    for weight, weight_name, output_name in zip(
            [y_aff_weight, y_kd_weight, y_ki_weight, y_ic50_weight, use_clf],
            ['y_aff_weight', 'y_kd_weight', 'y_ki_weight', 'y_ic50_weight',
             'use_clf'],
            ['y_score_aff', 'y_score_Kd', 'y_score_Ki', 'y_score_IC50',
             'y_clf']):
        if weight and (output_name not in results):
            raise ValueError(
                f"You have specified that the ``{output_name}`` output should"
                f"be used (``{weight_name}`` parameter was set to"
                f"``{weight}``), but the output is not available in the"
                f"results DataFrame.")

    # Issue warning if final output already computed (old screening results)
    if 'y_score' in results:
        warnings.warn(
            "Final output scores already computed (possibly due to screening "
            "results having been produced prior to this implementation). The "
            "final scores will now be overridden.")

    # Issue warning if both `y_aff_weight` and one of {`y_kd_weight`,
    # `y_ki_weight, `y_ic50_weight`} are non-negative.
    if y_aff_weight > 0 and (y_kd_weight > 0 or y_ki_weight > 0 or
                             y_ic50_weight > 0):
        warnings.warn(
            "Both `y_aff_weight` and at least one of {``y_kd_weight``,"
            "``y_ki_weight``, ``y_ic50_weight``} were set to larger than zero."
            "Are you sure you want to use both the aggregated and individual"
            "network outputs?")

    sum_weights_reg = y_aff_weight + y_kd_weight + y_ki_weight + y_ic50_weight

    # If all weights are set to 0.0 and use_clf is False raise an Exception
    if sum_weights_reg == 0.0:
        if not use_clf:
            raise ValueError("At least one of {``y_kd_weight``,"
                             "``y_ki_weight``, ``y_ic50_weight``} must be"
                             "non-zero, or ``use_clf``must be ``True``.")
        else:
            use_only_clf = True
    else:
        use_only_clf = False

    if not use_only_clf:  # At least one regression output
        y_score = np.zeros((results.shape[0],))
        if 'y_score_aff' in results:
            y_score = y_score + results['y_score_aff'] * y_aff_weight

        if 'y_score_Kd' in results:
            y_score = y_score + results['y_score_Kd'] * y_kd_weight

        if 'y_score_Ki' in results:
            y_score = y_score + results['y_score_Ki'] * y_ki_weight

        if 'y_score_IC50' in results:
            y_score = y_score + results['y_score_IC50'] * y_ic50_weight

        # Normalize
        y_score /= sum_weights_reg

        if use_clf:
            if 'y_clf' in results:
                if clf_strategy == 'soft':
                    y_score = y_score * sigmoid(results['y_clf'])
                elif clf_strategy == 'hard':
                    y_score = y_score * (results['y_clf'] > 0.)
                else:
                    raise ValueError("Argument ``clf_strategy`` has to be "
                                     "specified when using a combination of"
                                     "regression and classification outputs.")
            else:
                raise ValueError("Argument ``use_clf`` was set to `True`, but "
                                 "`y_clf` is not available in results "
                                 "DataFrame.")
    else:  # Only classification output
        if clf_strategy is not None:
            warnings.warn(f"Argument ``clf_strategy`` was set to"
                          f"{clf_strategy}, but will be ignored because all"
                          f"regression output weights were set to zero.")

        if 'y_clf' in results:
            y_score = sigmoid(results['y_clf'])
        else:
            raise ValueError("Argument ``use_clf`` was set to ``True``, but "
                             "``y_clf`` is not available in results"
                             "DataFrame.")

    # Return a copy of the DataFrame so that we don't affect the original
    results_out = results.copy(deep=True)
    results_out['y_score'] = y_score
    return results_out
