import os
from typing import List

import pandas as pd

from configuration import Configuration

def export(config: Configuration, results: List[dict]):
    """
    Writes out a CSV file for the results.

    Parameters
    ----------
    config: Configuration
        A custom Configuration object containing important settings
    results: List[dict]
        A list of observations, each of which is a dictionary
    """

    dir = os.path.dirname(config.output_file)
    if not os.path.exists(dir):
        os.mkdir(dir)

    df = pd.DataFrame(results)

    df.to_csv(config.output_file)
