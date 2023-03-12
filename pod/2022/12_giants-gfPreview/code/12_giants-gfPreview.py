# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the prelim final Giants match-up
    and grand final preview for podcast.
    
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
os.chdir('..\\..\\..\..\\code\\matchCentre')
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
baseDir = '..\\..\\..\\..\\data\\matchCentre\\processed'

# %% Giants match-up: Key numbers that jumped out

#Some eerie similarities to the last match-up statistically
#The biggest disparity as with the last time they met was in the Super Shots
    #10-3 in the Giants favour, 6 of which came in the 2nd Q for the Gians
    #Made a huge difference in getting them back into the game at the end of the first half
#Again much like last time - the Giants had some missed opportunities
    #Giants led deflections 17-8 - but of those 17 deflections for the Giants only 2 resulted in gains
#The Vixens were outgained by the Giants 14-13, but it doesn't matter because we all know the Vixens win when they get +10 gains
#Perhaps the most important stat on the night though:
    #A 17-7 final quarter for the Vixens that dragged them across the line
    
#Was this the biggest final quarter comeback ever?
comebackData = {'matchId': [], 'year': [], 'matchType': [], 'end3rdMargin': [], 'end4thMargin': [], 'comeback': []}

#Read in scoreflow data
scoreFlowData = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = 'all',
                                            fileStem = 'scoreFlow',
                                            matchOptions = ['regular','final'])

#Loop through years
for year in scoreFlowData.keys():
    
    #Get match IDs
    matchIds = scoreFlowData[year]['matchId'].unique()
    
    #Loop through match Ids
    for matchId in matchIds:
        
        #Extract match data
        currMatch = scoreFlowData[year].loc[scoreFlowData[year]['matchId'] == matchId,]
        
        #Get final third quarter margin
        end3rdMargin = currMatch.loc[currMatch['period'] == 3,].reset_index().iloc[-1]['scoreDifferential']
        
        #Get end of match margin
        end4thMargin = currMatch.loc[currMatch['period'] == 4,].reset_index().iloc[-1]['scoreDifferential']
        
        #Check if the score flipped
        if end3rdMargin * end4thMargin < 0:
            
            #Extract data
            comebackData['matchId'].append(matchId)
            comebackData['year'].append(year)
            comebackData['matchType'].append(currMatch['matchType'].unique()[0])
            comebackData['end3rdMargin'].append(end3rdMargin)
            comebackData['end4thMargin'].append(end4thMargin)
            comebackData['comeback'].append(abs(end4thMargin - end3rdMargin))

#Convert to dataframe
comebackData_df = pd.DataFrame.from_dict(comebackData)

#Teams have outscore opponents by a little bit more - there's a couple of examples
#of teams outscoring their opponent by 11 in the final quarter, but they were less
#than 9 down in those matches.
#Coming back from 9 down is in fact the biggest 3rd quarter deficit a team has
#ever come back from to win in ANZC / SSN history!

# %% Has there ever been a game so close, but not?

#Set dictionary to store data
closenessData = {'matchId': [], 'year': [], 'squadIds': [], 'matchType': [],
                 'periodMargins': [], 'finalMargin': []}

#Read in team period stats
teamPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = 'all',
                                              fileStem = 'teamPeriodStats',
                                              matchOptions = ['regular','final'])

#Loop through years
for year in teamPeriodStats.keys():
    
    #Get match IDs
    matchIds = teamPeriodStats[year]['matchId'].unique()
    
    #Loop through match Ids
    for matchId in matchIds:
        
        #Extract match data
        currMatch = teamPeriodStats[year].loc[teamPeriodStats[year]['matchId'] == matchId,]
        
        #Get the two squad Ids
        squadIds = currMatch['squadId'].unique()
        
        #Extract the period scores
        if year < 2020:
            scoreA = currMatch.loc[currMatch['squadId'] == squadIds[0],
                                   ]['goals'].to_numpy()
            scoreB = currMatch.loc[currMatch['squadId'] == squadIds[1],
                                   ]['goals'].to_numpy()
        else:
            scoreA = currMatch.loc[currMatch['squadId'] == squadIds[0],
                                   ]['points'].to_numpy()
            scoreB = currMatch.loc[currMatch['squadId'] == squadIds[1],
                                   ]['points'].to_numpy()
            
        #Subtract the scores from one another
        scoreDiff = np.abs(scoreA - scoreB)
        
        #Check for all greater than or equal to 5
        if (scoreDiff >= 5).all():
            
            #Get the final margin from scoreflow data
            finalMargin = scoreFlowData[year].loc[scoreFlowData[year]['matchId'] == matchId,].reset_index().iloc[-1]['scoreDifferential']
            
            #Append data
            closenessData['matchId'].append(matchId)
            closenessData['year'].append(year)
            closenessData['squadIds'].append(squadIds)
            closenessData['matchType'].append(currMatch['matchType'].unique()[0])
            closenessData['periodMargins'].append(scoreA - scoreB)
            closenessData['finalMargin'].append(finalMargin)
        
#Convert to dataframe
closenessData_df = pd.DataFrame.from_dict(closenessData)

#I found 17 games in ANZC/SSN history where the goal differential has been 5 or more in every quarter
#Across 15 of these games the final margin ranged from 19 up to 43
#Then there's our game from the weekend where the final margin was 1
#And there is one other game where this happened:
    #A 2021 match-up between the Swifts and Fever
    #Very similar where the Fever jumped out to a lead, the Swifts took Q2 & 3, and then the Fever took back over in Q4
    #Unlike on the weekend though it was the Swifts who took those middle quarters coming out on top

# %% Contrasting stats from Vixens matches against Fever

#Read in the 2022 team stats
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular','final'])
teamStats_2022 = teamStats_2022[2022]

#Get Vixens team stats and extract Fever match-ups
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Vixens'],]
vixensTeamStats_2022_vsFever = vixensTeamStats_2022.loc[vixensTeamStats_2022['oppSquadId'] == squadNameDict['Fever'],]

#Shot attempts - 77 in first win; 77 in second win; 60 in loss (inc. only 43 standard shot attempts vs. 64 & 74)
#Made shots - 67 & 69 in wins, 50 in loss
#Centre pass to goal - 80% in both wins down to 67% in loss
#Contact penalties - 47 & 35 in wins, 60 in loss
#Obstruction penalties - 7 in both wins, 14 in loss
#Total penalties - 54 & 42 in wins, 74 in loss
#Circle feeds with attempts - 71 & 73 in wins, 55 in loss
#Gains - 10 & 13 in wins, 7 in loss
#Gain to goal percentage 80 & 92% in wins, 43% in loss
#General play TOs - 15 in both wins, 22 in loss
#Loose ball pickups - 9 & 16 in wins, 4 in loss
    
#Get Fever team stats and extract Vixens match-ups
feverTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == squadNameDict['Fever'],]
feverTeamStats_2022_vsVixens = feverTeamStats_2022.loc[feverTeamStats_2022['oppSquadId'] == squadNameDict['Vixens'],]

#Intercepts - 3 & 4 in loss, 8 in win
#Total possession changes - 22 & 20 in losses, 17 in win

# %% Moloney vs. Simmons match-up

#Get player stats for the year
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats',
                                               matchOptions = ['regular','final'])
playerStats_2022 = playerStats_2022[2022]

#Get the match Ids from the Fever-Vixens match-ups
matchUpIds = list(vixensTeamStats_2022_vsFever['matchId'].unique())

#Set Moloney & Simmons Ids
moloneySimmonsIds = [991901, 80473]

#Extract player stats from match-ups
centreMatchUpData = playerStats_2022.loc[(playerStats_2022['matchId'].isin(matchUpIds)) &
                                         (playerStats_2022['playerId'].isin(moloneySimmonsIds)),]

#Moloney in WD for 2nd match-up

#Simmons built up feeds in match-ups across the year:
    #23, 32 then 35 in win
#Moloney feeds contrasted from 1st win to 3rd match-up loss
    #29 & 16 (only 9 feeds with attempt in loss)
    
#Extract Simmons stats from the year
simmonsStats = playerStats_2022.loc[playerStats_2022['playerId'] == moloneySimmonsIds[1],]

# %% Fan question

#How often does first goal scorer win?

#Set counters
firstGoalWin = 0
firstGoalLoss = 0

#Loop through years
for year in scoreFlowData.keys():
    
    #Get match IDs
    matchIds = scoreFlowData[year]['matchId'].unique()
    
    #Loop through match Ids
    for matchId in matchIds:
        
        #Extract match data
        currMatch = scoreFlowData[year].loc[scoreFlowData[year]['matchId'] == matchId,].reset_index(drop = True)
        
        #Get first & last score differential
        firstScore = currMatch.loc[currMatch['scoreName'] == 'goal',].reset_index().iloc[0]['scoreDifferential']
        lastScore = currMatch.iloc[-1]['scoreDifferential']
        
        #Check for winner/loser
        if firstScore * lastScore > 0:
            firstGoalWin += 1
        else:
            firstGoalLoss += 1

#Summarise
print(f'First goal losses: {np.round(firstGoalLoss / (firstGoalWin + firstGoalLoss) * 100,2)}%')

#How often does first quarter winner lose?

#Set counters
firstQuarterWin = 0
firstQuarterLoss = 0

#Loop through years
for year in scoreFlowData.keys():
    
    #Get match IDs
    matchIds = scoreFlowData[year]['matchId'].unique()
    
    #Loop through match Ids
    for matchId in matchIds:
        
        #Extract match data
        currMatch = scoreFlowData[year].loc[scoreFlowData[year]['matchId'] == matchId,].reset_index(drop = True)
        
        #Get first & last score differential
        firstQuarter = currMatch.loc[currMatch['period'] == 1,].reset_index().iloc[0]['scoreDifferential']
        lastQuarter = currMatch.iloc[-1]['scoreDifferential']
        
        #Check for winner/loser
        if firstQuarter * lastQuarter > 0:
            firstQuarterWin += 1
        else:
            firstQuarterLoss += 1

#Summarise
print(f'First quarter leader losses: {np.round(firstQuarterLoss / (firstQuarterWin + firstQuarterLoss) * 100,2)}%')

# %% Predictions

# %%% ----- End of 12_giants-gfPreview.py -----