# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 3 SSN match-ups.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
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

#Create player list for years
playerLists = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerList',
                                          matchOptions = ['regular','final'])

#Create a unique player dictionary
#Create dictionary to append players to
playerDict = {'playerId': [],
              'firstName': [], 'surname': [], 'fullName': []}
for year in list(playerLists.keys()):
    
    #Get unique player Id's for year
    uniquePlayerIds = list(playerLists[year]['playerId'].unique())
    
    #Loop through unique player Id's
    for playerId in uniquePlayerIds:
        
        #Check if player Id already in dictionary list
        if not playerId in playerDict['playerId']:
        
            #Extract player details
            playerDetails = playerLists[year].loc[playerLists[year]['playerId'] == playerId,]
            
            #Collate player name variables and append
            playerDict['playerId'].append(playerId)
            playerDict['firstName'].append(playerDetails['firstname'].unique()[0])
            playerDict['surname'].append(playerDetails['surname'].unique()[0])
            playerDict['fullName'].append(f'{playerDetails["firstname"].unique()[0]} {playerDetails["surname"].unique()[0]}')

#Convert to dataframes
playerData = pd.DataFrame.from_dict(playerDict)

# %% Round match-ups

#Mostly reviewing match stat sheets throughout here --- comments added

# %% Swifts vs. Firebirds

#Exact same number of goal attempts and misses
    #Super shot makes the difference

# %% Lightning vs. Thunderbirds

#Centre pass to goal %
    #75% to 54% in favour of Thunderbirds
#Pickups 14-2 in favour of Thunderbirds

# %% Fever vs. Magpies

#100 feeds - how many times has that happened?

#Read in team stats
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular', 'final'])

#Loop through years and display
for year in teamStats.keys():
    #See how many times happened in year
    n100Feeds = np.sum(teamStats[year]['feeds'] >= 100)
    #Print output
    print(f'Number of 100 feed games in {year}: {n100Feeds}')
    print(f'Proportion of 100 feed games in {year}: {n100Feeds / len(teamStats[year]["matchId"].unique()) * 100}')

#Typically happens in less than 20% of games

#596 netpoints to 224 in favour of Fever

#Check netpoints at or above this level & disparity
for year in teamStats.keys():
    if 'netPoints' in list(teamStats[year].columns):
        #Calculate times eqaul or above 596
        nMaxNetPoints = np.sum(teamStats[year]['netPoints'] >= 596)
        #Print output
        print(f'Number of games with as high netpoints in {year}: {nMaxNetPoints}')

#Check other max in 2022
np.max(teamStats[2022]['netPoints'])

#2nd highest team netpoints ever
    #Only beaten by 649 by Firebirds against Lightning in round 2 last year


# %% Vixens vs. Giants

#Vixens 11 gains - +10 again for the win

# %% Maddy Proud's powerful performance

#Read in player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'])

#Collate Proud's performances
proudId = 80439

#Review max performances over years
for year in playerStats.keys():
    #Check if Proud in current year
    if proudId in list(playerStats[year]['playerId'].unique()):
        #Check max stats for year
        proudYearStats = playerStats[year].loc[playerStats[year]['playerId'] == proudId,]
        #Get max stats for key metrics and display
        proudYearStats


#Concatenate Proud stats
proudPlayerStats = pd.concat([playerStats[year].loc[playerStats[year]['playerId'] == proudId,] for year in playerStats.keys()])

#Get netpoints as variable
proudNetPoints = proudPlayerStats[['matchId','netPoints']]

# %% Super Shot influence

#Get scoreflow data from Super Shot years
scoreFlowSuperShot = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = [2020, 2021, 2022, 2023],
                                                 fileStem = 'scoreFlow',
                                                 matchOptions = ['regular', 'final'])

#Collate data to answer queries

#Set-up dictionary to store data for score in Super Shot period
scoringPower5 = {'matchId': [], 'year': [], 'roundNo': [], 'squadId': [], 'period': [],
                 'superAttempts': [], 'standardAttempts': [],
                 'superMakes': [], 'superMisses': [], 'standardMakes': [], 'standardMisses': [],
                 'score': []}

#Loop through years to collate data
for year in scoreFlowSuperShot.keys():
    
    #Loop through matches
    for matchId in scoreFlowSuperShot[year]['matchId'].unique():
        
        #Get the two squads
        squads = scoreFlowSuperShot[year].loc[scoreFlowSuperShot[year]['matchId'] == matchId,
                                              ]['squadId'].unique()
        
        #Loop through the two squads
        for squadId in squads:
            
            #Get metrics for current match and squad
            currSquadData = scoreFlowSuperShot[year].loc[(scoreFlowSuperShot[year]['matchId'] == matchId) &
                                                         (scoreFlowSuperShot[year]['squadId'] == squadId) &
                                                         (scoreFlowSuperShot[year]['periodSeconds'] >= 600),]
            
            #Set basic metrics
            roundNo = currSquadData['roundNo'].unique()[0]
            
            #Loop through periods
            for periodNo in currSquadData['period'].unique():
                
                #Get current period data
                currSquadPeriodData = currSquadData.loc[currSquadData['period'] == periodNo,]
                
                #Collate generic data
                scoringPower5['matchId'].append(matchId)
                scoringPower5['year'].append(year)
                scoringPower5['roundNo'].append(roundNo)
                scoringPower5['squadId'].append(squadId)
                scoringPower5['period'].append(periodNo)
                
                #Check if a shot was attempted
                if len(currSquadPeriodData) > 0:
                    
                    #Collate data
                    scoringPower5['superAttempts'].append(len(currSquadPeriodData.loc[currSquadPeriodData['scoreName'].isin(['2pt Goal', '2pt Miss'])]))
                    scoringPower5['standardAttempts'].append(len(currSquadPeriodData.loc[currSquadPeriodData['scoreName'].isin(['goal', 'miss'])]))
                    scoringPower5['superMakes'].append(len(currSquadPeriodData.loc[currSquadPeriodData['scoreName'].isin(['2pt Goal'])]))
                    scoringPower5['superMisses'].append(len(currSquadPeriodData.loc[currSquadPeriodData['scoreName'].isin(['2pt Miss'])]))
                    scoringPower5['standardMakes'].append(len(currSquadPeriodData.loc[currSquadPeriodData['scoreName'].isin(['goal'])]))
                    scoringPower5['standardMisses'].append(len(currSquadPeriodData.loc[currSquadPeriodData['scoreName'].isin(['miss'])]))
                    scoringPower5['score'].append(currSquadPeriodData['scorePoints'].sum())
                    
                else:
                    
                    #Allocate zeros
                    scoringPower5['superAttempts'].append(0)
                    scoringPower5['standardAttempts'].append(0)
                    scoringPower5['superMakes'].append(0)
                    scoringPower5['superMisses'].append(0)
                    scoringPower5['standardMakes'].append(0)
                    scoringPower5['standardMisses'].append(0)
                    scoringPower5['score'].append(0)

#Convert to dataframe
scoringPower5_df = pd.DataFrame.from_dict(scoringPower5)
                    
#Add in a squad name variable for ease of use
scoringPower5_df['squadName'] = [squadDict[squadId] for squadId in scoringPower5_df['squadId']]

#Extract Giants data
scoringPower5_giants = scoringPower5_df.loc[scoringPower5_df['squadName'] == 'GIANTS',]

#How often does a zero score in the Power 5 period happen?
5 / (len(scoringPower5_df) / 2) * 100

#In this season, who is shooting the least and most number of Super Shots
#Get average stats for teams from this year
teamStats[2023]['squadName'] = [squadDict[squadId] for squadId in teamStats[2023]['squadId']]
avgTeamStats2023 = teamStats[2023].groupby('squadName').mean(numeric_only = True)

#who's been missing the most Super Shots this year
avgScoringPower5_2023 = scoringPower5_df.loc[scoringPower5_df['year'] == 2023,].groupby('squadName').mean(numeric_only = True)

#How many times have individual teams and both not scored a super shot in a whole game?
scoringPower5_teamMatchGrouped = scoringPower5_df.groupby(['matchId','squadName']).sum(numeric_only = True)
19 / (len(scoringPower5_teamMatchGrouped) / 2) * 100
scoringPower5_matchGrouped = scoringPower5_df.groupby('matchId').sum(numeric_only = True)

#Collate individual player stats over Super Shot years
playerStats_superShot = pd.concat([playerStats[year] for year in [2020,2021,2022,2023]])
playerStats_superShot['playerName'] = [playerData.loc[playerData['playerId'] == playerId,]['fullName'].iloc[0] for playerId in playerStats_superShot['playerId']]

# %% Time-scoring continuum

#How many goals are scored each game
#Concatenate all dataframes over the last five years and average
sumTeamsStat_fiveYears = pd.concat([teamStats[year] for year in [2019,2020,2021,2022,2023]]).groupby('matchId').sum(numeric_only = True)

#Get range and avg
print(f'Average goals per game: {np.mean(sumTeamsStat_fiveYears["goals"])}')
print(f'Min goals per game: {np.min(sumTeamsStat_fiveYears["goals"])}') #actually 82
print(f'Max goals per game: {np.max(sumTeamsStat_fiveYears["goals"])}')

#Multiply this by 2.5 seconds
print(f'Average goals per game: {np.mean(sumTeamsStat_fiveYears["goals"]) * 2.5}')
print(f'Min goals per game: {np.min(sumTeamsStat_fiveYears["goals"]) * 2.5}') #actually 82
print(f'Max goals per game: {np.max(sumTeamsStat_fiveYears["goals"]) * 2.5}')

# %% Question - what key stat dictates match outcome in X to goal stats

#Collate differentials in X to goal outputs and margin
goalsFrom = {'matchId': [], 'year': [],
             'centrePassDiff': [], 'turnoverDiff': [], 'gainsDiff': [],
             'scoreDiff': []}

#Loop through years
for year in teamStats.keys():
    
    #Check if stats are present in year
    if 'goalsFromGain' in list(teamStats[year].columns) and 'goalsFromTurnovers' in list(teamStats[year].columns) and 'goalsFromCentrePass' in list(teamStats[year].columns):
        
        #Loop through match Id's
        for matchId in teamStats[year]['matchId'].unique():
            
            #Append general data
            goalsFrom['matchId'].append(matchId)
            goalsFrom['year'].append(year)
            
            #Extract the current match data
            currMatchStats = teamStats[year].loc[teamStats[year]['matchId'] == matchId, ].reset_index(drop = True)
            
            #Extract the differencesa and append
            goalsFrom['centrePassDiff'].append(currMatchStats.iloc[0]['goalsFromCentrePass'] - currMatchStats.iloc[1]['goalsFromCentrePass'])
            goalsFrom['turnoverDiff'].append(currMatchStats.iloc[0]['goalsFromTurnovers'] - currMatchStats.iloc[1]['goalsFromTurnovers'])
            goalsFrom['gainsDiff'].append(currMatchStats.iloc[0]['goalsFromGain'] - currMatchStats.iloc[1]['goalsFromGain'])
            if 'points' in list(currMatchStats.columns):
                goalsFrom['scoreDiff'].append(currMatchStats.iloc[0]['points'] - currMatchStats.iloc[1]['points'])
            else:
                goalsFrom['scoreDiff'].append(currMatchStats.iloc[0]['goals'] - currMatchStats.iloc[1]['goals'])

#Convert to dataframe
goalsFromData = pd.DataFrame.from_dict(goalsFrom).dropna().reset_index(drop = True)
    
#Run linear models on data

#Centre pass
regr_CP = linear_model.LinearRegression()
regr_CP.fit(goalsFromData['centrePassDiff'].to_numpy().reshape(-1,1),
            goalsFromData['scoreDiff'].to_numpy().reshape(-1,1))
pred_CP = regr_CP.predict(goalsFromData['centrePassDiff'].to_numpy().reshape(-1,1))
print('***** CENTRE PASS *****')
print("Mean squared error: %.2f" % mean_squared_error(goalsFromData['scoreDiff'].to_numpy().reshape(-1,1), pred_CP))
print("Coefficient of determination: %.2f" % r2_score(goalsFromData['scoreDiff'].to_numpy().reshape(-1,1), pred_CP))

#Turnovers
regr_TO = linear_model.LinearRegression()
regr_TO.fit(goalsFromData['turnoverDiff'].to_numpy().reshape(-1,1),
            goalsFromData['scoreDiff'].to_numpy().reshape(-1,1))
pred_TO = regr_TO.predict(goalsFromData['turnoverDiff'].to_numpy().reshape(-1,1))
print('***** TURNOVERS *****')
print("Mean squared error: %.2f" % mean_squared_error(goalsFromData['scoreDiff'].to_numpy().reshape(-1,1), pred_TO))
print("Coefficient of determination: %.2f" % r2_score(goalsFromData['scoreDiff'].to_numpy().reshape(-1,1), pred_TO))

#Gains
regr_GN = linear_model.LinearRegression()
regr_GN.fit(goalsFromData['gainsDiff'].to_numpy().reshape(-1,1),
            goalsFromData['scoreDiff'].to_numpy().reshape(-1,1))
pred_GN = regr_GN.predict(goalsFromData['gainsDiff'].to_numpy().reshape(-1,1))
print('***** GAINS *****')
print("Mean squared error: %.2f" % mean_squared_error(goalsFromData['scoreDiff'].to_numpy().reshape(-1,1), pred_GN))
print("Coefficient of determination: %.2f" % r2_score(goalsFromData['scoreDiff'].to_numpy().reshape(-1,1), pred_GN))

# %% Prediction

#Get Liz Watson's player stats from this year and last year
watsonId = 994224
watsonStats_2022 = playerStats[2022].loc[playerStats[2022]['playerId'] == watsonId,]
watsonStats_2023 = playerStats[2023].loc[playerStats[2023]['playerId'] == watsonId,]

#Liz Watson hasn't been putting up the huge numbers like normal this year
#This might be about to change, as she got 40 feeds for the first time this season on the weekend
    #Last year, whenever she had a 40 feed game, it was never a one-off, they were always joined to another 40+ feed game
#Predicting another big circle feed game from Watson this weekend, with a nother 40+



# %% ----- End of 03_rd3_analysis.py ----- %% #