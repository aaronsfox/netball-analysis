# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 3 Giants match-up and Round 4
    Fever preview for podcast
    
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
squadDict ={804: 'Vixens',
            806: 'Swifts',
            807: 'Firebirds',
            8117: 'Lightning',
            810: 'Fever',
            8119: 'Magpies',
            801: 'Thunderbirds',
            8118: 'GIANTS'}

#Set relevatn squad Id'ss
vixensSquadId = 804
giantsSquadId = 8118
feverSquadId = 810
lightningSquadId = 8117

#Identify round data directory for any specific loading
procDatDir = '..\\..\\..\\..\\data\\matchCentre\\processed\\116650301_2022_SSN_11665_r3_g1\\'

#Set base directory for processed data
baseDir = '..\\..\\..\\..\\data\\matchCentre\\processed'

# %% Key numbers that jumped out

#Reviewed team stats spreadsheets
#Gains 20 - 9 in Vixens favour
#Goals from gains 16 - 5 in Vixens favour

#Was this the first time Vixens have only used one line-up?

#Load in line-up data
lineUps_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                           years = [2022],
                                           fileStem = 'lineUps')

#Extract just Vixens and regular season games
vixensLineUps_2022 = lineUps_2022[2022].loc[(lineUps_2022[2022]['squadId'] == vixensSquadId) &
                                            (lineUps_2022[2022]['matchType'] == 'regular'),
                                            ].reset_index(drop = True)

# %% How was Austin's game?

#Set Austin id
austinId = 1001708

#Manually check score contribution
#Austin 24 goals total; Kumwenda 38 goals total
austinContribution = 24 / (24+38) * 100

#How does this realte to Austin's scoring contribution with the GIANTS

#Extract player stats from 2020 (Austin last full season)
playerStats_2020 = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = [2020],
                                                 fileStem = 'playerStats')

#Extract to dataframe
playerStats_2020 = playerStats_2020[2020]

#Extract matchs Austin played in
austinMatchId = list(playerStats_2020.loc[playerStats_2020['playerId'] == austinId,
                                          ]['matchId'].unique())
austinMatches_2020 = playerStats_2020.loc[playerStats_2020['matchId'].isin(austinMatchId),]

#Extract Austin's goals in every match
austinGoals = austinMatches_2020.loc[austinMatches_2020['playerId'] == austinId,
                                     ['matchId','goal1','goal2']]
austinGoals['goal2'] = austinGoals['goal2']*2
austinGoalsSum = austinGoals.groupby('matchId').sum()
austinGoalsSum['goals'] = austinGoalsSum['goal1'] + austinGoalsSum['goal2']

#Extract team goals
teamGoals = austinMatches_2020.loc[austinMatches_2020['squadId'] == giantsSquadId,
                                   ['matchId', 'goal1','goal2']]
teamGoals['goal2'] = teamGoals['goal2']*2
teamGoalsSum = teamGoals.groupby('matchId').sum()
teamGoalsSum['goals'] = teamGoalsSum['goal1'] + teamGoalsSum['goal2']

#calculate contribution to each match
austinAvgPer = np.mean(austinGoalsSum['goals'] / teamGoalsSum['goals'] * 100)
austinSdPer = np.std(austinGoalsSum['goals'] / teamGoalsSum['goals'] * 100)

# %% Review defensive ends effort

#Set relevant player Ids
mannixId = 994213
westonId = 80577
eddyId = 1001701

#Gains - Weston = 7, Mannix = 6, Eddy = 4
#Deflections w/ no gain - Mannix = 5, Weston 3, Eddy 2

#Review how many times this has happened  across a single game

#Get all player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats')

#Create stat counters
occurCounter = 0
notOccurCounter = 0

#Loop through years of data
for year in list(playerStats.keys()):
    
    #Check if deflectionWithNoGain stat present
    if 'deflectionWithNoGain' in list(playerStats[year].columns):
    
        #Get match Id's for year
        #If 2022 limit to regular season matches
        if year == 2022:
            matchIds = list(playerStats[year].loc[playerStats[year]['matchType'] == 'regular',
                                                  ]['matchId'].unique())            
        else:
            matchIds = list(playerStats[year]['matchId'].unique())
        
        #Loop through match Id'ss
        for matchId in matchIds:
            
            #Extract match data
            matchData = playerStats[year].loc[playerStats[year]['matchId'] == matchId,]
            
            #Get squad Ids
            squadIds = list(matchData['squadId'].unique())
            
            #Loop through squad Ids
            for squadId in squadIds:
                
                #Extract squad data
                squadData = matchData.loc[matchData['squadId'] == squadId,]
                
                #Sort by gains and get third value
                thirdMostGains = squadData.sort_values(by = 'gain',
                                                       ascending = False)['gain'].reset_index(
                                                           drop = True)[2]
                                                           
                #Sort by deflections with no gain and get third most value
                thirdMostDeflections = squadData.sort_values(by = 'deflectionWithNoGain',
                                                             ascending = False)['deflectionWithNoGain'].reset_index(
                                                                 drop = True)[2]
                                                                 
                #Check for criteria
                if thirdMostGains >= 4 and thirdMostDeflections >=2:
                    #Add to counter
                    occurCounter += 1
                else:
                    #Add to counter
                    notOccurCounter += 1
                    
    else:
        #Print that they didn't collect this
        print(f'Deflections with no gain not counted in {year}')
                
#Calculate proportion of times it's happened (outside of the 1 we recorded)
perHappened = (occurCounter-1) / (occurCounter + notOccurCounter) * 100
            
    


#Review GIANTS pace vs. earlier games

#Collate team stats from year
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats')

#Extract GIANTS regular season games
giantsTeamStats_2022 = teamStats_2022[2022].loc[(teamStats_2022[2022]['squadId'] == giantsSquadId) &
                                                (teamStats_2022[2022]['matchType'] == 'regular'),
                                                ].reset_index(drop = True)

# %% What about Watson's game

#Set Watson Id
watsonId = 994224

#Extract player stats from 2022
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                               years = [2022],
                                               fileStem = 'playerStats')

#Extract to dataframe and get regular season games
playerStats_2022 = playerStats_2022[2022].loc[playerStats_2022[2022]['matchType'] == 'regular',]

#Leverage earlier 2022 player stats but just to round 2
playerStats_round3 = playerStats_2022.loc[playerStats_2022['roundNo'] == 3,]

#Get player lists for comparing
playerList_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerList')
playerList_2022 = playerList_2022[2022]

# %% What's happening with the Fever

#Grab out team stats and get Fever's scores
feverGoals = teamStats_2022[2022].loc[(teamStats_2022[2022]['squadId'] == feverSquadId) &
                                      (teamStats_2022[2022]['matchType'] == 'regular'),
                                      ]['points']
avgFeverGoals = np.mean(feverGoals)

#Compare to average team points in 2020 and 2021
teamStats_2020and2021 = collatestats.getSeasonStats(baseDir = baseDir,
                                                    years = [2020, 2021],
                                                    fileStem = 'teamStats')

#Get average team scores from 2020 and 2021
#2020
teamStats_2020and2021[2020].groupby(['squadId'])['points'].mean().reset_index(
    drop = False).replace(squadDict).sort_values(by = 'points', ascending = False)
#2021
teamStats_2020and2021[2021].groupby(['squadId'])['points'].mean().reset_index(
    drop = False).replace(squadDict).sort_values(by = 'points', ascending = False)

#Extract Fever's and opponents scores from each of these years

#Loop through years
for year in list(teamStats_2020and2021.keys()):
    
    #Set lists to store
    feverScore = []
    oppScore = []
    
    #Extract fever match Id's
    matchIds = list(teamStats_2020and2021[year].loc[teamStats_2020and2021[year]['squadId'] == feverSquadId,
                                                    ]['matchId'].unique())
    
    #Extract scores from these games
    for matchId in matchIds:
        feverScore.append(teamStats_2020and2021[year].loc[(teamStats_2020and2021[year]['matchId'] == matchId) &
                                                          (teamStats_2020and2021[year]['squadId'] == feverSquadId),
                                                          ]['points'].values[0])
        oppScore.append(teamStats_2020and2021[year].loc[(teamStats_2020and2021[year]['matchId'] == matchId) &
                                                        (teamStats_2020and2021[year]['squadId'] != feverSquadId),
                                                        ]['points'].values[0])
        
    #Set to dataframe
    scoreComp = pd.DataFrame(zip(feverScore, oppScore),
                             columns = ['Fever', 'Opp'])
    
    #Calculate margin
    scoreComp['margin'] = scoreComp['Fever'] - scoreComp['Opp']
    
    #Sort by Fever score
    scoreComp.sort_values(by = 'Fever')
        
# %% Questions

#Vixens shooters

#Get player stats from each year
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats')

#Get player list to match up data to
playerList = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = 'all',
                                         fileStem = 'playerList')

#Loop through years and collate Vixens shooting ranks
for year in list(playerStats.keys()):
    
    #Get player stats dataframe out
    if year == 2022:
        data = playerStats[year].loc[playerStats[year]['matchType'] == 'regular',]
    else:
        data = playerStats[year]
    
    #Get player list out
    players = playerList[year]
    
    #Get total count of players goals
    if year < 2020:
        totalPlayerGoals = data.groupby('playerId')['goals'].sum().sort_values(ascending = False).reset_index(drop = False)
    else:
        totalPlayerGoals = data.groupby('playerId')['points'].sum().sort_values(ascending = False).reset_index(drop = False)
        
    #Loop through player Id's and add names/squads
    playerName = []
    playerSquad = []
    for playerId in totalPlayerGoals['playerId']:
        #Get player name
        playerName.append(players.loc[players['playerId'] == playerId,]['displayName'].unique()[0])
        #Get squad Id
        playerSquad.append(players.loc[players['playerId'] == playerId,]['squadId'].unique()[0])
    #Append to dataframe
    totalPlayerGoals['playerName'] = playerName
    totalPlayerGoals['squadName'] = playerSquad
    totalPlayerGoals['squadName'].replace(squadDict, inplace = True)
    
    #Identify Vixens ranks for top 3 shooters
    vixensShooters = totalPlayerGoals.loc[totalPlayerGoals['squadName'] == 'Vixens',]
    vixensRanks = list(vixensShooters.iloc[0:3].index)
    vixensPlayers = list(vixensShooters.iloc[0:3]['playerName'])
    
    #Print output
    print(f'\nIn year {year} Vixens shooters ranked:')
    for ii in range(len(vixensRanks)):
        print('#'+str(vixensRanks[ii]+1)+' '+vixensPlayers[ii])


# %% Predictions...

#Fever scoring rate of 70+ is ending

#Sunshine Coast Match-up

#Grab Lightning team stats
lightningTeamStats = teamStats_2022[2022].loc[(teamStats_2022[2022]['matchType'] == 'regular') &
                         (teamStats_2022[2022]['squadId'] == lightningSquadId),
                         ]

#Grab Lightnings player stats
lightningPlayerStats = playerStats_2022.loc[playerStats_2022['squadId'] == lightningSquadId,]


# %%% ----- End of 03_giants_analysis.py -----