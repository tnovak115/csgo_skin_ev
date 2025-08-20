import numpy as np
import pandas as pd

drop_rates = {
    "Mil-Spec": 0.7992,
    "Restricted": 0.1598,
    "Classified": 0.032,
    "Covert": 0.0064,
    "Special Item": 0.0026,
}

def pick_item(case_df, case_prices, specials_df=None):
    rarities = list(drop_rates.keys())
    