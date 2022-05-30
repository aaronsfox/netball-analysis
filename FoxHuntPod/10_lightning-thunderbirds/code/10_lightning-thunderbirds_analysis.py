# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 12 & 13 Lightning & Thunderbirds match-up
    for podcast.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns

# #Set matplotlib parameters
# from matplotlib import rcParams
# # rcParams['font.family'] = 'sans-serif'
# rcParams['font.sans-serif'] = 'Arial'
# rcParams['font.weight'] = 'bold'
# rcParams['axes.labelsize'] = 12
# rcParams['axes.titlesize'] = 16
# rcParams['axes.linewidth'] = 1.5
# rcParams['axes.labelweight'] = 'bold'
# rcParams['legend.fontsize'] = 10
# rcParams['xtick.major.width'] = 1.5
# rcParams['ytick.major.width'] = 1.5
# rcParams['legend.framealpha'] = 0.0
# rcParams['savefig.dpi'] = 300
# rcParams['savefig.format'] = 'pdf'

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Create dictionary to map squad names to ID's
squadDict = {804: 'Vixens',
             806: 'Swifts',
             807: 'Firebirds',
             8117: 'Lightning',
             810: 'Fever',
             8119: 'Magpies',
             801: 'Thunderbirds',
             8118: 'GIANTS'}
squadNameDict = {'Vixens': 804,
                 'Swifts': 806,
                 'Firebirds': 807,
                 'Lightning': 8117,
                 'Fever': 810,
                 'Magpies': 8119,
                 'Thunderbirds': 801,
                 'GIANTS': 8118}

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% Lightning match-up: Key numbers that jumped out

#Shot attempts:
    #77-59 in Vixens favour; 75-47 standard shots for Vixens to 12-2 Super Shots for Lightning
    #Overall shooting percentage of 81.8% for Vixens vs. 88.1% for Lightning
    #Better percetnage despite taking potentially riskier shots
#Huge gain game from both teams:
    #20 for Vixens and 18 for Lightning
#Missed goal turnovers still equal though
    #Vixens hauled in all 7 of the Lightning's missies - no 2nd chances
    #Lightning only hauled in 7 of the Vixen's 14 misses
#Goals from gains:
    #Once again the Vixens led this 14-11
#Super Shots:
    #8 to 1 (i.e. 16 goals to 2) for the Lightning

# %% Gains & deflections in the match

#Get Vixens and Lightning team stats
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'])
teamStats_2022 = teamStats_2022[2022]
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Vixens'],]
lightningTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Lightning'],]

#20 gains for the Vixen's - was this their highest for the season?
    #Equal highest gain game for the Vixens

#18 gains for the Lightning - was this their highest for the season?
    #Highest gain game for the Lightning

#Possession changes - 24 to Vixens, 29 to Lightning. Most in a game?

#Group team stats by match Id and sum
totalMatchStats_2022 = teamStats_2022.groupby('matchId').sum()

#Not really - not a lot of unforced turnovers

#20 deflections for the Vixen's - was this their highest for the season?
    #Second highest deflections game for Vixens

#17 deflections for the Lightning - was this their highest for the season?
    #Highest deflection game for Lightning
    
# %% Lightning Super Shots

#Particularly first quarter kept them in it
#Was their total proportion from Super Shots one of the highest?

#Read in quarter stats from the year
teamPeriodStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2022],
                                                   fileStem = 'teamPeriodStats',
                                                   matchOptions = ['regular'])
teamPeriodStats_2022 = teamPeriodStats_2022[2022]

#Create new variable that calculates proportion of total goals from Super Shots
teamPeriodStats_2022['superScoreProp'] = (teamPeriodStats_2022['goal2']*2) / teamPeriodStats_2022['points'] * 100
superScoreProp = teamPeriodStats_2022[['matchId', 'squadId', 'oppSquadId', 'period', 'superScoreProp']]

#Equal 9th highest proportion in a quarter coming from Super Shots at ~46.1%
#2nd highest proportion in a quarter for the Lightning for the year (once at ~58.8% in rd. 10, 4th quarter)

# %% Weston & Mannix 

#7 gains each in game
#Has this happened so far this year?

#Create dictionary to store data in
topTwoGains = {'matchId': [], 'squadId': [],
               'playerId_1': [], 'gain_1': [],
               'playerId_2': [], 'gain_2': []}

#Get player stats for the year
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats',
                                               matchOptions = ['regular'])
playerStats_2022 = playerStats_2022[2022]

#Loop through match Id's
matchIds = list(playerStats_2022['matchId'].unique())
for matchId in matchIds:
    
    #Get the squad Id's
    squadIds = list(playerStats_2022.loc[playerStats_2022['matchId'] == matchId,
                                         ]['squadId'].unique())
    
    #Loop through the two squad Id's
    for squadId in squadIds:
        
        #Extract data and sort by gains
        sortedByGains = playerStats_2022.loc[(playerStats_2022['matchId'] == matchId) &
                                             (playerStats_2022['squadId'] == squadId),
                                             ].sort_values(by = 'gain', ascending = False).reset_index()
        
        #Append data
        topTwoGains['matchId'].append(matchId)
        topTwoGains['squadId'].append(squadId)
        topTwoGains['playerId_1'].append(sortedByGains['playerId'][0])
        topTwoGains['gain_1'].append(sortedByGains['gain'][0])
        topTwoGains['playerId_2'].append(sortedByGains['playerId'][1])
        topTwoGains['gain_2'].append(sortedByGains['gain'][1])
        
#Convert to dataframe
topTwoGains_df = pd.DataFrame.from_dict(topTwoGains)

#Calculate variable that describes minimum of the two players gains
topTwoGains_df['minGainsByTwo'] = [np.min(np.array((topTwoGains_df['gain_1'][ind[0]],topTwoGains_df['gain_2'][ind[0]]))) for ind in enumerate(topTwoGains_df['matchId'])]
    
#7 gains by two players is the equal highest for the season
#Only other time it happened was also in round 12, game 1 by Magpies

# %% Watson's Game

#Another 40 feeds for Watson
#How many times has she reached 40+ feeds? How many times have others in the league done this?

#Grab unique player Ids from player stats
playerIds = list(playerStats_2022['playerId'].unique())

#Set-up dictionary to store data in
fortyPlusFeeds = {'playerId': [], 'nGames': []}

#Loop through players
for playerId in playerIds:
    
    #Extract players data and sort by feeds
    playerFeeds = playerStats_2022.loc[playerStats_2022['playerId'] == playerId,
                                       ].sort_values(by = 'feeds', ascending = False).reset_index(drop = True)
    
    #Find index of feeds less than 40
    n40PlusFeeds = np.where(playerFeeds['feeds'].to_numpy() < 40)[0][0]
    
    #Append to dataframe
    fortyPlusFeeds['playerId'].append(playerId)
    fortyPlusFeeds['nGames'].append(n40PlusFeeds)
    
#Convert to dataframe
fortyPlusFeeds_df = pd.DataFrame.from_dict(fortyPlusFeeds)

#Liz Watson has 9 40+ feed games this year - more than anyone else in comp
#playerId 80439 has 8, next most has 4

# %% Predictions

#Last week - predicted highest rebound game for season for the Vixens
#Vixens recorded 9 rebounds - which wasn't their highest
    #Had one game with 11 rebounds and three with 10
#Lightning didn't help having their second least amount of goal misses for the year
    #well below their average goal misses
#If anything Kumwenda helped this one out a little bit with some easy misses that she quickly pulled down

# %%% ----- End of 10_lightning-thunderbirds_analysis.py -----