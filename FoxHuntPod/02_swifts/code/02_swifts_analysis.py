# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 2 Swifts match-up for podcast
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#Set matplotlib parameters
from matplotlib import rcParams
# rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Arial'
rcParams['font.weight'] = 'bold'
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 16
rcParams['axes.linewidth'] = 1.5
rcParams['axes.labelweight'] = 'bold'
rcParams['legend.fontsize'] = 10
rcParams['xtick.major.width'] = 1.5
rcParams['ytick.major.width'] = 1.5
rcParams['legend.framealpha'] = 0.0
rcParams['savefig.dpi'] = 300
rcParams['savefig.format'] = 'pdf'

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set Firebirds and Vixens squad Id'ss
vixensSquadId = 804
swiftsSquadId = 806

#Identify round data directory for any specific loading
procDatDir = '..\\..\\..\\data\\matchCentre\\processed\\116650201_2022_SSN_11665_r2_g1\\'

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% How was Mannix's game?

#Set Mannix id
mannixId = 994213

#Let's check this games stats vs. others
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = list(np.linspace(2009,2021,13, dtype = int)),
                                          fileStem = 'playerStats')

#Get years form dataframe
years = list(playerStats.keys())

#Loop through years and extract mannix data
mannixData = {}
for year in years:
    #Extract Mannix data
    mannixData[year] = playerStats[year].loc[playerStats[year]['playerId'] == mannixId,]

#Mannix gains
#6 gains in 2016 ANZC first week of finals
#10 gains in round 4 and 13 of 2017 SSN (also had 8 in round 8)
#9 gains in round 9 of 2019 SSN
#12 gains in round 7 of 2020

#Also check quarter stats
playerPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                                years = list(np.linspace(2009,2021,13, dtype = int)),
                                                fileStem = 'playerPeriodStats')

#Loop through years and extract mannix data
mannixPeriodData = {}
for year in years:
    #Extract Mannix data
    mannixPeriodData[year] = playerPeriodStats[year].loc[playerPeriodStats[year]['playerId'] == mannixId,]

#4 in a quarter in round 13 & 14 of SSN
#4 in round 1 of 2018 SSN
#5 in round 8 & 4 in round 9 & 11 of 2019 SSN
#4 in round 3 & 7 of 2020 SSN

# %% Shooting circle - Kumwenda, Austin, Samason

#Set player Id's
kumwendaId = 80540
austinId = 1001708
samasonId = 1013077

#Check out Samason's efficiency versus other shooting players

#Get the player stats for this year
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats')
playerStats_2022 = playerStats_2022[2022]

#Get just the SSN data
playerStats_2022 = playerStats_2022.loc[playerStats_2022['compType'] == 'SSN',]

#Get total goals
playerStats_2022['totalGoals'] = playerStats_2022['goal1'] + (playerStats_2022['goal2']*2)

#Calculate scoring efficiency as goals per 60 mins of play

#Group by player and sum goals and minutes
playerTotals_2022 = playerStats_2022.groupby('playerId').sum()

#Create goals per 60 mins played for season
playerTotals_2022['scoringEfficiency_per60'] = playerTotals_2022['totalGoals'] / (playerTotals_2022['minutesPlayed'] / 60)

#Extract efficiency series
playerScoringEfficiency_2022 = playerTotals_2022['scoringEfficiency_per60']

# %% Liz Watson's game vs. others this week

#Set Watson Id
watsonId = 994224

#Leverage earlier 2022 player stats but just to round 2
playerStats_round2 = playerStats_2022.loc[playerStats_2022['roundNo'] == 2,]

#Get player lists for comparing
playerList_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerList')
playerList_2022 = playerList_2022[2022]

#6 for feeds in the round but #2 for feeds with attempt (Lara Dunkley #1)
    #Watson had 30
    #Proud had 28
#6 for centre pass receptions in round 2 (Gretel Bueta #1)
    #Watson had 18
    #Proud had 12

#1 for all of these stats in the game though

# %% What about Sophie Fawns from the Swifts?

#In 37.17 mins she scored 16 goals
fawnsEfficiency = 16 / (37.17 / 60)

#Compare to Garbin's debut?
garbinId = 1001711

#Loop through years and extract garbin data
garbinData = {}
for year in years:
    #Extract Mannix data
    garbinData[year] = playerStats[year].loc[playerStats[year]['playerId'] == garbinId,]

#Garbin's first game for the Swifts in round 1 of 2018
#Minutes played = 30
#Goals = 18
#Feeds = 2

# %% Fan question - scoring within quarters

#Get the scoring data from Super Shot era years
scoreFlow_SuperShotEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2020, 2021, 2022],
                                                     fileStem = 'scoreFlow')

#Add year to each dataframe
for year in list(scoreFlow_SuperShotEra.keys()):
    scoreFlow_SuperShotEra[year]['year'] = [year] * len(scoreFlow_SuperShotEra[year])

#Concatenate all of the data
scoreFlowData = pd.concat((
    scoreFlow_SuperShotEra[2020],
    scoreFlow_SuperShotEra[2021],
    scoreFlow_SuperShotEra[2022]
    ))

#Just keep the SSN comps
scoreFlowData = scoreFlowData.loc[scoreFlowData['compType'] == 'SSN',].reset_index(drop = True)

#Create dictionary to map squad names to ID's
squadDict ={804: 'Vixens',
            806: 'Swifts',
            807: 'Firebirds',
            8117: 'Lightning',
            810: 'Fever',
            8119: 'Magpies',
            801: 'Thunderbirds',
            8118: 'GIANTS'}

#Map squads to dataframe as variable
scoreFlowData['squadName'] = [squadDict[squadId] for squadId in scoreFlowData['squadId']]


# #Set-up dictionary to store data in
# scoreDict = {'matchId': [], 'squadName': [], 'year': [], 'timeFrame': []}

#Append an 'Early', 'Middle' or 'Late' variable based on period seconds data
timeFrame = []
for scoreInd in range(len(scoreFlowData)):
    if scoreFlowData['periodSeconds'][scoreInd] < 300:
        timeFrame.append('Early')
    elif scoreFlowData['periodSeconds'][scoreInd] >= 300 and scoreFlowData['periodSeconds'][scoreInd] < 600:
        timeFrame.append('Mid')
    else:
        timeFrame.append('Late')
scoreFlowData['timeFrame'] = timeFrame

#Sum the scoring by team, year, match Id and time frame
scoreSums = scoreFlowData.groupby(['year', 'matchId', 'squadName', 'timeFrame']).sum()['scorePoints'].reset_index(drop = False)

#Create figure
g = sns.FacetGrid(scoreSums, col = 'squadName', col_wrap = 2, height = 3, aspect = 1.5)

#Map the boxplot to the facet grid
g.map_dataframe(sns.boxplot, x = 'year', y = 'scorePoints', hue = 'timeFrame')

#Above isn't pretty - but provides some interesting points
    # - Somewhat of a league wide trend since 2020 that scoring goes in this triangular pattern
    #   (i.e. scoring peaks in middle 5 mins of the quarter, and is typically lower in the early and last 5 minutes)
    # - Vixens have followed this trend in every year with the Super Shot and are continuing to do so this year
    #   BUT...that peak in the middle of the quarter isn't as pronounced so far this year - i.e. more consistent scoring
    # - The Vixens opponents this week, the GIANTS, I'd say have been typically known as the Super Shot team are actually
    #   seeing a big drop in their scoring during the final five minutes of quarters    

# %% Prediction

#How many times over 2020 and 2021 did the Swifts score 48

#Load in the team stats from 2020 and 2021
teamStats_SuperShotEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2020, 2021],
                                                     fileStem = 'teamStats')

#Check Swifts scores for less than 48
#Do this across both years
for year in list(teamStats_SuperShotEra.keys()):
    #Extract number of times score was equal to or less than 48
    nUnder48 = len(teamStats_SuperShotEra[year].loc[(teamStats_SuperShotEra[year]['squadId'] == swiftsSquadId) &
                                                   ((teamStats_SuperShotEra[year]['goal1'] + (teamStats_SuperShotEra[year]['goal2']*2)) <= 48),
                                                   ['goals']])
    #Print out result
    print(f'Times equal to or less than 48 in {year}: {nUnder48}')

#Extract Austin's stats to take a look
austinStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == austinId,]


# %%% ----- End of 02_swifts_analysis.py -----