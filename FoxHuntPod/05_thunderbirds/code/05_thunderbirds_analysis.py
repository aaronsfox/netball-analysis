# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 6 Thunderbirds match-up for
    podcast.
    
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
os.chdir('..\\..\..\\code\\matchCentre')
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

#Set relevant squad Id's
vixensSquadId = 804
thunderbirdsSquadId = 801
magpiesSquadId = 8119

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% Key numbers that jumped out - Thunderbirds match

#Reviewed team stats spreadsheets
#A little bit of missed opportunities for Vixens
    # Outgained Thunderbirds 14-8, but had 2 more total turnovers in the match (24 - 22 TOs)
    # Sort of indicative of the Vixens throwing the ball away a little with 16 of there 24 TOs being unforced
#On the flipside, Vixens more opportunistic in defensive areas
    # Both teams had 11 missed shots but the Vixens reeled in 7 of these for rebounds, Adelaide only 1
#Adelaide perhaps a little unopportunistic with Vixens turnovers
    # TO to goal % 71 Vixens - 44 Adelaide
    
#Pull in season team stats to check some things
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['regular'])
teamStats_2022 = teamStats_2022[2022]

#Get Vixens 2022 stats
vixensTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == vixensSquadId,]

#Check unforced to general turnover ratio for Vixens
vixensTeamStats_2022['unforcedTurnovers'] / vixensTeamStats_2022['generalPlayTurnovers']

# %% How was Austin's game?

#Set Austin id
austinId = 1001708

#Manually check Austin's stats
# 16 CPRs and 5 2nd phase - involvement at 21 of 44 Vixen's centre passes
# 15 total goals
# 4 gains - 2nd only to Weston's 7 for the Vixen's

#Is this the most gains Austin has ever produced in a match?

#Get player stats
playerStats = collatestats.getSeasonStats(baseDir = baseDir,
                                          years = 'all',
                                          fileStem = 'playerStats',
                                          matchOptions = ['regular', 'finals'])

#Loop through years
for year in list(playerStats.keys()):
    
    #Check if Austin in dataframe
    if austinId in list(playerStats[year]['playerId'].unique()):
        
        #Extract Austin's data
        austinMaxGain = playerStats[year].groupby('playerId').max()['gain'][austinId]
        
        #Print out result
        print(f'Austin max gains in {year}: {austinMaxGain}')
        
    else:
        
        #Print out result
        print(f'No data for Austin in {year}')
            
# %% Hannah Mundy vs. Moloney's season so far

#Set Moloney id
moloneyId = 991901

#Collate Moloney's season averages for player stats
playerStats_2022 = playerStats[2022]

#Calculate player averages
playerStatAverages_2022 = playerStats_2022.groupby('playerId').mean().reset_index(drop = False)

#Extract Moloney's data
moloneyStatAverages_2022 = playerStatAverages_2022.loc[playerStatAverages_2022['playerId'] == moloneyId,]

#Compare to Mundy's first half numbers (i.e. half Moloney's averages)
# Moloney feeds for half = 11; Mundy 1st half feeds = 14
# Moloney feeds with attempt for half = 7.5; Mundy 1st half feeds with attempt = 8
# Moloney second phase receives for half = 4.5; Mundy 1st half 2nd phase receives = 6
# Moloney general play turnovers for a half ~ 1.3; Mundy 1st half general TOs = 4
# Moloney averages around 1 deflection per half; Mundy didn't record any deflections across the match

# %% Thunderbirds gains

#Extract Thunderbirds team stats for the year
thunderbirdsTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == thunderbirdsSquadId,]

#Lowest gains by a long way this year
# Only 8, next lowest was 16 in round 4 and they have recorded 19 or more in their remaining 4 games this year

#What about turnovers though?
#Extract match Id's from Thunderbirds games
tbirdMatchIds = list(thunderbirdsTeamStats_2022['matchId'])

#Extract opposition stats
tbirdOppTeamStats_2022 = teamStats_2022.loc[(teamStats_2022['matchId'].isin(tbirdMatchIds)) &
                                            (teamStats_2022['squadId'] != thunderbirdsSquadId), ]

#Perhaps had surprisingly little effect on the turnovers generated
#Was still close to the highest opposition number of turnovers with 24 - with 25 the max this season

#What about the effect on player motivation?
#Use Sterling as an example
sterlingId = 80830

#Extract Sterling stats for the year
sterlingStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == sterlingId,]

#Leading the league in blocks and gains?
playerStatTotals = playerStats_2022.groupby('playerId').sum()

#Get player list to check players
playerList_2022 = collatestats.getSeasonStats(baseDir = baseDir,
                                              years = [2022],
                                              fileStem = 'playerList',
                                              matchOptions = ['regular'])

# %% Watson's game vs. others this year

#Set Watson Id
watsonId = 994224

#Extract Watson's stats
watsonPlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == watsonId,]

# %% Review team stats from the Magpies

#Extract magpies team stats
magpiesTeamStats_2022 = teamStats_2022.loc[teamStats_2022['squadId'] == magpiesSquadId,]

#Magpies have won in round 4 & 6 - anything stand out from this?

# %% Fan questions

#Margin shifts in Power 5 periods

#Read in scoreflow data from 2020 onwards
scoreFlowData = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = [2020, 2021, 2022],
                                            fileStem = 'scoreFlow',
                                            matchOptions = ['regular', 'finals'])

#Set up dictionary to store data
superMarginDict = {
    'matchId': [],
    'year': [],
    'roundNo': [],
    'matchType': [],
    'homeSquadId': [],
    'awaySquadId': [],
    'period': [],
    'startingMargin': [],
    'endMargin': [],
    'marginDiff': [],
    'absMarginDiff': []
    }

#Loop through years
for year in list(scoreFlowData.keys()):
    
    #Get match Id's from current year
    matchIds = list(scoreFlowData[year]['matchId'].unique())
    
    #Loop through match Id's
    for matchId in matchIds:
        
        #Loop through periods for matches
        for period in [1,2,3,4]:
            
            #Extract current matches period
            currPeriod = scoreFlowData[year].loc[(scoreFlowData[year]['matchId'] == matchId) &
                                                 (scoreFlowData[year]['period'] == period),
                                                 ].reset_index(drop = True)
            
            #Identify two squads
            squadIds = list(currPeriod['squadId'].unique())
            
            #Identify which is home squad and which is away
            homeSquadId = currPeriod['squadId'][currPeriod['homeSquadScore'].diff() > 0].unique()[0]
            awaySquadId = currPeriod['squadId'][currPeriod['awaySquadScore'].diff() > 0].unique()[0]
            
            #Identify the margin when the Power 5 period starts
            power5_indStart = (currPeriod['periodSeconds'] > 600).argmax() - 1
            startMargin = currPeriod['scoreDifferential'][power5_indStart]
            
            #Identify end margin as final differential
            endMargin = currPeriod['scoreDifferential'][len(currPeriod)-1]
            
            #Append data
            superMarginDict['matchId'].append(matchId)
            superMarginDict['year'].append(year)
            superMarginDict['roundNo'].append(currPeriod['roundNo'].unique()[0])
            superMarginDict['matchType'].append(currPeriod['matchType'].unique()[0])
            superMarginDict['homeSquadId'].append(homeSquadId)
            superMarginDict['awaySquadId'].append(awaySquadId)
            superMarginDict['period'].append(period)
            superMarginDict['startingMargin'].append(startMargin)
            superMarginDict['endMargin'].append(endMargin)
            superMarginDict['marginDiff'].append(np.diff((startMargin,endMargin))[0])
            superMarginDict['absMarginDiff'].append(np.abs(np.diff((startMargin,endMargin))[0]))
            
#Convert to datafram
superMarginData = pd.DataFrame.from_dict(superMarginDict)

#Replace the squad Id's with names
superMarginData.replace(squadDict, inplace = True)

#Cleanest defender - gains vs. penalties

#Take out gains and penalties from player stats dataframe from 2010 onwards
gainsPen = {}
for year in list(np.linspace(2010,2022,13,dtype = int)):
    gainsPen[year] = playerStats[year][['playerId','gain','penalties']]
    
#Concatenate the dataframes together
gainsPenAll = pd.concat((gainsPen[2010],gainsPen[2011],gainsPen[2012],gainsPen[2013],
                         gainsPen[2014],gainsPen[2015],gainsPen[2016],gainsPen[2017],
                         gainsPen[2018],gainsPen[2019],gainsPen[2020],gainsPen[2021],
                         gainsPen[2022]))
gainsPenAll.reset_index(drop = True, inplace = True)

#Get stat totals by player id
gainsPenSum = gainsPenAll.groupby('playerId').sum().reset_index(drop = False)

#Drop anyone with < 100 gains (arbitrary)
gainsPenInclude = gainsPenSum.loc[gainsPenSum['gain'] >= 100,]

#Create a penalties to gains ratio
gainsPenInclude['ratio'] = gainsPenInclude['penalties'] / gainsPenInclude['gain']

#Get player list to map names against
playerList = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = 'all',
                                         fileStem = 'playerList',
                                         matchOptions = ['regular', 'finals'])

#Extract display names for unique player Id's
playerId = []
displayName = []

#Loop through years
for year in list(playerList.keys()):
    
    #Get unique player Id's
    playerIds = playerList[year]['playerId'].unique()
    
    #Loop through Ids
    for pId in playerIds:
        
        #Check if in list already
        if pId not in playerId:
            
            #Extract and append
            playerId.append(pId)
            displayName.append(playerList[year].loc[playerList[year]['playerId'] == pId,
                                                    ['displayName']]['displayName'].unique()[0])
    
#Convert to player Id to name dictionary
playerIdDict = dict(zip(playerId, displayName))

#Replace player Id's with names
gainsPenInclude.replace(playerIdDict, inplace = True)

#Sort values and reset index
gainsPenInclude.sort_values(by = 'ratio', inplace = True)
gainsPenInclude.reset_index(drop = True, inplace = True)

#Export this to file
gainsPenInclude.to_csv('..\\outputs\\PG-rating.csv', index = False)

# %% Predictions

#Review gains to turnovers for last week

#Extract match Id's from Thunderbirds games
vixensMatchIds = list(vixensTeamStats_2022['matchId'])

#Extract opposition stats
vixensOppTeamStats_2022 = teamStats_2022.loc[(teamStats_2022['matchId'].isin(vixensMatchIds)) &
                                             (teamStats_2022['squadId'] != vixensSquadId), ]

#Check kumwenda stats for this year
kumwendaId = 80540
kumwendaPlayerStats_2022 = playerStats_2022.loc[playerStats_2022['playerId'] == kumwendaId,]

# %%% ----- End of 05_thunderbirds_analysis.py -----