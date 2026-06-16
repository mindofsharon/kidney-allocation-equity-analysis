import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import textwrap

#load data
cand_kipa = pd.read_csv('cand_kipa.csv')
tx_ki = pd.read_csv('tx_ki.csv')

#Filter out candidates who received living donations
living_donor_ids = tx_ki[tx_ki['DON_TY'] == 'L']['PX_ID'].unique()

cand_filtered = cand_kipa[~cand_kipa['PX_ID'].isin(living_donor_ids)]

#Filter to only keep candidates listed for kidney only (KI)
cand_filtered = cand_filtered[cand_filtered['WL_ORG'] == 'KI']

#Categorize candidates 

cand_deceased = [8]
cand_unsuitable = [5, 6, 11, 12, 13, 17]
cand_removed_other = [7, 9, 10, 14, 20, 22, 24]
removed_from_list = cand_deceased + cand_unsuitable + cand_removed_other

transplant_fail = [21]
transplant_success = [4, 18]
received_transplant = transplant_fail + transplant_success

conditions_cat = [
    cand_filtered['CAN_REM_CD'].isin(removed_from_list),
    cand_filtered['CAN_REM_CD'].isin(received_transplant)
]
choices_cat = [
    "Removed from waitlist", 
    "Received transplant"
]

cand_filtered['Waitlist_Category'] = np.select(
    conditions_cat, 
    choices_cat, 
    default="Currently on waitlist"
)


conditions_sub = [
    cand_filtered['CAN_REM_CD'].isin(cand_deceased),
    cand_filtered['CAN_REM_CD'].isin(cand_unsuitable),
    cand_filtered['CAN_REM_CD'].isin(cand_removed_other),
    cand_filtered['CAN_REM_CD'].isin(transplant_fail),
    cand_filtered['CAN_REM_CD'].isin(transplant_success)
]
choices_sub = [
    "Candidate deceased",
    "Candidate unsuitable",
    "Candidate removed - Other",
    "Candidate died during transplant",
    "Candidate successfully received transplant"
]

cand_filtered['Waitlist_Subcategory'] = np.select(
    conditions_sub, 
    choices_sub, 
    default="Currently on waitlist"
)


import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# Set a clean visual theme
sns.set_theme(style="whitegrid")

# --- Helper Function for Y-Axis Formatting ---
def format_units(x, pos):
    """Formats large numbers into K (thousands) or M (millions)."""
    if x >= 1e6:
        return f'{x*1e-6:.1f}M'
    elif x >= 1e3:
        return f'{x*1e-3:.0f}K'
    return f'{x:.0f}'

formatter = FuncFormatter(format_units)

# ==========================================
# --- Figure 1: Waitlist Category ---
# ==========================================
plt.figure(figsize=(10, 6))
category_counts = cand_filtered['Waitlist_Category'].value_counts()
ax1 = sns.barplot(x=category_counts.index, y=category_counts.values, palette="Blues_r")
ax1.yaxis.set_major_formatter(formatter)


for container in ax1.containers:
    ax1.bar_label(container, fmt='{:,.0f}', padding=3, fontsize=11)

plt.title('Distribution of Candidates by Waitlist Category', fontsize=14, pad=15)
plt.xlabel('Waitlist Category', fontsize=12)
plt.ylabel('Number of Candidates', fontsize=12)
plt.xticks(rotation=0)
plt.tight_layout()


plt.show()

# ==========================================
# --- Chart 2: Waitlist Subcategory ---
# ==========================================
plt.figure(figsize=(12, 7))
subcategory_counts = cand_filtered['Waitlist_Subcategory'].value_counts()
ax2 = sns.barplot(x=subcategory_counts.index, y=subcategory_counts.values, palette="crest")
ax2.yaxis.set_major_formatter(formatter)

for container in ax2.containers:
    ax2.bar_label(container, fmt='{:,.0f}', padding=3, fontsize=10)

max_width = 15
wrapped_labels = [textwrap.fill(label, max_width) for label in subcategory_counts.index]

ax2.set_xticklabels(wrapped_labels, rotation=0)

plt.title('Distribution of Candidates by Subcategory', fontsize=14, pad=15)
plt.xlabel('Waitlist Subcategory', fontsize=12)
plt.ylabel('Number of Candidates', fontsize=12)

# Use tight_layout so the multiline labels don't get cut off at the bottom
plt.tight_layout()

# Display the charts
plt.show()
