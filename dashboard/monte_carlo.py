import numpy as np
import pandas as pd

drop_rates = {
    "Mil-Spec": 0.7992,
    "Restricted": 0.1598,
    "Classified": 0.032,
    "Covert": 0.0064,
    "Special Item": 0.0026,
}

wear_ranges = {
    "Factory New": (0.00,0.07),
    "Min Wear": (0.07,0.15),
    "Field-Tested": (0.15,0.38),
    "Well-Worn": (0.38,0.45),
    "Battle-Scarred": (0.45,1.00),
}

def pick_item(case_df, specials_df=None):
    rarities = list(drop_rates.keys())
    probs = list(drop_rates.values())

    rarity = np.random.choice(rarities,p=probs)
    if rarity == "Special Item":
        if specials_df is not None:
            specials_df = specials_df[1:].dropna()
            return np.random.choice(specials_df), True
        else:
            candidates = case_df[case_df["Rarity"] == "Covert"]
            return candidates.sample(1).iloc[0], False
    
    else:
        candidates = case_df[case_df["Rarity"] == rarity]
        if len(candidates) == 0: return None
        return candidates.sample(1).iloc[0], False
    
def simulate_case(case_df, case_price, specials_df=None, n_trails=1000):
    res = []
    for _ in range(n_trails):
        item, special = pick_item(case_df, specials_df)
        wear_float = np.random.uniform(0,1)
        wear = ""
        for condition, (low,high) in wear_ranges.items():
            if low<=wear_float<=high:
                wear = condition

        num = np.random.uniform(0,1)
        if num <= 0.1:
            if wear == "Well-Worn":
                wear = "StatTrak Well Worn"
            else:
                wear = "StatTrak " + wear
        if special:
            price = item
        else:
            price = float(item[wear].replace("$",""))
        net = price- 2.50 - case_price
        res.append(net)
    return np.array(res)