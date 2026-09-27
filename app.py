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
            labels_info.append({'group': group, 'orig_y': final_y, 'y': final_y})
            
    # Sort labels strictly by their final y-value (descending order)
    labels_info.sort(key=lambda x: x['orig_y'], reverse=True)
            
    # 1D Vertical repulsion to avoid overlap while preserving sorted order
    min_spacing = 0.045
    for _ in range(20):
        for i in range(len(labels_info) - 1):
            diff = labels_info[i]['y'] - labels_info[i+1]['y']
            if diff < min_spacing:
                push = (min_spacing - diff) / 2
                labels_info[i]['y'] += push
                labels_info[i+1]['y'] -= push

    # Render adjusted labels to the right of the lines with connector lines
    label_x = actual_max + 1.0
    for label in labels_info:
        group = label['group']
        orig_y = label['orig_y']
        adjusted_y = label['y']
        c = color_map[group]
        
        # Draw thin connector line from the data point to the label anchor
        ax.plot([actual_max, label_x - 0.2], [orig_y, adjusted_y], color='#999999', linewidth=1.0, alpha=0.6)
        
        # Render the label block
        ax.text(label_x, adjusted_y + 0.002, group, color=c, fontsize=14, fontweight='bold', ha='left', va='bottom')
        ax.text(label_x, adjusted_y - 0.002, rate_ranges[group], color='grey', fontsize=11, alpha=0.8, ha='left', va='top')

    # Dynamically extend x-axis to make room for labels and connector lines
    x_padding = max(4.0, (actual_max - actual_min) * 0.35)
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
