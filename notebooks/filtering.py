def target_intersection(targets):
    """
    Returns target intersection.

    Args:
        targets: iterable
            Iterable (list/tuple) of lists with arbitrary number of elements.

    Returns:
        targets_inter: list
            Intersection of targets from lists provided.
    """
    return list(set.intersection(*map(set, targets)))


def target_union(targets):
    """
    Returns target union.

    Args:
        targets: iterable
            Iterable (list/tuple) of lists with arbitrary number of elements.

    Return:
        targets_inter: list
            Union of targets from lists provided.
    """
    return list(set.union(*map(set, targets)))


def target_difference(targets_1, targets_2):
    """
    Returns difference between two iterables (e.g. list, sets) of targets.

    Args:
        targets_1: iterable
            Target set 1.

        targets_2: iterable
            Target set 2.

    Returns:
        target_diff: set
            Set with difference between Target set 1 and Target set 2.
    """
    return set(targets_1) - set(targets_2)


def filter_targets(results, targets):
    """
    Filters results DataFrame so that only specified targets are kept.

    Args:
        results: pd.DataFrame
            Results DataFrame that has column `target_id`.

        targets: list
            List of targets to keep.

    Returns:
        results_filtered: pd.DataFrame
            Filtered results DataFrame.
    """
    return results[results['target_id'].isin(targets)].reset_index(drop=True)