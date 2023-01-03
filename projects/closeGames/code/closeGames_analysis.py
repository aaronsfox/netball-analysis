# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Short script to investigate rarity of close finishes in ANZC/SSN
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np

# %% Set-up

#Set analysis directory
analysisDir = os.getcwd()

#Get helper functions
os.chdir('..\\..\..\\code\\matchCentre')
import collatestats

#Get back to analysis directory
os.chdir(analysisDir)

#Set base directory for processed data
baseDir = '..\\..\\..\\data\\matchCentre\\processed'

# %% Run analysis

#Get the team stats data from SSN years
scoreFlowData = collatestats.getSeasonStats(baseDir = baseDir,
                                            years = 'all',
                                            fileStem = 'scoreFlow')

#Set-up lists to store data in on margin and last second shots
preMargin = []
endMargin = []
timeLastShot = []
lastSecondShot = []

#Loop through years
for year in list(scoreFlowData.keys()):
    
    #Loop through matches
    for matchId in list(scoreFlowData[year]['matchId'].unique()):
        
        #Extract end margin for the game
        endMargin.append(scoreFlowData[year].loc[scoreFlowData[year]['matchId'] == matchId,
                                                 ].reset_index(drop = True).iloc[-1]['scoreDifferential'])
        
        #Extract margin just before the final score
        preMargin.append(scoreFlowData[year].loc[scoreFlowData[year]['matchId'] == matchId,
                                                 ].reset_index(drop = True).iloc[-2]['scoreDifferential'])
        
        #Extract the time of the last score
        timeLastShot.append(scoreFlowData[year].loc[scoreFlowData[year]['matchId'] == matchId,
                                                    ].reset_index(drop = True).iloc[-1]['periodSeconds'])
        
        #Identify if last shot was within 10 seconds of 900 second period finish
        if scoreFlowData[year].loc[scoreFlowData[year]['matchId'] == matchId,
                                                        ].reset_index(drop = True).iloc[-1]['periodSeconds'] >= 890:
            lastSecondShot.append(True)
        else:
            lastSecondShot.append(False)
        
#Create a counter for various things
#Games decided by 1 goal
oneGoalMargin = 0
#Games decided by a last second winning shot
winningShot = 0

#Loop through various matches to count occurrences
for ii in range(len(endMargin)):
    
    #Check if game was decided by 1 goal
    if endMargin[ii] == 1 or endMargin == -1:
        
        #Add to counter
        oneGoalMargin += 1
        
        #Check if there was a last second shot for this one goal match
        if lastSecondShot[ii]:
            
            #Check if the pre last scoring shot was 0 - hence it was a game winner
            if preMargin[ii] == 0:
                
                #Add to the counter
                winningShot += 1
                
#Calculate and print percentages
print(f'Number and percentage of one goal margins: {oneGoalMargin} & {np.round(oneGoalMargin / len(endMargin) * 100, 2)}')
print(f'Number and percentage of winning shots: {winningShot} & {np.round(winningShot / len(endMargin) * 100, 2)}')
    

# %% ----- End of closeGames_analysis.py -----