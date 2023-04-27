# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 5 SSN match-ups.
    
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

#Mostly reviewing match stat sheets throughout here --- comments added

# %% GIANTS vs. Magpies

#Super shot attempts
    #14 to 6, but more from the Magpies
#14 gains for Magpies but Gain to goal % of 36%

# %% Thunderbirds vs. Vixens

#Gains
    #19-9 - Vixens missed their 10+ mark and lost
#Vixens gain to goal % of 22% vs. 79% Thunderbirds
    #Thunderbirds were Vixen like from last year in this way

# %% Firebirds vs. Fever

#A lot of stats flipped from 1st to 2nd half from both teams
    #Big one - Firebirds 8 of 10 gains came in 2nd half

# %% Lightning vs. Swifts

#Pretty clean attacking game
    #15 possession changes each, rare to see a game with both teams < 20
#Swifts efficiency entering goal circle
    #Lightning had 16 more feeds, but only 3 more feeds with attempts
    
# %% Liz Watson's game

#Read in player stats over last few years
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2020, 2021, 2022, 2023],
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular','final']) 

#Add year column to dataframes
for year in playerStats.keys():
    playerStats[year]['year'] = [year] * len(playerStats[year])

#Concatenate dataframes
playerStats_all = pd.concat([playerStats[year] for year in playerStats.keys()]).reset_index(drop = True)

#Set Watson id
watsonId = 994224

#Extract Watson stats
watsonPlayerStats = playerStats_all.loc[playerStats_all['playerId'] == watsonId,].reset_index(drop = True)

#Export to review
watsonPlayerStats.to_csv('..\\files\\watsonPlayerStats.csv', index = False)

#Equal 3rd worst general play TO game
    #Couple games with 9 - and then 5 games with 7 - and then this one and some others with 6
#8 contact penalties equals her 3rd highest in an SSN game over last 3 years
#The 16 goal assists is her 2nd lowest over last few years
#30 feeds is actually 3rd lowest game over last few years
#51.5 Netpoints is 7th lowest over last few years
#Bad game - and these few key stats that Watson excels in all declined in this particular game

# %% Shamera Sterling's year

#Extract Sterling player stats
sterlingId = 80830
sterlingPlayerStats = playerStats_all.loc[playerStats_all['playerId'] == sterlingId,].reset_index(drop = True)

#Group by year and average/max
sterlingAvg = sterlingPlayerStats.groupby('year').mean(numeric_only = True)
sterlingMax = sterlingPlayerStats.groupby('year').max(numeric_only = True)

#Export to review
sterlingAvg.to_csv('..\\files\\sterlingAvg.csv', index = True)
sterlingMax.to_csv('..\\files\\sterlingMax.csv', index = True)

#Averaging 1 block per game - just below her highest season average in 2020
    #Leads the league this year (next highest is 0.2)
#Averaging 5.6 contact penalties per game - lowest in SSN career
#Averaging 7.4 gains per game - only down by the tiniest bit from her highest of 7.43 in 2022
    #Leads the league this year
#Averaging 8 deflections per game - highest in SSN career
    #leads the league this year
#Averaging 0.8 general play turnovers - lowest in SSN career
#Averaging 7 penalties per game - lowest in SSN career
#Penalties to gain ratio avg. of 0.95 - less penalties than gains - best in SSN career (would argue best ever probably)
#Averaging 107.8 NetPoints - 23 higher than any other of her season averages
    #Leads the league this year

#Extract 2023 stats, group by player Id and average - export to file
playerStats[2023].groupby('playerId').mean(numeric_only = True).to_csv('..\\files\\playerStats2023.csv', index = True)

# %% Clutch shooting

#Read in scoreflow data from Super Shot era
scoreFlow = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2020, 2021, 2022, 2023],
                                        fileStem = 'scoreFlow',
                                        matchOptions = ['regular','final'])

#Add year column to dataframes
for year in scoreFlow.keys():
    scoreFlow[year]['year'] = [year] * len(scoreFlow[year])

#Concatenate dataframes
scoreFlow_all = pd.concat([scoreFlow[year] for year in scoreFlow.keys()]).reset_index(drop = True)

#Loop through cases and label as clutch shots
#Add a boolean for make and miss as well
#Add option for Super Shot vs. standard
#Clutch definition is when shot puts margin < 5 in the last five minutes of a match
clutchShot = []
makeMiss = []
superShot = []
for ii in scoreFlow_all.index:
    #Get key info
    period = scoreFlow_all.iloc[ii]['period']
    differential = scoreFlow_all.iloc[ii]['scoreDifferential']
    seconds = scoreFlow_all.iloc[ii]['periodSeconds']
    #Check for clutch shot
    if period >= 4 and differential <= 5 and seconds >= 600:
        clutchShot.append(True)
    else:
        clutchShot.append(False)
    #Check for make
    if scoreFlow_all.iloc[ii]['scorePoints'] > 0:
        makeMiss = True
    else:
        makeMiss = False
    #Check for Super Shot
    if scoreFlow_all.iloc[ii]['scoreName'] == '2pt Miss' or scoreFlow_all.iloc[ii]['scoreName'] == '2pt Goal':
        superShot.append(True)
    else:
        superShot.append(False)
        
#Append to dataframe
scoreFlow_all['clutchShot'] = clutchShot
scoreFlow_all['makeMiss'] = makeMiss
scoreFlow_all['superShot'] = superShot

#Extract clutch shots
clutchShots = scoreFlow_all.loc[clutchShot]

#Group by player Id and average score points
playerClutchShotAvg = clutchShots.groupby(['playerId'])['scorePoints'].mean()
playerClutchShotAvg.to_csv('..\\files\\playerClutchShotAvg.csv', index = True)

#Group by player and get a count of makes and misses
playerClutchShotsMakeMiss = clutchShots.groupby(['playerId'])['makeMiss'].value_counts()
playerClutchShotsMakeMiss.to_csv('..\\files\\playerClutchShotsMakeMiss.csv', index = True)

#Look into Super Shots
playerClutchShotSuperMakeMiss = clutchShots.loc[clutchShots['superShot']].groupby(['playerId'])['makeMiss'].value_counts()
playerClutchShotSuperMakeMiss.to_csv('..\\files\\playerClutchShotSuperMakeMiss.csv', index = True)    

#Housby 8th highest number of clutch makes since 2020
    #Only players with more clutch made shots
        #Fowler, Kumwenda, Harten, Koenen, Aiken-George, Nelson, Wood
#Housby 4th highest number of clutch Super Shots made since 2020
    #Only players with more
        #Harten, Wood, Kumwenda
#Housby clutch Super Shot % is 64%
    #Harten is 62.5%, Wood is 74%, Kumwenda is 30%

# %% NetPoints in winning and losing

#Read in team stats from when netpoints started (2018 onwards)
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2018, 2019, 2020, 2021, 2022, 2023],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular','final'])

#Add year column to dataframes
for year in teamStats.keys():
    teamStats[year]['year'] = [year] * len(teamStats[year])

#Concatenate dataframes
teamStats_all = pd.concat([teamStats[year] for year in teamStats.keys()]).reset_index(drop = True)

#Identify winning and losing teams and append variable to dataframe
matchResult = []
for ii in teamStats_all.index:
    #Get match id and squad Id
    matchId = teamStats_all.iloc[ii]['matchId']
    squadId = teamStats_all.iloc[ii]['squadId']
    #Get team score
    if teamStats_all.iloc[ii]['year'] < 2020:
        teamScore = teamStats_all.iloc[ii]['goals']
    else:
        teamScore = teamStats_all.iloc[ii]['points']
    #Get opposition score
    if teamStats_all.iloc[ii]['year'] < 2020:
        oppScore = teamStats_all.loc[(teamStats_all['matchId'] == matchId) &
                                      (teamStats_all['oppSquadId'] == squadId),
                                      ]['goals'].values[0]
    else:
        oppScore = teamStats_all.loc[(teamStats_all['matchId'] == matchId) &
                                      (teamStats_all['oppSquadId'] == squadId),
                                      ]['points'].values[0]
    #Append match result
    if teamScore > oppScore:
        matchResult.append('win')
    elif teamScore < oppScore:
        matchResult.append('loss')
    else:
        matchResult.append('draw')
#Append to dataframe
teamStats_all['matchResult'] = matchResult

#Group by match result and average out netpoints over players
avgPlayerNetPoints = teamStats_all.groupby('matchResult')['netPoints'].mean() / 7

#Check variance 
sdPlayerNetPoints = teamStats_all.groupby('matchResult')['netPoints'].std() / 7

#Wins = 55.5 / Loss = 39.6 / Draw = 45.5
#No real difference in the variance or spread between winning and losing matches

#Check the cutpoint of 50 for proportion of wins
over50NetPointsCount = teamStats_all.loc[teamStats_all['netPoints'] > (50*7)].groupby('matchResult').count()

#81% of games if your team averages > 50 NetPoints per 7 players

#Check the cutpoint of 55 for proportion of wins
over55NetPointsCount = teamStats_all.loc[teamStats_all['netPoints'] > (55*7)].groupby('matchResult').count()

#87% of games if your team averages > 55 NetPoints per 7 players

# %% Prediction

#Read in team stats from SSN
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular','final'])

# Goals scored across entire weekend will sit in top #5
# Check accuracy of this prediction

#Review what this needs to reach to achieve top 5
roundScoring = {'year': [], 'roundNo': [], 'totalGoals': []}

#Loop through years of Super Netball
for year in [2017, 2018, 2019, 2020, 2021, 2022, 2023]:
    
    #Identify regular season matches for current year
    currYearStats = teamStats[year].loc[teamStats[year]['matchType'] == 'regular',].reset_index(drop = True)
    
    #Identify rounds in year
    allRounds = list(currYearStats['roundNo'].unique())
    
    #Loop through rounds
    for roundNo in allRounds:
        
        #Extract and total goals or points
        if year < 2020:
            totalGoals = currYearStats.loc[currYearStats['roundNo'] == roundNo,]['goals'].sum()
        else:
            totalGoals = currYearStats.loc[currYearStats['roundNo'] == roundNo,]['points'].sum()
            
        #Append data
        roundScoring['year'].append(year)
        roundScoring['roundNo'].append(roundNo)
        roundScoring['totalGoals'].append(totalGoals)
    
#Convert to dataframe
roundScoringData = pd.DataFrame.from_dict(roundScoring)

#Equal 14th highest in SSN history
#Expected more from the Giants Magpies game to push the total scoring up

#Round 6 prediction

#Read in team stats from SSN regular
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'])

#One of the closest rounds in SSN history

#Review what this needs to reach to achieve top 5
marginScoring = {'year': [], 'roundNo': [], 'totalMargin': []}

#Loop through years of Super Netball
for year in [2017, 2018, 2019, 2020, 2021, 2022, 2023]:
    
    #Identify regular season matches for current year
    currYearStats = teamStats[year].loc[teamStats[year]['matchType'] == 'regular',].reset_index(drop = True)
    
    #Identify rounds in year
    allRounds = list(currYearStats['roundNo'].unique())
    
    #Loop through rounds
    for roundNo in allRounds:
        
        #Get current round stats
        currRoundStats = currYearStats.loc[currYearStats['roundNo'] == roundNo,]
        
        #Set variable to store margins in
        margin = []
        
        #Extract and total goals or points
        if year < 2020:            
            #Loop through matches
            for matchId in currRoundStats['matchId'].unique():                
                #Sum margin
                scores = currRoundStats.loc[currRoundStats['matchId'] == matchId,]['goals'].to_numpy()
                margin.append(np.abs(scores[0] - scores[1]))            
        else:            
            #Loop through matches
            for matchId in currRoundStats['matchId'].unique():                
                #Sum margin
                scores = currRoundStats.loc[currRoundStats['matchId'] == matchId,]['points'].to_numpy()
                margin.append(np.abs(scores[0] - scores[1]))
                
        #Append data
        marginScoring['year'].append(year)
        marginScoring['roundNo'].append(roundNo)
        marginScoring['totalMargin'].append(np.sum(margin))
    
#Convert to dataframe
marginScoringData = pd.DataFrame.from_dict(marginScoring)

#There was a round in 2020 where the total margin across games came to 7 all up
#To crack top 10 here we need the total margins added to be less than 20 --- which I think is doable

# %% ----- End of 05_rd5_analysis.py ----- %% #

