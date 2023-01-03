# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This script tests out the idea that player selection can be solved in a similar
    way to the multiple choice knapsack problem via integer programming. Here we
    take the price of plauyers at the start of the season, alongside their total
    score for the year and optimise who our picks would have been at the start of
    the year to maximise end of year scoring. 
    
    Through the code some other additions might be added, such as:
        - Adding other considerations to cost function (like score volatilty or price growth)
        
    The NS fantasy rules are as follows:
        - A total salary cap of $750,000
        - 3 players from the shooters category
        - 3 players from the midcourters category
        - 3 players from the defenders category
    
"""

# %% Import packages

import pandas as pd
import os
from difflib import SequenceMatcher
import numpy as np
import matplotlib.pyplot as plt
import pulp as pl

# %% Set-up

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

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\..\\..\\data\\matchCentre\\processed'

#Read in player stats data for 2022 season
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2022],
                                          fileStem = 'playerPeriodStats',
                                          matchOptions = ['regular'])
playerStats = playerStats[2022]

#Read in substitutions data
lineUpData = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2022],
                                         fileStem = 'lineUps',
                                         matchOptions = ['regular'])
lineUpData = lineUpData[2022]

#Create player list for years
playerList = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2022],
                                         fileStem = 'playerList',
                                         matchOptions = ['regular'])
playerList = playerList[2022]

#Create dictionary to append players to
playerDict = {'playerId': [],
              'firstName': [], 'surname': [], 'fullName': [],
              'squadId': []}

#Get unique player Id's for year
uniquePlayerIds = list(playerList['playerId'].unique())

#Loop through unique player Id's
for playerId in uniquePlayerIds:
    
    #Extract player details
    playerDetails = playerList.loc[playerList['playerId'] == playerId,]
    
    #Collate player name variables and append
    playerDict['playerId'].append(playerId)
    playerDict['firstName'].append(playerDetails['firstname'].unique()[0])
    playerDict['surname'].append(playerDetails['surname'].unique()[0])
    playerDict['fullName'].append(f'{playerDetails["firstname"].unique()[0]} {playerDetails["surname"].unique()[0]}')
    playerDict['squadId'].append(playerDetails['squadId'].unique()[0])
    
#Convert to dataframe
playerData = pd.DataFrame.from_dict(playerDict)

# %% Read in starting player prices and link up to player data

#Read in starting price data and details
fantasyPlayerDetails = pd.read_csv('..\\..\\data\\startingPrices\\startingPrices_2022.csv')

#Link up player Id's to price database

#Create list to store data in
playerPriceIds = []

#Loop through players in price list
for ii in fantasyPlayerDetails.index:
    
    #Get player full name
    playerFullName = f'{fantasyPlayerDetails.iloc[ii]["firstName"]} {fantasyPlayerDetails.iloc[ii]["surname"].capitalize()}'
    
    #Compare current player name ratio to all from current year
    nameRatios = [SequenceMatcher(None, playerFullName, fullName).ratio() for fullName in playerData['fullName']]
    
    #Get index of maximum ratio
    maxRatioInd = nameRatios.index(np.max(nameRatios))
    
    #Get player Id at the index and append to list
    playerPriceIds.append(playerData.iloc[maxRatioInd]['playerId'])
    
#Append player Id's to price list dataframe
fantasyPlayerDetails['playerId'] = playerPriceIds

# %% Calculate 2022 fantasy scores

#Select the stats to keep in dataset based on what's relevant to fantasy scoring
selectStatsList = ['matchId', 'squadId', 'oppSquadId', 'playerId', 'roundNo',
                  'attempts1', 'attempts2',
                  'goal1', 'goal2', 'goalMisses', 'goalAssists',
                  'feeds', 'feedWithAttempt', 'centrePassReceives',
                  'gain', 'intercepts', 'deflections', 'deflectionWithGain',
                  'deflectionWithNoGain', 'rebounds', 'pickups',
                  'contactPenalties', 'obstructionPenalties',
                  'generalPlayTurnovers', 'interceptPassThrown',
                  'badHands', 'badPasses', 'offsides',
                  'minutesPlayed']

#Extract the stats to use in calculations
fantasyStats = playerStats[selectStatsList]

#Set the 2022 scoring system
pointVals = {'goal1': 2, 'goal2': 5, 'goalMisses': -5,
             'goalAssists': 3, 'feedWithAttempt': 1,
             'gain': 5, 'intercepts': 7, 'deflections': 6,
             'rebounds': 5, 'pickups': 7,
             'generalPlayTurnovers': -5, 'interceptPassThrown': -2,
             'badHands': -2, 'badPasses': -2, 'offsides': -2}

#Create a dictionary to store data in
fantasyScoresDict = {'playerId': [], 'matchId': [], 'roundNo': [],
                     'fantasyScore': []}

#Loop through players and calculate fantasy scores for each round
for playerId in list(fantasyStats['playerId'].unique()):
    
    #Extract current players data
    playerFantasyData = fantasyStats.loc[fantasyStats['playerId'] == playerId,]
    
    #Extract current players position from fantasy data
    #Here we'll just make life easy and not look at any players who aren't in starting price list
    #NOTE: this is a significant limitation that should be fixed in real-world scenarios
    try:
        playerPos = fantasyPlayerDetails.loc[fantasyPlayerDetails['playerId'] == playerId,].reset_index()['position'].iloc[0]
    
        #Loop through rounds to calculate score for each match
        for roundNo in list(playerFantasyData['roundNo'].unique()):
            
            #Set a variable to calculate fantasy score
            fantasyScore = 0
            
            #Extract the data for the current round
            playerRoundFantasyData = playerFantasyData.loc[playerFantasyData['roundNo'] == roundNo,]
            
            #Extract matchId & squad Id
            matchId = playerRoundFantasyData['matchId'].unique()[0]
            squadId = playerRoundFantasyData['squadId'].unique()[0]
            
            #Sum the minutes played and if it's above zero then the player got on court
            totalMinutesPlayed = playerRoundFantasyData['minutesPlayed'].sum()
            
            #Calculate scores if the player was on-court
            if totalMinutesPlayed > 0:
                
                #Add to fantasy score for getting on court
                fantasyScore += 16 #starting score allocated to those who get on court
                
                #Check how many quarters the player was on for
                #Give them the 4 points for each quarter played
                fantasyScore += np.count_nonzero(playerRoundFantasyData['minutesPlayed'].to_numpy()) * 4
                
                #Loop through the scoring elements and add the scoring for these
                for stat in list(pointVals.keys()):
                    fantasyScore += playerRoundFantasyData[stat].sum() * pointVals[stat]
                    
                #Calculate centre pass receives points
                #This requires different point values across the various positions
                if 'GA' in playerPos or 'WA' in playerPos:
                    fantasyScore += np.floor(playerRoundFantasyData['centrePassReceives'].sum() / 2) * 1
                elif 'GD' in playerPos or 'WD' in playerPos:
                    fantasyScore += playerRoundFantasyData['centrePassReceives'].sum() * 3
                    
                #Calculate penalty points
                fantasyScore += np.floor((playerRoundFantasyData['obstructionPenalties'].sum() + playerRoundFantasyData['contactPenalties'].sum()) / 2) * -1
                
                #Check for time in WD from line up data
                #Get the line up data for the match where the player is in WD
                wdLineUpData = lineUpData.loc[(lineUpData['matchId'] == matchId) &
                                              (lineUpData['WD'] == playerId),]
                #Get all line ups used for the team
                teamLineUpData = lineUpData.loc[(lineUpData['matchId'] == matchId) &
                                                (lineUpData['squadId'] == squadId),]
                #Check if they ever played at WD and calculate points if necessary
                if len(wdLineUpData) > 0:
                    #The player played at WD, so we need to check for points
                    #Check if all of the players squad line ups include them at WD
                    #This is indicative of a full game at WD
                    if len(wdLineUpData) == len(teamLineUpData):
                        fantasyScore += 16 #score allocated to full game at WD
                    else:
                        #Check if they played at least half a game at WD
                        #Calculate minutes played at WD and check for over half a game (i.e. 30 mins)
                        if wdLineUpData['duration'].sum() / 60 >= 30:
                            fantasyScore += 8 #score allocated for at least half a game at WD
                            
            #Append data to dictionary
            fantasyScoresDict['playerId'].append(playerId)
            fantasyScoresDict['matchId'].append(matchId)
            fantasyScoresDict['roundNo'].append(roundNo)
            fantasyScoresDict['fantasyScore'].append(fantasyScore)
            
    except:
        
        #Print that player isn't in price list, so we'll just skip for now
        print(f'{playerData.loc[playerData["playerId"] == playerId,].reset_index()["fullName"].iloc[0]} not found in starting list...')
            
#Convert scoring dictionary to dataframe
fantasyScoreData = pd.DataFrame.from_dict(fantasyScoresDict)
      
#Append each players total score to the fantasy details dataframe
#Create list to append to
totalSeasonScores = []
#Loop through player Id's
for playerId in fantasyPlayerDetails['playerId']:
    #Calculate and append total score
    totalSeasonScores.append(fantasyScoreData.loc[fantasyScoreData['playerId'] == playerId,
                                                  ]['fantasyScore'].sum())
#Add to the dataframe
fantasyPlayerDetails['points2022'] = totalSeasonScores
            
### NOTE: scores are pretty accurate, but slightly off - maybe due to stats errors?

# %% Run an integer programming optimisation to identify an optimal 10-player team

#Set-up the integer variables to use in the optimisation

#Set the n for the number of players
n = len(fantasyPlayerDetails)

#Player id as a string linked to the fantasy data index
players = [str(ii) for ii in range(n)]

#Points
points = {str(ii): float(fantasyPlayerDetails['points2022'][ii]) for ii in range(n)}

#Price
price = {str(ii): float(fantasyPlayerDetails['price'][ii]) for ii in range(n)}

#Position variables

#### TODO: likely update the court position labels with the 0.5 options in the
#### next code section. This could be embedded in the same loop as below...

# #Set-up a dictionary to store all positional dictionaries in
# positionLabels = {}
# #Loop through court positions and create individual dictionaries for each
# #Create list of court positions
# courtPositions = ['GK', 'GD', 'WD', 'C', 'WA', 'GA', 'GS']
# #Loop through court positions
# for courtPos in courtPositions:
#     #Create the blank dictionary
#     positionLabels[courtPos] = {}
#     #Loop through player number and identify value for current position
#     for ii in range(n):
#         if courtPos in fantasyPlayerDetails['position'][ii]:
#             positionLabels[courtPos][str(ii)] = 1
#         else:
#             positionLabels[courtPos][str(ii)] = 0
            
#Positional group variables
#Set-up a dictionary to store all group dictionaries in
groupLabels = {'defender': {}, 'midcourt': {}, 'shooter': {}}
#Loop through court groupings and create individual dictionaries for each
#Create lists and dictionaries that link court positions to positional groups
courtGroups = ['defender', 'midcourt', 'shooter']
positionalGroups = {'defender': ['GK', 'GD'],
                    'midcourt': ['WD', 'C', 'WA'],
                    'shooter': ['GA', 'GS']}

#### TODO: does the 0.5 allocation work for DPP?
#### TODO: need to deal with DPP in the same grouping...as they get a 0.5
#Loop through player number and identify value for current group
for ii in range(n):
    
    #Figure out positional groupings for current player
    playerGroups = [not set(fantasyPlayerDetails['position'][ii].split('/')).isdisjoint(positionalGroups[group]) for group in courtGroups]
    #Set the value by summing the boolean values. If it's > 1 then they are a
    #half position; if it's 1 then it's just a single group
    if sum(playerGroups) > 1:
        playerGroupVal = 0.5
    else:
        playerGroupVal = 1.0
    #Allocate the values to the dictionary
    for group in courtGroups:
        if not set(fantasyPlayerDetails['position'][ii].split('/')).isdisjoint(positionalGroups[group]):
            groupLabels[group][str(ii)] = playerGroupVal
        else:
            groupLabels[group][str(ii)] = 0

#Create the problem
problem = pl.LpProblem('netballFantasyKnapsack', pl.LpMaximize)

#Create the player variable
playerVar = pl.LpVariable.dicts('players', players, 0, 1, pl.LpBinary)

#Add the objective function to the problem
#This function is the sum of total points
problem += pl.lpSum([points[ii] * playerVar[ii] for ii in players]), 'objectiveValue'

#Add the constraints
#Total number of players being 10
problem += pl.lpSum([playerVar[ii] for ii in players]) == 10, 'totalPlayers10'
#Total price being under $750,000
problem += pl.lpSum([price[ii] * playerVar[ii] for ii in players]) <= 750000, 'totalPrice750k'
#Have 3:4:3 players from defenders:midcourt:shooters groups
problem += pl.lpSum([groupLabels['defender'][ii] * playerVar[ii] for ii in players]) == 3, 'defenderLimit'
problem += pl.lpSum([groupLabels['midcourt'][ii] * playerVar[ii] for ii in players]) == 4, 'midcourtLimit'
problem += pl.lpSum([groupLabels['shooter'][ii] * playerVar[ii] for ii in players]) == 3, 'shooterLimit'
#At least one player from each position
for courtPos in courtPositions:
    problem += pl.lpSum([positionLabels[courtPos][ii] * playerVar[ii] for ii in players]) >= 1, f'desired{courtPos}'

#Solve the problem
status = problem.solve()

#Print the general status of the problem
print(f'Status: {pl.LpStatus[problem.status]}')

#Create a list that grabs index for selected players
selectedPlayers = []
#Loop through players
for player in problem.variables():
    #Check if player was selected
    if player.varValue == 1.0:
        #Append player index to list
        selectedPlayers.append(int(player.name.split('_')[1]))

#Extract the players from the fantasy details dataframe
selectedPlayerDetails = fantasyPlayerDetails.iloc[selectedPlayers]

#Print out some details about the team
#Price
print(f'Total Price: {selectedPlayerDetails["price"].sum()}')
#Season score
print(f'Season Score: {selectedPlayerDetails["points2022"].sum()}')

#### NOTE: the use of half points for multiple position groups seems to ensure
#### the rules are met for selecting enough players from each positional group

# %% Run an integer programming optimisation to identify an optimal 7-player starting team

#### NOTE: the set-up to pick the 7 isn't exactly working...

#Set-up the integer variables to use in the optimisation

#Set the n for the number of players
n = len(fantasyPlayerDetails)

#Player id as a string linked to the fantasy data index
players = [str(ii) for ii in range(n)]

#Points
points = {str(ii): float(fantasyPlayerDetails['points2022'][ii]) for ii in range(n)}

#Price
price = {str(ii): float(fantasyPlayerDetails['price'][ii]) for ii in range(n)}

#Position variables

#Create list of court positions
courtPositions = ['GK', 'GD', 'WD', 'C', 'WA', 'GA', 'GS']

#Set-up a dictionary to store all positional dictionaries in
positionLabels = {courtPos: {} for courtPos in courtPositions}

# #Loop through court positions and create individual dictionaries for each

# #Loop through court positions
# for courtPos in courtPositions:
#     #Create the blank dictionary
#     positionLabels[courtPos] = {}
#     #Loop through player number and identify value for current position
#     for ii in range(n):
#         if courtPos in fantasyPlayerDetails['position'][ii]:
#             positionLabels[courtPos][str(ii)] = 1
#         else:
#             positionLabels[courtPos][str(ii)] = 0
            
#Loop through player number and identify value for current group
for ii in range(n):
    
    #Figure out positional labels for current player
    playerPositions = [courtPos in fantasyPlayerDetails['position'][ii] for courtPos in courtPositions]
    #Set the value by summing the boolean values. If it's > 1 then they are a
    #half position; if it's 1 then it's just a single group
    if sum(playerGroups) > 1:
        playerPosVal = 0.5
    else:
        playerPosVal = 1.0
    #Allocate the values to the dictionary
    for courtPos in courtPositions:
        if courtPos in fantasyPlayerDetails['position'][ii]:
            positionLabels[courtPos][str(ii)] = playerPosVal
        else:
            positionLabels[courtPos][str(ii)] = 0

#Create the problem
problem = pl.LpProblem('netballFantasyKnapsack', pl.LpMaximize)

#Create the player variable
playerVar = pl.LpVariable.dicts('players', players, 0, 1, pl.LpBinary)

#Add the objective function to the problem
#This function is the sum of total points
problem += pl.lpSum([points[ii] * playerVar[ii] for ii in players]), 'objectiveValue'

#Add the constraints
#Total number of players being 7
problem += pl.lpSum([playerVar[ii] for ii in players]) == 7, 'totalPlayers7'
#Total price being under $650,000
#### NOTE: this could be too high to fill with 3 additional players
problem += pl.lpSum([price[ii] * playerVar[ii] for ii in players]) <= 650000, 'totalPrice650k'
#At least one player from each position to cover starting 7
for courtPos in courtPositions:
    problem += pl.lpSum([positionLabels[courtPos][ii] * playerVar[ii] for ii in players]) >= 1, f'desired{courtPos}'

#Solve the problem
status = problem.solve()

#Print the general status of the problem
print(f'Status: {pl.LpStatus[problem.status]}')

#Create a list that grabs index for selected players
selectedPlayers = []
#Loop through players
for player in problem.variables():
    #Check if player was selected
    if player.varValue == 1.0:
        #Append player index to list
        selectedPlayers.append(int(player.name.split('_')[1]))

#Extract the players from the fantasy details dataframe
startingPlayerDetails = fantasyPlayerDetails.iloc[selectedPlayers]

#Print out some details about the team
#Price
print(f'Total Price: {startingPlayerDetails["price"].sum()}')
#Season score
print(f'Season Score: {startingPlayerDetails["points2022"].sum()}')

#### NOTE: the same issue comes up with using full points for the positions that
#### certain players can account for both positions, so you get a double up. Therefore
#### likely need to allocate half points for specific court positions too...
#### This doesn't really work as expected though, as there are so many multiples
#### you can get a 7 that still doesn't cover it...

# %%% ----- End of knapsackTeamProblem.py -----