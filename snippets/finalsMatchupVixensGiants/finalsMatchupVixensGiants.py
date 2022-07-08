# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to check out statistics relating to panel questions.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\data\\matchCentre\\processed'

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

# %% Collate relevant data

#Bring in team stats from regular season
teamStatsRegular = collatestats.getSeasonStats(baseDir = baseDir,
                                        years = [2022],
                                        fileStem = 'teamStats',
                                        matchOptions = ['regular'])
teamStatsRegular = teamStatsRegular[2022]

#Bring in team stats from finals
teamStatsFinal = collatestats.getSeasonStats(baseDir = baseDir,
                                             years = [2022],
                                             fileStem = 'teamStats',
                                             matchOptions = ['final'])
teamStatsFinal = teamStatsFinal[2022]

# %% Review each teams stats

#Vixens team stats
vixensTeamStatsRegular = teamStatsRegular.loc[teamStatsRegular['squadId'] == squadNameDict['Vixens'],]

#Giants team stats
giantsTeamStatsRegular = teamStatsRegular.loc[teamStatsRegular['squadId'] == squadNameDict['GIANTS'],]

#Key Vixens stat:
    #Vixens have recorded 10 or more gains in 12 of their 15 games this year - won every one of those, lost the others
    #Links back to round 3 win against the GIANTS:
        #Gains were huge in early season GIANTS win - where Weston had 7, Mannix 6, Eddy 4
    
#Key GIANTS stat:
    #Turnovers - GIANTS recorded 6 matches with 20+ turnovers; lost 5 of 6 of these
    
# %% Review average team stats from regular season

#Get team averages
avgTeamStatsRegular = teamStatsRegular.groupby('squadId').mean().reset_index(drop = False)
avgTeamStatsRegular['squadId'].replace(squadDict, inplace = True)

#Get team variation
sdTeamStatsRegular = teamStatsRegular.groupby('squadId').std().reset_index(drop = False)
sdTeamStatsRegular['squadId'].replace(squadDict, inplace = True)

#Export sheets
avgTeamStatsRegular.to_csv('avgTeamStatsRegular.csv', index = False)
sdTeamStatsRegular.to_csv('sdTeamStatsRegular.csv', index = False)

#Conflicting scoring strategies:
    #GIANTS no. 1 for Super Shot attempts at just over 13 per game / #1 for makes as well at just over 7 a game
    #Vixens ranked second last for Super Shot attempts at just under 7 per game / second last for makes as well at just over 3 per game
    
    #Links back to round 9 match-up where they had their second highest number of made Super Shots with 12:
        #Remembering back to this game the Super Shots was the only thing keeping them with the Vixens
        
#GIANTS fast paced approach:
    #GIANTS are the number 2 ranked team in league (just behind Firebirds) for 'pace' (i.e. no. of possessions per game)
    #Their two match-ups against the Vixens though have been 2 of their 3 slowest paced games for the year
    #Vixens effective in slowing the GIANTS down in attack
    
#Getting to the loose balls:
    #Vixens ranked first in the league for pickups at ~11.5 per game
    #Giants ranked second last in league for pickups at ~8 per game
    
    #Links back to last match-up in round 9:
        #GIANTS generated 19 deflections that didn't result in a turnover
        #Likely because the Vixens led the pickups stat 22-7 in that match
    

# %% Did the GIANTS dodge a bullet with scoring so low?

#GIANTS also have the most variable scoring in the league across the regular season
    #Have fluctuated round to round more than any other team
    #Up to 82 all the way down to 43

#Extract scores from season of 55 or less
giantsLowScoreMatches = giantsTeamStatsRegular.loc[giantsTeamStatsRegular['points'] <= 55,]

#Semi-final was the lowest score for the year where GIANTS have managed to win
#Didn't win a game the 3 times this year they scored 55 or less
#Probably can't afford another scoring game this low and expect to win

# %% Review player stats for key details

#Get regular season player stats
playerStatsRegular = collatestats.getSeasonStats(baseDir = baseDir,
                                                 years = [2022],
                                                 fileStem = 'playerStats',
                                                 matchOptions = ['regular'])
playerStatsRegular = playerStatsRegular[2022]

#Get Kumwenda stats
kumwendaId = 80540
kumwendaPlayerStatsRegular = playerStatsRegular.loc[playerStatsRegular['playerId'] == kumwendaId,]

#Kumwenda had a dominant game against the GIANTS last time:
    #50 goals from 50 attempts
    #This was the last time she had 50 goals in a match
    #Finished the last 2 rounds with 33 and 24 total goals made + had 20 against Fever in final
    #Key player alert

# %% ----- End of finalsMatchupVixensGiants.py -----