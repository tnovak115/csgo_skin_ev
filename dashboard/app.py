import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import sys, os
import seaborn as sns
from monte_carlo import simulate_case
from utils import calc_ev, monte_carlo_heatmap
case_mapping = {
    "Anubis_Collection_Package": "Anubis",
    "Chroma_2_Case": "Chroma 2",
    "Chroma_3_Case": "Chroma 3",
    "Chroma_Case": "Chroma",
    "Clutch_Case": "Clutch",
    "CS20_Case": "CS20",
    "Danger_Zone_Case": "Danger Zone",
    "Dreams_&_Nightmares_Case": "Dreams & Nightmares",
    "eSports_2013_Winter_Case": "eSports 2013",
    "eSports_2014_Winter_Case": "eSports 2014",
    "Falchion_Case": "Falchion",
    "Fever_Case": "Fever",
    "Fracture_Case": "Fracture",
    "Gallery_Case": "Gallery",
    "Gamma_2_Case": "Gamma 2",
    "Gamma_Case": "Gamma",
    "Glove_Case": "Glove",
    "Horizon_Case": "Horizon",
    "Huntsman_Weapon_Case": "Huntsman",
    "Kilowatt_Case": "Kilowatt",
    "Operation_Bravo_Case": "Bravo",
    "Operation_Broken_Fang_Case": "Broken Fang",
    "Operation_Breakout_Weapon_Case": "Breakout",
    "Operation_Hydra_Case": "Hydra",
    "Operation_Phoneix_Weapon_Case": "Phoenix",
    "Operation_Riptide_Case": "Riptide",
    "Operation_Vanguard_Weapon_Case": "Vanguard",
    "Operation_Wildfire_Case": "Wildfire",
    "Prisma_2_Case": "Prisma 2",
    "Prisma_Case": "Prisma",
    "Recoil_Case": "Recoil",
    "Revolution_Case": "Revolution",
    "Revolver_Case": "Revolver",
    "Shadow_Case": "Shadow",
    "Shattered_Web_Case": "Shaattered Web",
    "Snakebite_Case": "Snakebite",
    "Spectrum_2_Case": "Spectrum 2",
    "Spectrum_Case": "Spectrum",
    "Winter_Offensive_Weapon_Case": "Winter Offensive",
}

#load data
@st.cache_data
def load_data():
    case_files = glob.glob("data/cases/*.csv")
    cases = {}
    for f in case_files:
        case_name = os.path.splitext(os.path.basename(f))[0]
        df = pd.read_csv(f)
        if "skin_name" in df.columns:
            df = df.set_index("skin_name")
        cases[case_name] = df

    specials_path = "data/csgo_special_items.csv"
    specials = pd.read_csv(specials_path, header=None)
    if "skin_name" in specials.columns:
        specials = specials.set_index("skin_name")

    case_prices = pd.read_csv("data/csgo_case_prices.csv")
    if "case_name" in case_prices.columns:
        case_prices = case_prices.set_index("case_name")

    return cases, specials, case_prices


# Load everything once
cases, specials, case_prices = load_data()
#sidebars
st.sidebar.title("⚙️ Case Simulator Controls")
case_choice = st.sidebar.selectbox("Choose a Case", list(cases.keys()))
num_sim = st.sidebar.slider("Number of Simulations", 1000, 100000, 10000, step=1000)
include_specials = st.sidebar.checkbox("Include Special Items?", value=True)

case_df = cases[case_choice]

#case general stuff
st.title(f"🎒 {case_mapping[case_choice]} Analysis")
st.subheader("Case Contents")

st.dataframe(case_df)

#drop rate
st.subheader("Case Rarity Composition")

rarity_counts = case_df["Rarity"].value_counts()
fig, ax = plt.subplots()
ax.pie(rarity_counts, labels=rarity_counts.index, autopct="%1.1f%%")
st.pyplot(fig)
#monte carlo sim
st.subheader("Monte Carlo Simulation")
price = case_prices.loc[case_prices["Case Name"] == case_mapping[case_choice], "Case Price"].values[0]

row = specials[specials[0]==case_mapping[case_choice]].iloc[0]
if pd.isna(row[1]):
    row = None
#drop stuff
outcomes = simulate_case(case_df,price,row, n_trails=num_sim)


fig, ax = plt.subplots(figsize=(10,6))
bin_num = int(num_sim/10)
ax.hist(outcomes, bins=bin_num, color="skyblue", edgecolor="black", alpha=0.7)

# Symmetric log scale: linear between -10 and 10, log beyond that
linthresh = 10
ax.set_xscale("symlog", linthresh=linthresh)
ax.set_yscale("symlog")
# Labels
ax.set_xlabel("Profit per Case Opening ($)")
ax.set_ylabel("Frequency")

# Expected value line
ev = calc_ev(case_df, case_mapping[case_choice]) - 2.50 - price
ax.axvline(ev, color="red", linestyle="--", label=f"EV = {ev:.2f}")

# Customize ticks: linear ticks between -linthresh and linthresh
linear_ticks = np.arange(-linthresh, linthresh+1, 2)  # every 2 dollars
all_ticks = np.concatenate([linear_ticks, ax.get_xticks()])  # include automatic log ticks
ax.set_xticks(all_ticks)
ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())  # show linear numbers

ax.legend()
st.pyplot(fig)
st.write(f"💰 Average Return: {np.mean(outcomes):.2f}")
st.write(f"📉 Median Return: {np.median(outcomes):.2f}")
st.write(f"📈 Chance of Profit: {np.mean(outcomes > (2.50+price)) * 100:.1f}%")  # example: case cost = $2.50

st.subheader("💎 Expected Value Comparison Across Cases")

# Compute EV for each case using friendly names from case_mapping
ev_dict = {}
for raw_case_name, df in cases.items():
    friendly_name = case_mapping.get(raw_case_name, raw_case_name)
    try:
        ev_dict[friendly_name] = calc_ev(df, friendly_name) - 2.50 - case_prices.loc[case_prices["Case Name"] == friendly_name, "Case Price"].values[0]
    except Exception as e:
        print(f"Error calculating EV for {friendly_name}: {e}")
        ev_dict[friendly_name] = np.nan

# Convert to Series and sort
ev_series = pd.Series(ev_dict).sort_values(ascending=False)

# Plot
fig, ax = plt.subplots(figsize=(14,6))
ax.bar(ev_series.index, ev_series.values, color="skyblue")
ax.set_ylabel("Expected Value ($)")
ax.set_title("EV Comparison Across All Cases")
ax.set_xticklabels(ev_series.index, rotation=45, ha="right")
st.pyplot(fig)

st.subheader("📊 Probability Heatmap: Skin Value Thresholds")

num_cases_list = [1, 5, 10, 20, 50, 100, 250]           # Number of cases opened
value_thresholds = [5, 10, 20, 50, 100, 200, 500, 1000]  # Value thresholds in $

prob_matrix = monte_carlo_heatmap(case_df, num_cases_list, value_thresholds, n_sim=5000)

fig, ax = plt.subplots(figsize=(10,6))
sns.heatmap(prob_matrix, annot=True, fmt=".2f", xticklabels=num_cases_list, yticklabels=value_thresholds, cmap="Blues", cbar_kws={'label':'Probability'})
ax.set_xlabel("Number of Cases Opened")
ax.set_ylabel("Total Skin Value Threshold ($)")
ax.set_title(f"Probability of Reaching Value Thresholds for {case_mapping[case_choice]}")
st.pyplot(fig)