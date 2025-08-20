import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
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
    specials = pd.read_csv(specials_path)
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
st.title(f"🎒 {case_choice} Analysis")
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

def simulate_case(prices, probs, n_sim):
    """Simulate opening a case n_sim times and return total values."""
    outcomes = np.random.choice(prices, size=n_sim, p=probs)
    return outcomes

#drop stuff
prices = case_df["price"].values
probs = [1/len(prices)] * len(prices)

outcomes = simulate_case(prices, probs, num_sim)

fig, ax = plt.subplots()
ax.hist(outcomes, bins=20, edgecolor="black")
ax.set_title("Distribution of Returns per Case")
st.pyplot(fig)

st.write(f"💰 Average Return: {np.mean(outcomes):.2f}")
st.write(f"📉 Median Return: {np.median(outcomes):.2f}")
st.write(f"📈 Chance of Profit: {np.mean(outcomes > 2.50) * 100:.1f}%")  # example: case cost = $2.50

#breaking even
st.subheader("Break-Even Over Multiple Cases")

cases_opened = np.arange(1, 201)
expected_returns = np.cumsum(np.random.choice(prices, size=(len(cases_opened),), p=probs))

fig, ax = plt.subplots()
ax.plot(cases_opened, expected_returns, label="Total Return")
ax.plot(cases_opened, cases_opened * 2.50, label="Total Cost")  # example cost = $2.50
ax.legend()
st.pyplot(fig)

#special item
st.subheader("Special Item Analysis")
if include_specials and not specials.empty:
    st.dataframe(specials.head())
    st.write(f"Average Special Item Price: {specials['price'].mean():.2f}")
else:
    st.info("This case does not contain special items.")

#comparison
st.subheader("Compare Two Cases")

col1, col2 = st.columns(2)
with col1:
    compare_case1 = st.selectbox("Case 1", list(cases.keys()), key="c1")
with col2:
    compare_case2 = st.selectbox("Case 2", list(cases.keys()), key="c2")

if compare_case1 != compare_case2:
    avg1 = cases[compare_case1]["price"].mean()
    avg2 = cases[compare_case2]["price"].mean()
    st.write(f"📊 {compare_case1} avg item price: {avg1:.2f}")
    st.write(f"📊 {compare_case2} avg item price: {avg2:.2f}")