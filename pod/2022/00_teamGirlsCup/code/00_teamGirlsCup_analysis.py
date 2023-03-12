# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to compile some data examining the Team Girsl Cup final for podcast
    
"""

# %% Import packages

import pandas as pd
from glob import glob
import json
import numpy as np

# %% Set-up

#Set Fever and Vixens squad Id'ss
vixensSquadId = 804
feverSquadId = 810

#Identify team girls cup 2022 data folders
procDatDir = '..\\..\\..\\..\\data\\matchCentre\\processed\\'
folderList = glob(procDatDir+'2022_TGC_*\\', recursive = True)

# %% General stats that stood out

#Combine team stats data from across TGC for comparative values
for folderInd in range(len(folderList)):
    
    #Load team stats data
    matchLabel = folderList[folderInd].split('\\')[-2]
    teamStats_df = pd.read_csv(f'{folderList[folderInd]}teamStats_{matchLabel}.csv')
    
    #Start dataframe or concatenate
    if folderInd == 0:
        tgc_teamStats = teamStats_df
    else:
        tgc_teamStats = pd.concat([tgc_teamStats, teamStats_df])

#Contact penalties
#Fever = 38; Vixens = 21 (5th least across tournament)

#Total penalties
#Fever = 47; Vixens = 30 (4th least across tournament)

#Time in possession
#Fever = 39%; #Vixens = 61% (biggest differential across tournament)

#Combine team stats period data from across TGC for comparative values
for folderInd in range(len(folderList)):
    
    #Load team stats data
    matchLabel = folderList[folderInd].split('\\')[-2]
    teamPeriodStats_df = pd.read_csv(f'{folderList[folderInd]}teamPeriodStats_{matchLabel}.csv')
    
    #Start dataframe or concatenate
    if folderInd == 0:
        tgc_teamPeriodStats = teamPeriodStats_df
    else:
        tgc_teamPeriodStats = pd.concat([tgc_teamPeriodStats, teamPeriodStats_df])

#Q2 and Q3 was where Vixens where getting on top
#Across these quarters

#Feeds
#Fever = 17; Vixens = 27

#Feeds w/ attempts
#Fever = 13; Vixens = 21

#Fever centre pass to goal percentage in Q2 = 22%

#In the fourth quarter where the Fever where getting back into it

#Fever centre pass to goal percentage in Q2 = 100%

#Feeds
#Fever = 13; Vixens = 10

#Feeds w/ attempts
#Fever = 12; Vixens = 9
#(just about as many for Fever in Q4 as Q2 & Q3 combined)

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

# %%% ----- End of 00_teamGirlsCup_analysis.py -----