import os
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import textwrap

# Load data from a local data directory
DATA_DIR = Path(os.getenv('DATA_DIR', 'data'))
cand_kipa_path = DATA_DIR / 'cand_kipa.csv'
tx_ki_path = DATA_DIR / 'tx_ki.csv'

cand_kipa = pd.read_csv(cand_kipa_path)
tx_ki = pd.read_csv(tx_ki_path)

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

# missing values

target_cols = ['CAN_RACE', 'CAN_GENDER', 'CAN_EDUCATION', 'CAN_AGE_AT_LISTING', 'CAN_CITIZENSHIP', 'CAN_PRIMARY_PAY']

null_counts = cand_filtered[target_cols].isnull().sum()
null_percentages = (null_counts / len(cand_filtered)) * 100

null_table = pd.DataFrame({
    'Column': null_counts.index,
    'Missing_Count': null_counts,
    'Missing_Percentage': null_percentages
})

# ==========================================
# --- Data Cleaning: Demographics---
# ==========================================

# ---helper function to build tables---

def format_table(df, col):
    counts = df[col].value_counts()
    frequencies = counts / len(df) * 100
    return pd.DataFrame({
        "Characteristics": counts.index,
        "Frequency": frequencies.values

    })

# Demographics - Race

race_map = {
    8 : "White",
    16 : "Black",
    32 : "American Indian",
    64 : "Asian",
    128 : "Pacific Islander",
    256 : "Middle Eastern",
    512 : "Indian",
    2000 : "Hispanic",
    1024 : "Unknown",
    '' : "Missing"
}

cand_filtered['Race'] = cand_filtered['CAN_RACE'].apply(
    lambda x: race_map.get(x, "Multi-Racial")
)

race_counts = cand_filtered['Race'].value_counts()

# Demographics - Gender

gender_map = {
    'M': "Male",
    'F': "Female",
}

cand_filtered['Gender'] = cand_filtered['CAN_GENDER'].apply(
    lambda x: gender_map.get(x, "Unknown")
)

gender_counts = cand_filtered['Gender'].value_counts()

table = pd.crosstab(
    cand_filtered['Gender'],
    cand_filtered['Waitlist_Category'],
    normalize='columns'
) *100



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


# ==========================================
# --- Chart 3: Demographics ---
# ==========================================

# Gender distribution
plt.figure(figsize=(10, 6))
ax3 = sns.barplot(x=gender_counts.index, y=gender_counts.values, palette="Accent")

for container in ax3.containers:
    ax3.bar_label(container, fmt='{:,.0f}', padding=3, fontsize=11)

plt.title('Distribution of Candidates by Gender', fontsize=14, pad=15)
plt.xlabel('Gender', fontsize=12)
plt.ylabel('Number of Candidates', fontsize=12)
plt.show()

# Race distribution
plt.figure(figsize=(10, 6))
ax4 = sns.barplot(x=race_counts.index, y=race_counts.values, palette="gist_earth")

for container in ax4.containers:
    ax4.bar_label(container, fmt='{:,.0f}', padding=3, fontsize=11)

plt.title('Distribution of Candidates by Race', fontsize=14, pad=15)
plt.xlabel('Race', fontsize=12)
plt.ylabel('Number of Candidates', fontsize=12)
plt.show()

# Age distribution
plt.figure(figsize=(10, 6))
plt.hist(cand_filtered['CAN_AGE_AT_LISTING'], bins=20, color='skyblue', edgecolor='black')
plt.title('Distribution of Candidates by Age', fontsize=14, pad=15)
plt.xlabel('Age', fontsize=12)
plt.ylabel('Number of Candidates', fontsize=12)
plt.show()
