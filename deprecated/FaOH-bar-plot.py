#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 25 16:01:15 2022

@author: Yun Su
"""

import numpy as np
import pandas as pd
import scipy
from scipy import stats
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.patches import Patch
from matplotlib import container
plt.rcParams["font.family"] = "Arial"
plt.rcParams['axes.titlesize'] = 6
plt.rcParams['axes.labelsize'] = 6
plt.rcParams['xtick.labelsize'] = 5
plt.rcParams['ytick.labelsize'] = 5
plt.rcParams['legend.fontsize'] = 5
plt.rcParams['legend.title_fontsize'] = 6
import seaborn as sns
pd.options.display.max_rows = 9999
display.max_columns = 9999
figure_width = 6
figure_height = 3.7
alcohols = ['Butanol','Hexanol','Octanol','Decanol','Dodecanol','Tetradecanol','Hexadecanol','Octadecanol','Eicosanol']
bar_width = 0.35
strain_count = 3 # <THIS SHOULD BE AUTOMATED
# Initiate a high-resolution figure
fig = plt.figure(figsize=(figure_width, figure_height), dpi=500)
# Color mapping for alcohols 
color_map = sns.color_palette('bwr',10)[1:10] # Pick 9 points out of a 10 points out of the 10 point palette. 
cdict={alcohols[i]:color_map[i] for i in range(len(alcohols))} # Assign them to alcohols
# Set up the x axis positions for the bars and initiate the bottom tracking variable. 
ind = np.arange(strain_count) + 1
bottoms = np.zeros(len(ind))
for alc in alcohols: 
    bar_heights = [1,0.75,0.5] # <These values you'll want to get (or calculate) from a dataframe you built.
    error_bars = [0.25,0.2,0.15] # <Similarly get these (or calculate) from your dataframe. 
    plt.bar(ind,bar_heights,yerr = error_bars, width = bar_width, bottom = bottoms, color = cdict[alc], linewidth = 0.5, edgecolor = 'black', error_kw = {'elinewidth': 0.5, 'markeredgewidth': 0.5}, capsize = 2, label = alc)
    bottoms += bar_heights
# Y-Axis Settings
plt.ylim(0,10)
plt.ylabel('Y-Axis Label')
plt.yticks([0,2.5,5,7.5,10]) # One list, the points to put nubmer ticks at
# X-Axis Settings
plt.xlim(ind[0]-0.5,ind[-1]+0.5)
plt.xlabel('X-Axis Label')
plt.xticks([1,2,3],['Strain 1','Strain 2','Strain 3']) # One list, the points to put nubmer ticks at
# Legend - Reverse the natural order so the colors match the order of the barchart
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles[::-1],labels[::-1], title = 'Legend', frameon = False, loc = 'center left', bbox_to_anchor = (1,0.5))
plt.show()