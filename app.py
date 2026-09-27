import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Yield Rate at U.S. Colleges", layout="centered")

@st.cache_data
def load_data():
    # Read the pre-processed data directly as instructed
    df = pd.read_csv("weighted_yield.csv", index_col="year")
    return df

weighted_yield = load_data()

# Extracted exact hex color mapping
color_map = {
    'Elite': '#3492D6',             
    'Selective': '#43B797',         
    'Somewhat Selective': '#FA9E5A',
    'Less Selective': '#F486C7',    
    'Much Less Selective': '#F4686C'
}

# Rate range mapping
rate_ranges = {
    'Elite': '<20% admissions rate',
    'Selective': '20%-40% admissions rate',
    'Somewhat Selective': '40%-60% admissions rate',
    'Less Selective': '60%-80% admissions rate',
    'Much Less Selective': '>80% admissions rate'
}

# Original preferred x-coordinates for labels
ideal_x_positions = {
    'Elite': 2018,
    'Selective': 2014,
    'Somewhat Selective': 2005,
    'Less Selective': 2013,
    'Much Less Selective': 2017
}

# 1. Interactive Controls
groups = ['Elite', 'Selective', 'Somewhat Selective', 'Less Selective', 'Much Less Selective']
selected_groups = st.multiselect("Select Selectivity Groups:", groups, default=groups)

min_val = int(weighted_yield.index.min())
max_val = int(weighted_yield.index.max())
min_year, max_year = st.slider("Select Year Range:", min_val, max_val, (min_val, max_val))

# 2. Warning if no groups are selected
if not selected_groups:
    st.warning("Please select at least one selectivity group to display the chart.")
else:
    # 3. Filter Data
    mask = (weighted_yield.index >= min_year) & (weighted_yield.index <= max_year)
    df_filtered = weighted_yield[mask]

    # 4. Generate the Plot
    # Initialize solitary plot with explicit 1:1 ratio
    fig, ax = plt.subplots(figsize=(10, 10))
    
    for group in selected_groups:
        if group in df_filtered.columns:
            # Plot the trajectory
            ax.plot(df_filtered.index, df_filtered[group], linewidth=2.5, color=color_map[group])
            
            # Dynamically calculate label coordinates based on visible year range
            ideal_x = ideal_x_positions[group]
            
            # Constrain x to stay within the currently selected bounds
            dynamic_x = max(min_year, min(ideal_x, max_year))
            
            # Ensure the dynamic_x exists in the filtered index, snapping to nearest if necessary
            if dynamic_x not in df_filtered.index:
                dynamic_x = min(df_filtered.index, key=lambda x: abs(x - dynamic_x))
                
            # Extract the exact y-coordinate from the data to sit directly on the line
            dynamic_y = df_filtered.loc[dynamic_x, group]
            
            # Inject primary selectivity label (matching line color) slightly above the line
            ax.text(dynamic_x, dynamic_y + 0.008, group, color=color_map[group], fontsize=15, fontweight='bold', ha='center')
            
            # Inject secondary rate range label (lighter grey) slightly below the line
            ax.text(dynamic_x, dynamic_y - 0.015, rate_ranges[group], color='grey', fontsize=12, alpha=0.8, ha='center')

    # Configure axes and styling
    ax.set_title('Yield Rate at U.S. Colleges, by Selectivity', fontweight='bold', fontsize=20, loc='left', pad=45)

    # Positioned slightly higher (1.05) on the axes transform to fit neatly above the chart
    ax.text(0, 1.05, 'The yield rate is the percentage of admitted students choosing to enroll.', 
            transform=ax.transAxes, fontsize=13, color='black', ha='left', va='bottom')

    ax.set_ylabel('Yield Rate', fontsize=12)

    # Extend ylim to 55% to create buffer space, but keep tick marks capped at 50%
    ax.set_ylim(0.10, 0.55)
    ax.set_yticks([0.10, 0.20, 0.30, 0.40, 0.50])

    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # Format y-axis to display percentages natively and increase tick font size slightly
    ax.set_yticklabels([f'{int(y*100)}%' for y in ax.get_yticks()], fontsize=11)
    ax.tick_params(axis='x', labelsize=11)

    # Hide top and right spines for a clean aesthetic
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.xlabel('Year', fontsize=12)
    plt.tight_layout()
    
    # Render in Streamlit
    st.pyplot(fig)
