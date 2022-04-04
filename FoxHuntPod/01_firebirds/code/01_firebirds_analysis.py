# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Round 1 Firebirds match-up for podcast
    
"""

# %% Import packages

import pandas as pd
import os

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set Firebirds and Vixens squad Id'ss
vixensSquadId = 804
firebirdsSquadId = 807

#Identify round data directory for any specific loading
procDatDir = '..\\..\\..\\data\\matchCentre\\processed\\116650103_2022_SSN_11665_r1_g3\\'

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% Introductory comparison stats

#How many times over 2020 and 2021 did the Vixens score 70 goals in a match?

#Load in the team stats from 2020 and 2021
teamStats_SuperShotEra = collatestats.getSeasonStats(baseDir = baseDir, years = [2020, 2021], fileStem = 'teamStats')

#Extract Vixens matches and determine number of times they scored 70 or over
#Do this across both years
for year in list(teamStats_SuperShotEra.keys()):
    #Extract number of times score was equal to or over 70
    nOver70 = len(teamStats_SuperShotEra[year].loc[(teamStats_SuperShotEra[year]['squadId'] == vixensSquadId) &
                                                   (teamStats_SuperShotEra[year]['goals'] >= 70),
                                                   ['goals']])
    #Print out result
    print(f'Times equal to or over 70 in {year}: {nOver70}')
    
#How many times did the Vixens score 25 or more in a quarter?

#Load in the team period stats from 2020 and 2021
teamPeriodStats_SuperShotEra = collatestats.getSeasonStats(baseDir = baseDir, years = [2020, 2021], fileStem = 'teamPeriodStats')

#Extract Vixens matches and determine number of times they scored 70 or over
#Do this across both years
for year in list(teamPeriodStats_SuperShotEra.keys()):
    #Extract number of times score was equal to or over 70
    nOver25 = len(teamPeriodStats_SuperShotEra[year].loc[(teamPeriodStats_SuperShotEra[year]['squadId'] == vixensSquadId) &
                                                         (teamPeriodStats_SuperShotEra[year]['goals'] >= 25),
                                                         ['goals']])
    #Print out result
    print(f'Times equal to or over 25 in {year}: {nOver25}')
    

# %% General stats that stood out

#Load the team stats from the current year to review comparative to other matches
teamStats_2022 = collatestats.getSeasonStats(baseDir = baseDir, years = [2022], fileStem = 'teamStats')

#Just extract the SSN stats
teamStats_2022_SSN = teamStats_2022[2022].loc[teamStats_2022[2022]['compType'] == 'SSN',]

#Get just match of interest
teamStats_2022_SSN_Vixens = teamStats_2022_SSN.loc[teamStats_2022_SSN['squadId'].isin([vixensSquadId,
                                                                                       firebirdsSquadId]),
                                                   ]

#Opportunistic Vixens

#Goals from turnovers
#Vixens = 12, Firebirds = 7 --- difference in the match

#Missed shot conversion
#Vixens = 60%, Firebirds = 18%

#Slightly messy Firebirds

#Contact penalties
#Vixens = 51, Firebirds = 69

#Obstruction penalties
#Vixens = 19, Firebirds = 22

#Firebirds most penalised side by far in round 1

# %% What about Kumwenda's game?

#Load in player stats
playerStats_2022 = collatestats.getSeasonStats(baseDir = baseDir, years = [2022], fileStem = 'playerStats')

#Set Kumwenda Id
kumwendaId = 80540

#Get out Kumwenda's from SSN
kumwendaStats = playerStats_2022[2022].loc[(playerStats_2022[2022]['compType'] == 'SSN') &
                                           (playerStats_2022[2022]['playerId'] == kumwendaId),
                                           ]

# %% Comparing Mannix to Lewis

#Reviewed player stats sheet for comparison

#Lewis more contact penalties than Mannix
#Lewis = 7; Mannix = 3

#Lewis more gains than Mannix
#Lewis = 5; Mannix = 0

#Lewis collected more rebounds than Mannix
#Lewis = 3; Mannix = 0

# %% What about Liz Watson's game?

#Load in the player stats from 2017 to 2020
playerStats_2017to2020 = collatestats.getSeasonStats(baseDir = baseDir,
                                                     years = [2017, 2018, 2019, 2020],
													 fileStem = 'playerStats')

#Set Watson Id
watsonId = 994224

#Loop through years and calculate total CPRs, feeds and goal assists
for year in [2017, 2018, 2019, 2020]:
    
    #Extract the current years data
    #Group by player Id and sum data
    summedData = playerStats_2017to2020[year].loc[playerStats_2017to2020[year]['matchType'] == 'regular',
                                                  ].groupby(['playerId']).sum()
    
    #Centre pass receives
    
    #Sort by centre pass receives and find where Watson ranks
    sortedData = summedData.sort_values(by = 'centrePassReceives',
                                        ascending = False).reset_index(drop = False)
    
    #Find where Watson ranks
    watsonRank = sortedData.loc[sortedData['playerId'] == watsonId,].index[0] + 1
    
    #Print output
    print(f'Watson rank for CPR in {year}: {watsonRank}')
    
    #Feeds
    
    #Sort by centre pass receives and find where Watson ranks
    sortedData = summedData.sort_values(by = 'feeds',
                                        ascending = False).reset_index(drop = False)
    
    #Find where Watson ranks
    watsonRank = sortedData.loc[sortedData['playerId'] == watsonId,].index[0] + 1
    
    #Print output
    print(f'Watson rank for feeds in {year}: {watsonRank}')
    
    #Goal assists
    
    #Sort by centre pass receives and find where Watson ranks
    sortedData = summedData.sort_values(by = 'goalAssists',
                                        ascending = False).reset_index(drop = False)
    
    #Find where Watson ranks
    watsonRank = sortedData.loc[sortedData['playerId'] == watsonId,].index[0] + 1
    
    #Print output
    print(f'Watson rank for goal assists in {year}: {watsonRank}')

# %% What about Jo Weston's game?

#Reviewed player statistics sheet for summary

#Weston's gains of 2 and 3 in the 2nd and 3rd quarter were where the match started
#to separate --- consider them timely interventions

# %% What about the penalty count?

#Let's take a look at Firebirds penalties in recent years

#Load in the team stats from 2017 to 2020
teamStats_2017to2021 = collatestats.getSeasonStats(baseDir = baseDir,
												   years = [2017, 2018, 2019, 2020, 2021],
												   fileStem = 'teamStats')

#Loop through years and calculate penalties and check the Firebirds ranks
for year in [2017, 2018, 2019, 2020, 2021]:
    
    #Extract the current years data
    #Group by player Id and sum data
    summedData = teamStats_2017to2021[year].loc[teamStats_2017to2021[year]['matchType'] == 'regular',
                                                ].groupby(['squadId']).sum()
    
    #Contact penalties
    
    #Sort by centre pass receives and find where Watson ranks
    sortedData = summedData.sort_values(by = 'contactPenalties',
                                        ascending = False).reset_index(drop = False)
    
    #Find where Firebirds ranks
    firebirdsRank = sortedData.loc[sortedData['squadId'] == firebirdsSquadId,].index[0] + 1
    
    #Print output
    print(f'Firebirds rank for contact penalties in {year}: {firebirdsRank}')
    
    #Obstruction penalties
    
    #Sort by centre pass receives and find where Watson ranks
    sortedData = summedData.sort_values(by = 'obstructionPenalties',
                                        ascending = False).reset_index(drop = False)
    
    #Find where Firebirds ranks
    firebirdsRank = sortedData.loc[sortedData['squadId'] == firebirdsSquadId,].index[0] + 1
    
    #Print output
    print(f'Firebirds rank for obstruction penalties in {year}: {firebirdsRank}')










# %%

# %% How did the Vixens defense impact the Fever in the final?

#Extract the team stats for the fever across the tournament
tgc_teamStats_fever = tgc_teamStats.loc[tgc_teamStats['squadId'] == feverSquadId, ]

# %% What about Liz Watson's numbers dropping off vs. Ruby Barkmeyer's rising?

#Reviewed player stats data

# %% Barkmeyer didn't put up a shot in the last quarter - how often does that happen?

#### TODO: I don't think this is working...

#Identify SSN data folders
folderListSSN = glob(procDatDir+'*_SSN_*\\', recursive = True)

#Set-up lists to store data into
noShots_playerId = []
noShots_matchLabel = []
noShots_period = []

#Loop through SSN data folders and grab out relevant data
for folderSSN in folderListSSN:
    
    #Get match label
    matchLabel = folderSSN.split('\\')[-2]
    
    # #Load lineup data
    # lineUpData = pd.read_csv(f'{folderSSN}lineUps_{matchLabel}.csv')
    
    #Read in substitutions data
    substitutionsData = pd.read_csv(f'{folderSSN}substitutions_{matchLabel}.csv')
    
    #Just grab the GA data
    substitutionsData_GA = substitutionsData.loc[substitutionsData['startingPos'] == 'GA',]
    
    #Identify players who played GA in the match
    playedGA = substitutionsData_GA['playerId'].unique()
    
    #Load in player stats period data
    playerStatsPeriod = pd.read_csv(f'{folderSSN}playerPeriodStats_{matchLabel}.csv')
    
    #Load in match details
    with open(f'{folderSSN}matchInfo_{matchLabel}.json', 'r') as f:
        matchInfo = json.load(f)
    
    #Identify period start and end times
    periodEnd = np.cumsum(matchInfo['periodSeconds'])
    periodStart = periodEnd - periodEnd[0]
    
    #Loop through the GA's and determine if they played a quarter and didn't put up a shot
    for playerId in playedGA:
        
        #Get the time frames where the current player played GA
        gaTimes = substitutionsData_GA.loc[substitutionsData_GA['playerId'] == playerId,
                                           ['startingTime', 'finishTime']].reset_index(drop = True)
        
        #Loop through the periods and identify if the GA played the entire period
        for periodInd in range(len(periodStart)):
            #Check if GA line up covers entire quarter
            playedQtr = []
            for timeInd in range(len(gaTimes)):
                if int(gaTimes['startingTime'][timeInd]) <= int(periodStart[periodInd]) & int(gaTimes['finishTime'][timeInd]) >= int(periodStart[periodInd]):
                    playedQtr.append(True)
                else:
                    playedQtr.append(False)
            
            #Grab shot attempts if the player played across the quarter
            if True in playedQtr:
                
                #Get the shot attempts
                goalAttempts = playerStatsPeriod.loc[(playerStatsPeriod['playerId'] == playerId) &
                                                     (playerStatsPeriod['period'] == periodInd+1),
                                                     ['goalAttempts']].values[0][0]
                
                #Check if zero and append to list if relevant
                if goalAttempts == 0:
                    noShots_playerId.append(playerId)
                    noShots_matchLabel.append(matchLabel)
                    noShots_period.append(periodInd+1)
        
# %% Who was Fowler's best shooting partner?

#Reviewed line-up data

# %%% ----- End of 01_firebirds_analysis.py -----