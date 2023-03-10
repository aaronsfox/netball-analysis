# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This code runs through simulations of the 2022 season to select an optimised
    fantasy team for the NetballScoop competition. This will serve asa foundation
    for the 2023 competition.
    
"""

# %% Import packages

import helperFunctions as helper
import pandas as pd
import pulp as pl
import matplotlib.pyplot as plt
import os
import numpy as np
from difflib import SequenceMatcher

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
playerScoreScales = pd.read_csv('..\\data\\fantasyBot2023\\statPredictionsScales\\pastSeasonToPreseasonScales_2023.csv')

#Create list to store score and price predictions in
playerPredictedScores = []
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
    pastSeasonScale = playerScoreScales.loc[playerScoreScales['playerId'] == playerId,]['pastSeasonScale'].values[0]
    preseasonScale = playerScoreScales.loc[playerScoreScales['playerId'] == playerId,]['preseasonScale'].values[0]
    
    #Read in predicted season scores and calculate predicted total
    predictedPlayerData_season = pd.read_csv(f'..\\data\\fantasyBot2023\\statPredictionsFullSeason\\{playerId}_season.csv')
    predictedPlayerData_preseason = pd.read_csv(f'..\\data\\fantasyBot2023\\statPredictionsFullSeason\\{playerId}_preseason.csv')
    
    #Calculate total predicted fantasy score from each dataset
    #Scale by the relative parameters here
    totalFantasyScore_season = predictedPlayerData_season['fantasyScore'].sum() * pastSeasonScale
    totalFantasyScore_preseason = predictedPlayerData_preseason['fantasyScore'].sum() * preseasonScale
    
    #Calculate total predicted fantasy score
    totalFantasyScore = totalFantasyScore_season + totalFantasyScore_preseason
    
    #Work through round to round data to progressively calculate updated price
    #This will be used to calculate end of year price and price change
    for roundNo in roundList:
        
        #Check to see if new player price needs to be calculated based 
        #on the threshold of 3 games being played
        if roundNo > 2:                
            
            #Get the sum of the most recent 3 scores scaled to season/preseason
            recentScoreSum_season = predictedPlayerData_season.iloc[roundNo-3:roundNo]['fantasyScore'].to_numpy().sum() * pastSeasonScale
            recentScoreSum_preseason = predictedPlayerData_preseason.iloc[roundNo-3:roundNo]['fantasyScore'].to_numpy().sum() * preseasonScale
            recentScoreSum = recentScoreSum_season + recentScoreSum_preseason
            #Calculate exact new fantasy price
            exactNewPrice = np.round((playerPrice * 0.00067) + (np.sum(recentScoreSum) / 9))
            #Round down to nearest 5k as per pricing rules
            #Update the player price variable here
            playerPrice = np.floor(exactNewPrice / 5) * 5 * 1000
        
    #Append predicted data alongside player Id, total predicted score & final price to lists
    playerPredictedScores.append(totalFantasyScore)
    playerPredictedFinalPrice.append(playerPrice)
    
#Append new variables to dataframe
fantasyPlayerDetails['predictedPoints'] = playerPredictedScores
fantasyPlayerDetails['predictedPointsAvg'] = fantasyPlayerDetails['predictedPoints'] / len(roundList)
fantasyPlayerDetails['predictedFinalPrice'] = playerPredictedFinalPrice

#Calculate price change variables and errors
fantasyPlayerDetails['predictedPriceChange'] = fantasyPlayerDetails['predictedFinalPrice'] - fantasyPlayerDetails['price']

# %% Make an initial team selection based on whole season simulation

"""

Here we use the overall season prediction to identify an optimal team line-up
that maximises fantasy scoring.

Player selection is solved in a similar way to the multiple choice knapsack
problem via integer programming. Here we take the price of plauyers at the start
of the season, alongside their total score for the year and optimise who our
picks would have been at the start of the year to maximise end of year scoring. 

The problem is split in two parts, whereby the first part picks a starting 7 from
a significant portion of the budget; while the second part picks three for the bench
in a similar way but with a smaller budget.

Through the code some other additions might be added, such as:
    - Adding other considerations to cost function (like score volatilty or price growth)
    
The NS fantasy rules are as follows:
    - A total salary cap of $800,000
    - 3 players from the shooters category
    - 4 players from the midcourters category
    - 3 players from the defenders category

"""

# %% Select the starting seven

#Set the starting seven budget
startingSevenBudget = 715000

#Run an integer programming optimisation to identify an optimal 7-player team

#Set-up the integer variables to use in the optimisation

#Set the n for the number of players
n = len(fantasyPlayerDetails)

#Player id as a string linked to the fantasy data index
players = [str(ii) for ii in range(n)]

#Points
points = {str(ii): float(fantasyPlayerDetails['predictedPoints'][ii]) for ii in range(n)}

#Price
price = {str(ii): float(fantasyPlayerDetails['price'][ii]) for ii in range(n)}

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

#### NOTE: the use of half points for multiple position groups seems to ensure
#### the rules are met for selecting enough players from each positional group

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
# Tier 1: >= 120 (>= 2)
# Tier 2: >= 90 < 120 (<= 3)
# Tier 3: >= 70 < 90 (>= 2)
# Tier 4: >= 40 < 70 (<= 1)
# Tier 5: < 40 (== 0)

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

#Create the problem
problemStarters = pl.LpProblem('netballFantasyStarters', pl.LpMaximize)

#Create the player variable
playerVar = pl.LpVariable.dicts('players', players, 0, 1, pl.LpBinary)

#Add the objective function to the problem
#This function is the sum of total points
problemStarters += pl.lpSum([points[ii] * playerVar[ii] for ii in players]), 'objectiveValue'

#Add the constraints

#Total number of players being 7
problemStarters += pl.lpSum([playerVar[ii] for ii in players]) == 7, 'totalPlayers7'

#Total price being under budget
problemStarters += pl.lpSum([price[ii] * playerVar[ii] for ii in players]) <= startingSevenBudget, 'priceBudget'

#Get each court position at least covered by 1 player
for pos in courtPositions:
    problemStarters += pl.lpSum([positionLabels[pos][ii] * playerVar[ii] for ii in players]) == 1, f'starter{pos}'
    
# #Have 3:4:3 players from defenders:midcourt:shooters groups
# # problem += pl.lpSum([groupLabels['defender'][ii] * playerVar[ii] for ii in players]) == 3, 'defenderLimit'
# # problem += pl.lpSum([groupLabels['midcourt'][ii] * playerVar[ii] for ii in players]) == 4, 'midcourtLimit'
# # problem += pl.lpSum([groupLabels['shooter'][ii] * playerVar[ii] for ii in players]) == 3, 'shooterLimit'
# problem += pl.lpSum([groupLabels['defender'][ii] * playerVar[ii] for ii in players]) == 2, 'defenderLimit'
# problem += pl.lpSum([groupLabels['midcourt'][ii] * playerVar[ii] for ii in players]) == 3, 'midcourtLimit'
# problem += pl.lpSum([groupLabels['shooter'][ii] * playerVar[ii] for ii in players]) == 3, 'shooterLimit'

#Get desired number of players from each tier
problemStarters += pl.lpSum([tierLabels['tier1'][ii] * playerVar[ii] for ii in players]) == 2, 'desiredTier1'
problemStarters += pl.lpSum([tierLabels['tier2'][ii] * playerVar[ii] for ii in players]) == 3, 'desiredTier2'
problemStarters += pl.lpSum([tierLabels['tier3'][ii] * playerVar[ii] for ii in players]) == 2, 'desiredTier3'
problemStarters += pl.lpSum([tierLabels['tier4'][ii] * playerVar[ii] for ii in players]) == 0, 'desiredTier4'
problemStarters += pl.lpSum([tierLabels['tier5'][ii] * playerVar[ii] for ii in players]) == 0, 'desiredTier5'

#Solve the problem
status = problemStarters.solve()

#Print the general status of the problem
print(f'Status: {pl.LpStatus[problemStarters.status]}')

#Create a list that grabs index for selected players
selectedStarters = []
#Loop through players
for player in problemStarters.variables():
    #Check if player was selected
    if player.varValue == 1.0:
        #Append player index to list
        selectedStarters.append(int(player.name.split('_')[1]))

#Extract the players from the fantasy details dataframe
selectedStartersDetails = fantasyPlayerDetails.iloc[selectedStarters]

#Print out some details about the starters

#Price
print(f'Purchase Price: {selectedStartersDetails["price"].sum()}')

#Predicted season score
print(f'Predicted Season Score: {selectedStartersDetails["predictedPoints"].sum()}')

# %% Select the remaining bench players

#Set the starting seven budget
benchBudget = 800000 - selectedStartersDetails['price'].sum()

#Create a dataframe which removes the selected starters
#Also only select players whose price is <= 50k & whose price decreases
fantasyPlayerDetailsRemaining = fantasyPlayerDetails.loc[
    (~fantasyPlayerDetails['playerId'].isin(list(selectedStartersDetails['playerId']))) &
    (fantasyPlayerDetails['price'] <= 50000) &
    (fantasyPlayerDetails['predictedPriceChange'] >= 0)
    ].reset_index(drop = True)

#Run an integer programming optimisation to identify an optimal 3-player bench

#Set-up the integer variables to use in the optimisation

#Set the n for the number of players
n = len(fantasyPlayerDetailsRemaining)

#Player id as a string linked to the fantasy data index
players = [str(ii) for ii in range(n)]

#Points
points = {str(ii): float(fantasyPlayerDetailsRemaining['predictedPoints'][ii]) for ii in range(n)}

#Price
price = {str(ii): float(fantasyPlayerDetailsRemaining['price'][ii]) for ii in range(n)}

#Price change
priceChange = {str(ii): float(fantasyPlayerDetailsRemaining['predictedPriceChange'][ii]) for ii in range(n)}

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

#### NOTE: the use of half points for multiple position groups seems to ensure
#### the rules are met for selecting enough players from each positional group

#Loop through player number and identify value for current group
for ii in range(n):
    
    #Figure out positional groupings for current player
    playerGroups = [not set(fantasyPlayerDetailsRemaining['position'][ii].replace(' ','').split('/')).isdisjoint(positionalGroups[group]) for group in courtGroups]
    playerPositions = [pos in fantasyPlayerDetailsRemaining['position'][ii].replace(' ','').split('/') for pos in courtPositions]
    
    ##### Groups #####
    
    #Set the value by summing the boolean values. If it's > 1 then they are a
    #half position; if it's 1 then it's just a single group
    if sum(playerGroups) > 1:
        playerGroupVal = 0.5
    else:
        playerGroupVal = 1.0
        
    #Allocate the values to the dictionary
    for group in courtGroups:
        if not set(fantasyPlayerDetailsRemaining['position'][ii].replace(' ','').split('/')).isdisjoint(positionalGroups[group]):
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
        if pos in fantasyPlayerDetailsRemaining['position'][ii].replace(' ','').split('/'):
            positionLabels[pos][str(ii)] = playerPositionVal
        else:
            positionLabels[pos][str(ii)] = 0

#Create the problem
problemBench = pl.LpProblem('netballFantasyBench', pl.LpMaximize)

#Create the player variable
playerVar = pl.LpVariable.dicts('players', players, 0, 1, pl.LpBinary)

#Add the objective function to the problem
#This function is the sum of total points + predicted price change
problemBench += pl.lpSum([(points[ii] + priceChange[ii]) * playerVar[ii] for ii in players]), 'objectiveValue'
# problemBench += pl.lpSum([points[ii] * playerVar[ii] for ii in players]), 'objectiveValuePoints'
# problemBench += pl.lpSum([priceChange[ii] * playerVar[ii] for ii in players]), 'objectiveValuePriceChange'

#Add the constraints

#Total number of players being 3
problemBench += pl.lpSum([playerVar[ii] for ii in players]) == 3, 'totalPlayers3'

#Total price being under budget
problemBench += pl.lpSum([price[ii] * playerVar[ii] for ii in players]) <= benchBudget, 'priceBudget'

# #End up with each court position at least covered by 1 player
# for pos in courtPositions:
#     problemStarters += pl.lpSum([positionLabels[pos][ii] * playerVar[ii] for ii in players]) == 1, f'starter{pos}'
    
#Have 1 player each from defenders, midcourt, shooters groups
problemBench += pl.lpSum([groupLabels['defender'][ii] * playerVar[ii] for ii in players]) == 1, 'defenderLimit'
problemBench += pl.lpSum([groupLabels['midcourt'][ii] * playerVar[ii] for ii in players]) == 1, 'midcourtLimit'
problemBench += pl.lpSum([groupLabels['shooter'][ii] * playerVar[ii] for ii in players]) == 1, 'shooterLimit'

#Solve the problem
status = problemBench.solve()

#Print the general status of the problem
print(f'Status: {pl.LpStatus[problemBench.status]}')

#Create a list that grabs index for selected players
selectedBench = []
#Loop through players
for player in problemBench.variables():
    #Check if player was selected
    if player.varValue == 1.0:
        #Append player index to list
        selectedBench.append(int(player.name.split('_')[1]))

#Extract the players from the fantasy details dataframe
selectedBenchDetails = fantasyPlayerDetailsRemaining.iloc[selectedBench]

#Print out some details about the starters

#Price
print(f'Purchase Price: {selectedBenchDetails["price"].sum()}')

#Predicted season score
print(f'Predicted Season Score: {selectedBenchDetails["predictedPoints"].sum()}')

#Predicted price change
print(f'Predicted Price Change: {selectedBenchDetails["predictedPriceChange"].sum()}')

# %% Save team details to file

#Concatenate the dataframes
fantasyTeam = pd.concat(
    [selectedStartersDetails, selectedBenchDetails]
    )[['price', 'surname', 'firstName', 'team', 'position', 'playerId']]

#Print to file
fantasyTeam.to_csv('..\\botTeam\\round1\\teamList.csv', index = False)

# %% ----- End of fantasyBot023_startingTeam.py ----- %% #