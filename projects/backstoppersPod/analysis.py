# -*- coding: utf-8 -*-
"""

@author:

    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

    Some code to collate some stats for podcast discussion.

"""

# =========================================================================
# Import packages
# =========================================================================

import pandas as pd
import os
import numpy as np

# =========================================================================
# Set-up
# =========================================================================

# General settings
# -------------------------------------------------------------------------

# Set analysis directory
analysis_dir = os.getcwd()

# Get helper functions
os.chdir(os.path.join('..','..','code','matchCentre'))
import collatestats

# Get back to analysis directory
os.chdir(analysis_dir)

# Set base directory for processed data
base_dir = os.path.join('..','..','data','matchCentre','processed')

# Create dictionary to map squad names to ID's
squad_dict = {804: 'Vixens',
              806: 'Swifts',
              807: 'Firebirds',
              8117: 'Lightning',
              810: 'Fever',
              8119: 'Magpies',
              801: 'Thunderbirds',
              8118: 'GIANTS',
              9698: 'Mavericks'}
squad_name_dict = {'Vixens': 804,
                   'Swifts': 806,
                   'Firebirds': 807,
                   'Lightning': 8117,
                   'Fever': 810,
                   'Magpies': 8119,
                   'Thunderbirds': 801,
                   'GIANTS': 8118,
                   'Mavericks': 9698}

# =========================================================================
# Run analysis
# =========================================================================

# Read in SSN stats
# -------------------------------------------------------------------------

# Get team stats
team_stats = collatestats.getSeasonStats(baseDir = base_dir,
                                         years = np.arange(2017,2026+1).tolist(),
                                         fileStem = 'teamStats',
                                         matchOptions = ['regular','final'],
                                         joined = True, addSquadNames = True)

# Get player stats
player_stats = collatestats.getSeasonStats(baseDir = base_dir,
                                           years = np.arange(2017,2026+1).tolist(),
                                           fileStem = 'playerStats',
                                           matchOptions = ['regular','final'],
                                           joined = True, addSquadNames = True)

# Get player lists
player_list = collatestats.getSeasonStats(baseDir = base_dir,
                                          years = np.arange(2017,2026+1).tolist(),
                                          fileStem = 'playerList',
                                          matchOptions = ['regular','final'],
                                          joined = True, addSquadNames = True)

# Extract Weston and Mannix stats
# -------------------------------------------------------------------------

# Get Weston and Mannix ID's
weston_id = player_list.loc[(player_list['surname']=='Weston') &
                            (player_list['firstname']=='Jo'),]['playerId'].unique()[0]
mannix_id = player_list.loc[(player_list['surname']=='Mannix') &
                            (player_list['firstname']=='Emily'),]['playerId'].unique()[0]

# Extract player stats and export to review
weston_stats = player_stats.loc[player_stats['playerId']==weston_id,]
mannix_stats = player_stats.loc[player_stats['playerId']==mannix_id,]
weston_stats.to_csv('weston_player_stats.csv', index=False)
mannix_stats.to_csv('mannix_player_stats.csv', index=False)

# Extract Vixen team stats
# -------------------------------------------------------------------------

# Get Vixen team stats and export to review
vixen_stats = team_stats.loc[team_stats['squadId']==squad_name_dict['Vixens'],]

# Determine win/loss by getting opposition points
opp_score = []
vix_score = []
for match_id in vixen_stats['matchId']:
    # Get opposition points for match Id
    try:
        opp_points = int(team_stats.loc[(team_stats['matchId'] == match_id) &
                                        (team_stats['squadId'] != squad_name_dict['Vixens']),]['points'].values[0])
        vix_points = int(team_stats.loc[(team_stats['matchId'] == match_id) &
                                        (team_stats['squadId'] == squad_name_dict['Vixens']),]['points'].values[0])

    except:
        opp_points = int(team_stats.loc[(team_stats['matchId'] == match_id) &
                                        (team_stats['squadId'] != squad_name_dict['Vixens']),]['goals'].values[0])
        vix_points = int(team_stats.loc[(team_stats['matchId'] == match_id) &
                                        (team_stats['squadId'] == squad_name_dict['Vixens']),]['goals'].values[0])
    # Append to list
    opp_score.append(opp_points)
    vix_score.append(vix_points)
# Add to dataframe
vixen_stats['opp_score'] = opp_score
vixen_stats['vix_score'] = vix_score

# Create win loss column
result = []
for ii in range(len(vixen_stats)):
    if vixen_stats.iloc[ii]['vix_score'] > vixen_stats.iloc[ii]['opp_score']:
        result.append('win')
    elif vixen_stats.iloc[ii]['vix_score'] < vixen_stats.iloc[ii]['opp_score']:
        result.append('loss')
    else:
        result.append('draw')
vixen_stats['result'] = result

# Export for review
vixen_stats.to_csv('vixens_team_stats.csv', index=False)

# Collate average team stats across this year
# -------------------------------------------------------------------------

# Get 20206 team stats and group by squad
team_stats_2026 = team_stats.loc[team_stats['year']==2026,]

# Get average stats and export
team_stats_2026.groupby('squadName').mean(numeric_only=True).to_csv('team_stats_avg_2026.csv', index=True)

# Avergae Super Shots over time
# -------------------------------------------------------------------------

# Collate average per year
team_stats.groupby('year').mean(numeric_only=True)['attempt2']

# %% ---------- end of analysis.py ---------- %% #
