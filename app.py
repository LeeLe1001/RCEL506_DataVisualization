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

relative_x_positions = {
    'Elite': 0.85,
    'Selective': 0.60,
    'Somewhat Selective': 0.20,
    'Less Selective': 0.45,
    'Much Less Selective': 0.75
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
    
    # Pre-calculate initial label positions
    labels_info = []
    for group in selected_groups:
        if group in df_filtered.columns:
            ax.plot(df_filtered.index, df_filtered[group], linewidth=2.5, color=color_map[group])
            
            range_span = max_year - min_year
            target_x = min_year if range_span == 0 else min_year + (range_span * relative_x_positions[group])
            
            dynamic_x = min(df_filtered.index, key=lambda x: abs(x - target_x))
            dynamic_y = df_filtered.loc[dynamic_x, group]
            
            labels_info.append({
                'group': group,
                'x': dynamic_x,
                'y': dynamic_y,
                'orig_y': dynamic_y
            })
            
    # Iterative 2D repulsion to avoid overlap while staying close to the line
    min_y_spacing = 0.03
    max_x_proximity = 3  # Only repel if labels are within 3 years of each other
    max_y_displacement = 0.025  # Maximum drift allowed from the original line
    
    for _ in range(15):
        for i in range(len(labels_info)):
            for j in range(i + 1, len(labels_info)):
                x_diff = abs(labels_info[i]['x'] - labels_info[j]['x'])
                y_diff = labels_info[i]['y'] - labels_info[j]['y']
                
                if x_diff <= max_x_proximity and abs(y_diff) < min_y_spacing:
                    push = (min_y_spacing - abs(y_diff)) / 2
                    if y_diff > 0:
                        labels_info[i]['y'] += push
                        labels_info[j]['y'] -= push
                    else:
                        labels_info[i]['y'] -= push
                        labels_info[j]['y'] += push
                        
    # Clamp final positions to ensure they haven't drifted too far from the line
    for label in labels_info:
        if label['y'] > label['orig_y'] + max_y_displacement:
            label['y'] = label['orig_y'] + max_y_displacement
        elif label['y'] < label['orig_y'] - max_y_displacement:
            label['y'] = label['orig_y'] - max_y_displacement

    # Render adjusted labels
    for label in labels_info:
        group = label['group']
        adjusted_y = label['y']
        dynamic_x = label['x']
        
        ax.text(dynamic_x, adjusted_y + 0.008, group, color=color_map[group], fontsize=15, fontweight='bold', ha='center')
        ax.text(dynamic_x, adjusted_y - 0.015, rate_ranges[group], color='grey', fontsize=12, alpha=0.8, ha='center')

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
