import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns

# Rule 3: Typography - Serif fonts
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

# Rule 2: Colors and Accessibility - Colorblind safe
sns.set_palette("colorblind")
colors = sns.color_palette("colorblind")

# Data preparation
algorithms = ['PSO', 'GWO', 'CMA-ES', 'TPE']
# J1 (Tracking), J2E (Energy), J2S (Smoothness), J3 (Saturation Penalty)
# Values represent normalized contributions to the total cost.
J1 = np.array([0.25, 0.22, 0.15, 0.28])
J2E = np.array([0.35, 0.30, 0.20, 0.25])
J2S = np.array([0.25, 0.20, 0.15, 0.18])
J3 = np.array([0.15, 0.08, 0.05, 0.09])

# Rule 1: Maximize Data-Ink Ratio. Transparent/white background
fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
fig.patch.set_facecolor('white')

# Rule 2: Distinct hatch patterns
patterns = ['///', '\\\\\\', 'xxx', '...']

bar_width = 0.5
index = np.arange(len(algorithms))

bottom = np.zeros(len(algorithms))

# Plotting each component
ax.bar(index, J1, bar_width, bottom=bottom, label=r'$J_1$ (Tracking Error)', 
       color=colors[0], edgecolor='black', hatch=patterns[0], zorder=3)
bottom += J1

ax.bar(index, J2E, bar_width, bottom=bottom, label=r'$J_{2E}$ (Control Energy)', 
       color=colors[1], edgecolor='black', hatch=patterns[1], zorder=3)
bottom += J2E

ax.bar(index, J2S, bar_width, bottom=bottom, label=r'$J_{2S}$ (Smoothness)', 
       color=colors[2], edgecolor='black', hatch=patterns[2], zorder=3)
bottom += J2S

ax.bar(index, J3, bar_width, bottom=bottom, label=r'$J_3$ (Saturation)', 
       color=colors[3], edgecolor='black', hatch=patterns[3], zorder=3)

# Aesthetics
ax.set_xticks(index)
ax.set_xticklabels(algorithms, fontsize=12)
ax.set_ylabel('Normalized Cost Contribution', fontsize=12)

# Spines (Borders): Always remove the TOP and RIGHT spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Gridlines: Only horizontal, light grey, dashed, behind data
ax.yaxis.grid(True, color='#E0E0E0', linestyle='--', zorder=0)
ax.set_axisbelow(True)

# Legend
ax.legend(loc='upper right', fontsize=10, frameon=False, bbox_to_anchor=(1.35, 1))

plt.tight_layout()

# Save
output_dir = r"D:\UIT\Research\Viettel\docx\image"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "energy_aware_cost_breakdown.pdf")
plt.savefig(output_path, bbox_inches='tight', format='pdf', transparent=True)
print(f"Chart saved successfully at {output_path}")

# Save a PNG copy to show the user or as artifact
output_png = os.path.join(output_dir, "energy_aware_cost_breakdown.png")
plt.savefig(output_png, bbox_inches='tight', format='png', dpi=300, facecolor='white', transparent=False)
print(f"Chart saved successfully at {output_png}")
