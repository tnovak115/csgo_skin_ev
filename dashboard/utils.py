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
    "Factory New": 0.07,
    "Min Wear": 0.08,
    "Field-Tested": 0.23,
    "Well-Worn": 0.07,
    "Battle-Scarred": 0.55,
}

knife_ev = {
    "Fever": 580.83,
    "Kilowatt": 352.69,
    "Revolution": 618.75,
    "Recoil": 601.66,
    "Dreams & Nightmares": 587.80,
    "Riptide": 636.40,
    "Snakebite": 562.38,
    "Broken Fang": 562.38,
    "Fracture": 440.80,
    "Prisma 2": 685.00,
    "CS20": 371.54,
    "Shattered Web": 432.00,
    "Prisma": 633.33,
    "Danger Zone": 516.48,
    "Horizon": 392.40,
    "Clutch": 532.50,
    "Spectrum 2": 540.40,
    "Hydra": 549.00,
    "Spectrum": 540.4,
    "Glove": 549.00,
    "Gamma 2": 892.00,
    "Gamma": 878.26,
    "Chroma 3": 829.13,
    "Wildfire": 305.00,
    "Revolver": 591.20,
    "Shadow": 249.23,
    "Falchion": 296.92,
    "Anubis": None,
    "Chroma 2": 1083.81,
    "Chroma": 1083.91,
    "Vanguard": 676.00,
    "eSports 2014": 676.00,
    "Breakout": 1603.85,
    "Huntsman": 320.00,
    "Phoneix": 788.00,
    "Weapon Case 3": 788.00,
    "Winter Offensive": 788.00,
    "Weapon Case 2": 788.00,
    "Bravo": 788.00,
    "Weapon Case": 788.00,
}

def calc_ev(case_df, case_choice):
    for col in case_df.columns:
        if col not in ["Skin Name", "Rarity"]:
            case_df[col] = (
                case_df[col].astype(str)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .replace({"": np.nan, "nan": np.nan})
            )
            case_df[col] = pd.to_numeric(case_df[col], errors="coerce")

    ev_by_rarity = {}
    total_ev = 0.0

    for rarity, r_prob in drop_rates.items():
        sub = case_df[case_df["Rarity"] == rarity]
        if sub.empty:
            continue

        num_skins = len(sub)
        if num_skins == 0:
            continue

        skin_prob = r_prob / num_skins
        rarity_ev = 0.0

        for _, row in sub.iterrows():
            for wear, wear_prob in wear_ranges.items():
                if wear in row and pd.notna(row[wear]):
                    val = float(row[wear])
                    prob = skin_prob * wear_prob * .9
                    rarity_ev += val * prob

                st_col = f"StatTrak {wear}"
                if st_col in row and pd.notna(row[st_col]):
                    val = float(row[st_col])
                    prob = skin_prob * wear_prob * .1
                    rarity_ev += val * prob

        ev_by_rarity[rarity] = rarity_ev
        total_ev += rarity_ev

    price = knife_ev.get(case_choice)
    if price is not None:
        total_ev += price * drop_rates.get("Special Item", 0.0026)

    return total_ev


def monte_carlo_heatmap(case_df, num_cases_list, value_thresholds, stattrak_prob=0.1, n_sim=1000):
    """
    Simulate opening multiple cases and compute probability of reaching each threshold.
    
    :param case_df: DataFrame with skin prices and rarities
    :param num_cases_list: list of number of cases to simulate (e.g., [1,5,10,20])
    :param value_thresholds: list of value thresholds to check (e.g., [5,10,20,50,100])
    :param stattrak_prob: chance a skin is StatTrak
    :param n_sim: simulations per scenario
    :return: probability matrix (len(thresholds) x len(num_cases_list))
    """
    prob_matrix = np.zeros((len(value_thresholds), len(num_cases_list)))
    
    # Flatten all skin+wear options with probabilities
    events = []
    for rarity, r_prob in drop_rates.items():
        sub = case_df[case_df["Rarity"] == rarity]
        if sub.empty:
            continue
        num_skins = len(sub)
        skin_prob = r_prob / num_skins
        for _, row in sub.iterrows():
            for wear, wear_prob in wear_ranges.items():
                # Non-StatTrak
                if wear in row and pd.notna(row[wear]):
                    events.append((row[wear], skin_prob * wear_prob * (1-stattrak_prob)))
                # StatTrak
                st_col = f"StatTrak {wear}"
                if st_col in row and pd.notna(row[st_col]):
                    events.append((row[st_col], skin_prob * wear_prob * stattrak_prob))
    
    values = np.array([v for v, p in events])
    probs  = np.array([p for v, p in events])
    probs /= probs.sum()
    
    # Run simulations for each case count
    for j, n_cases in enumerate(num_cases_list):
        sims = np.random.choice(values, size=(n_sim, n_cases), p=probs)
        total_per_sim = sims.sum(axis=1)
        for i, threshold in enumerate(value_thresholds):
            prob_matrix[i,j] = (total_per_sim >= threshold).mean()
            
    return prob_matrix