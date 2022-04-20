# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Short script to ruun some analysis of the Magpies for Erin.
    
"""

# %% Import packages

import pandas as pd
import os
import numpy as np

#Define functions
def find_sub_list(sl,l):
    results=[]
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            results.append((ind,ind+sll-1))

    return results

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

#Create dictionary to map squad names to ID's
squadDict ={804: 'Vixens',
            806: 'Swifts',
            807: 'Firebirds',
            8117: 'Lightning',
            810: 'Fever',
            8119: 'Magpies',
            801: 'Thunderbirds',
            8118: 'GIANTS'}

# %% Run analysis

#Get the team stats data from SSN years
teamStatsSSN = collatestats.getSeasonStats(baseDir = baseDir,
                                           years = [2017, 2018, 2019, 2020, 2021],
                                           fileStem = 'teamStats')

#Set-up dictionary to store match results in
resultsData = {'matchId': [], 'year': [], 'round': [],
               'squadId': [], 'score': [], 'margin': []}

#Loop through years to collate data
for year in list(teamStatsSSN.keys()):
    
    #Extract dataframe and just get regular season matches
    data = teamStatsSSN[year].loc[teamStatsSSN[year]['matchType'] == 'regular',]
    
    #Get unique match Id's
    matchIds = data['matchId'].unique()
    
    #Loop through match Id's and extract results
    for matchId in matchIds:
        
        #Extract match data
        matchData = data.loc[data['matchId'] == matchId,]
        
        #Get the two squad Id's
        squadIds = list(matchData['squadId'].unique())
        
        #Loop through squad Ids
        for squadId in squadIds:
            
            #Get score
            if year < 2020:
                #Squad score
                score = matchData.loc[matchData['squadId'] == squadId,['goals']].to_numpy()[0][0]
                #Opponent score
                oppScore = matchData.loc[matchData['squadId'] != squadId,['goals']].to_numpy()[0][0]
            else:
                #Squad score
                score = matchData.loc[matchData['squadId'] == squadId,['goal1']].to_numpy()[0][0] + \
                    (matchData.loc[matchData['squadId'] == squadId,['goal2']].to_numpy()[0][0] * 2)
                #Opponent score
                oppScore = matchData.loc[matchData['squadId'] != squadId,['goal1']].to_numpy()[0][0] + \
                    (matchData.loc[matchData['squadId'] != squadId,['goal2']].to_numpy()[0][0] * 2)
                    
            #Append data to dictionary
            resultsData['matchId'].append(matchId)
            resultsData['year'].append(year)
            resultsData['round'].append(matchData['roundNo'].unique()[0])
            resultsData['squadId'].append(squadId)
            resultsData['score'].append(score)
            resultsData['margin'].append(score - oppScore) 

#Convert to dataframe
resultsDf = pd.DataFrame.from_dict(resultsData)

#Create a win loss categorical column
winLoss = []
for margin in resultsDf['margin']:
    if margin < 0:
        winLoss.append('L')
    elif margin > 0:
        winLoss.append('W')
    else:
        winLoss.append('D')
resultsDf['winLoss'] = winLoss

#Create a squad name variable based on squad Id mapping
resultsDf['squadName'] = [squadDict[squadId] for squadId in resultsDf['squadId']]

#Collate total win-loss ratio
winLoss_bySquad = resultsDf.groupby(['squadName', 'winLoss']).count()

#Print win loss outputs
for squadName in list(resultsDf['squadName'].unique()):
    #get wins, loss and draws
    nWin = winLoss_bySquad.loc[squadName,'W']['matchId']
    nLoss = winLoss_bySquad.loc[squadName,'L']['matchId']
    nDraw = winLoss_bySquad.loc[squadName,'D']['matchId']
    #Calculate win %
    winPer = nWin / (nWin + nLoss + nDraw) * 100
    #Print output
    print(f"{squadName}: Wins - {nWin}; Loss - {nLoss}; Draw - {nDraw}; Win % - {np.round(winPer,2)}")

#Collate win-loss ratio by year
winLoss_bySquadYear = resultsDf.groupby(['squadName', 'winLoss', 'year']).count()

#Print average win loss outputs
for squadName in list(resultsDf['squadName'].unique()):
    #Calculate average wins and losses
    avgWin = np.mean(winLoss_bySquadYear.loc[squadName,'W']['matchId'].values)
    avgLoss = np.mean(winLoss_bySquadYear.loc[squadName,'L']['matchId'].values)
    avgDraw = np.mean(winLoss_bySquadYear.loc[squadName,'D']['matchId'].values)
    #Print output
    print(f"{squadName}: Avg. Wins - {np.round(avgWin,2)}; Avg. Loss - {np.round(avgLoss,2)}; Avg. Draw - {np.round(avgDraw,2)}")

#Collate average winning margin
for squadName in list(resultsDf['squadName'].unique()):
    #Extract squad data
    squadData = resultsDf.loc[resultsDf['squadName'] == squadName,]
    #Calculate average win margin
    avgWinMargin= np.mean(squadData.loc[squadData['margin'] > 0,]['margin'].values)
    #Calculate average loss margin
    avgLossMargin = np.abs(np.mean(squadData.loc[squadData['margin'] < 0,]['margin'].values))
    #Print output
    print(f"{squadName}: Avg. Win Margin - {np.round(avgWinMargin,2)}; Avg. Loss Margin - {np.round(avgLossMargin,2)}")
    
#Identify consecutive streaks
for squadName in list(resultsDf['squadName'].unique()):
    #Set dictionary to store values in
    streaksDict = {'year': [], 'winStreak': [], 'lossStreak': [],
                   'winLocStr': [], 'lossLocStr': []}
    #Loop through years
    for year in list(resultsDf['year'].unique()):
        #Extract squad win loss sequences data
        squadData = list(resultsDf.loc[(resultsDf['squadName'] == squadName) &
                                       (resultsDf['year'] == year),]['winLoss'])
        #Count up the win streak for the year
        bestWinStreak = 0
        winCounter = 0
        for winLossResult in squadData:
            #Check for win
            if winLossResult == 'W':
                #Add to counter
                winCounter += 1
                #Replace max if greater than previous
                if winCounter > bestWinStreak:
                    bestWinStreak = winCounter
            else:
                #A loss is obtained so reset win counter
                winCounter = 0
        #Count up the loss streak for the year
        worstLossStreak = 0
        lossCounter = 0
        for winLossResult in squadData:
            #Check for win
            if winLossResult == 'L':
                #Add to counter
                lossCounter += 1
                #Replace max if greater than previous
                if lossCounter > worstLossStreak:
                    worstLossStreak = lossCounter
            else:
                #A loss is obtained so reset win counter
                lossCounter = 0
        #Find where streaks occurred
        #Set win pattern list
        if bestWinStreak > 0:
            winPattern = ['W']*bestWinStreak
            winStreakLoc = find_sub_list(winPattern, squadData)
            #Create string that highlights round streaks
            winLocStr = [f"Rd. {winStreakLoc[ii][0]+1} to Rd. {winStreakLoc[ii][1]+1}" for ii in range(len(winStreakLoc))]
        else:
            winStreakLoc = 'NA'
            winLocStr = 'NA'
        #Set loss pattern list
        if worstLossStreak > 0:
            lossPattern = ['L']*worstLossStreak
            lossStreakLoc = find_sub_list(lossPattern, squadData)
            #Create string that highlights round streaks
            lossLocStr = [f"Rd. {lossStreakLoc[ii][0]+1} to Rd. {lossStreakLoc[ii][1]+1}" for ii in range(len(lossStreakLoc))]
        else:
            lossStreakLoc = 'NA'
            lossLocStr = 'NA'
        #Append to dictionary
        streaksDict['year'].append(year)
        streaksDict['winStreak'].append(bestWinStreak)
        streaksDict['lossStreak'].append(worstLossStreak)
        streaksDict['winLocStr'].append(', '.join(winLocStr))
        streaksDict['lossLocStr'].append(', '.join(lossLocStr))

    #Print squad output
    for ii in range(len(streaksDict['year'])):
        print(f"{squadName}: Best Win Streak in {streaksDict['year'][ii]} - {streaksDict['winStreak'][ii]} ({streaksDict['winLocStr'][ii]}); Worst Loss Streak in {streaksDict['year'][ii]} - {streaksDict['lossStreak'][ii]} ({streaksDict['lossLocStr'][ii]})")

# %%% ----- End of thePies_analysis.py -----