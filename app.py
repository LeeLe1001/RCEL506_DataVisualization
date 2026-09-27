import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.title("College Yield Rates")

weighted_yield = pd.read_csv(
    "weighted_yield.csv",
    index_col="year"
)

weighted_yield.index = pd.to_numeric(weighted_yield.index)
weighted_yield = weighted_yield.sort_index()

st.write("Data preview:")
st.dataframe(weighted_yield)

fig, ax = plt.subplots(figsize=(10, 6))

for column in weighted_yield.columns:
    ax.plot(
        weighted_yield.index,
        weighted_yield[column],
        label=column
    )

ax.set_xlabel("Year")
ax.set_ylabel("Yield Rate")
ax.legend()

st.pyplot(fig)
