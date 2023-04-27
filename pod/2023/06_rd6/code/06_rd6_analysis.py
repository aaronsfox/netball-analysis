# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 6 SSN match-ups.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
from math import log as ln
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

# %% Swifts vs. Vixens

#Gain to goal percentage not great for either team
    #56% for Vixens - 63% for Swifts
#Another anomaly of more NetPoints for the losing team
    #Vixens 447 to Swifts 430.5
#Jo Weston 18 penalties = 1/3 of teams


# %% Firebirds vs. GIANTS

#Super Shots again kept GIANTS close
    #58-40 standard shots Firebirds vs. GIANTS
    #13-6 super shots GIANTS vs. Firebirds
#Fast paced game with lots of possession changes
    #32 possession changes for GIANTS / 26 possession changes for Firebirds

# %% Fever vs. Thunderbirds

#Felt like old Thunderbirds were coming out in Q2 & Q3
    #Lots of gains - but gain to goal % was 25% & 60%
    #Luckily came back around with 5 gains at 80% conversion in Q4
#4 super shots equating to 8 goals in Q4 big difference
    #0 for Fever in Q4
#22-16 general play turnovers for Fever vs. TBirds

# %% Lightning vs. Magpies

#Another fast paced game
    #34 possession changes Magpies / 28 possession changes Lightning
#Penalties
    #60 = Magpies / 32 = Lightning
#56% centre pass to goal conversion for Magpies

# %% Spread of gains

#Define function to calculate Shannon diversity index
#See: https://gist.github.com/audy/783125
def sdi(data):
    """ Given a hash { 'species': count } , returns the SDI
    
    >>> sdi({'a': 10, 'b': 20, 'c': 30,})
    1.0114042647073518"""
    
    from math import log as ln
    
    def p(n, N):
        """ Relative abundance """
        if n == 0:
            return 0
        else:
            return (float(n)/N) * ln(float(n)/N)
            
    N = sum(data.values())
    
    return -sum(p(n, N) for n in data.values() if n != 0)

#Collate diversity index for gains within a team population
#Note that values closer to zero = evenness, values closer to 1 = diversity
gainDiversity = {'matchId': [], 'year': [], 'squadId': [], 'roundNo': [], 'sDI': []}

#Read in player stats from regular season matches over SSN era
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular'])

#Loop through teams and matches and calculate gains evenness / diversity

#Loop through years
for year in playerStats.keys():
    
    #Loop through match Id's
    for matchId in playerStats[year]['matchId'].unique():
        
        #Identify the two squads from the match
        squads = playerStats[year].loc[playerStats[year]['matchId'] == matchId,]['squadId'].unique()
        
        #Loop through squads
        for squadId in squads:
            
            #Get round number
            roundNo = playerStats[year].loc[(playerStats[year]['matchId'] == matchId) &
                                                (playerStats[year]['squadId'] == squadId),
                                                ]['roundNo'].unique()[0]
            
            #Get data for current squad only taking those who played
            currPlayerData = playerStats[year].loc[(playerStats[year]['matchId'] == matchId) &
                                                   (playerStats[year]['squadId'] == squadId) & 
                                                   (playerStats[year]['minutesPlayed'] > 0),].reset_index(drop = True)
            
            #Put player gain data in dictionary
            playerGains = {currPlayerData.iloc[ii]['playerId']: currPlayerData.iloc[ii]['gain'] for ii in currPlayerData.index}
            
            #Calculate diversity index
            sInd = 1 - (sdi(playerGains) / ln(len(playerGains.keys())))
            
            #Append data to dictionary
            gainDiversity['matchId'].append(matchId)
            gainDiversity['year'].append(year)
            gainDiversity['squadId'].append(squadId)
            gainDiversity['roundNo'].append(roundNo)
            gainDiversity['sDI'].append(sInd)

#Convert to dataframe
gainDiversityData = pd.DataFrame.from_dict(gainDiversity)

#Average by squad and year
gainDiversityDataSeasonAvg = gainDiversityData.groupby(['year','squadId']).mean()['sDI'].reset_index(drop = False)

#Take a look at average and game-by-game Thunderbirds data
gainDiversityDataSeasonAvg_Thunderbirds = gainDiversityDataSeasonAvg.loc[gainDiversityDataSeasonAvg['squadId'] == squadNameDict['Thunderbirds'],]
gainDiversityData_Thunderbirds = gainDiversityData.loc[(gainDiversityData['year'] == 2023) &
                                                       (gainDiversityData['squadId'] == squadNameDict['Thunderbirds'])]

# %% NetPoints team of the round

#Read in regular season player stats for NetPoints era
playerStatsNetPoints = collatestats.getSeasonStats(baseDir = baseDir,
                                                   years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                   fileStem = 'playerStats',
                                                   matchOptions = ['regular'])

#Get line-up data over concurrent period
lineUpsNetPoints = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2018, 2019, 2020, 2021, 2022, 2023],
                                               fileStem = 'lineUps',
                                               matchOptions = ['regular'])

#Set-up dictionary to store data
netPointsData = {'matchId': [], 'playerId': [], 'year': [], 'roundNo': [],
                 'primaryPos': [], 'netPoints': []}

#Loop years
for year in playerStatsNetPoints.keys():
    
    #Loop through player entries
    for ii in range(len(playerStatsNetPoints[year])):
        
        #Get details for current entry
        matchId = playerStatsNetPoints[year].iloc[ii]['matchId']
        playerId = playerStatsNetPoints[year].iloc[ii]['playerId']
        roundNo = playerStatsNetPoints[year].iloc[ii]['roundNo']
        netPoints = playerStatsNetPoints[year].iloc[ii]['netPoints']
        
        #Get players primary position
        #Get current match line-ups
        currLineUps = lineUpsNetPoints[year].loc[lineUpsNetPoints[year]['matchId'] == matchId,]
        
        #Loop through and extract durations of court positions
        posDurations = []
        for courtPos in courtPositions:
            posDurations.append(currLineUps.loc[currLineUps[courtPos] == playerId,]['duration'].sum())
        #Identify maximum time if any greater than zero
        if np.sum(posDurations) > 0:
            primaryPos = courtPositions[np.argmax(posDurations)]
        else:
            primaryPos = 'B'
            
        #Append data to dictionary
        netPointsData['matchId'].append(matchId)
        netPointsData['playerId'].append(playerId)
        netPointsData['year'].append(year)
        netPointsData['roundNo'].append(roundNo)
        netPointsData['primaryPos'].append(primaryPos)
        netPointsData['netPoints'].append(netPoints)
        
#Convert to dataframe
netPointsAll = pd.DataFrame.from_dict(netPointsData)

#Collate team of the week by year and rounds
teamOfTheWeekData = {'year': [], 'roundNo': [], 'playerId': [],
                     'pos': [], 'netPoints': []}

#Loop through years
for year in playerStatsNetPoints.keys():
    
    #Loop through unique rounds
    yearRounds = netPointsAll.loc[netPointsAll['year'] ==  year,]['roundNo'].unique()
    yearRounds.sort()
    for roundNo in yearRounds:
        
        #Loop through court positions
        for courtPos in courtPositions:
        
            #Extract current year and round data for court position
            currNetPointsData = netPointsAll.loc[(netPointsAll['year'] == year) &
                                                 (netPointsAll['roundNo'] == roundNo) &
                                                 (netPointsAll['primaryPos'] == courtPos),
                                                 ].reset_index(drop = True)
            
            #Identify maximum netpoints
            maxInd = np.argmax(currNetPointsData['netPoints'].to_numpy())
            
            #Extract details
            teamOfTheWeekData['year'].append(year)
            teamOfTheWeekData['roundNo'].append(roundNo)
            teamOfTheWeekData['playerId'].append(currNetPointsData['playerId'].to_numpy()[maxInd])
            teamOfTheWeekData['pos'].append(courtPos)
            teamOfTheWeekData['netPoints'].append(currNetPointsData['netPoints'].to_numpy()[maxInd])
            
#Convert to dataframe
teamOfTheWeek = pd.DataFrame.from_dict(teamOfTheWeekData)
            
#Which players have been named the most
#Create a count
teamOfTheWeekCount = teamOfTheWeek.groupby('playerId').count()['netPoints'].reset_index(drop = False)
#Add player names for ease of use
playerName = []
#Loop through player names
for playerId in teamOfTheWeekCount['playerId']:
    
    #Reset year to 2023
    year = 2023
    
    #Set searchingName to true
    searchName = True
    
    #Set while loop to continue to find player name
    while searchName:
    
        #Search in current year
        if len(playerData[year].loc[playerData[year]['playerId'] == playerId,]) > 0:
            #Get player id and break while loop
            playerName.append(playerData[year].loc[playerData[year]['playerId'] == playerId,]['fullName'].values[0])
            searchName = False
        else:
            #Subtract year to go back
            year -= 1
#Add to dataframe
teamOfTheWeekCount['playerName'] = playerName

#Note there have been 5 * 14 + 6 teams = 76 teams for regular season

#Average by player Id and position to get average NetPoints team
teamOfTheWeekAvg = netPointsAll.groupby(['playerId', 'primaryPos']).mean()['netPoints'].reset_index(drop = False)
#Add player names for ease of use
playerName = []
#Loop through player names
for playerId in teamOfTheWeekAvg['playerId']:
    
    #Reset year to 2023
    year = 2023
    
    #Set searchingName to true
    searchName = True
    
    #Set while loop to continue to find player name
    while searchName:
    
        #Search in current year
        if len(playerData[year].loc[playerData[year]['playerId'] == playerId,]) > 0:
            #Get player id and break while loop
            playerName.append(playerData[year].loc[playerData[year]['playerId'] == playerId,]['fullName'].values[0])
            searchName = False
        else:
            #Subtract year to go back
            year -= 1
#Add to dataframe
teamOfTheWeekAvg['playerName'] = playerName

#Identify number of times the player has taken that position
posCount = []
for ii in teamOfTheWeekAvg.index:
    
    #Get player Id and position
    playerId = teamOfTheWeekAvg.iloc[ii]['playerId']
    pos = teamOfTheWeekAvg.iloc[ii]['primaryPos']
    
    #Get count
    posCount.append(len(netPointsAll.loc[(netPointsAll['playerId'] == playerId) &
                                         (netPointsAll['primaryPos'] == pos),]))
teamOfTheWeekAvg['posCount'] = posCount
    
# %% Fits and starts

#Read in score flow data from this year
scoreFlow2023 = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2023],
                                            fileStem = 'scoreFlow',
                                            matchOptions = ['regular']) 
scoreFlow2023 = scoreFlow2023[2023]

#Set dictionary to collect data
fitsAndStarts = {'matchId': [], 'squadId': [], 'period': [],
                 'startDiff': [], 'finishDiff': []}

#Loop through match Id's
for matchId in scoreFlow2023['matchId'].unique():
    
    #Extract current match
    currMatchScoreFlow = scoreFlow2023.loc[scoreFlow2023['matchId'] == matchId,]
    
    #Get the two squads and figure out who is home vs. away
    goals = currMatchScoreFlow.loc[currMatchScoreFlow['scoreName'] == 'goal',].reset_index(drop = True)
    if goals.iloc[1]['scoreDifferential'] < goals.iloc[0]['scoreDifferential']:
        awaySquad = goals.iloc[1]['squadId']
        homeSquad = goals.iloc[1]['oppSquadId']
    else:
        homeSquad = goals.iloc[1]['squadId']
        awaySquad = goals.iloc[1]['oppSquadId']
        
    #Loop through periods and examine margin halfway through vs. at end of period
    for periodNo in [1,2,3,4]:
        
        #Extract current period data
        currPeriodScoreFlow = currMatchScoreFlow.loc[currMatchScoreFlow['period'] == periodNo,].reset_index(drop = True)
        
        #Check for scoring
        if len(currPeriodScoreFlow) > 0:
        
            #Identify index closest to mid-point of period
            midInd = np.where(np.abs(currPeriodScoreFlow['periodSeconds'].to_numpy() - (900/2)) == np.min(np.abs(currPeriodScoreFlow['periodSeconds'].to_numpy() - (900/2))))[0][0]
            
            #Split scoring into first and second half of period
            currPeriodScoreFlowStart = currPeriodScoreFlow[:midInd+1]
            currPeriodScoreFlowFinish = currPeriodScoreFlow[midInd+1:]
            
            #Identify home and away scoring in first half of period
            homeScoringStart = currPeriodScoreFlowStart.loc[currPeriodScoreFlowStart['squadId'] == homeSquad,]['scorePoints'].sum()
            awayScoringStart = currPeriodScoreFlowStart.loc[currPeriodScoreFlowStart['squadId'] == awaySquad,]['scorePoints'].sum()
            
            #Identify home and away scoring in second half of period
            homeScoringFinish = currPeriodScoreFlowFinish.loc[currPeriodScoreFlowFinish['squadId'] == homeSquad,]['scorePoints'].sum()
            awayScoringFinish = currPeriodScoreFlowFinish.loc[currPeriodScoreFlowFinish['squadId'] == awaySquad,]['scorePoints'].sum()
            
            #Calculate scoring differential at start and finish points for each team
            #Home team
            homeDiffStart = homeScoringStart - awayScoringStart
            homeDiffFinish = homeScoringFinish - awayScoringFinish
            #Away team
            awayDiffStart = awayScoringStart - homeScoringStart
            awayDiffFinish = awayScoringFinish - homeScoringFinish
            
            #Append to dictionary
            #Home team
            fitsAndStarts['matchId'].append(matchId)
            fitsAndStarts['squadId'].append(homeSquad)
            fitsAndStarts['period'].append(periodNo)
            fitsAndStarts['startDiff'].append(homeDiffStart)
            fitsAndStarts['finishDiff'].append(homeDiffFinish)
            #Away team
            fitsAndStarts['matchId'].append(matchId)
            fitsAndStarts['squadId'].append(awaySquad)
            fitsAndStarts['period'].append(periodNo)
            fitsAndStarts['startDiff'].append(awayDiffStart)
            fitsAndStarts['finishDiff'].append(awayDiffFinish)
            
#Convert to dataframe
fitsAndStartsData = pd.DataFrame.from_dict(fitsAndStarts)
        
#Create a differential from start to finish
fitsAndStartsData['differential'] = fitsAndStartsData['finishDiff'] - fitsAndStartsData['startDiff']

#Group by squad and average to examine
fitsAndStartsDataAvg = fitsAndStartsData.groupby('squadId').mean()['differential']
        
# %% Games tied up

#Read in scoreflow data across all matches
scoreFlow = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'scoreFlow',
                                        matchOptions = ['regular', 'final']) 

#Set-up dictionary to store data
scoreEndPeriod = {'matchId': [], 'year': [], 'roundNo': [],
                  'endOfPeriod': [], 'scoreDifferential': []}

#Loop through years
for year in scoreFlow.keys():
    
    #Loop through match Id's
    for matchId in scoreFlow[year]['matchId'].unique():
        
        #Loop through four periods
        for periodNo in [1,2,3,4]:
            
            #Quickly check if scoring is available
            if len(scoreFlow[year].loc[(scoreFlow[year]['matchId'] == matchId) &
                                       (scoreFlow[year]['period'] == periodNo)]) > 0:
                
                #Get period data
                periodData = scoreFlow[year].loc[(scoreFlow[year]['matchId'] == matchId) &
                                                 (scoreFlow[year]['period'] == periodNo)].reset_index(drop = True)
                
                #Get and append details
                scoreEndPeriod['matchId'].append(matchId)
                scoreEndPeriod['year'].append(year)
                scoreEndPeriod['roundNo'].append(periodData['roundNo'].unique()[0])
                scoreEndPeriod['endOfPeriod'].append(periodNo)
                scoreEndPeriod['scoreDifferential'].append(periodData.iloc[-1]['scoreDifferential'])
        
#Convert to dataframe
scoreEndPeriodData = pd.DataFrame.from_dict(scoreEndPeriod)

#Calculate number of matches
nMatches = len(scoreEndPeriodData['matchId'].unique())

#Extract just tied up quarter breaks
tiedEndPeriods = scoreEndPeriodData.loc[scoreEndPeriodData['scoreDifferential'] == 0,]

#Group data by quarters and count
quarterTiedCounts = tiedEndPeriods.groupby('endOfPeriod').count()['matchId']

#Group data by year and count
yearTiedCounts = tiedEndPeriods.groupby('year').count()['matchId'].reset_index(drop = False)

#Examine relative to total number of matches
tiedPer = []
for year in yearTiedCounts['year']:
    yearMatches = len(scoreEndPeriodData.loc[scoreEndPeriodData['year'] == year]['matchId'].unique())
    tiedPer.append(yearTiedCounts.loc[yearTiedCounts['year'] == year]['matchId'].values[0] / yearMatches)
yearTiedCounts['relPer'] = tiedPer

# %% Prediction review

#Review prediction

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

#Calculate average (considering games)
marginScoringData['avgMargin'] = marginScoringData['totalMargin'] / 4


# %% ----- End of 06_rd6_analysis.py ----- %% #

