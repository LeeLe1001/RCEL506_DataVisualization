import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Yield Rate at U.S. Colleges", layout="centered")

@st.cache_data
def load_data():
    return pd.read_csv("weighted_yield.csv", index_col="year")

weighted_yield = load_data()

color_map = {
    'Elite': '#3492D6',             
    'Selective': '#43B797',         
    'Somewhat Selective': '#FA9E5A',
    'Less Selective': '#F486C7',    
    'Much Less Selective': '#F4686C'
}

rate_ranges = {
    'Elite': '<20% admissions rate',
    'Selective': '20%-40% admissions rate',
    'Somewhat Selective': '40%-60% admissions rate',
    'Less Selective': '60%-80% admissions rate',
    'Much Less Selective': '>80% admissions rate'
}

groups = ['Elite', 'Selective', 'Somewhat Selective', 'Less Selective', 'Much Less Selective']
selected_groups = st.multiselect("Select Selectivity Groups:", groups, default=groups)

min_val = int(weighted_yield.index.min())
max_val = int(weighted_yield.index.max())
min_year, max_year = st.slider("Select Year Range:", min_val, max_val, (min_val, max_val))

if not selected_groups:
    st.warning("Please select at least one selectivity group to display the chart.")
else:
    mask = (weighted_yield.index >= min_year) & (weighted_yield.index <= max_year)
    df_filtered = weighted_yield[mask]

    fig, ax = plt.subplots(figsize=(10, 10))
    
    labels_info = []
    actual_max = df_filtered.index.max()
    actual_min = df_filtered.index.min()
    
    for group in selected_groups:
        if group in df_filtered.columns:
            ax.plot(df_filtered.index, df_filtered[group], linewidth=2.5, color=color_map[group])
            
            # Extract the y-value at the absolute right-most visible edge
            final_y = df_filtered.loc[actual_max, group]
            labels_info.append({'group': group, 'y': final_y})
            
    # 1D Vertical repulsion to avoid overlap at the right edge
    min_spacing = 0.04
    for _ in range(15):
        for i in range(len(labels_info)):
            for j in range(i + 1, len(labels_info)):
                diff = labels_info[i]['y'] - labels_info[j]['y']
                if abs(diff) < min_spacing:
                    push = (min_spacing - abs(diff)) / 2
                    if diff > 0:
                        labels_info[i]['y'] += push
                        labels_info[j]['y'] -= push
                    else:
                        labels_info[i]['y'] -= push
                        labels_info[j]['y'] += push

    # Render adjusted labels to the right of the lines
    label_x = actual_max + 0.5
    for label in labels_info:
        group = label['group']
        adjusted_y = label['y']
        
        ax.text(label_x, adjusted_y + 0.004, group, color=color_map[group], fontsize=14, fontweight='bold', ha='left', va='bottom')
        ax.text(label_x, adjusted_y - 0.004, rate_ranges[group], color='grey', fontsize=11, alpha=0.8, ha='left', va='top')

    # Dynamically extend x-axis to make room for labels
    x_padding = max(3, (actual_max - actual_min) * 0.25)
    ax.set_xlim(actual_min, actual_max + x_padding)

    ax.set_title('Yield Rate at U.S. Colleges, by Selectivity', fontweight='bold', fontsize=20, loc='left', pad=45)
    ax.text(0, 1.05, 'The yield rate is the percentage of admitted students choosing to enroll.', 
            transform=ax.transAxes, fontsize=13, color='black', ha='left', va='bottom')

    ax.set_ylabel('Yield Rate', fontsize=12)
    ax.set_ylim(0.10, 0.55)
    ax.set_yticks([0.10, 0.20, 0.30, 0.40, 0.50])
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    ax.set_yticklabels([f'{int(y*100)}%' for y in ax.get_yticks()], fontsize=11)
    ax.tick_params(axis='x', labelsize=11)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.xlabel('Year', fontsize=12)
    plt.tight_layout()
    
    st.pyplot(fig)
