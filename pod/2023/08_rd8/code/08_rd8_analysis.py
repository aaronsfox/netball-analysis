# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 7 SSN match-ups.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
from math import log as ln
import itertools
import random
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
                                         matchOptions = ['regular', 'final'])

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerList',
                                          matchOptions = ['regular','final'])

#Create a unique player dictionary for each year
#As part of this also give each player a primary court position for the year
#based on where they've played the majority of their time.
#When predicting data for a new season, this data obviously won't be available
#so we will need to take a primary position from Super Netball's squad data
playerDict = {}
for year in list(playerLists.keys()):
    
    #Create dictionary to append players to
    playerDict[year] = {'playerId': [],
                        'firstName': [], 'surname': [], 'fullName': [],
                        'squadId': [], 'primaryPosition': []}
    
    #Get unique player Id's for year
    uniquePlayerIds = list(playerLists[year]['playerId'].unique())
    
    #Loop through unique player Id's
    for playerId in uniquePlayerIds:
        
        #Extract player details
        playerDetails = playerLists[year].loc[playerLists[year]['playerId'] == playerId,]
        
        #Collate player name variables and append
        playerDict[year]['playerId'].append(playerId)
        playerDict[year]['firstName'].append(playerDetails['firstname'].unique()[0])
        playerDict[year]['surname'].append(playerDetails['surname'].unique()[0])
        playerDict[year]['fullName'].append(f'{playerDetails["firstname"].unique()[0]} {playerDetails["surname"].unique()[0]}')
        playerDict[year]['squadId'].append(playerDetails['squadId'].unique()[0])
        
        #Extract the players primary position from the line-up data
        #Create a variable to store durations in
        posDurations = []
        #Loop through and extract durations of court positions
        for courtPos in courtPositions:
            posDurations.append(lineUpData[year].loc[lineUpData[year][courtPos] == playerId,]['duration'].sum())
        #Identify max duration index and look this up in court position list
        #Append this as players primary position for the year
        playerDict[year]['primaryPosition'].append(courtPositions[np.argmax(posDurations)])

#Convert to dataframes
playerData = {}
for year in list(playerLists.keys()):
    playerData[year] = pd.DataFrame.from_dict(playerDict[year])

# %% Round match-ups

#Mostly reviewing match stat sheets throughout here --- comments added where necessary

# %% Firebirds vs. Magpies

# %% Thunderbirds vs. GIANTS

#Gain to goal %
    #Low for both - 53%-23% in Thunderbirds favour
#Time in possession listed as 54-46% in GIANTS favour

# %% Vixens vs. Fever

#Vixens < 10 gains in a win - when did that last happen?

#Read in team stats over Super Netball era
teamStats_superEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                                 fileStem = 'teamStats',
                                                 matchOptions = ['regular', 'final'],
                                                 joined = True, addSquadNames = True)

#Extract Vixens matches
teamStats_superEra_Vixens = teamStats_superEra.loc[teamStats_superEra['squadName'] == 'Vixens',]

#Identify gains and whether match was won or lost
vixensGains_outcomes = {'matchId': [], 'year': [], 'roundNo': [], 'oppSquadName': [],
                        'gains': [], 'margin': [], 'outcome': []}

#Loop through match Id's
for matchId in teamStats_superEra_Vixens['matchId']:
    
    #Get Vixens and opponents score
    if teamStats_superEra.loc[teamStats_superEra['matchId'] == matchId, ]['year'].unique()[0] < 2020:
        vixensScore = teamStats_superEra.loc[(teamStats_superEra['matchId'] == matchId) &
                                             (teamStats_superEra['squadName'] == 'Vixens'),
                                             ]['goals'].values[0]
        oppScore = teamStats_superEra.loc[(teamStats_superEra['matchId'] == matchId) &
                                          (teamStats_superEra['squadName'] != 'Vixens'),
                                          ]['goals'].values[0]
    else:
        vixensScore = teamStats_superEra.loc[(teamStats_superEra['matchId'] == matchId) &
                                             (teamStats_superEra['squadName'] == 'Vixens'),
                                             ]['points'].values[0]
        oppScore = teamStats_superEra.loc[(teamStats_superEra['matchId'] == matchId) &
                                          (teamStats_superEra['squadName'] != 'Vixens'),
                                          ]['points'].values[0]
        
    #Get Vixens gains
    vixensGains = teamStats_superEra.loc[(teamStats_superEra['matchId'] == matchId) &
                                         (teamStats_superEra['squadName'] == 'Vixens'),
                                         ]['gain'].values[0]
    
    #Get opposition squad name, year and round number
    oppSquadName = teamStats_superEra.loc[(teamStats_superEra['matchId'] == matchId) &
                                          (teamStats_superEra['squadName'] != 'Vixens'),
                                          ]['squadName'].values[0]
    year = teamStats_superEra.loc[teamStats_superEra['matchId'] == matchId, ]['year'].unique()[0]
    roundNo = teamStats_superEra.loc[teamStats_superEra['matchId'] == matchId, ]['roundNo'].unique()[0]
    
    #Get margin
    marginVal = vixensScore - oppScore
    
    #Set outcome
    if marginVal > 0:
        outcome = 'win'
    elif marginVal < 0:
        outcome = 'loss'
    else:
        outcome = 'draw'
        
    #Append data
    vixensGains_outcomes['matchId'].append(matchId)
    vixensGains_outcomes['year'].append(year)
    vixensGains_outcomes['roundNo'].append(roundNo)
    vixensGains_outcomes['oppSquadName'].append(oppSquadName)
    vixensGains_outcomes['gains'].append(vixensGains)
    vixensGains_outcomes['margin'].append(marginVal)
    vixensGains_outcomes['outcome'].append(outcome)
    
#Convert to dataframe
vixensGains_df = pd.DataFrame.from_dict(vixensGains_outcomes)

# %% Swifts vs. Lightning

# %% Possession changes

#Read in all team stats
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular', 'final'],
                                        joined = True, addSquadNames = True)

#Extract from when possession changes have been included
teamStats_2018onwards = teamStats.loc[teamStats['year'] >= 2018].reset_index(drop = True)

#Group by match Id and sum the total possession changes across teams
possessionChangesSum = teamStats_2018onwards.groupby('matchId').sum(numeric_only = True)['possessionChanges']

#Group by matchId & squad name to get team possession changes
possessionChangesTeam = teamStats_2018onwards.groupby(['matchId','squadName']).sum(numeric_only = True)['possessionChanges']

#Grab average possession changes from this year
avgPossessionChanges = teamStats_2018onwards.loc[teamStats_2018onwards['year'] == 2023,
                                                 ].groupby('squadName').mean(
                                                     numeric_only = True)['possessionChanges']

# %% Kiera Austin's performance

#Set player Id
austinId = 1001708

#Read in player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'],
                                          joined = True, addSquadNames = True)

#Extract Austin stats
playerStats_Austin = playerStats.loc[playerStats['playerId'] == austinId,]

#Get netpoints ranking
playerStats_Austin_netPoints = playerStats_Austin[['matchId', 'year', 'roundNo', 'squadName', 'netPoints']]

#Get deflections ranking
playerStats_Austin_deflections = playerStats_Austin[['matchId', 'year', 'roundNo', 'squadName', 'deflections']]
playerStats_Austin_deflectionsWithGain = playerStats_Austin[['matchId', 'year', 'roundNo', 'squadName', 'deflectionWithGain']]

#Get goals ranking
playerStats_Austin_goals = playerStats_Austin[['matchId', 'year', 'roundNo', 'squadName', 'goals']]
playerStats_Austin_goals1 = playerStats_Austin[['matchId', 'year', 'roundNo', 'squadName', 'goal1']]

#Get intercepts ranking
playerStats_Austin_intercepts = playerStats_Austin[['matchId', 'year', 'roundNo', 'squadName', 'intercepts']]

# %% Finals calculator

#Generate the possible outcomes for a favourite (F) vs. roughie (R) in each remaining round
# matchOutcomes = {f'round{roundNo}': list(itertools.product('FR', repeat = 4)) for roundNo in range(9,15)}
matchOutcomes = list(itertools.product('FR', repeat = 4*6))

#Set a dictionary of tuples for the remaining games that are left
matchesLeft = {'round9': [('Thunderbirds','Firebirds'), ('Fever', 'Swifts'), ('Lightning','Vixens'), ('Magpies', 'GIANTS')], #round 9
               'round10': [('GIANTS','Lightning'), ('Vixens', 'Thunderbirds'), ('Swifts','Magpies'), ('Fever', 'Firebirds')], #round 10
               'round11': [('Lightning','Magpies'), ('Thunderbirds', 'Fever'), ('Vixens','Swifts'), ('GIANTS', 'Firebirds')], #round 11
               'round12': [('Magpies','Thunderbirds'), ('Fever', 'Lightning'), ('Swifts','GIANTS'), ('Firebirds', 'Vixens')], #round 12
               'round13': [('Thunderbirds','Lightning'), ('Fever', 'GIANTS'), ('Firebirds','Swifts'), ('Vixens', 'Magpies')], #round 13
               'round14': [('Swifts','Thunderbirds'), ('Magpies', 'Fever'), ('Lightning','Firebirds'), ('GIANTS', 'Vixens')], #round 14
               }

#Set a matching favourites-roughies dictionary based on ladder positions at the end of round 8
matchesOdds = {'round9': [('F','R'), ('F', 'R'), ('R','F'), ('R', 'F')], #round 9
               'round10': [('R','F'), ('R', 'F'), ('F','R'), ('F', 'R')], #round 10
               'round11': [('F','R'), ('F', 'R'), ('R','F'), ('F', 'R')], #round 11
               'round12': [('R','F'), ('F', 'R'), ('F','R'), ('R', 'F')], #round 12
               'round13': [('F','R'), ('F', 'R'), ('R','F'), ('F', 'R')], #round 13
               'round14': [('R','F'), ('R', 'F'), ('F','R'), ('R', 'F')], #round 14
               }

#Unpack every match that's left to a single list
matchesLeft_all = []
for roundNo in matchesLeft.keys():
    for matchNo in range(len(matchesLeft[roundNo])):
        matchesLeft_all.append(matchesLeft[roundNo][matchNo])
        
#Unpack every odds that's left to a single list
matchesOdds_all = []
for roundNo in matchesOdds.keys():
    for matchNo in range(len(matchesOdds[roundNo])):
        matchesOdds_all.append(matchesOdds[roundNo][matchNo])

#Set the current ladder points
ladderPoints = {'Thunderbirds': 26, 'Fever': 24, 'Swifts': 22, 'Vixens': 20,
                'Lightning': 12, 'GIANTS': 8, 'Firebirds': 8, 'Magpies': 8}

#Set the current ladder percentage for tiebreak
ladderPerc = {'Thunderbirds': 114.47, 'Fever': 109.49, 'Swifts': 98.6, 'Vixens': 102.01,
              'Lightning': 99.59, 'GIANTS': 95.22, 'Firebirds': 92.66, 'Magpies': 91.84}

#Create dictionary to store outcomes
finalsOutcomes = {'finalists': [], 'favouritesProp': [], 'roughiesProp': []}

#### NOTE: the below brute force approach takes too long, need to randomly sample instead...

# #Loop through the possible match result outcomes
# for outcomes in matchOutcomes:
    
#     #Set list to append winners to
#     winners = []
    
#     #Loop through each match in this outcome series and extract winner
#     for ii in range(len(outcomes)):
        
#         #Get the two relevant tuples from sets
#         matchUp = matchesLeft_all[ii]
#         odd = matchesOdds_all[ii]
        
#         #Select the winner
#         winners.append(matchUp[list(odd).index(outcomes[ii])])
        
#     #Identify the resultant ladder points from this outcome
#     newLadderPoints = [winners.count(squadName)*4 + ladderPoints[squadName] for squadName in ladderPoints.keys()]
    
#     #Create a ladder dataframe
#     finalLadder = pd.DataFrame(list(zip(list(ladderPoints.keys()), newLadderPoints, list(ladderPerc.values()))),
#                                columns = ['squadName', 'points', 'per'])
    
#     #Sort dataframe and extract finalists
#     finalists = list(finalLadder.sort_values(by = ['points', 'per'],
#                                              ascending = False).reset_index(
#                                                  drop = True).iloc[0:4]['squadName'])
                                                 
#     #Collate proportion of favourites that won
#     favouritesProp = outcomes.count('F') / len(matchesLeft_all) * 100
#     roughiesProp = 100 - favouritesProp
    
#     #Append data to dictionary
#     finalsOutcomes['finalists'].append(finalists)
#     finalsOutcomes['favouritesProp'].append(favouritesProp)
#     finalsOutcomes['roughiesProp'].append(roughiesProp)

#First test out the all favourites option, which is first outcome in list
outcomes = matchOutcomes[0]

#Set list to store winners
winners = []

#Loop through each match in this outcome series and extract winner
for ii in range(len(outcomes)):
    
    #Get the two relevant tuples from sets
    matchUp = matchesLeft_all[ii]
    odd = matchesOdds_all[ii]
    
    #Select the winner
    winners.append(matchUp[list(odd).index(outcomes[ii])])
    
#Identify the resultant ladder points from this outcome
newLadderPoints = [winners.count(squadName)*4 + ladderPoints[squadName] for squadName in ladderPoints.keys()]

#Create a ladder dataframe
finalLadder = pd.DataFrame(list(zip(list(ladderPoints.keys()), newLadderPoints, list(ladderPerc.values()))),
                            columns = ['squadName', 'points', 'per'])

#Sort dataframe and extract finalists
finalists = list(finalLadder.sort_values(by = ['points', 'per'],
                                          ascending = False).reset_index(
                                              drop = True).iloc[0:4]['squadName'])

#Unsurprisingly we end up with the same top 4 - Thunderbirds, Fever, Swifts, Vixens

#Next test out no favourites winning, which is last outcome in list
outcomes = matchOutcomes[-1]

#Set list to store winners
winners = []

#Loop through each match in this outcome series and extract winner
for ii in range(len(outcomes)):
    
    #Get the two relevant tuples from sets
    matchUp = matchesLeft_all[ii]
    odd = matchesOdds_all[ii]
    
    #Select the winner
    winners.append(matchUp[list(odd).index(outcomes[ii])])
    
#Identify the resultant ladder points from this outcome
newLadderPoints = [winners.count(squadName)*4 + ladderPoints[squadName] for squadName in ladderPoints.keys()]

#Create a ladder dataframe
finalLadder = pd.DataFrame(list(zip(list(ladderPoints.keys()), newLadderPoints, list(ladderPerc.values()))),
                            columns = ['squadName', 'points', 'per'])

#Sort dataframe and extract finalists
finalists = list(finalLadder.sort_values(by = ['points', 'per'],
                                          ascending = False).reset_index(
                                              drop = True).iloc[0:4]['squadName'])

#With this option, we get Firebirds, Magpies, Swifts & Fever

#Take a random sampling approach and run 100,000 sims

#Set number of sims
nSims = 100000

#Select 100,000 random outcomes from sample
random.seed(12345)
selectedOutcomes = random.sample(matchOutcomes, nSims)

#Iterate over outcomes
for outcomes in selectedOutcomes:
    
    #Set list to store winners
    winners = []
    
    #Loop through each match in this outcome series and extract winner
    for ii in range(len(outcomes)):
        
        #Get the two relevant tuples from sets
        matchUp = matchesLeft_all[ii]
        odd = matchesOdds_all[ii]
        
        #Select the winner
        winners.append(matchUp[list(odd).index(outcomes[ii])])
        
    #Identify the resultant ladder points from this outcome
    newLadderPoints = [winners.count(squadName)*4 + ladderPoints[squadName] for squadName in ladderPoints.keys()]
    
    #Create a ladder dataframe
    finalLadder = pd.DataFrame(list(zip(list(ladderPoints.keys()), newLadderPoints, list(ladderPerc.values()))),
                                columns = ['squadName', 'points', 'per'])
    
    #Sort dataframe and extract finalists
    finalists = list(finalLadder.sort_values(by = ['points', 'per'],
                                              ascending = False).reset_index(
                                                  drop = True).iloc[0:4]['squadName'])
                                                 
    #Collate proportion of favourites that won
    favouritesProp = outcomes.count('F') / len(matchesLeft_all) * 100
    roughiesProp = 100 - favouritesProp
    
    #Append data to dictionary
    finalsOutcomes['finalists'].append(finalists)
    finalsOutcomes['favouritesProp'].append(favouritesProp)
    finalsOutcomes['roughiesProp'].append(roughiesProp)
    
#Convert to dataframe
finalsOutcomes_df = pd.DataFrame.from_dict(finalsOutcomes)

#Convert the finalists to a singular text variable
finalsOutcomes_df['joinedFinalists'] = ['-'.join(ii) for ii in finalsOutcomes_df['finalists']]

#Group by joined outcomes to get the most common finalists scenario
finalsOutcomes_count = finalsOutcomes_df.groupby('joinedFinalists').count()['finalists']

#Probabilities for each team
finalsProbs = {'squadName': [], 'finalsProb': [],
               'avgFavProp': [], 'minFavProp': [], 'maxFavProp': [],
               'avgRoughiesProp': [], 'minRoughiesProp': [], 'maxRoughiesProp': []}

#Loop through squads
for squadName in ladderPoints.keys():
    
    #Identify where the Thunderbirds are in the finalists list
    inFinals = []
    for finalists in finalsOutcomes_df['finalists']:        
        if squadName in finalists:
            inFinals.append(True)
        else:
            inFinals.append(False)
            
    #Calculate proportion of times in finals
    finalsProb = np.sum(inFinals) / nSims * 100
    
    #Calculate min, max & avg proportion of favourites in finals scenarios
    avgFavProp = finalsOutcomes_df['favouritesProp'][inFinals].mean()
    minFavProp = finalsOutcomes_df['favouritesProp'][inFinals].min()
    maxFavProp = finalsOutcomes_df['favouritesProp'][inFinals].max()
    
    #Do the same for roughies
    avgRoughiesProp = finalsOutcomes_df['roughiesProp'][inFinals].mean()
    minRoughiesProp = finalsOutcomes_df['roughiesProp'][inFinals].min()
    maxRoughiesProp = finalsOutcomes_df['roughiesProp'][inFinals].max()
    
    #Append data
    finalsProbs['squadName'].append(squadName)
    finalsProbs['finalsProb'].append(finalsProb)
    finalsProbs['avgFavProp'].append(avgFavProp)
    finalsProbs['minFavProp'].append(minFavProp)
    finalsProbs['maxFavProp'].append(maxFavProp)
    finalsProbs['avgRoughiesProp'].append(avgRoughiesProp)
    finalsProbs['minRoughiesProp'].append(minRoughiesProp)
    finalsProbs['maxRoughiesProp'].append(maxRoughiesProp)
    
#Convert to dataframe
finalsProbs_df = pd.DataFrame.from_dict(finalsProbs)
    
# %% Winning with more penalties

#Read in all team stats
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular', 'final'],
                                        joined = True, addSquadNames = True)

#Set-up a dictionary to store data
winningWithPenalties = {'matchId': [], 'year': [], 'roundNo': [],
                        'squad1': [], 'squad2': [],
                        'squad1_penalties': [], 'squad2_penalties': [],
                        'squad1_score': [], 'squad2_score': [],
                        'morePenalties': [], 'winner': [],
                        'winnerWithMorePenalties': [], 'margin': [], 'penaltyDifferential': []}

#Loop through match Id's
for matchId in teamStats['matchId'].unique():
    
    #Extract data
    currMatch = teamStats.loc[teamStats['matchId'] == matchId,].reset_index(drop = True)
    
    #Extract the two squad names
    squad1 = currMatch.iloc[0]['squadName']
    squad2 = currMatch.iloc[1]['squadName']
    
    #Extract penalties
    squad1_penalties = currMatch.iloc[0]['penalties']
    squad2_penalties = currMatch.iloc[1]['penalties']
    
    #Extract scores
    if currMatch.iloc[0]['year'] < 2020:
        squad1_score = currMatch.iloc[0]['goals']
        squad2_score = currMatch.iloc[1]['goals']
    else:
        squad1_score = currMatch.iloc[0]['points']
        squad2_score = currMatch.iloc[1]['points']
        
    #Extract squad with more penalties and winner
    if squad1_penalties > squad2_penalties:
        morePenalties = currMatch.iloc[0]['squadName']
    elif squad1_penalties < squad2_penalties:
        morePenalties = currMatch.iloc[1]['squadName']
    else:
        morePenalties = 'tie'
        
    #Extract winning squad
    if squad1_score > squad2_score:
        winner = currMatch.iloc[0]['squadName']
    elif squad1_score < squad2_score:
        winner = currMatch.iloc[1]['squadName']
    else:
        winner = 'tie'
        
    #Set margin & penalty differential
    margin = np.abs(squad2_score - squad1_score)
    penaltyDifferential = np.abs(squad2_penalties - squad1_penalties)
    
    #Identify if winner had more penalties
    if morePenalties == winner:
        winnerWithMorePenalties = True
    else:
        winnerWithMorePenalties = False
        
    #Append to dictionary
    winningWithPenalties['matchId'].append(matchId)
    winningWithPenalties['year'].append(currMatch.iloc[0]['year'])
    winningWithPenalties['roundNo'].append(currMatch.iloc[0]['roundNo'])
    winningWithPenalties['squad1'].append(squad1)
    winningWithPenalties['squad2'].append(squad2)
    winningWithPenalties['squad1_penalties'].append(squad1_penalties)
    winningWithPenalties['squad2_penalties'].append(squad2_penalties)
    winningWithPenalties['squad1_score'].append(squad1_score)
    winningWithPenalties['squad2_score'].append(squad2_score)
    winningWithPenalties['morePenalties'].append(morePenalties)
    winningWithPenalties['winner'].append(winner)
    winningWithPenalties['winnerWithMorePenalties'].append(winnerWithMorePenalties)
    winningWithPenalties['margin'].append(margin)
    winningWithPenalties['penaltyDifferential'].append(penaltyDifferential)
    
#Convert to dataframe
winningWithPenalties_df = pd.DataFrame.from_dict(winningWithPenalties)

#Calculate general probability of winning with more penalties
print(f'% Games Won with More Penalties: {winningWithPenalties_df["winnerWithMorePenalties"].sum() / len(winningWithPenalties_df) * 100}')

#Extract the games where this was the case to review
winningWithPenalties_morePenalties = winningWithPenalties_df.loc[winningWithPenalties_df['winnerWithMorePenalties']]
    
# %% Prediction review

#Check Firebirds and Magpies possession changes for the year

#Extract this years team stats
teamStats_2023 = teamStats.loc[teamStats['year'] == 2023].reset_index(drop = True)

#Get the Magpies and Firebirds possession changes
possessionChanges_Magpies = teamStats_2023.loc[teamStats_2023['squadName'] == 'Magpies',
                                               ][['matchId', 'roundNo', 'squadName', 'oppSquadName', 'possessionChanges']]
possessionChanges_Firebirds = teamStats_2023.loc[teamStats_2023['squadName'] == 'Firebirds',
                                                 ][['matchId', 'roundNo', 'squadName', 'oppSquadName', 'possessionChanges']]

# %% Prediction - penalties matching name length

#Read in player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'],
                                          joined = True, addSquadNames = True)

#Look up how many times a player has matched penalty count to name length
penaltiesNameLength = {'matchId': [], 'playerId': [], 'playerName': [],
                       'year': [], 'roundNo': [], 'matchType': [],
                       'nameLength': [], 'penaltyCount': [],
                       'match': []}

#Loop through player entries
for ii in playerStats.index:
    
    #Get player and match details
    playerId = playerStats.iloc[ii]['playerId']
    matchId = playerStats.iloc[ii]['matchId']
    year = playerStats.iloc[ii]['year']
    roundNo = playerStats.iloc[ii]['roundNo']
    matchType = playerStats.iloc[ii]['matchType']
    penaltyCount = playerStats.iloc[ii]['penalties']
    
    #Get player name
    playerName = playerData[year].loc[playerData[year]['playerId'] == playerId,
                                      ]['fullName'].values[0]
    nameLength = len(playerName.replace(' ',''))
    
    #Check for match
    if nameLength == penaltyCount:
        match = True
    else:
        match = False
        
    #Append in dictionary
    penaltiesNameLength['matchId'].append(matchId)
    penaltiesNameLength['playerId'].append(playerId)
    penaltiesNameLength['playerName'].append(playerName)
    penaltiesNameLength['year'].append(year)
    penaltiesNameLength['roundNo'].append(roundNo)
    penaltiesNameLength['matchType'].append(matchType)
    penaltiesNameLength['nameLength'].append(nameLength)
    penaltiesNameLength['penaltyCount'].append(penaltyCount)
    penaltiesNameLength['match'].append(match)
    
#Convert to dataframe
penaltiesNameLength_df = pd.DataFrame.from_dict(penaltiesNameLength)

#Calculate proportion of matches
print(f'% Players with Matched Name Length to Penalties: {penaltiesNameLength_df["match"].sum() / len(penaltiesNameLength_df) * 100}')

#Extract data to look at examples
penaltiesNameLength_matches = penaltiesNameLength_df.loc[penaltiesNameLength_df['match']]

#Look at most frequent in this situation
penaltiesNameLength_matchesCount = penaltiesNameLength_matches.groupby('playerName').count()['nameLength']


# %% ----- End of 08_rd8_analysis.py ----- %% #

