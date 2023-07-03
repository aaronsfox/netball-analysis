# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data for special FATF episode.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore
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
             8118: 'GIANTS',
             809:'Magic',
             805: 'Mystics',
             803: 'Pulse',
             808: 'Steel',
             802: 'Tactix'}
squadNameDict = {'Vixens': 804,
                 'Swifts': 806,
                 'Firebirds': 807,
                 'Lightning': 8117,
                 'Fever': 810,
                 'Magpies': 8119,
                 'Thunderbirds': 801,
                 'GIANTS': 8118,
                 'Magic': 809,
                 'Mystics': 805,
                 'Pulse': 803,
                 'Steel': 808,
                 'Tactix': 802}

#Create a court positions variable
courtPositions = ['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']

#Set base directory for processed data
baseDir = '..\\..\\..\\..\\data\\matchCentre\\processed'

#Read in line-up data
lineUpData = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = 'all',
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular', 'final'],
                                         joined = True, addSquadNames = True)

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerList',
                                          matchOptions = ['regular','final'],
                                          joined = True, addSquadNames = True)

#Grab unique players from each year
playerData = playerLists.drop_duplicates(subset = ['playerId', 'year'], keep = 'last')[
    ['year', 'playerId', 'firstname', 'surname', 'displayName', 'squadId']
    ].reset_index(drop = True)

# %% Highest scoring years?

#Read in team stats from regular season over time
teamStats_regSeason = collatestats.getSeasonStats(baseDir = baseDir,
                                                  years = 'all',
                                                  fileStem = 'teamStats',
                                                  matchOptions = ['regular'],
                                                  joined = True, addSquadNames = True)

#Extract goals and points stats
teamStats_scoring = teamStats_regSeason[['year', 'squadName', 'roundNo', 'goals', 'points']]

#Collate average simply grouped by year
avgYearlyScoring = teamStats_scoring.groupby('year').mean(numeric_only = True)[['goals','points']]

#Collate average grouped by year and team
avgYearlyTeamScoring = teamStats_scoring.groupby(['year','squadName']).mean(numeric_only = True)[['goals','points']]

# %% Breakdown of scoring by quarter

#Read in team period stats in Super Shot era
teamPeriodStats_superShotEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                           years = [2020, 2021, 2022, 2023],
                                                           fileStem = 'teamPeriodStats',
                                                           matchOptions = ['regular'],
                                                           joined = True, addSquadNames = True)

#Extract goals and points stats
teamPeriodStats_scoring = teamPeriodStats_superShotEra[['year', 'squadName', 'roundNo', 'period',
                                                        'goals', 'points', 'goalAttempts', 'goalMisses',
                                                        'attempts1', 'attempts2', 'goal1', 'goal2']]

#Group by period to investigate scoring
avgPeriodScoring = teamPeriodStats_scoring.groupby('period').mean(numeric_only = True)[['goals', 'points', 'goalAttempts', 'goalMisses',
                                                                                        'attempts1', 'attempts2', 'goal1', 'goal2']]

#Calculate shooting percentage over periods

#Sum the shooting metrics over the periods
sumShootingStats = teamPeriodStats_scoring.groupby('period').sum(numeric_only = True)[['goals', 'goalAttempts', 'goalMisses',
                                                                                       'attempts1', 'attempts2', 'goal1', 'goal2']]

#Calculate various shooting percentages
sumShootingStats['totalShootingPer'] = (sumShootingStats['goalAttempts'] - sumShootingStats['goalMisses']) / sumShootingStats['goalAttempts'] * 100
sumShootingStats['standardShootingPer'] = sumShootingStats['goal1'] / sumShootingStats['attempts1'] * 100
sumShootingStats['superShootingPer'] = sumShootingStats['goal2'] / sumShootingStats['attempts2'] * 100

# %% Average losing margins

#Read in team stats over time
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular', 'final'],
                                        joined = True, addSquadNames = True)

#Collate match results and margins for all games
matchResult = []
margin = []

#Loop through entries
for ii in teamStats.index:
    
    #Set scoring metric
    if teamStats.iloc[ii]['year'] < 2020:
        scoreVar = 'goals'
    else:
        scoreVar = 'points'
        
    #Get teams score
    teamScore = teamStats.iloc[ii][scoreVar]
    
    #Get opposition score
    matchId = teamStats.iloc[ii]['matchId']
    squadId = teamStats.iloc[ii]['squadId']
    oppScore = teamStats.loc[(teamStats['matchId'] == matchId) &
                             (teamStats['squadId'] != squadId),
                             ][scoreVar].values[0]
    
    #Calculate match result and margin
    
    #Margin
    gameMargin = teamScore - oppScore
    margin.append(gameMargin)
    
    #Match result
    if gameMargin < 0:
        matchResult.append('loss')
    elif gameMargin > 0:
        matchResult.append('win')
    else:
        matchResult.append('draw')
        
#Append to dataframe
teamStats['margin'] = margin
teamStats['matchResult'] = matchResult

#Extract just losses
teamStats_losses = teamStats.loc[teamStats['matchResult'] == 'loss',]

#Group by year and team to calculate average losing margin
avgLosingMargins = teamStats_losses.groupby(['year','squadName']).mean(numeric_only = True)[['margin']]

#Calculate number of losses for reference
noOfLosses = teamStats_losses.groupby(['year','squadName']).count()[['matchResult']]

# %% Diamonds player stats

#Read in the player stats from this year
playerStats_2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2023],
                                               fileStem = 'playerStats',
                                               matchOptions = ['regular'],
                                               joined = True, addSquadNames = True)

#Grab 2023 player and line-up data
playerData_2023 = playerData.loc[playerData['year'] == 2023,].reset_index(drop = True)
lineUps_2023 = lineUpData.loc[lineUpData['year'] == 2023,].reset_index(drop = True)

#Identify main major positional grouping for each player
posGroup = []
posGroupings = ['att', 'mid', 'def']

#Loop through players
for ii in playerData_2023.index:
    #Get player Id
    playerId = playerData_2023.iloc[ii]['playerId']
    #Loop through and sum duration in positions
    posTimes = [lineUps_2023.loc[lineUps_2023[pos] == playerId,].sum()[pos] for pos in courtPositions]
    #Calculate the sums for each group
    posSum = np.zeros(3)
    posSum[0] = posTimes[0] + posTimes[1]
    posSum[1] = posTimes[2] + posTimes[3] + posTimes[4]
    posSum[2] = posTimes[5] + posTimes[6]
    #Find maximum and identify the appropriate label
    #Check if player has time on court
    if posSum.sum() > 0:
        posGroup.append(posGroupings[np.argmax(posSum)])
    else:
        posGroup.append('N/A')

#Append to dataframe
playerData_2023['posGroup'] = posGroup

#Set the list of internationals to remove
internationalPlayers = [1006558, 80830, 1019205, 80078, 999128, 1019170, 80010,
                        1010545, 1011747, 80826, 1007298, 1001920, 80559, 80150,
                        80540]

#Set the list of Diamonds players
diamondsPlayers = [80475, 1001708, 1001711, 1001357, 994224, 80299, 80574, 80701,
                   1014130, 80343, 998404, 80577, 1016035, 991901, 1021253]

#Remove international players
playerStatsAus = playerStats_2023.loc[~playerStats_2023['playerId'].isin(internationalPlayers)].reset_index(drop = True)

#Identify diamonds vs. non-diamonds entries
#Add court grouping variable as well
inDiamonds = []
courtGroup = []

#Loop through players
for ii in playerStatsAus.index:
    
    #Diamonds check
    if playerStatsAus.iloc[ii]['playerId'] in diamondsPlayers:
        inDiamonds.append('yes')
    else:
        inDiamonds.append('no')
        
    #Court grouping
    courtGroup.append(playerData_2023.loc[playerData_2023['playerId'] == playerStatsAus.iloc[ii]['playerId'],
                                          ]['posGroup'].values[0])
        
#Add to dataframe
playerStatsAus['inDiamonds'] = inDiamonds
playerStatsAus['courtGroup'] = courtGroup

#Drop the N/A's
playerStatsAus = playerStatsAus.loc[playerStatsAus['courtGroup'] != 'N/A'].reset_index(drop = True)

#Group by diamonds presence and court group to get average stats
avgPlayerStatsDiamonds = playerStatsAus.groupby(['inDiamonds','courtGroup']).mean(numeric_only = True)

#Identify top 3 similar players to Diamonds

#Set list of stats to compare
statsToCompare = ['badHands', 'badPasses', 'blocked', 'blocks', 'centrePassReceives',
                  'contactPenalties', 'deflectionWithGain', 'deflectionWithNoGain',
                  'feedWithAttempt', 'feeds', 'gain', 'generalPlayTurnovers',
                  'goalAssists', 'goalAttempts', 'goalMisses', 'goals',
                  'interceptPassThrown', 'intercepts', 'obstructionPenalties',
                  'pickups', 'rebounds', 'secondPhaseReceive', 'unforcedTurnovers']

#Group player stats and sum the data
sumPlayerStats = playerStatsAus.groupby('playerId').sum(numeric_only = True)

#Convert key stats to per 60 minute values
for stat in statsToCompare:
    sumPlayerStats[stat] = sumPlayerStats[stat] / (sumPlayerStats['minutesPlayed'] / 60)
    
#Extract the per 60 versions of the stats to compare
per60Stats = sumPlayerStats[statsToCompare]

#Apply z-score calculation to stats
per60Stats_z = per60Stats.apply(zscore)

#Extract non-Diamond player Id's stats into Diamonds and non-Diamonds dataframes
nonDiamondsPlayers = list(playerStatsAus.loc[playerStatsAus['inDiamonds'] == 'no',
                                             ]['playerId'].unique())

#Create dictionary to store Diamond comparisons in
playerCompDict = {pId: {'playerId': [], 'distance': []} for pId in diamondsPlayers}

#Create dictionary to store top 3 comparisons
diamondsComparisons = {'diamondsPlayerId': [], 'comp1': [], 'comp2': [], 'comp3': []}

#Loop through Diamonds player Id's
for diamondsId in diamondsPlayers:
    
    #Extract the current Diamonds players statistics
    diamondsStats = per60Stats_z.loc[diamondsId].to_numpy()
    
    #Loop through the non-Diamonds player Ids
    for nonDiamondsId in nonDiamondsPlayers:
        
        #Extract the current non-Diamonds player stats
        nonDiamondsStats = per60Stats_z.loc[nonDiamondsId].to_numpy()
        
        #Calculate Euclidean distance
        playerDist = np.linalg.norm(nonDiamondsStats - diamondsStats)
        
        #Append to dictionary
        playerCompDict[diamondsId]['playerId'].append(nonDiamondsId)
        playerCompDict[diamondsId]['distance'].append(playerDist)
        
    #Append diamonds Id to dictionary
    diamondsComparisons['diamondsPlayerId'].append(diamondsId)
    
    #Sort top 3 comparions
    allDistances = np.array(playerCompDict[diamondsId]['distance'])
    allPlayers = np.array(playerCompDict[diamondsId]['playerId'])
    sortedDistances = np.sort(allDistances)
    
    #Append to dictionary
    diamondsComparisons['comp1'].append(allPlayers[np.where(allDistances == sortedDistances[0])[0][0]])
    diamondsComparisons['comp2'].append(allPlayers[np.where(allDistances == sortedDistances[1])[0][0]])
    diamondsComparisons['comp3'].append(allPlayers[np.where(allDistances == sortedDistances[2])[0][0]])
    
#Convert to dataframe
diamondsComparisons_df = pd.DataFrame.from_dict(diamondsComparisons)

#Convert to player names
diamondsName = []
comp1Name = []
comp2Name = []
comp3Name = []
for ii in diamondsComparisons_df.index:
    diamondsName.append(playerData_2023.loc[playerData_2023['playerId'] == diamondsComparisons_df.iloc[ii]['diamondsPlayerId'],]['displayName'].values[0])
    comp1Name.append(playerData_2023.loc[playerData_2023['playerId'] == diamondsComparisons_df.iloc[ii]['comp1'],]['displayName'].values[0])
    comp2Name.append(playerData_2023.loc[playerData_2023['playerId'] == diamondsComparisons_df.iloc[ii]['comp2'],]['displayName'].values[0])
    comp3Name.append(playerData_2023.loc[playerData_2023['playerId'] == diamondsComparisons_df.iloc[ii]['comp3'],]['displayName'].values[0])
    
#Create dataframe
diamondsPlayerComps = pd.DataFrame(list(zip(diamondsName, comp1Name, comp2Name, comp3Name)),
                                   columns = ['diamondsPlayer', 'comp1', 'comp2', 'comp3'])

# %% Defensive gains in first vs. second half

#Get team period stats for this year
teamPeriodStats_2023 =  collatestats.getSeasonStats(baseDir = baseDir,
                                                    years = [2023],
                                                    fileStem = 'teamPeriodStats',
                                                    matchOptions = ['regular', 'final'],
                                                    joined = True, addSquadNames = True)

#Allocate variable to first or second half
half = []
for ii in teamPeriodStats_2023.index:
    if teamPeriodStats_2023.iloc[ii]['period'] == 1 or teamPeriodStats_2023.iloc[ii]['period'] == 2:
        half.append('first')
    elif teamPeriodStats_2023.iloc[ii]['period'] == 3 or teamPeriodStats_2023.iloc[ii]['period'] == 4:
        half.append('second')
    else:
        half.append('overtime')
        
#Append to dataframe
teamPeriodStats_2023['half'] = half

#Group by half and squad name then average to get gains
halfDefStats = teamPeriodStats_2023.groupby(['half','squadName']).mean(numeric_only = True)[['gain']]

# %% Possession changes across season

#Get team stats for this year
teamStats_2023 = collatestats.getSeasonStats(baseDir = baseDir,years = [2023],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'],
                                             joined = True, addSquadNames = True)

#Group by squad and average possession changes
posChanges = teamStats_2023.groupby('squadName').mean(numeric_only = True)[['possessionChanges']]


# %% ----- End of 16_fatf_analysis.py ----- %% #
