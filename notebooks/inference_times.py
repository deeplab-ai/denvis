import json
import pandas as pd


def read_denvis_times(path, version=0, ckpt=0):
    """Returns DENVIS average time per protein-ligand pair.
   
    Args:
        path: str
            Path.
        
        version: int, optional (default=0)
            Version number.
        
        ckpt: int, optional (default=0)
            Checkpoint number.
        
    Returns:
        times: float
            Average inference time per protein-ligand pair.
    """
    with open(path) as f:
        results_json = json.load(f)
    
    return results_json['version_' + str(version)]['ckpt_' + str(ckpt)]['times']


def read_deepdta_times(path):
    """Returns DeepDTA average time per protein-ligand pair.
   
    Args:
        path: str
            Path.
        
    Returns:
        times: float
            Average inference time per protein-ligand pair.
    """
    times = pd.read_csv(path)
    return times['Times'].mean()