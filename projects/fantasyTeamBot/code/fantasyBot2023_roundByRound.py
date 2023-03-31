# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This code runs through the predicted data from the 2023 season to select a
    team with respect to trades for the Netball Scoop fantasy competition.
    
"""

# %% Import packages

import helperFunctions as helper
import pandas as pd
import pulp as pl
import matplotlib.pyplot as plt
import os
import numpy as np
from difflib import SequenceMatcher

# %% Inputs

##### CHANGE INFO WITHIN HERE ######

#Predict from which round
startPredictionsFromRound = 3

#Set number of trades made
#NOTE: trades made for round 2 = 1
tradesMadeSoFar = 1

##### CHANGE INFO WITHIN HERE ######

# %% Set-up

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

#Create dictionary to map squad names to ID's
#ID to name
squadDict = {804: 'Vixens', 806: 'Swifts', 807: 'Firebirds', 8117: 'Lightning',
             810: 'Fever', 8119: 'Magpies', 801: 'Thunderbirds', 8118: 'GIANTS'}
#Name to ID
squadNameDict = {'Vixens': 804, 'Swifts': 806, 'Firebirds': 807, 'Lightning': 8117,
                 'Fever': 810, 'Magpies': 8119, 'Thunderbirds': 801, 'GIANTS': 8118}

#Create a court positions variable
courtPositions = ['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']

#Create a round list to work through
roundList = [ii for ii in range(1,15)]

#Select the stats to keep in dataset based on what's relevant to fantasy scoring
selectStatsList = ['matchId', 'squadId', 'oppSquadId', 'playerId', 'roundNo',
                   'attempt1', 'attempt2',
                   'goal1', 'goal2', 'goalMisses', 'goalAssists',
                   'feeds', 'feedWithAttempt', 'centrePassReceives',
                   'gain', 'intercepts', 'deflections', 'deflectionWithGain',
                   'deflectionWithNoGain', 'rebounds', 'pickups',
                   'contactPenalties', 'obstructionPenalties',
                   'generalPlayTurnovers', 'interceptPassThrown',
                   'badHands', 'badPasses', 'offsides',
                   'netPoints', 'minutesPlayed']

#Create a list of stats to predict
predictStatsList = ['attempt1', 'attempt2',
                    'goal1', 'goal2', 'goalMisses', 'goalAssists',
                    'feeds', 'feedWithAttempt', 'centrePassReceives',
                    'gain', 'intercepts', 'deflections', 'deflectionWithGain',
                    'deflectionWithNoGain', 'rebounds', 'pickups',
                    'contactPenalties', 'obstructionPenalties',
                    'generalPlayTurnovers', 'interceptPassThrown',
                    'badHands', 'badPasses', 'offsides',
                    'minutesPlayed']

#Set the primary stats to examine across the various primary positions
courtPosPrimaryStats = {'GS': ['attempt1', 'attempt2', 'goal1', 'goal2', 'goalMisses', 'goalAssists'], 
                        'GA': ['attempt1', 'attempt2', 'goal1', 'goal2', 'goalMisses', 'goalAssists', 'feeds', 'feedWithAttempt', 'centrePassReceives'], 
                        'WA': ['feeds', 'feedWithAttempt', 'centrePassReceives', 'gain', 'intercepts', 'deflections', 'pickups', 'generalPlayTurnovers'], 
                        'C': ['feeds', 'feedWithAttempt', 'gain', 'intercepts', 'deflections', 'pickups', 'generalPlayTurnovers'], 
                        'WD': ['gain', 'intercepts', 'deflections', 'pickups', 'generalPlayTurnovers', 'contactPenalties', 'obstructionPenalties'], 
                        'GD': ['gain', 'intercepts', 'deflections', 'contactPenalties', 'obstructionPenalties', 'rebounds'], 
                        'GK': ['gain', 'intercepts', 'deflections', 'contactPenalties', 'obstructionPenalties', 'rebounds'], 
                        }

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% Read in relevant data

#Read in line-up data
lineUpData = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2020, 2021, 2022, 2023],
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular', 'preseason'])

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2020, 2021, 2022, 2023],
                                          fileStem = 'playerList',
                                          matchOptions = ['regular','preseason'])

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
playerData[2020] = pd.DataFrame.from_dict(playerDict[2020])
playerData[2021] = pd.DataFrame.from_dict(playerDict[2021])
playerData[2022] = pd.DataFrame.from_dict(playerDict[2022])
playerData[2023] = pd.DataFrame.from_dict(playerDict[2023])

# %% Read in fantasy player details and link up to player details

#Read in starting player prices and link up to player data

#Read in starting price data and details
##### TODO: this might need to change once we progress into rounds...
fantasyPlayerDetails = pd.read_csv('..\\data\\startingPrices\\startingPrices_2023.csv')

#Link up player Id's to price database

#Create list to store data in
playerPriceIds = []
playerNameRatioCheck = []
primaryPos = []

#Loop through players in price list
for ii in fantasyPlayerDetails.index:
    
    #Get player full name
    playerFullName = f'{fantasyPlayerDetails.iloc[ii]["firstName"]} {fantasyPlayerDetails.iloc[ii]["surname"].capitalize()}'
    
    #Compare current player name ratio to all from current year
    #Check 2022 ratios first
    nameRatios = [SequenceMatcher(None, playerFullName, fullName).ratio() for fullName in playerData[2022]['fullName']]
    #If the max here is 1 (or greater than 0.99) then we take it
    if np.max(nameRatios) > 0.94:    
        #Get index of maximum ratio
        maxRatioInd = nameRatios.index(np.max(nameRatios))
        #Get player Id at the index and append to list
        playerPriceIds.append(playerData[2022].iloc[maxRatioInd]['playerId'])
        #Append ratio to check
        playerNameRatioCheck.append(np.max(nameRatios))
        #Append primary court position from 2022
        primaryPos.append(playerData[2022].iloc[maxRatioInd]['primaryPosition'])
    else:
        #We go to check the 2023 preseason name data
        nameRatios = [SequenceMatcher(None, playerFullName, fullName).ratio() for fullName in playerData[2023]['fullName']]
        #Get index of maximum ratio
        maxRatioInd = nameRatios.index(np.max(nameRatios))
        #Get player Id at the index and append to list
        playerPriceIds.append(playerData[2023].iloc[maxRatioInd]['playerId'])
        #Append ratio to check
        playerNameRatioCheck.append(np.max(nameRatios))
        #Append primary court position from 2023
        primaryPos.append(playerData[2023].iloc[maxRatioInd]['primaryPosition'])
    
#Append player Id's to price list dataframe
fantasyPlayerDetails['playerId'] = playerPriceIds
fantasyPlayerDetails['nameRatioCheck'] = playerNameRatioCheck
fantasyPlayerDetails['primaryPosition'] = primaryPos

# %% Read in stat predictions and use to calculate season scores and price changes

#Read in the stat prediction scales
playerScoreScales = pd.read_csv(f'..\\data\\fantasyBot2023\\statPredictionsScales\\regularSeasonScales_2023_rd{startPredictionsFromRound}-onwards.csv')

#Create list to store score and price predictions in
playerPredictedScores = []
playerPredictedScores_fromRound = []
playerPredictedFinalPrice = []

#Loop through players in price list
for playerInd in fantasyPlayerDetails.index:
    
    #Get player full name
    playerFullName = f'{fantasyPlayerDetails.iloc[playerInd]["firstName"]} {fantasyPlayerDetails.iloc[playerInd]["surname"].capitalize()}'
    
    #Store certain data to variables for easier use in calculation
    playerId = fantasyPlayerDetails.iloc[playerInd]['playerId']
    playerPrice = fantasyPlayerDetails.iloc[playerInd]['price']
    playerPrimaryPos = fantasyPlayerDetails.iloc[playerInd]['primaryPosition']
    
    #Get the season vs. preseason scaling for current player
    regularSeasonScale = playerScoreScales.loc[playerScoreScales['playerId'] == playerId,]['regularSeasonScale'].values[0]
    preseasonScale = playerScoreScales.loc[playerScoreScales['playerId'] == playerId,]['preseasonScale'].values[0]
    
    #Read in predicted season scores and calculate predicted total
    predictedPlayerData_season = pd.read_csv(f'..\\data\\fantasyBot2023\\statPredictionsPartialSeason\\rd{startPredictionsFromRound}_onwards\\{playerId}_season.csv')
    predictedPlayerData_preseason = pd.read_csv(f'..\\data\\fantasyBot2023\\statPredictionsPartialSeason\\rd{startPredictionsFromRound}_onwards\\{playerId}_preseason.csv')
    
    #Calculate total predicted fantasy score from each dataset
    
    #Set starting values
    fantasyScoreRegular = []
    fantasyScorePreseason = []
    
    #Loop through rounds
    for roundNo in roundList:
        #Check for actual round data < round to predict onwards
        if roundNo < startPredictionsFromRound:
            #Check for actual data from the round
            try:                
                #Just grab the score from the dataset & multiply by generic scale
                fantasyScoreRegular.append(predictedPlayerData_season.loc[predictedPlayerData_season['roundNo'] == roundNo,
                                                                          ].reset_index(drop = True).iloc[0]['fantasyScore'] * regularSeasonScale)
                fantasyScorePreseason.append(predictedPlayerData_season.loc[predictedPlayerData_season['roundNo'] == roundNo,
                                                                            ].reset_index(drop = True).iloc[0]['fantasyScore'] * preseasonScale)
            #Otherwise append zeros for no score
            except:
                fantasyScoreRegular.append(0)
                fantasyScorePreseason.append(0)
        #Otherwise get the predicted score and scale by expectation
        else:
            #Get the current round expectation for the player
            expScale = playerScoreScales.loc[playerScoreScales['playerId'] == playerId,][f'rd{roundNo}_exp'].values[0]
            #Grab the scores and scale by both factors
            fantasyScoreRegular.append(predictedPlayerData_season.loc[predictedPlayerData_season['roundNo'] == roundNo,
                                                                      ].reset_index(drop = True).iloc[0]['fantasyScore'] * regularSeasonScale * expScale)
            fantasyScorePreseason.append(predictedPlayerData_season.loc[predictedPlayerData_season['roundNo'] == roundNo,
                                                                        ].reset_index(drop = True).iloc[0]['fantasyScore'] * preseasonScale * expScale)

    #Calculate total predicted fantasy score
    #Do this for the entire season plus for from the round onwards we're predicting from
    totalFantasyScore = np.sum(fantasyScoreRegular) + np.sum(fantasyScorePreseason)
    totalFantasyScore_fromRound = np.sum(fantasyScoreRegular[roundList.index(startPredictionsFromRound):]) + np.sum(fantasyScorePreseason[roundList.index(startPredictionsFromRound):])
    
    #Work through round to round data to progressively calculate updated price
    #This will be used to calculate end of year price and price change
    for roundNo in roundList:
        
        #Check to see if new player price needs to be calculated based 
        #on the threshold of 3 games being played
        if roundNo > 2:                
            
            #Get all scores up to the current round
            recentScoreSum_season = fantasyScoreRegular[:roundNo]
            recentScoreSum_preseason = fantasyScorePreseason[:roundNo]
            recentScoreSum = np.array(recentScoreSum_season) + np.array(recentScoreSum_preseason)
            
            #Drop zeros for no gameplay
            recentScoreSum = recentScoreSum[recentScoreSum != 0]
            
            #Check if the player still has 3 valid games
            if len(recentScoreSum) > 2:
                #Grab the most recent 3 games
                recentScoreSum = recentScoreSum[-3:]
                #Calculate exact new fantasy price
                exactNewPrice = np.round((playerPrice * 0.00067) + (np.sum(recentScoreSum) / 9))
                #Round down to nearest 5k as per pricing rules
                #Update the player price variable here
                playerPrice = np.floor(exactNewPrice / 5) * 5 * 1000
        
    #Append predicted data alongside player Id, total predicted score & final price to lists
    playerPredictedScores.append(totalFantasyScore)
    playerPredictedScores_fromRound.append(totalFantasyScore_fromRound)
    playerPredictedFinalPrice.append(playerPrice)
    
#Append new variables to dataframe
fantasyPlayerDetails['predictedPoints'] = playerPredictedScores
fantasyPlayerDetails['predictedPoints_fromRound'] = playerPredictedScores_fromRound
fantasyPlayerDetails['predictedPointsAvg'] = fantasyPlayerDetails['predictedPoints'] / len(roundList)
fantasyPlayerDetails['predictedPointsAvg_fromRound'] = fantasyPlayerDetails['predictedPoints_fromRound'] / (len(roundList) - (startPredictionsFromRound-1))
fantasyPlayerDetails['predictedFinalPrice'] = playerPredictedFinalPrice

#Calculate price change variables and errors
fantasyPlayerDetails['predictedPriceChange'] = fantasyPlayerDetails['predictedFinalPrice'] - fantasyPlayerDetails['price']

# %% Identify a potential new optimised team based on 2 or less trades

"""

Here we start with the original team and identify the optimal 2 trades to both
maximise the team points for the starting seven and maximise profit from the 
bench players.

Through the code some other additions might be added, such as:
    - Adding other considerations to cost function (like score volatilty or price growth)
    
The NS fantasy rules are as follows:
    - A total salary cap of $800,000
    - 3 players from the shooters category
    - 4 players from the midcourters category
    - 3 players from the defenders category

"""

#Read in the team from the prior round as the starting point
priorRoundTeam = pd.read_csv(f'..\\botTeam\\round{startPredictionsFromRound-1}\\teamList.csv')
priorStartingSeven = priorRoundTeam.iloc[0:7]
priorBench = priorRoundTeam.iloc[7:10].reset_index(drop = True)

# %% Create the trade selection problem

#Set the weights for the points and profit factors
weightPoints = 5
weightProfit = 0.1

#Set the team budget
#### TODO: this will change on the basis of player price changes...
teamBudgetMax = 800000
teamBudgetMin = 750000

#Run an integer programming optimisation to identify an optimal 10-player team
#Considering what we currently have + maximising score & price w/ 2 trades

#Set-up the integer variables to use in the optimisation

#Set the n for the number of players
n = len(fantasyPlayerDetails)

#Player id as a string linked to the fantasy data index
players = [str(ii) for ii in range(n)]

#Points (from predicted round onwards)
points = {str(ii): float(fantasyPlayerDetails['predictedPoints_fromRound'][ii]) for ii in range(n)}

#Price
price = {str(ii): float(fantasyPlayerDetails['price'][ii]) for ii in range(n)}

#Price change
priceChange = {str(ii): float(fantasyPlayerDetails['predictedPriceChange'][ii]) for ii in range(n)}

#Position variables
          
#Positional group variables
#Set-up a dictionary to store all group & position dictionaries in
groupLabels = {'defender': {}, 'midcourt': {}, 'shooter': {}}
positionLabels = {'GK': {}, 'GD': {}, 'WD': {}, 'C': {}, 'WA': {}, 'GA': {}, 'GS': {}}
#Loop through court groupings and create individual dictionaries for each
#Create lists and dictionaries that link court positions to positional groups
#Court groupings
courtGroups = ['defender', 'midcourt', 'shooter']
positionalGroups = {'defender': ['GK', 'GD'],
                    'midcourt': ['WD', 'C', 'WA'],
                    'shooter': ['GA', 'GS']}
#Court positions
courtPositions = ['GK', 'GD', 'WD', 'C', 'WA', 'GA', 'GS']

#Loop through player number and identify value for current group
for ii in range(n):
    
    #Figure out positional groupings for current player
    playerGroups = [not set(fantasyPlayerDetails['position'][ii].replace(' ','').split('/')).isdisjoint(positionalGroups[group]) for group in courtGroups]
    playerPositions = [pos in fantasyPlayerDetails['position'][ii].replace(' ','').split('/') for pos in courtPositions]
    
    ##### Groups #####
    
    #Set the value by summing the boolean values. If it's > 1 then they are a
    #half position; if it's 1 then it's just a single group
    if sum(playerGroups) > 1:
        playerGroupVal = 0.5
    else:
        playerGroupVal = 1.0
        
    #Allocate the values to the dictionary
    for group in courtGroups:
        if not set(fantasyPlayerDetails['position'][ii].replace(' ','').split('/')).isdisjoint(positionalGroups[group]):
            groupLabels[group][str(ii)] = playerGroupVal
        else:
            groupLabels[group][str(ii)] = 0
            
    ##### Positions #####
    
    #Set the value by summing the boolean values. If it's > 1 then they are a
    #half position; if it's 1 then it's just a single group
    if sum(playerPositions) > 1:
        playerPositionVal = 0.5
    else:
        playerPositionVal = 1.0
        
    #Allocate the values to the dictionary
    for pos in courtPositions:
        if pos in fantasyPlayerDetails['position'][ii].replace(' ','').split('/'):
            positionLabels[pos][str(ii)] = playerPositionVal
        else:
            positionLabels[pos][str(ii)] = 0

#Tier variables
##### TODO: these might change across the season depending on player value
# Tier 1: >= 120 (>= 2)
# Tier 2: >= 90 < 120 (<= 3)
# Tier 3: >= 70 < 90 (>= 2)
# Tier 4: >= 40 < 70 (<= 1)
# Tier 5: < 40 (<= 3)

#Set desired number of players (or limit value) from each tier
desiredTier1 = 2
desiredTier2 = 3
desiredTier3 = 2
desiredTier4 = 1
desiredTier5 = 3

#Set-up a dictionary to store all group & position dictionaries in
tierLabels = {'tier1': {}, 'tier2': {}, 'tier3': {}, 'tier4': {}, 'tier5': {}}

#Loop through player number and identify value for current group
for ii in range(n):
    
    #Figure out positional groupings for current player
    playerPrice = fantasyPlayerDetails['price'][ii]
    
    #Allocate a starting boolean of Falses for all tiers
    playerTierBool = [False] * len(tierLabels.keys())
    
    #Identify player tier
    if playerPrice >= 120000:
        playerTierBool[0] = True
    elif playerPrice >= 90000:
        playerTierBool[1] = True
    elif playerPrice >= 70000:
        playerTierBool[2] = True
    elif playerPrice >= 40000:
        playerTierBool[3] = True
    else:
        playerTierBool[4] = True
        
    #Allocate tier value to dictionary
    for tierInd in range(len(tierLabels.keys())):
        tierLabels[list(tierLabels.keys())[tierInd]][str(ii)] = playerTierBool[tierInd] * 1.0

#Set variable for players currently on the team
#This will need to be included in the problem as a variable to limit trades
onTeam = {str(ii): 1.0 if fantasyPlayerDetails['playerId'][ii] in list(priorRoundTeam['playerId']) else 0.0 for ii in range(n)}

#Create the problem
problemTeam = pl.LpProblem('netballFantasyTeam', pl.LpMaximize)

#Create the player variable
playerVar = pl.LpVariable.dicts('players', players, 0, 1, pl.LpBinary)

#Add the objective function to the problem
#This function is the sum of total points and profit weighted by factors
#This weighted function is essentially giving players a generic combined 'value'
#that we are trying to maximise with our team
problemTeam += pl.lpSum([((points[ii] * weightPoints) + (priceChange[ii] * weightProfit)) * playerVar[ii] for ii in players]), 'objectiveValue'
# problemTeam += pl.lpSum([points[ii] * playerVar[ii] for ii in players]), 'objectiveValue'

#Add the constraints

#Total number of players being 10
problemTeam += pl.lpSum([playerVar[ii] for ii in players]) == 10, 'totalPlayers10'

#Total price being within budget
problemTeam += pl.lpSum([price[ii] * playerVar[ii] for ii in players]) <= teamBudgetMax, 'teamBudgetMax'
problemTeam += pl.lpSum([price[ii] * playerVar[ii] for ii in players]) >= teamBudgetMin, 'teamBudgetMin'
# problemTeam += pl.lpSum([price[ii] * playerVar[ii] for ii in players]) <= teamBudget, 'teamBudget'

#Get each court position covered by at least 1 player
for pos in courtPositions:
    problemTeam += pl.lpSum([positionLabels[pos][ii] * playerVar[ii] for ii in players]) >= 1, f'starter{pos}'
    
#Have 3:4:3 players from defenders:midcourt:shooters groups
problemTeam += pl.lpSum([groupLabels['defender'][ii] * playerVar[ii] for ii in players]) == 3, 'defenderLimit'
problemTeam += pl.lpSum([groupLabels['midcourt'][ii] * playerVar[ii] for ii in players]) == 4, 'midcourtLimit'
problemTeam += pl.lpSum([groupLabels['shooter'][ii] * playerVar[ii] for ii in players]) == 3, 'shooterLimit'

#Get desired number of players from each tier
problemTeam += pl.lpSum([tierLabels['tier1'][ii] * playerVar[ii] for ii in players]) >= desiredTier1, 'desiredTier1'
problemTeam += pl.lpSum([tierLabels['tier2'][ii] * playerVar[ii] for ii in players]) <= desiredTier2, 'desiredTier2'
problemTeam += pl.lpSum([tierLabels['tier3'][ii] * playerVar[ii] for ii in players]) >= desiredTier3, 'desiredTier3'
problemTeam += pl.lpSum([tierLabels['tier4'][ii] * playerVar[ii] for ii in players]) <= desiredTier4, 'desiredTier4'
problemTeam += pl.lpSum([tierLabels['tier5'][ii] * playerVar[ii] for ii in players]) <= desiredTier5, 'desiredTier5'

#Set trade limit to 2 by retaining at least 8 players from original team
problemTeam += pl.lpSum([onTeam[ii] * playerVar[ii] for ii in players]) >= 8, 'tradeLimit'

#Solve the problem
status = problemTeam.solve()

#Print the general status of the problem
print(f'Status: {pl.LpStatus[problemTeam.status]}')

#Create a list that grabs index for selected players
selectedTeam = []
#Loop through players
for player in problemTeam.variables():
    #Check if player was selected
    if player.varValue == 1.0:
        #Append player index to list
        selectedTeam.append(int(player.name.split('_')[1]))

#Extract the players from the fantasy details dataframe
selectedTeamDetails = fantasyPlayerDetails.iloc[selectedTeam]

#Print out some details about the starters

#Price
print(f'Purchase Price: {selectedTeamDetails["price"].sum()}')

#Predicted season score
print(f'Predicted Season Score: {selectedTeamDetails["predictedPoints"].sum()}')

# %% Chek if trades are logical (i.e. does score improve)

#Identify players who have been traded
tradedPlayersBool = [priorRoundTeam['playerId'][ii] not in list(selectedTeamDetails['playerId']) for ii in priorRoundTeam.index]
tradedPlayers = priorRoundTeam[tradedPlayersBool]

#Identify newly signed players
signedPlayersBool = [selectedTeamDetails['playerId'][ii] not in list(priorRoundTeam['playerId']) for ii in selectedTeamDetails.index]
signedPlayers = selectedTeamDetails[signedPlayersBool]

#Summary for round 2:
    #Verity Simmons proposed trade for Mahalia Cassidy (-ve points) [VOID]
    #Ashleigh Ervin proposed trade for Remi Kamo (+ve points) [APPROVE]
    #TOTAL TRADES MADE = 1
    
#Summary for round 3:
    #Verity Simmons proposed trade for Jess Anstiss (+ve points) [APPROVE]
    #Sunday Aryang proposed trade for Jo Weston (-ve points) [VOID]
    #TOTAL TRADES MADE = 1
    
# %% Save team details to file

#Print to file
try:
    os.mkdir(f'..\\botTeam\\round{startPredictionsFromRound}')
except:
    print('Directory already made for printing current team round...')
selectedTeamDetails[['price', 'surname', 'firstName', 'team', 'position', 'playerId']].to_csv(f'..\\botTeam\\round{startPredictionsFromRound}\\teamList.csv', index = False)

# %% ----- End of fantasyBot2023_roundByRound.py ----- %% #