# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the round 14 SSN match-ups.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from itertools import groupby
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

# %% Dead rubber effect

"""

Concept here is to calculate a ladder up to the final round and check for match
ups between teams no longer able to make finals vs. those who are no chance of
missing finals.

"""

#Read in team and team period stats over Super Netball years
teamStats = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'],
                                        joined = True, addSquadNames = True)
teamPeriodStats = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2017, 2018, 2019, 2020, 2021, 2022, 2023],
                                              fileStem = 'teamPeriodStats',
                                              matchOptions = ['regular'],
                                              joined = True, addSquadNames = True)

#Create dictionary for dead rubber data
deadRubberData = {'year': [],
                  'liveTeam': [], 'liveTeamLadderPos': [],
                  'deadTeam': [], 'deadTeamLadderPos': [],
                  'matchWinner': [], 'margin': []}

#Loop through years
for year in teamStats['year'].unique():

    #Identify number of rounds
    nRounds = teamStats.loc[teamStats['year'] == year,]['roundNo'].max()
    
    #Extract current years data without final round
    teamStatsCurrentYear = teamStats.loc[(teamStats['year'] == year) &
                                         (teamStats['roundNo'] < nRounds),].reset_index(drop = True)
    
    #Extract team period stats for current year without final round (if necessary)
    if year in [2018,2019]:
        teamPeriodStatsCurrentYear = teamPeriodStats.loc[(teamPeriodStats['year'] == year) &
                                                         (teamPeriodStats['roundNo'] < nRounds),].reset_index(drop = True)
    
    #Create dataframe to store ladder data
    ladderData = pd.DataFrame(list(zip([0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
                                       [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0])),
                              columns = ['points', 'W', 'D', 'L', 'GF', 'GA'],
                              index = list(teamStatsCurrentYear['squadName'].unique()))
    
    #Loop through match Id's to allocate ladder points and goals for/against
    for matchId in teamStatsCurrentYear['matchId'].unique():
        
        #Get current match data
        currMatch = teamStatsCurrentYear.loc[teamStatsCurrentYear['matchId'] == matchId,].reset_index(drop = True)
        
        #Get period stats for current match (if necessary)
        if year in [2018,2019]:
            currMatchPeriods = teamPeriodStatsCurrentYear.loc[teamPeriodStatsCurrentYear['matchId'] == matchId,].reset_index(drop = True)
        
        #Get the squad names
        matchSquads = [currMatch['squadName'].iloc[0], currMatch['squadName'].iloc[1]]
        
        #Get the scores for each team
        if year < 2020:
            matchScores = [int(currMatch['goals'].iloc[0]), int(currMatch['goals'].iloc[1])]
        else:
            matchScores = [int(currMatch['points'].iloc[0]), int(currMatch['points'].iloc[1])]
            
        #Determine winner
        if matchScores[0] > matchScores[1]:
            matchWinner = matchSquads[0]
            matchLoser = matchSquads[1]
        elif matchScores[0] < matchScores[1]:
            matchWinner = matchSquads[1]
            matchLoser = matchSquads[0]
        else:
            matchWinner = 'draw'
        
        #Allocate 4 match points to winner
        if matchWinner != 'draw':
            ladderData.at[matchWinner, 'points'] = ladderData.at[matchWinner, 'points'] + 4
            ladderData.at[matchWinner, 'W'] = ladderData.at[matchWinner, 'W'] + 1
            ladderData.at[matchLoser, 'L'] = ladderData.at[matchLoser, 'L'] + 1
        else:
            #Allocate 2 points each for draw
            ladderData.at[matchSquads[0], 'points'] = ladderData.at[matchSquads[0], 'points'] + 2
            ladderData.at[matchSquads[1], 'points'] = ladderData.at[matchSquads[1], 'points'] + 2
            ladderData.at[matchSquads[0], 'D'] = ladderData.at[matchSquads[0], 'D'] + 1
            ladderData.at[matchSquads[1], 'D'] = ladderData.at[matchSquads[1], 'D'] + 1
            
        #Add goals for and against
        ladderData.at[matchSquads[0], 'GF'] = ladderData.at[matchSquads[0], 'GF'] + matchScores[0]
        ladderData.at[matchSquads[0], 'GA'] = ladderData.at[matchSquads[0], 'GA'] + matchScores[1]
        ladderData.at[matchSquads[1], 'GF'] = ladderData.at[matchSquads[1], 'GF'] + matchScores[1]
        ladderData.at[matchSquads[1], 'GA'] = ladderData.at[matchSquads[1], 'GA'] + matchScores[0]
        
        #Add bonus points for relevant years
        if year in [2018,2019]:
            
            #Loop through periods
            for periodNo in currMatchPeriods['period'].unique():
                
                #Get current period data
                currPeriodData = currMatchPeriods.loc[currMatchPeriods['period'] == periodNo, ].reset_index(drop = True)
                
                #Get the squads from this data frame
                periodSquads = [currPeriodData['squadName'].iloc[0], currPeriodData['squadName'].iloc[1]]
                
                #Get scores for current period
                periodScores = [int(currPeriodData['goals'].iloc[0]), int(currPeriodData['goals'].iloc[1])]
                
                #Determine winner of the period
                if periodScores[0] > periodScores[1]:
                    periodWinner = periodSquads[0]
                elif periodScores[0] < periodScores[1]:
                    periodWinner = periodSquads[1]
                else:
                    periodWinner = 'draw'
                    
                #Allocate bonus point to winner
                if periodWinner != 'draw':
                    ladderData.at[periodWinner, 'points'] = ladderData.at[periodWinner, 'points'] + 1
                    
    #Calculate percentage for ladder
    ladderData['per'] = ladderData['GF'] / ladderData['GA'] * 100
    
    #Sort ladder by points then percentgae
    ladderData.sort_values(by = ['points', 'per'], ascending = False, inplace = True)
    
    #Extract the match-ups for the final round and create a dataframe of these
    finalRoundMatches = teamStats.loc[(teamStats['year'] == year) &
                                      (teamStats['roundNo'] == nRounds),].reset_index(drop = True)
    
    #Set the total distance in points that can be achieved in one match
    if year in [2018, 2019]:
        distanceLength = 8
    else:
        distanceLength = 4
    
    #Loop through unique match Id's
    for matchId in finalRoundMatches['matchId'].unique():
        
        #Extract squads from current match
        matchSquads = list(finalRoundMatches.loc[finalRoundMatches['matchId'] == matchId,
                                                 ]['squadName'].unique())
        
        #Check how far off from 4th spot points the two squads are
        offFinals = [ladderData.at[matchSquads[0], 'points'] - int(ladderData.iloc[3]['points']),
                     ladderData.at[matchSquads[1], 'points'] - int(ladderData.iloc[3]['points'])]
        
        #Check how far off from 5th spot points the two squads are
        offElimination = [ladderData.at[matchSquads[0], 'points'] - int(ladderData.iloc[4]['points']),
                          ladderData.at[matchSquads[1], 'points'] - int(ladderData.iloc[4]['points'])]
        
        #Check for greater than 4 points off the pace
        outOfFinals = [offFinals[ii] < -(distanceLength) for ii in range(len(offFinals))]
        
        #Check for greater than 4 points ahead of the pace
        inFinals = [offElimination[ii] > distanceLength for ii in range(len(offFinals))]
        
        #If the sum of each of the above variables is 1, then there is one team that
        #is out of finals and another that is definitely in finals, therefore meeting
        #our dead rubber criteria
        if sum(outOfFinals) == 1 and sum(inFinals) == 1:
            deadRubber = True
        else:
            deadRubber = False
            
        #Record results if dead rubber
        if deadRubber:
            
            #Get current match data
            currMatch = finalRoundMatches.loc[finalRoundMatches['matchId'] == matchId,].reset_index(drop = True)
            
            #Recordthe match result
            if year < 2020:
                matchScores = [finalRoundMatches.loc[(finalRoundMatches['matchId'] == matchId) &
                                                     (finalRoundMatches['squadName'] == matchSquads[0]),
                                                     ]['goals'].values[0],
                               finalRoundMatches.loc[(finalRoundMatches['matchId'] == matchId) &
                                                                    (finalRoundMatches['squadName'] == matchSquads[1]),
                                                                    ]['goals'].values[0]]
            else:
                matchScores = [finalRoundMatches.loc[(finalRoundMatches['matchId'] == matchId) &
                                                     (finalRoundMatches['squadName'] == matchSquads[0]),
                                                     ]['points'].values[0],
                               finalRoundMatches.loc[(finalRoundMatches['matchId'] == matchId) &
                                                                    (finalRoundMatches['squadName'] == matchSquads[1]),
                                                                    ]['points'].values[0]]
                
            #Identify the winner
            if matchScores[0] > matchScores[1]:
                matchWinner = matchSquads[0]
            elif matchScores[0] < matchScores[1]:
                matchWinner = matchSquads[1]
            else:
                matchWinner = 'draw'
                
            #Identify the live and dead teams + their ladder position
            liveTeam = np.array(matchSquads)[np.array(inFinals)][0]
            deadTeam = np.array(matchSquads)[np.array(outOfFinals)][0]
            liveTeamLadderPos = np.where(ladderData.index == liveTeam)[0][0] + 1
            deadTeamLadderPos = np.where(ladderData.index == deadTeam)[0][0] + 1
                    
            #Append data to dictionary
            deadRubberData['year'].append(year)
            deadRubberData['liveTeam'].append(liveTeam)
            deadRubberData['liveTeamLadderPos'].append(liveTeamLadderPos)
            deadRubberData['deadTeam'].append(deadTeam)
            deadRubberData['deadTeamLadderPos'].append(deadTeamLadderPos)
            deadRubberData['matchWinner'].append(matchWinner)
            deadRubberData['margin'].append(np.abs(np.diff(matchScores)[0]))
        
#Convert to dataframe
deadRubberData_df = pd.DataFrame.from_dict(deadRubberData)  

#Create logical for whether match winner was dead team
deadRubberData_df['deadTimeWinning'] = deadRubberData_df['deadTeam'] == deadRubberData_df['matchWinner']
    
# %% Latanya Wilsons game

#Read in player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular','final'],
                                          joined = True, addSquadNames = True)

#Wilson's game comparable to others
wilsonId = 1019205
wilsonPlayerStats = playerStats.loc[playerStats['playerId'] == wilsonId,]

#Review key stats
wilsonKeyStats = wilsonPlayerStats[['year', 'roundNo', 'oppSquadName',
                                    'netPoints', 'gain', 'deflections', 'intercepts', 'penalties']]
wilsonKeyStats['PG'] = wilsonKeyStats['gain'] / wilsonKeyStats['penalties']
        
# %% How often do we see players in 3 positions?

#Create dictionary to store data
threePosPlayers = {'year': [], 'matchId': [], 'playerId': [], 'posPlayed': []}

#Loop through unique player Id's
for playerId in playerData['playerId'].unique():
    
    #Extract line-ups where player is present
    playerLineUps = lineUpData.loc[(lineUpData['GS'] == playerId) |
                                   (lineUpData['GA'] == playerId) |
                                   (lineUpData['WA'] == playerId) |
                                   (lineUpData['C'] == playerId) |
                                   (lineUpData['WD'] == playerId) |
                                   (lineUpData['GD'] == playerId) |
                                   (lineUpData['GK'] == playerId),].reset_index(drop = True)
    
    #Loop through match Id's
    for matchId in playerLineUps['matchId'].unique():
        
        #Extract duration in court positions for current match and player
        courtPosDur = [playerLineUps.loc[(playerLineUps['matchId'] == matchId) & 
                                         (playerLineUps[courtPos] == playerId)]['duration'].sum() for courtPos in courtPositions]
        
        #Check for three position player in match
        if sum([courtPosDur[ii] > 0 for ii in range(len(courtPosDur))]) >= 3:
            
            #Record data
            threePosPlayers['year'].append(playerLineUps.loc[(playerLineUps['matchId'] == matchId)]['year'].unique()[0])
            threePosPlayers['matchId'].append(matchId)
            threePosPlayers['playerId'].append(playerId)
            threePosPlayers['posPlayed'].append(list(np.array(courtPositions)[np.array([courtPosDur[ii] > 0 for ii in range(len(courtPosDur))])]))
            
#Convert to dataframe
threePosPlayers_df = pd.DataFrame.from_dict(threePosPlayers)

#Add a player name for clarity
playerName = []
for ii in threePosPlayers_df.index:
    playerName.append(playerData.loc[(playerData['playerId'] == threePosPlayers_df.iloc[ii]['playerId']) &
                                     (playerData['year'] == threePosPlayers_df.iloc[ii]['year']),
                                     ]['displayName'].values[0])
threePosPlayers_df['playerName'] = playerName

#Get a count of player Id
threePosCount = threePosPlayers_df.groupby('playerId').count()
    
# %% NetPoints drop off

#Read in player stats from NetPoints era
playerStats_netPointsEra = collatestats.getSeasonStats(baseDir = baseDir,
                                                       years = [2018, 2019, 2020, 2021, 2022, 2023],
                                                       fileStem = 'playerStats',
                                                       matchOptions = ['regular'],
                                                       joined = True, addSquadNames = True)

#Create dictionary to store values
netPointDropOff = {'year': [], 'playerId': [], 'roundNo': [],
                   'priorNetPoints': [], 'currentNetPoints': [], 'netPointDiff': []}

#Loop through years
for year in [2018, 2019, 2020, 2021, 2022, 2023]:
    
    #Get current year data
    currYearData = playerStats_netPointsEra.loc[playerStats_netPointsEra['year'] == year,].reset_index(drop = True)
    
    #Loop through unique player Id's
    for playerId in currYearData['playerId'].unique():
        
        #Grab current player data
        currPlayerData = currYearData.loc[currYearData['playerId'] == playerId,]
        
        #Drop any games they didn't play
        currPlayerData = currPlayerData.loc[currPlayerData['minutesPlayed'] > 0,]
        
        #Sort values by round
        currPlayerData.sort_values(by = 'roundNo', ascending = True, inplace = True)
        
        #Calculate the difference in NetPoints
        netPointDiff = np.diff(np.array(currPlayerData['netPoints']))
        
        #Extract associated netPoints for those weeks
        netPoints = np.array(currPlayerData['netPoints'])
        
        #Extract associated rounds
        netPointsRounds = np.array(currPlayerData['roundNo'])[1:]
        
        #Append data
        for ii in range(len(netPointDiff)):
            netPointDropOff['year'].append(year)
            netPointDropOff['playerId'].append(playerId)
            netPointDropOff['roundNo'].append(netPointsRounds[ii])
            netPointDropOff['priorNetPoints'].append(netPoints[ii])
            netPointDropOff['currentNetPoints'].append(netPoints[ii+1])
            netPointDropOff['netPointDiff'].append(netPointDiff[ii])
    
#Convert to dataframe
netPointDropOff_df = pd.DataFrame.from_dict(netPointDropOff)

#Add player name for clarity
playerName = []
for ii in netPointDropOff_df.index:
    playerName.append(playerData.loc[(playerData['playerId'] == netPointDropOff_df.iloc[ii]['playerId']) &
                                     (playerData['year'] == netPointDropOff_df.iloc[ii]['year']),
                                     ]['displayName'].values[0])
netPointDropOff_df['playerName'] = playerName

# %% Prediction

#Average margin of week 1 finals

#Read in team stats from finals across Super Netball years
teamStatsFinals_superNetball = collatestats.getSeasonStats(baseDir = baseDir,
                                                           years = [2017, 2018, 2019, 2020, 2021, 2022],
                                                           fileStem = 'teamStats',
                                                           matchOptions = ['final'],
                                                           joined = True, addSquadNames = True)

#Collate average margin from round 1 of each year
teamStatsFinals_rd1 = teamStatsFinals_superNetball.loc[teamStatsFinals_superNetball['roundNo'] == 1,]

#Set dictionary to store margins
marginData = {'matchId': [], 'year': [], 'margin': []} 

#Loop through match Id's
for matchId in teamStatsFinals_rd1['matchId'].unique():
    
    #Get current match
    currMatch = teamStatsFinals_rd1.loc[teamStatsFinals_rd1['matchId'] == matchId,
                                        ].reset_index(drop = True)
    
    #Calculate margin for the match
    if currMatch.iloc[0]['year'] < 2020:
        margin = np.abs(currMatch.iloc[1]['goals'] - currMatch.iloc[0]['goals'])
    else:
        margin = np.abs(currMatch.iloc[1]['points'] - currMatch.iloc[0]['points'])
        
    #Store data
    marginData['matchId'].append(matchId)
    marginData['year'].append(currMatch.iloc[0]['year'])
    marginData['margin'].append(margin)
    
#Group by year and average
marginData_df = pd.DataFrame.from_dict(marginData)
avgMargin_rd1 = marginData_df.groupby('year').mean()['margin']
    
    


# %% ----- End of 14_rd14_analysis.py ----- %% #