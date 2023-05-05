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

# %% Vixens vs. Firebirds

#Tale of two halves
    #gains - firebirds 9-6; then Vixens 8-5
    #gain to goal - firebirds 77% H1 to 50% in H2 
    #CP to goal - vixens 58% H1 to 79% in H2
    #posession changes  Vixens 17 in H1 to 8 in H2
#2nd half demolition
    #45-28 2nd half scoring
    
#Was that the biggest single half margin?
#Read in scoreflow data
scoreFlow = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'scoreFlow',
                                        matchOptions = ['regular', 'final'],
                                        joined = True, addSquadNames = True)

#Store dictionary for half margins
halfMargins = {'matchId': [], 'year': [], 'roundNo': [], 
               'squad1': [], 'squad2':[], 'half': [], 'margin': [], 'leadSquad': []}

#Loop through match Id's
for matchId in scoreFlow['matchId'].unique():
    
    #Get current match data
    currMatch = scoreFlow.loc[scoreFlow['matchId'] == matchId,]
    
    #Get the two squad names
    squadNames = currMatch['squadName'].unique()
    
    #Create a half variable
    currMatch['half'] = ['first' if period < 3 else 'second' for period in currMatch['period']]
    
    #Group by squad and half
    halfScores = currMatch.groupby(['squadName', 'half']).sum(numeric_only = True)['scorePoints']
    
    #Subtract scores to get margin
    try:
        firstMargin = halfScores[squadNames[0]]['first'] - halfScores[squadNames[1]]['first']
    except:
        print(f'No first half data for {matchId}...')
    try:
        secondMargin = halfScores[squadNames[0]]['second'] - halfScores[squadNames[1]]['second']
    except:
        print(f'No second half data for {matchId}...')
    
    #Allocate to dataframe
    #First half
    halfMargins['matchId'].append(matchId)
    halfMargins['year'].append(currMatch['year'].unique()[0])
    halfMargins['roundNo'].append(currMatch['roundNo'].unique()[0])
    halfMargins['squad1'].append(squadNames[0])
    halfMargins['squad2'].append(squadNames[1])
    halfMargins['half'].append('first')
    halfMargins['margin'].append(np.abs(firstMargin))
    if firstMargin < 0:
        halfMargins['leadSquad'].append(squadNames[1])
    elif firstMargin > 0:
        halfMargins['leadSquad'].append(squadNames[0])
    elif firstMargin == 0:
        halfMargins['leadSquad'].append('tie')
    #Second half
    halfMargins['matchId'].append(matchId)
    halfMargins['year'].append(currMatch['year'].unique()[0])
    halfMargins['roundNo'].append(currMatch['roundNo'].unique()[0])
    halfMargins['squad1'].append(squadNames[0])
    halfMargins['squad2'].append(squadNames[1])
    halfMargins['half'].append('second')
    halfMargins['margin'].append(np.abs(secondMargin))
    if secondMargin < 0:
        halfMargins['leadSquad'].append(squadNames[1])
    elif secondMargin > 0:
        halfMargins['leadSquad'].append(squadNames[0])
    elif secondMargin == 0:
        halfMargins['leadSquad'].append('tie')
    
#Convert to dataframe
halfMargins_df = pd.DataFrame.from_dict(halfMargins)

#Not quite the highest
    #Saw a 23 goal margin by the Fever over the Tactix in the first half of a round 3 of 2014
#Firebirds fans look away, because this year they hold the top 3 biggest half blowouts:
    #18 in the first half of round 2 vs. Lightning
    #17 in the second half of round 7 against Vixens
    #16 in the second half of round 1 against Thunderbirds

# %% GIANTS vs. Swifts

#Super Shots probably again kept GIANTS close
    #57-46 standard shots 
    #9-5 super shots
#16 gains to 7 in Swifts favour
#80-70% CP conversion in Swifts favour
    #Quite high for the Swifts

# %% Lightning vs. Fever

#Centre pass to goal %
    #91-71% in Fever favour - highest recorded by a team ever
#Only 6 gains to 8 in Lightning favour
    #Low
    #But converted to goal for 100% by both teams
#Missed goal TO
    #1 for Fever; 8 for Lightning
    #75% missed shot conversion to 0 for Fever-Lightning

#Has both team 100% gain to goal ever occurred before?
#Read in team stats data
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = 'all',
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular', 'final'],
                                        joined = True, addSquadNames = True)

#Create counter
gain100CounterYes = 0
gain100CounterNo = 0

#Loop through match Id's
for matchId in teamStats['matchId'].unique():
    
    #Get each teams gain to goal percentage
    gainToGoal = teamStats.loc[teamStats['matchId'] == matchId, ]['gainToGoalPerc'].to_numpy()
    
    #Check if nan
    if not np.isnan(gainToGoal[0]):
    
        #Check if both 100
        if gainToGoal[0] == 100 and gainToGoal[1] == 100:
            gain100CounterYes += 1
        else:
            gain100CounterNo += 1
            
#Actually the first time out of 328 games where both teams gain to goal were 100%

# %% Thunderbirds vs. Magpies

#58% CP to goal conversion for Magpies
    #Dipped as low as 40% in Q1
#Pies had 23 deflections - but no gains from these
#Pies 10 possession changes in first quarter
    #Highest ever?
    
#Read in team period stats
teamPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = 'all',
                                              fileStem = 'teamPeriodStats',
                                              matchOptions = ['regular', 'final'],
                                              joined = True, addSquadNames = True)

#Get possession changes
teamPeriodStats_possessionChanges = teamPeriodStats[['matchId', 'year', 'squadName', 'oppSquadName', 'possessionChanges']]

#Not the highest
#GIANTS had 15 against the Fever in 2020, and other examples are present higher

# %% What is the highest number of penalties in a quarter?

#Extract penalties from period stats imported earlier
teamPeriodStats_penalties = teamPeriodStats[['matchId', 'year', 'roundNo', 'squadName', 'oppSquadName', 'penalties']]

#Highest ever was 34 by the Pulse against the Fever in round 8 of 2011
#Some examples of 33, 32 & 31
    #But only 8 quarters have ever had higher than 30
#Easily the highest so far this year
    #Next highest was 25 in a Q by the Firebirds against the Vixens - also in rd 7

# %% How many players with -ve NNP in a quarter?

#Read in player period stats over NNP years (2018+)
playerPeriodStats_eraNNP = collatestats.getSeasonStats(baseDir = baseDir,
                                                       years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                       fileStem = 'playerPeriodStats',
                                                       matchOptions = ['regular', 'final'],
                                                       joined = True, addSquadNames = True)

#Create dictionary to store data
negNNP = {'matchId': [], 'year': [], 'roundNo': [], 'period': [],
          'squadName': [], 'noNegNNP': []}

#Loop through match Ids
for matchId in playerPeriodStats_eraNNP['matchId'].unique():
    
    #Get current match
    currMatch = playerPeriodStats_eraNNP.loc[playerPeriodStats_eraNNP['matchId'] == matchId,]
    
    #Get the two squads
    squads = currMatch['squadId'].unique()
    
    #Loop through squads
    for squadId in squads:
        
        #Loop through 4 periods
        for periodNo in range(1,5):
            
            #Extract the current teams player stats for the period
            currTeamPeriod = currMatch.loc[(currMatch['squadId'] == squadId) &
                                           (currMatch['period'] == periodNo),]
            
            #Check if period was played
            if len(currTeamPeriod) > 0:
            
                #Count number of players with -ve NNP
                noNegNNP = np.sum(currTeamPeriod['netPoints'].to_numpy() < 0)
                
                #Append data
                negNNP['matchId'].append(matchId)
                negNNP['year'].append(currTeamPeriod['year'].unique()[0])
                negNNP['roundNo'].append(currTeamPeriod['roundNo'].unique()[0])
                negNNP['period'].append(periodNo)
                negNNP['squadName'].append(squadDict[squadId])
                negNNP['noNegNNP'].append(noNegNNP)
                
#Convert to dataframe
negNNP_df = pd.DataFrame.from_dict(negNNP)

# %% What is the worst NNP performance?

#Read in player stats over NNP years (2018+)
playerStats_eraNNP = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                 fileStem = 'playerStats',
                                                 matchOptions = ['regular', 'final'],
                                                 joined = True, addSquadNames = True)

#Extract netpoints into dataframe
playerStats_eraNNP_NNP = playerStats_eraNNP[['matchId', 'playerId', 'year', 'squadName', 'oppSquadName', 'netPoints']]

#Add player name
playerName = []
for ii in playerStats_eraNNP_NNP.index:
    playerName.append(playerData[playerStats_eraNNP_NNP.iloc[ii]['year']].loc[
        playerData[playerStats_eraNNP_NNP.iloc[ii]['year']]['playerId'] == playerStats_eraNNP_NNP.iloc[ii]['playerId'],
        ]['fullName'].values[0])
playerStats_eraNNP_NNP['playerName'] = playerName

#Jo Harten dropped a -63 in a 2022 match-up vs. the Thunderbirds
#Kaylia Stanton dropped a -61.5 in a 2021 match-up vs. the Swifts while playing for the Vixens
#Sophie Garbin currently has the 2 lowest for the year at -23.5 and -23 from matches against the TBirds & Fever

# %% What is the lowest ever Q1 score?

#Extract scoring from period stats imported earlier
teamPeriodStats_scoring = teamPeriodStats[['matchId', 'year', 'roundNo', 'squadName', 'oppSquadName', 'period', 'goals', 'points']]

#Eliminate ET periods  & focus on super shot era
teamPeriodStats_scoring = teamPeriodStats_scoring.loc[(teamPeriodStats_scoring['period'] < 5) &
                                                      (teamPeriodStats_scoring['year'] >= 2020),]

#Since Super Shots have been in play
    #3 quarters that have had 6 scored (2 x in Q4, 1 x in Q1 Vixens vs. Swifts)
    #1 quarter the Tbirds scored 5 (in Q4) vs. Vixens
    #7 has been scored twice by the Firebirds in Rd 1 Q4 and Rd 2 Q2
        #7 by the Magpies equal lowest Q score for the year & lowest Q1 for the year
    
# %% Is 91% CP to Goal % a record?

#Extract from the team stats data
teamStats_cpToGoal = teamStats[['matchId', 'year', 'squadName', 'oppSquadName', 'roundNo', 'centrePassToGoalPerc']]

#91% is the highest recorded for the whole match
#85% achieved 4 times
    #Lightning in 2019
    #Fever in 2021
    #Fever in 2022
    #Magpies in 2022
#Fever has 3 of the top 5 matches for CP to goal %
    #1 each in 2021, 2022 & 2023

# %% Has a GK played the entire game and got zero contact penalties?

#Read in player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'final'],
                                          joined = True, addSquadNames = True)

#Read in line-up data
lineUps = collatestats.getSeasonStats(baseDir = baseDir,
                                      years = 'all',
                                      fileStem = 'lineUps',
                                      matchOptions = ['regular', 'final'],
                                      joined = True, addSquadNames = True)

#Create dictionary to store data
gkMatches = {'matchId': [], 'year': [], 'roundNo': [], 'squadName': [], 
             'playerId': [], 'playerName': [], 'contactPenalties': []}

#Loop through match Id's
for matchId in lineUps['matchId'].unique():
    
    #Get current match
    currMatch = lineUps.loc[lineUps['matchId'] == matchId,]
    
    #Get the two squads
    squads = currMatch['squadId'].unique()
    
    #Loop through squads
    for squadId in squads:
        
        #Get the player Id's in GK
        GKs = currMatch.loc[currMatch['squadId'] == squadId,]['GK'].unique()
        
        #Check for singular GK & relevant player ID(i.e. not a -ve Id)
        if len(GKs) == 1 and GKs[0]> 0:
            
            #Get their contact penalties
            contactPenalties = playerStats.loc[(playerStats['matchId'] == matchId) &
                                               (playerStats['playerId'] == GKs[0]),
                                               ]['contactPenalties'].values[0]
            
            #Get player name
            playerName = playerData[currMatch['year'].unique()[0]].loc[
                playerData[currMatch['year'].unique()[0]]['playerId'] == GKs[0],
                ]['fullName'].values[0]
            
            #Append data
            gkMatches['matchId'].append(matchId)
            gkMatches['year'].append(currMatch['year'].unique()[0])
            gkMatches['roundNo'].append(currMatch['roundNo'].unique()[0])
            gkMatches['squadName'].append(squadDict[squadId])
            gkMatches['playerId'].append(GKs[0])
            gkMatches['playerName'].append(playerName)
            gkMatches['contactPenalties'].append(contactPenalties)
            
#Convert to dataframe
gkMatches_df = pd.DataFrame.from_dict(gkMatches)
            
#Although there is some data to suggest GKs have played entire game with no contact
#penelaties - manually checking these show inaccuracies in early substitution data

#If we check from 2017 onwards for Super Netball era
gkMatches_df_superEra = gkMatches_df.loc[gkMatches_df['year'] >= 2017,]

#Unsurprisingly no other player has achieved this
#Tara Hinchliffe closest with 2 for Firebirds in 2020 rd 8
#Players with 3
    #Sam Poolman twice, once in 2020 and once in 2021
    #Geva Mentor once in 2021
    #Sarah Klau once in 2023
    #Shamera Sterling twice in 2022

# %% Contest for Diamonds WD

#Set Brazill & Parmenter IDs
brazillId = 80299
parmenterId = 1001356

#Extract their player stats
playerStats_WD = playerStats.loc[playerStats['playerId'].isin([brazillId,parmenterId]),]

#Review this years data & average
playerStats_WD_avg2023 = playerStats_WD.loc[playerStats_WD['year'] == 2023,].groupby('playerId').mean(numeric_only = True)

#Review last years data & average
playerStats_WD_avg2022 = playerStats_WD.loc[playerStats_WD['year'] == 2022,].groupby('playerId').mean(numeric_only = True)

# %% Gains, deflections and intercepts of GA & WA

#Get 2010 onwards data as this is when gains started being recorded
playerStats_defensive = playerStats.loc[playerStats['year'] >= 2010,].reset_index(drop = True)

#Set variable to add as attacking-mid
attackingMid = []

#Loop through player stats and identify primary WA & GA players
for ii in playerStats_defensive.index:
    
    #Get player Id & primary position
    playerId = playerStats_defensive.iloc[ii]['playerId']
    year = playerStats_defensive.iloc[ii]['year']
    playerPos = playerData[year].loc[playerData[year]['playerId'] == playerId,
                                     ]['primaryPosition'].values[0]
    
    #Set whether attacking mid
    if playerPos == 'WA' or playerPos == 'GA':
        attackingMid.append(True)
    else:
        attackingMid.append(False)
        
#Add to dataframe
playerStats_defensive['attackingMid'] = attackingMid

#Extract attacking-mid players
playerStats_attackingDefenders = playerStats_defensive.loc[playerStats_defensive['attackingMid'],]
playerStats_attackingDefenders  = playerStats_attackingDefenders[['matchId','squadId','playerId','gain','deflections','intercepts']]

#Group by player Id and average out
playerStats_attackingDefenders_avg = playerStats_attackingDefenders.groupby('playerId').mean(numeric_only = True)[
    ['gain','deflections','intercepts']].reset_index(drop = False)

#Add player names
playerName = []
#Loop through player names
for playerId in playerStats_attackingDefenders_avg['playerId']:
    
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
playerStats_attackingDefenders_avg['playerName'] = playerName

# %% Prediction review

#Vixens with 14 gains & the win

# %% Prediction

#Possession changes in super netball
#Read in team stats data for Super Netball years
teamStats_super = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                              fileStem = 'teamStats',
                                              matchOptions = ['regular', 'final'],
                                              joined = True, addSquadNames = True)

#Group by match ID and sum to get total possession changes
superNetball_posessionChangeSums = teamStats_super.groupby('matchId').sum(numeric_only = True)[['possessionChanges']]


# %% ----- End of 07_rd7_analysis.py ----- %% #

