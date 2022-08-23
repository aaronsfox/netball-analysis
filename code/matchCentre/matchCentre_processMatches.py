# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Script collates data from the .json netball match centre files into separated
    and more easy-to-use file formats.
        
    *** TODO: can probably map possessions a little better with possession changes etc. ***
    
"""

# %% Import packages

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import os
import json
import re
import numpy as np

# %% Define functions

#Sort file list alpha-numerically so that round 1 remains first
def sortedNicely(l):
    """ Sorts the given iterable in the way that is expected.
    Required arguments:
    l -- The iterable to be sorted. """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

# %% Set-up

#Set data directory
datDir = os.getcwd()+'\\..\\..\\data\matchCentre\\raw\\'

#Set processed directory
procDir = os.getcwd()+'\\..\\..\\data\matchCentre\\processed\\'

#Get the list of .json files in raw data folder
jsonFileList = list()
for file in os.listdir(datDir):
    if file.endswith('.json'):
        jsonFileList.append(file)
        
#Sort file list 'nicely'
jsonFileList = sortedNicely(jsonFileList)

#Set lists to store some general information
#Squad information
squadData = {'squadId': [], 'squadCode': [], 'squadName': [], 'squadNickname': []}

# %% Extract match data

#Set variable to process all or only new files
#Whether data has been processed is determined by if the folder exists
processCondition = 'new' #or 'all' or 'new'

#Loop through match files
for jsonFile in jsonFileList:
    
    #Load the .json file
    with open(datDir+jsonFile) as fileToOpen:
        data = json.load(fileToOpen)
    
    #Check if match was completed
    if data['matchInfo']['matchStatus'][0] == 'complete':
    
        #Get quick access to match ID for data storage
        quickMatchId = data['matchInfo']['matchId'][0]
    
        #Make a directory to store processed data in
        if not os.path.isdir('..\\..\\data\\matchCentre\\processed\\'+str(quickMatchId)+'_'+jsonFile.split('.')[0]):
            #Create directory
            os.mkdir('..\\..\\data\\matchCentre\\processed\\'+str(quickMatchId)+'_'+jsonFile.split('.')[0])
            #Create a variable indicating data hasn't been processed
            dataExists = False
        else:
            #Create a variable indicating data hasn't been processed
            dataExists = True
    
        #Determine whether to process data based on conditions
        if processCondition == 'all':
            processData = True
        elif processCondition == 'new':
            if not dataExists:
                processData = True
            else:
                processData = False
        else:
            raise ValueError('processCondition variable must be string of "all" or "new"')
    
        #Process data if required        
        if processData:
        
            #Set the directory to store data
            matchFileDir = '..\\..\\data\\matchCentre\\processed\\'+str(quickMatchId)+'_'+jsonFile.split('.')[0]+'\\'
                
            #Check if game was completed
            if data['matchInfo']['matchStatus'][0] == 'complete':
                
                #Run a check as sometimes period second info isn't listed
                if len(data['periodInfo']['qtr']) < 4:
                    #Add some default seconds periods of 905 seconds (5 second buffer)
                    #Determine how many periods to add
                    periodsToAdd = 4 - len(data['periodInfo']['qtr'])
                    #Loop through and add
                    for periodNo in range(len(data['periodInfo']['qtr']),4):
                        data['periodInfo']['qtr'].append(
                            {'periodSeconds': [905], 'period': [periodNo+1]}
                            )
                
                # %% Extract the general information
        
                #Check if squad is present in general squad dictionary
                #Dictionary is used for some lookup functions later on only
                for squadInd in range(len(data['teamInfo']['team'])):
                    if data['teamInfo']['team'][squadInd]['squadId'][0] not in squadData['squadId']:
                        #Add squad to general database
                        squadData['squadId'].append(data['teamInfo']['team'][squadInd]['squadId'][0])
                        squadData['squadCode'].append(data['teamInfo']['team'][squadInd]['squadCode'][0])
                        squadData['squadName'].append(data['teamInfo']['team'][squadInd]['squadName'][0])
                        squadData['squadNickname'].append(data['teamInfo']['team'][squadInd]['squadNickname'][0])    
                
                #Extract squad Id from the match for later checking
                squadIdCheck = [data['teamInfo']['team'][0]['squadId'][0],
                                data['teamInfo']['team'][1]['squadId'][0]]
                
                # %% Extract match info data
                
                #Put match info in dictionary
                matchInfo = {
                    'matchId': data['matchInfo']['matchId'][0],
                    'homeSquadId': data['matchInfo']['homeSquadId'][0],
                    'homeSquadName': squadData['squadName'][squadData['squadId'].index(data['matchInfo']['homeSquadId'][0])],
                    'homeSquadNickname': squadData['squadNickname'][squadData['squadId'].index(data['matchInfo']['homeSquadId'][0])],
                    'awaySquadId': data['matchInfo']['awaySquadId'][0],
                    'awaySquadName': squadData['squadName'][squadData['squadId'].index(data['matchInfo']['awaySquadId'][0])],
                    'awaySquadNickname': squadData['squadNickname'][squadData['squadId'].index(data['matchInfo']['awaySquadId'][0])],
                    'matchType': data['matchInfo']['matchType'][0],
                    'periodCompleted': data['matchInfo']['periodCompleted'][0],
                    'roundNumber': data['matchInfo']['roundNumber'][0],
                    'localStartTime': data['matchInfo']['localStartTime'][0],
                    'venueCode': data['matchInfo']['venueCode'][0],
                    'venueId': data['matchInfo']['venueId'][0],
                    'venueName': data['matchInfo']['venueName'][0],
                    'period': [data['periodInfo']['qtr'][periodInd]['period'][0] for periodInd in range(len(data['periodInfo']['qtr']))],
                    'periodSeconds': [data['periodInfo']['qtr'][periodInd]['periodSeconds'][0] for periodInd in range(len(data['periodInfo']['qtr']))]
                    }
                
                #Save match info data
                matchInfo_json = json.dumps(matchInfo)
                f = open(matchFileDir+str(quickMatchId)+'_'+'matchInfo_'+jsonFile.split('.')[0]+'.json', 'w')
                f.write(matchInfo_json)
                f.close()
                
                # %% Extract player lists
                
                #Setup dictionary to extract data to
                playerList = {
                    'matchId': [],
                    'playerId': [], 'firstname': [], 'surname': [],
                    'displayName': [], 'shortDisplayName': [],
                    'squadId': []
                    }
                
                #Loop through players
                for playerInd in range(len(data['playerInfo']['player'])):
                    playerList['matchId'].append(data['matchInfo']['matchId'][0])
                    playerList['playerId'].append(data['playerInfo']['player'][playerInd]['playerId'][0])
                    playerList['firstname'].append(data['playerInfo']['player'][playerInd]['firstname'][0])
                    playerList['surname'].append(data['playerInfo']['player'][playerInd]['surname'][0])
                    playerList['displayName'].append(data['playerInfo']['player'][playerInd]['displayName'][0])
                    playerList['shortDisplayName'].append(data['playerInfo']['player'][playerInd]['shortDisplayName'][0])
                    #Identify players squad by searching through the stats database
                    for playerStatsInd in range(len(data['playerStats']['player'])):
                        if data['playerStats']['player'][playerStatsInd]['playerId'][0] == data['playerInfo']['player'][playerInd]['playerId'][0]:
                            break
                    playerList['squadId'].append(data['playerStats']['player'][playerStatsInd]['squadId'][0])
                    
                #Convert to dataframe
                playerList_df = pd.DataFrame.from_dict(playerList)
                
                #Write player list to file
                playerList_df.to_csv(matchFileDir+str(quickMatchId)+'_'+'playerList_'+jsonFile.split('.')[0]+'.csv', index = False)
                    
                # %% Collate team period stats
                
                #Setup dictionary to extract data to
                teamPeriodStatsLong = {
                    'matchId': [],
                    'squadId': [],
                    'period': [],
                    'statistic': [],
                    'value': []
                    }
                
                #Loop through team entries
                for teamStatsInd in range(len(data['teamPeriodStats']['team'])):
                    #Loop through statistics
                    for statistic in list(data['teamPeriodStats']['team'][teamStatsInd].keys()):
                        #Check to not record squad Id, period
                        if statistic != 'squadId' and statistic != 'period':
                            #Record values
                            teamPeriodStatsLong['matchId'].append(data['matchInfo']['matchId'][0])
                            teamPeriodStatsLong['squadId'].append(data['teamPeriodStats']['team'][teamStatsInd]['squadId'][0])
                            teamPeriodStatsLong['period'].append(data['teamPeriodStats']['team'][teamStatsInd]['period'][0])
                            teamPeriodStatsLong['statistic'].append(statistic)
                            teamPeriodStatsLong['value'].append(data['teamPeriodStats']['team'][teamStatsInd][statistic][0])
                    
                #Convert to dataframe
                teamPeriodStatsLong_df = pd.DataFrame.from_dict(teamPeriodStatsLong)
                
                #Add opposition squad Id
                oppSquadId = []
                for squadId in teamPeriodStatsLong_df['squadId']:
                    if squadId == squadIdCheck[0]:
                        oppSquadId.append(squadIdCheck[1])
                    else:
                        oppSquadId.append(squadIdCheck[0])
                teamPeriodStatsLong_df['oppSquadId'] = oppSquadId
                
                #Convert to wide dataframe
                teamPeriodStatsWide_df = teamPeriodStatsLong_df.pivot(index = ['matchId', 'squadId', 'oppSquadId', 'period'],
                                                                      columns = 'statistic',
                                                                      values = 'value').reset_index(drop = False)
                
                #Weird cases where there are extra periods that don't have stats need
                #to be checked for
                #Get the periods included in the match
                matchPeriods = [data['periodInfo']['qtr'][ii]['period'][0] for ii in range(len(data['periodInfo']['qtr']))]
                #Extract just to the data from match periods
                teamPeriodStatsWide_df = teamPeriodStatsWide_df.loc[teamPeriodStatsWide_df['period'].isin(matchPeriods),
                                                                    ].reset_index(drop = True)
                
                #Add offensive, defensive and net rating statistics
                #As per Dave Scroggs' formulas
                
                #From 2018 onwards, offensive rebounds first need to be calculated
                if int(jsonFile.split('_')[0]) >= 2018:
                    teamPeriodStatsWide_df['offensiveRebounds'] = np.round(teamPeriodStatsWide_df['goalMisses'] * (teamPeriodStatsWide_df['missedShotConversion'] / 100))
                
                #Possessions
                #From 2018 onwards turnovers are renamed and missed shot turnovers need to be included
                if int(jsonFile.split('_')[0]) >= 2018:
                    teamPeriodStatsWide_df['possessions'] = (teamPeriodStatsWide_df['goalAttempts'] - teamPeriodStatsWide_df['offensiveRebounds']) + \
                        (teamPeriodStatsWide_df['generalPlayTurnovers'] + np.round(teamPeriodStatsWide_df['goalMisses'] * (1 - (teamPeriodStatsWide_df['missedShotConversion'] / 100))))
                else:
                    teamPeriodStatsWide_df['possessions'] = (teamPeriodStatsWide_df['goalAttempts'] - teamPeriodStatsWide_df['offensiveRebounds']) + \
                        teamPeriodStatsWide_df['turnovers']
                    
                #Pace (posessions per 60 minute)
                pacePer60 = []
                for statInd in range(len(teamPeriodStatsWide_df)):
                    pacePer60.append(teamPeriodStatsWide_df['possessions'][statInd] * \
                        (60 / (data['periodInfo']['qtr'][teamPeriodStatsWide_df['period'][statInd]-1]['periodSeconds'][0] / 60)))
                teamPeriodStatsWide_df['pacePer60'] = pacePer60
                
                #Offensive rating
                teamPeriodStatsWide_df['offensiveRating'] = teamPeriodStatsWide_df['goals'] / teamPeriodStatsWide_df['possessions'] * 100
                
                #Defensive rating
                defRating = []
                for statInd in range(len(teamPeriodStatsWide_df)):
                    #Get current squadId and period
                    squadId = teamPeriodStatsWide_df['squadId'][statInd]
                    period =  teamPeriodStatsWide_df['period'][statInd]
                    #Get opposition data for calculation
                    goalsAgainst = teamPeriodStatsWide_df.loc[(teamPeriodStatsWide_df['squadId'] != squadId) &
                                                              (teamPeriodStatsWide_df['period'] == period),
                                                              ['goals']].values[0][0]
                    possAgainst = teamPeriodStatsWide_df.loc[(teamPeriodStatsWide_df['squadId'] != squadId) &
                                                             (teamPeriodStatsWide_df['period'] == period),
                                                             ['possessions']].values[0][0]
                    #Append to list
                    defRating.append(goalsAgainst / possAgainst * 100)
                teamPeriodStatsWide_df['defensiveRating'] = defRating
                
                #Calculate net rating
                teamPeriodStatsWide_df['netRating'] = teamPeriodStatsWide_df['offensiveRating'] - teamPeriodStatsWide_df['defensiveRating']
                        
                #Write wide dataframe to file
                teamPeriodStatsWide_df.to_csv(matchFileDir+str(quickMatchId)+'_'+'teamPeriodStats_'+jsonFile.split('.')[0]+'.csv', index = False)
                
                # %% Collate team stats
                
                #Setup dictionary to extract data to
                teamStatsLong = {
                    'matchId': [],
                    'squadId': [],
                    'statistic': [],
                    'value': []
                    }
                
                #Loop through team entries
                for teamStatsInd in range(len(data['teamStats']['team'])):
                    #Loop through statistics
                    for statistic in list(data['teamStats']['team'][teamStatsInd].keys()):
                        #Check to not record squad Id, period
                        if statistic != 'squadId':
                            #Record values
                            teamStatsLong['matchId'].append(data['matchInfo']['matchId'][0])
                            teamStatsLong['squadId'].append(data['teamStats']['team'][teamStatsInd]['squadId'][0])
                            teamStatsLong['statistic'].append(statistic)
                            teamStatsLong['value'].append(data['teamStats']['team'][teamStatsInd][statistic][0])
                            
                #Convert to dataframe
                teamStatsLong_df = pd.DataFrame.from_dict(teamStatsLong)
                
                #Add opposition squad Id
                oppSquadId = []
                for squadId in teamStatsLong_df['squadId']:
                    if squadId == squadIdCheck[0]:
                        oppSquadId.append(squadIdCheck[1])
                    else:
                        oppSquadId.append(squadIdCheck[0])
                teamStatsLong_df['oppSquadId'] = oppSquadId
                
                #Convert to wide dataframe
                teamStatsWide_df = teamStatsLong_df.pivot(index = ['matchId', 'squadId', 'oppSquadId'],
                                                          columns = 'statistic',
                                                          values = 'value').reset_index(drop = False)
                
                #Add offensive, defensive and net rating statistics
                #As per Dave Scroggs' formulas
                
                #From 2018 onwards, offensive rebounds first need to be calculated
                if int(jsonFile.split('_')[0]) >= 2018:
                    teamStatsWide_df['offensiveRebounds'] = np.round(teamStatsWide_df['goalMisses'] * (teamStatsWide_df['missedShotConversion'] / 100))
                
                #Possessions
                #From 2018 onwards turnovers are renamed and missed shot turnovers need to be included
                if int(jsonFile.split('_')[0]) >= 2018:
                    teamStatsWide_df['possessions'] = (teamStatsWide_df['goalAttempts'] - teamStatsWide_df['offensiveRebounds']) + \
                        (teamStatsWide_df['generalPlayTurnovers'] + np.round(teamStatsWide_df['goalMisses'] * (1 - (teamStatsWide_df['missedShotConversion'] / 100))))
                else:
                    teamStatsWide_df['possessions'] = (teamStatsWide_df['goalAttempts'] - teamStatsWide_df['offensiveRebounds']) + \
                        teamStatsWide_df['turnovers']
                    
                #Pace (posessions per 60 minute)
                pacePer60 = []
                for statInd in range(len(teamStatsWide_df)):
                    pacePer60.append(teamStatsWide_df['possessions'][statInd] * \
                                     (60 / (np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(len(data['periodInfo']['qtr']))]) / 60)))
                teamStatsWide_df['pacePer60'] = pacePer60
                
                #Offensive rating
                teamStatsWide_df['offensiveRating'] = teamStatsWide_df['goals'] / teamStatsWide_df['possessions'] * 100
                
                #Defensive rating
                defRating = []
                for statInd in range(len(teamStatsWide_df)):
                    #Get current squadId and period
                    squadId = teamStatsWide_df['squadId'][statInd]
                    #Get opposition data for calculation
                    goalsAgainst = teamStatsWide_df.loc[teamStatsWide_df['squadId'] != squadId,
                                                        ['goals']].values[0][0]
                    possAgainst = teamStatsWide_df.loc[teamStatsWide_df['squadId'] != squadId,
                                                       ['possessions']].values[0][0]
                    #Append to list
                    defRating.append(goalsAgainst / possAgainst * 100)
                teamStatsWide_df['defensiveRating'] = defRating
                
                #Calculate net rating
                teamStatsWide_df['netRating'] = teamStatsWide_df['offensiveRating'] - teamStatsWide_df['defensiveRating']
                
                #Write wide dataframe to file
                teamStatsWide_df.to_csv(matchFileDir+str(quickMatchId)+'_'+'teamStats_'+jsonFile.split('.')[0]+'.csv', index = False)
                
                # %% Extract score flow data
                
                #Setup dictionary to extract data to
                scoreFlowData = {
                    'matchId': [],
                    'squadId': [],
                    'playerId': [],
                    'period': [],
                    'periodSeconds': [],
                    'distanceCode': [],
                    'positionCode': [],
                    'scoreName': [],
                    'scorePoints': [],
                    }
                
                #Loop through score flow entries
                for scoreFlowInd in range(len(data['scoreFlow']['score'])):
                    scoreFlowData['matchId'].append(data['matchInfo']['matchId'][0])
                    scoreFlowData['squadId'].append(data['scoreFlow']['score'][scoreFlowInd]['squadId'][0])
                    scoreFlowData['playerId'].append(data['scoreFlow']['score'][scoreFlowInd]['playerId'][0])
                    scoreFlowData['period'].append(data['scoreFlow']['score'][scoreFlowInd]['period'][0])
                    scoreFlowData['periodSeconds'].append(data['scoreFlow']['score'][scoreFlowInd]['periodSeconds'][0])
                    scoreFlowData['distanceCode'].append(data['scoreFlow']['score'][scoreFlowInd]['distanceCode'][0])
                    scoreFlowData['positionCode'].append(data['scoreFlow']['score'][scoreFlowInd]['positionCode'][0])
                    scoreFlowData['scoreName'].append(data['scoreFlow']['score'][scoreFlowInd]['scoreName'][0])
                    scoreFlowData['scorePoints'].append(data['scoreFlow']['score'][scoreFlowInd]['scorepoints'][0])
                    
                #Convert to dataframe
                scoreFlowData_df = pd.DataFrame.from_dict(scoreFlowData)
                
                #Calculate match seconds
                matchSeconds = []
                for scoreFlowInd in range(len(scoreFlowData_df)):
                    if scoreFlowData_df['period'][scoreFlowInd] == 1:
                        matchSeconds.append(scoreFlowData_df['periodSeconds'][scoreFlowInd])
                    else:
                        #Get a list of the period indices to add seconds from
                        periodAddInds = np.linspace(1, scoreFlowData_df['period'][scoreFlowInd]-1,
                                                    scoreFlowData_df['period'][scoreFlowInd]-1, dtype = int) - 1
                        #Get the seconds from the relevant periods
                        periodAddSecs = np.array([matchInfo['periodSeconds'][ii] for ii in periodAddInds])
                        #Sum the period addition seconds and add the current period to get match seconds
                        matchSeconds.append(np.sum(periodAddSecs) + scoreFlowData_df['periodSeconds'][scoreFlowInd])
                #Append to dataframe
                scoreFlowData_df['matchSeconds'] = matchSeconds
                
                #Add progressive scoreline
                #Set some lists and starting scores for data
                homeSquadScore = []
                currHomeScore = 0
                awaySquadScore = []
                currAwayScore = 0
                for scoreFlowInd in range(len(scoreFlowData_df)):
                    #Check if home team score flow
                    if scoreFlowData['squadId'][scoreFlowInd] == matchInfo['homeSquadId']:
                        #Add value to home score
                        currHomeScore += scoreFlowData['scorePoints'][scoreFlowInd]
                    else:
                        #Add value to away score
                        currAwayScore += scoreFlowData['scorePoints'][scoreFlowInd]
                    #Append current values to list
                    homeSquadScore.append(currHomeScore)
                    awaySquadScore.append(currAwayScore)
                #Append to datafram
                scoreFlowData_df['homeSquadScore'] = homeSquadScore
                scoreFlowData_df['awaySquadScore'] = awaySquadScore
                
                #Calculate score differential (relative to home team)
                scoreFlowData_df['scoreDifferential'] = scoreFlowData_df['homeSquadScore'] - scoreFlowData_df['awaySquadScore']
                
                #Add opposition squad Id
                oppSquadId = []
                for squadId in scoreFlowData_df['squadId']:
                    if squadId == squadIdCheck[0]:
                        oppSquadId.append(squadIdCheck[1])
                    else:
                        oppSquadId.append(squadIdCheck[0])
                scoreFlowData_df['oppSquadId'] = oppSquadId
                
                #Export scoreflow data to file
                scoreFlowData_df.to_csv(matchFileDir+str(quickMatchId)+'_'+'scoreFlow_'+jsonFile.split('.')[0]+'.csv', index = False)
                
                # %% Collate substitutions and player minutes
                
                #Setup dictionary to extract substitution data to
                substitutionsData = {
                    'matchId': [],
                    'playerId': [],
                    'squadId': [],
                    'startingPos': [],
                    'startingTime': [],
                    'finishPos': [],
                    'finishTime': []
                    }
                
                #Setup dictionary to extract minutes played data to
                minutesPlayedData = {
                    'matchId': [],
                    'playerId': [],
                    'squadId': [],
                    'minutesPlayed': []
                    }
                
                #Loop through players in list
                for playerInd in range(len(data['playerInfo']['player'])):
                    
                    #Get current player Id
                    playerId = data['playerInfo']['player'][playerInd]['playerId'][0]
                    
                    #Find index of current player Id in stats
                    for playerStatsInd in range(len(data['playerStats']['player'])):
                        if data['playerStats']['player'][playerStatsInd]['playerId'][0] == playerId:
                            break
                        
                    #Get players squad Id
                    squadId = data['playerStats']['player'][playerStatsInd]['squadId'][0]
                    
                    #Check if player recorded any minutes
                    if data['playerStats']['player'][playerStatsInd]['startingPositionCode'][0] == '-':
                        #Check if they recorded a substituion on
                        #Get all subbed on player Id's
                        if 'player' in data['playerSubs']: #initial check to see if subs made
                            subbedOn = []
                            #Check if single sub dictionary
                            if isinstance(data['playerSubs']['player'], dict):
                                subbedOn.append(data['playerSubs']['player']['playerId'][0])                        
                            else:                    
                                for nSubs in range(len(data['playerSubs']['player'])):
                                    subbedOn.append(data['playerSubs']['player'][nSubs]['playerId'][0])
                            #Check if player Id is in list
                            if playerId in subbedOn:
                                playedMins = True
                            else:
                                playedMins = False
                        else: #if no subs then obviously didn't play
                            playedMins = False
                    else:
                        #They started, so obviously played
                        playedMins = True
                    
                    #Extract player info if they played minutes
                    if playedMins:
                        
                        #Calculate the players positions and substitutions
                        #Set lists to store data in
                        startingPos = []
                        startingTime = []
                        finishPos = []
                        finishTime = []
                        
                        #Identify positions and timings
                        startingPos.append(data['playerStats']['player'][playerStatsInd]['startingPositionCode'][0])
                        startingTime.append(0)
                        #Loop through and identify any substitutions
                        if 'player' in data['playerSubs']:
                            
                            #Check if only one sub, as this has a different structure
                            if isinstance(data['playerSubs']['player'], dict):
                                #Examine the one substitution
                                if data['playerSubs']['player']['playerId'][0] == playerId:
                                    #Append info to finishing lists
                                    finishPos.append(data['playerSubs']['player']['toPos'][0])
                                    finishTime.append(data['playerSubs']['player']['periodSeconds'][0] + \
                                                      np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(data['playerSubs']['player']['period'][0] - 1)]))
                                    #Append same above info to starting time for next step
                                    startingPos.append(data['playerSubs']['player']['toPos'][0])
                                    startingTime.append(data['playerSubs']['player']['periodSeconds'][0] + \
                                                        np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(data['playerSubs']['player']['period'][0] - 1)]))                        
                            else:
                                #Loop through subs
                                for subNo in range(len(data['playerSubs']['player'])):
                                    if data['playerSubs']['player'][subNo]['playerId'][0] == playerId:
                                        
                                        #Append info to finishing lists
                                        finishPos.append(data['playerSubs']['player'][subNo]['toPos'][0])
                                        finishTime.append(data['playerSubs']['player'][subNo]['periodSeconds'][0] + \
                                                          np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(data['playerSubs']['player'][subNo]['period'][0] - 1)]))
                                        #Append same above info to starting time for next step
                                        startingPos.append(data['playerSubs']['player'][subNo]['toPos'][0])
                                        startingTime.append(data['playerSubs']['player'][subNo]['periodSeconds'][0] + \
                                                            np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(data['playerSubs']['player'][subNo]['period'][0] - 1)]))
                                        
                            #Wrap up finishing pos and finishing time once looping through subs
                            if len(finishPos) == 0:
                                #Player played the whole game
                                finishPos.append(startingPos[0])
                                finishTime.append(np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(len(data['periodInfo']['qtr']))]))                    
                            else:
                                #Player had some substitutions
                                finishPos.append(finishPos[-1])
                                finishTime.append(np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(len(data['periodInfo']['qtr']))]))
                            
                        else:
                            
                            #No subs were made
                            #Add finishing pos
                            finishPos.append(startingPos[0])
                            finishTime.append(np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(len(data['periodInfo']['qtr']))]))
                    
                    else:
                        
                        #Set lists to store data in
                        startingPos = []
                        startingTime = []
                        finishPos = []
                        finishTime = []
                        
                        #Allocate zero minute data to player
                        startingPos.append('S')
                        startingTime.append(0)
                        finishPos.append('S')
                        finishTime.append(np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(len(data['periodInfo']['qtr']))]))
                    
                    #Allocate data to dictionary
                    #Loop through positional entries
                    for posEntry in range(len(startingPos)):
                        #Append data
                        substitutionsData['matchId'].append(data['matchInfo']['matchId'][0])
                        substitutionsData['playerId'].append(playerId)
                        substitutionsData['squadId'].append(squadId)
                        substitutionsData['startingPos'].append(startingPos[posEntry])
                        substitutionsData['startingTime'].append(startingTime[posEntry])
                        substitutionsData['finishPos'].append(finishPos[posEntry])
                        substitutionsData['finishTime'].append(finishTime[posEntry])
                    
                #Convert substitutions data to dataframe
                substitutionsData_df = pd.DataFrame.from_dict(substitutionsData)
                
                #Put a check in place to drop any matching startin and finishing times
                #This seems to occur at the start of some games
                matchingSub = []
                for subInd in range(len(substitutionsData_df)):
                    if substitutionsData_df['startingTime'][subInd] == substitutionsData_df['finishTime'][subInd]:
                        matchingSub.append(True)
                    else:
                        matchingSub.append(False)
                substitutionsData_df.drop(list(np.where(matchingSub))[0], inplace = True)
        
                #Add a duration column
                substitutionsData_df['duration'] = substitutionsData_df['finishTime'] - substitutionsData_df['startingTime']
                
                #Replace any '-' with the 'S' indicator for substitute
                substitutionsData_df['startingPos'].replace('-', 'S', inplace = True)
                substitutionsData_df['finishPos'].replace('-', 'S', inplace = True)
                    
                #Loop through players and calculate minutes on court
                for playerId in list(substitutionsData_df['playerId'].unique()):
                    
                    #Extract the current players squad Id
                    squadId = substitutionsData_df.loc[substitutionsData_df['playerId'] == playerId,
                                                       ['squadId']]['squadId'].unique()[0]
                    
                    #Calculate the minutes played by the current player
                    minutesPlayed = np.sum(substitutionsData_df.loc[(substitutionsData_df['playerId'] == playerId) &
                                                                    (substitutionsData_df['startingPos'].isin(['GS','GA','WA','C','WD','GD','GK'])),
                                                                    ['duration']].to_numpy()) / 60
                    
                    #Check in place for the slight over-reach on four period matches that
                    #results in just over 60 minutes being played. This occurs in ANZC and
                    #SSN matches where the player is on court the whole match, and the resulting
                    #minutes played is just over 60 due to period seconds being slightly
                    #inflated each quarter
                    if jsonFile.split('_')[1] == 'ANZC' or jsonFile.split('_')[1] == 'SSN' or jsonFile.split('_')[1] == 'ANC':
                        if len(substitutionsData_df.loc[substitutionsData_df['playerId'] == playerId,]) == 1:
                            if 60 < minutesPlayed < 62:
                                #Correct to 60 mins
                                minutesPlayed = 60
                                
                    #Append data to dictionary
                    minutesPlayedData['matchId'].append(data['matchInfo']['matchId'][0])
                    minutesPlayedData['playerId'].append(playerId)
                    minutesPlayedData['squadId'].append(squadId)
                    minutesPlayedData['minutesPlayed'].append(minutesPlayed)
                        
                #Convert to dataframe
                minutesPlayedData_df = pd.DataFrame.from_dict(minutesPlayedData)
                
                #Add opposition squad Id
                #Substitutions dataframe
                oppSquadId = []
                for squadId in substitutionsData_df['squadId']:
                    if squadId == squadIdCheck[0]:
                        oppSquadId.append(squadIdCheck[1])
                    else:
                        oppSquadId.append(squadIdCheck[0])
                substitutionsData_df['oppSquadId'] = oppSquadId
                
                #Add opposition squad Id
                #Minutes played dataframe
                oppSquadId = []
                for squadId in minutesPlayedData_df['squadId']:
                    if squadId == squadIdCheck[0]:
                        oppSquadId.append(squadIdCheck[1])
                    else:
                        oppSquadId.append(squadIdCheck[0])
                minutesPlayedData_df['oppSquadId'] = oppSquadId
                
                #Export substitutions and minutes data to file
                substitutionsData_df.to_csv(matchFileDir+str(quickMatchId)+'_'+'substitutions_'+jsonFile.split('.')[0]+'.csv', index = False)
                minutesPlayedData_df.to_csv(matchFileDir+str(quickMatchId)+'_'+'minutesPlayed_'+jsonFile.split('.')[0]+'.csv', index = False)
                
                # %% Determine line-ups across match
                
                #Setup dictionary to extract data to
                lineUpData = {
                    'matchId': [],
                    'squadId': [],
                    'GS': [],
                    'GA': [],
                    'WA': [],
                    'C': [],
                    'WD': [],
                    'GD': [],
                    'GK': [],
                    'startingTime': [],
                    'finishTime': [],
                    'teamStartScore': [],
                    'teamEndScore': [],
                    'oppStartScore': [],
                    'oppEndScore': []
                    }
                
                #Set variable for court positions
                courtPositions = ['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']
                
                #Set-up a variable to loop through the two squad Id's
                matchSquads = [data['matchInfo']['homeSquadId'][0],
                               data['matchInfo']['awaySquadId'][0]]
                
                #Loop through squad Id's
                for squadId in matchSquads:
                    
                    #Allocate whether home squad
                    if squadId == data['matchInfo']['homeSquadId'][0]:
                        homeSquad = True
                    else:
                        homeSquad = False
            
                    #Extract substitutions data for current squad
                    #Drop any values that have the player on the bench the whole match
                    #Sort values by starting time
                    #It's easier to do this in multiple steps than wrapping in one command
                    squadSubstitutions = substitutionsData_df.loc[substitutionsData_df['squadId'] == squadId,]
                    squadSubstitutions.drop(squadSubstitutions[(squadSubstitutions['startingPos'] == 'S') & 
                                                               (squadSubstitutions['finishPos'] == 'S')].index,
                                            inplace = True)        
                    squadSubstitutions = squadSubstitutions.sort_values(by = 'startingTime')
                    
                    #Identify the starting line-up and append to dictionary
                    for courtPos in courtPositions:
                        #For some reason there are times where a court position isn't listed for a team
                        #Maybe they played without that position
                        #Nonetheless, need to check for this
                        if len(squadSubstitutions.loc[(squadSubstitutions['startingPos'] == courtPos) &
                                                      (squadSubstitutions['startingTime'] == 0),
                                                      ['playerId']]) == 0:
                            #Append a 'missing value
                            lineUpData[courtPos].append(-99999)
                        else:
                            lineUpData[courtPos].append(squadSubstitutions.loc[(squadSubstitutions['startingPos'] == courtPos) &
                                                                               (squadSubstitutions['startingTime'] == 0),
                                                                               ['playerId']].values[0][0])
                            
                    #Add additional details for starting line-up in dictionary
                    lineUpData['matchId'].append(data['matchInfo']['matchId'][0])
                    lineUpData['squadId'].append(squadId)
                    lineUpData['startingTime'].append(0)
                    
                    #Drop starting player/bench info from substitutions dataframe
                    #Drop any substitutions that aren't going on to the court (avoids double-ups)
                    squadSubstitutions.drop(squadSubstitutions[(squadSubstitutions['startingTime'] == 0) |
                                                               (squadSubstitutions['startingPos'] == 'S')].index,
                                            inplace = True)
                    
                    #Check if there were any substituions for the team
                    if len(squadSubstitutions) > 0:
                    
                        #Get unique substituion times
                        subTimes = list(squadSubstitutions['startingTime'].unique())
                        
                        #Append time and score details for starting lineup in accordance
                        #with first substitution time
                        lineUpData['finishTime'].append(subTimes[0])
                        lineUpData['teamStartScore'].append(0)
                        lineUpData['oppStartScore'].append(0)
                        
                        #Identify the score at the point of the first substitution and append
                        #Check to see if there has been a score yet
                        if subTimes[0] < scoreFlowData_df['matchSeconds'][0]:
                            #Just allocate zero scores
                            if homeSquad:
                                lineUpData['teamEndScore'].append(0)
                                lineUpData['oppEndScore'].append(0)
                            else:
                                lineUpData['teamEndScore'].append(0)
                                lineUpData['oppEndScore'].append(0)
                        else:
                            #Identify scores based on times
                            checkScoreInd = scoreFlowData_df.loc[scoreFlowData_df['matchSeconds'] > subTimes[0],
                                                                 ].index[0]-1
                            if homeSquad:
                                lineUpData['teamEndScore'].append(scoreFlowData_df['homeSquadScore'][checkScoreInd])
                                lineUpData['oppEndScore'].append(scoreFlowData_df['awaySquadScore'][checkScoreInd])
                            else:
                                lineUpData['teamEndScore'].append(scoreFlowData_df['awaySquadScore'][checkScoreInd])
                                lineUpData['oppEndScore'].append(scoreFlowData_df['homeSquadScore'][checkScoreInd])
                            
                        #Loop through substitution times and extract new position players
                        for subPoint in subTimes:
                            
                            #Extract the substitutions at the current point
                            currSubs = squadSubstitutions.loc[squadSubstitutions['startingTime'] == subPoint,]
                            
                            #Loop through and replace position if it has been changed
                            for courtPos in courtPositions:
                                
                                #Check if position has been subbed into
                                if len(currSubs.loc[currSubs['startingPos'] == courtPos, ]) > 0:
                                    #Identify the player subbed into the position and append
                                    lineUpData[courtPos].append(currSubs.loc[currSubs['startingPos'] == courtPos,
                                                                             ['playerId']].values[0][0])
                                    
                                else:
                                    #Use the existing player Id for this position
                                    lineUpData[courtPos].append(lineUpData[courtPos][-1])
                                    
                            #Append additional data for this line-up
                            lineUpData['matchId'].append(data['matchInfo']['matchId'][0])
                            lineUpData['squadId'].append(squadId)
                            lineUpData['startingTime'].append(subPoint)
                            
                            #Check if this is the last sub point and add final data accordingly
                            if subPoint == subTimes[-1]:
                                #Add finishing time
                                lineUpData['finishTime'].append(np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(len(data['periodInfo']['qtr']))]))
                                #Add starting scores from previous end scores
                                lineUpData['teamStartScore'].append(lineUpData['teamEndScore'][-1])
                                lineUpData['oppStartScore'].append(lineUpData['oppEndScore'][-1])
                                #Add end scores based on final score
                                if homeSquad:
                                    lineUpData['teamEndScore'].append(scoreFlowData_df['homeSquadScore'][len(scoreFlowData_df)-1])
                                    lineUpData['oppEndScore'].append(scoreFlowData_df['awaySquadScore'][len(scoreFlowData_df)-1])
                                else:
                                    lineUpData['teamEndScore'].append(scoreFlowData_df['awaySquadScore'][len(scoreFlowData_df)-1])
                                    lineUpData['oppEndScore'].append(scoreFlowData_df['homeSquadScore'][len(scoreFlowData_df)-1])
                            else:
                                #Add finishing time
                                lineUpData['finishTime'].append(subTimes[subTimes.index(subPoint)+1])
                                #Add starting scores from previous end scores
                                lineUpData['teamStartScore'].append(lineUpData['teamEndScore'][-1])
                                lineUpData['oppStartScore'].append(lineUpData['oppEndScore'][-1])
                                #Add end scores based on next substitution time
                                #Need to check if the score for the next index can be obtained
                                if len(scoreFlowData_df.loc[scoreFlowData_df['matchSeconds'] > subTimes[subTimes.index(subPoint)+1],]) > 0:
                                    checkScoreInd = scoreFlowData_df.loc[scoreFlowData_df['matchSeconds'] > subTimes[subTimes.index(subPoint)+1],
                                                                         ].index[0]-1
                                else:
                                    #Score to check is the final one
                                    checkScoreInd = len(scoreFlowData_df) - 1                                    
                                if homeSquad:
                                    lineUpData['teamEndScore'].append(scoreFlowData_df['homeSquadScore'][checkScoreInd])
                                    lineUpData['oppEndScore'].append(scoreFlowData_df['awaySquadScore'][checkScoreInd])
                                else:
                                    lineUpData['teamEndScore'].append(scoreFlowData_df['awaySquadScore'][checkScoreInd])
                                    lineUpData['oppEndScore'].append(scoreFlowData_df['homeSquadScore'][checkScoreInd])
                                  
                    else:
                        
                        #Only one line-up was used. Finishing time is sum of periods
                        #Append data to dictionary
                        lineUpData['finishTime'].append(np.sum([data['periodInfo']['qtr'][ii]['periodSeconds'][0] for ii in range(len(data['periodInfo']['qtr']))]))
                        lineUpData['teamStartScore'].append(0)
                        lineUpData['oppStartScore'].append(0)
                        if homeSquad:
                            lineUpData['teamEndScore'].append(scoreFlowData_df['homeSquadScore'][len(scoreFlowData_df)-1])
                            lineUpData['oppEndScore'].append(scoreFlowData_df['awaySquadScore'][len(scoreFlowData_df)-1])
                        else:
                            lineUpData['teamEndScore'].append(scoreFlowData_df['awaySquadScore'][len(scoreFlowData_df)-1])
                            lineUpData['oppEndScore'].append(scoreFlowData_df['homeSquadScore'][len(scoreFlowData_df)-1])
                            
                #Convert to dataframe
                lineUpData_df = pd.DataFrame.from_dict(lineUpData)
                        
                #Add a duration column
                lineUpData_df['duration'] = lineUpData_df['finishTime'] - lineUpData_df['startingTime']
                
                #Add a plus/minus column
                lineUpData_df['plusMinus'] = (lineUpData_df['teamEndScore'] - lineUpData_df['teamStartScore']) - \
                    (lineUpData_df['oppEndScore'] - lineUpData_df['oppStartScore'])
                    
                #Calculate plus minus per 60 minutes
                lineUpData_df['plusMinusPer60'] = lineUpData_df['plusMinus'] * (60 / (lineUpData_df['duration'] / 60))
                
                #Add opposition squad Id
                oppSquadId = []
                for squadId in lineUpData_df['squadId']:
                    if squadId == squadIdCheck[0]:
                        oppSquadId.append(squadIdCheck[1])
                    else:
                        oppSquadId.append(squadIdCheck[0])
                lineUpData_df['oppSquadId'] = oppSquadId
                
                #Export line-up data to file
                lineUpData_df.to_csv(matchFileDir+str(quickMatchId)+'_'+'lineUps_'+jsonFile.split('.')[0]+'.csv', index = False)
                
                # %% Collate player period statistics
                
                #Setup dictionary to extract data to
                playerPeriodStatsLong = {
                    'matchId': [],
                    'squadId': [],
                    'playerId': [],
                    'period': [],
                    'statistic': [],
                    'value': []
                    }
                
                #Loop through player entries
                for playerStatsInd in range(len(data['playerPeriodStats']['player'])):
                    #Loop through statistics
                    for statistic in list(data['playerPeriodStats']['player'][playerStatsInd].keys()):
                        #Check to not record squad Id, period, playerId, position codes
                        if statistic != 'squadId' and statistic != 'period' and statistic != 'currentPositionCode' and \
                            statistic != 'playerId' and statistic != 'startingPositionCode' and statistic != 'minutes':
                            #Record values
                            playerPeriodStatsLong['matchId'].append(data['matchInfo']['matchId'][0])
                            playerPeriodStatsLong['squadId'].append(data['playerPeriodStats']['player'][playerStatsInd]['squadId'][0])
                            playerPeriodStatsLong['playerId'].append(data['playerPeriodStats']['player'][playerStatsInd]['playerId'][0])
                            playerPeriodStatsLong['period'].append(data['playerPeriodStats']['player'][playerStatsInd]['period'][0])
                            playerPeriodStatsLong['statistic'].append(statistic)
                            playerPeriodStatsLong['value'].append(data['playerPeriodStats']['player'][playerStatsInd][statistic][0])
                            
                #Convert to dataframe
                playerPeriodStatsLong_df = pd.DataFrame.from_dict(playerPeriodStatsLong)
                
                #Add opposition squad Id
                oppSquadId = []
                for squadId in playerPeriodStatsLong_df['squadId']:
                    if squadId == squadIdCheck[0]:
                        oppSquadId.append(squadIdCheck[1])
                    else:
                        oppSquadId.append(squadIdCheck[0])
                playerPeriodStatsLong_df['oppSquadId'] = oppSquadId
                
                #Convert to wide dataframe
                playerPeriodStatsWide_df = playerPeriodStatsLong_df.pivot(index = ['matchId', 'squadId', 'oppSquadId', 'playerId', 'period'],
                                                                          columns = 'statistic',
                                                                          values = 'value').reset_index()
                
                #Weird cases where there are extra periods that don't have stats need
                #to be checked for
                #Get the periods included in the match
                matchPeriods = [data['periodInfo']['qtr'][ii]['period'][0] for ii in range(len(data['periodInfo']['qtr']))]
                #Extract just to the data from match periods
                playerPeriodStatsWide_df = playerPeriodStatsWide_df.loc[playerPeriodStatsWide_df['period'].isin(matchPeriods),
                                                                        ].reset_index(drop = True)
                
                #Export player period stats data to file
                playerPeriodStatsWide_df.to_csv(matchFileDir+str(quickMatchId)+'_'+'playerPeriodStats_'+jsonFile.split('.')[0]+'.csv', index = False)
                
                # %% Collate player statistics
                
                #Setup dictionary to extract data to
                playerStatsLong = {
                    'matchId': [],
                    'squadId': [],
                    'playerId': [],
                    'statistic': [],
                    'value': []
                    }
                
                #Loop through player entries
                for playerStatsInd in range(len(data['playerStats']['player'])):
                    #Loop through statistics
                    for statistic in list(data['playerStats']['player'][playerStatsInd].keys()):
                        #Check to not record squad Id, period, playerId, position codes
                        if statistic != 'squadId' and statistic != 'period' and statistic != 'currentPositionCode' and \
                            statistic != 'playerId' and statistic != 'startingPositionCode' and statistic != 'minutes':
                            #Record values
                            playerStatsLong['matchId'].append(data['matchInfo']['matchId'][0])
                            playerStatsLong['squadId'].append(data['playerStats']['player'][playerStatsInd]['squadId'][0])
                            playerStatsLong['playerId'].append(data['playerStats']['player'][playerStatsInd]['playerId'][0])
                            playerStatsLong['statistic'].append(statistic)
                            playerStatsLong['value'].append(data['playerStats']['player'][playerStatsInd][statistic][0])
                            
                #Convert to dataframe
                playerStatsLong_df = pd.DataFrame.from_dict(playerStatsLong)
                
                #Add opposition squad Id
                oppSquadId = []
                for squadId in playerStatsLong_df['squadId']:
                    if squadId == squadIdCheck[0]:
                        oppSquadId.append(squadIdCheck[1])
                    else:
                        oppSquadId.append(squadIdCheck[0])
                playerStatsLong_df['oppSquadId'] = oppSquadId
                
                #Convert to wide dataframe
                playerStatsWide_df = playerStatsLong_df.pivot(index = ['matchId', 'squadId', 'oppSquadId', 'playerId'],
                                                              columns = 'statistic',
                                                              values = 'value').reset_index()
                
                #Calculate per 60 mins stats
                #Get unique statistical categories
                statCategories = pd.Series(playerStatsLong['statistic']).unique()
                #Add the players minutes to the dataframe
                playerMins = []
                for playerId in playerStatsWide_df['playerId']:
                    playerMins.append(minutesPlayedData_df.loc[minutesPlayedData_df['playerId'] == playerId,
                                                               ['minutesPlayed']].values[0][0])
                playerStatsWide_df['minutesPlayed'] = playerMins
                #Loop through the stats categories and calculate new per60 columns
                for currStat in statCategories:
                    #Create new column name
                    newStatName = currStat+'Per60'
                    #Calculate values
                    playerStatsWide_df[newStatName] = playerStatsWide_df[currStat] * (60 / playerStatsWide_df['minutesPlayed'])
                    
                #Calculate player plus/minus while on court
                plusMinus = []
                for playerId in playerStatsWide_df['playerId']:
                    #First check if player played
                    if minutesPlayedData_df.loc[minutesPlayedData_df['playerId'] == playerId,
                                                ['minutesPlayed']].values[0][0] > 0:
                        #Extract the players substitutions data when on court
                        playerSubs = substitutionsData_df.loc[(substitutionsData_df['playerId'] == playerId) &
                                                              (substitutionsData_df['startingPos'].isin(courtPositions)),
                                                              ].reset_index(drop = True)
                        #Loop through and calculate the score differential while player is on court
                        #Check for home squad first
                        if playerSubs['squadId'].unique()[0] == data['matchInfo']['homeSquadId'][0]:
                            homeSquad = True
                        else:
                            homeSquad = False 
                        #Loop through times on court
                        playerPlusMinus = []
                        for subInd in range(len(playerSubs)):
                            #Find start and finish score check points
                            #Start scores
                            if playerSubs['startingTime'][subInd] == 0:
                                #Allocate starting scores as zero
                                teamStartScore = 0
                                oppStartScore = 0
                            else:
                                if len(scoreFlowData_df.loc[scoreFlowData_df['matchSeconds'] > playerSubs['startingTime'][subInd],]) == 0:
                                    scoreCheckStart = len(scoreFlowData_df) - 1
                                    #Identify score based on index
                                    if homeSquad:
                                        teamStartScore = scoreFlowData_df['homeSquadScore'][scoreCheckStart]
                                        oppStartScore = scoreFlowData_df['awaySquadScore'][scoreCheckStart]
                                    else:
                                        teamStartScore = scoreFlowData_df['awaySquadScore'][scoreCheckStart]
                                        oppStartScore = scoreFlowData_df['homeSquadScore'][scoreCheckStart]
                                else:
                                    #Check if sub start is before a score
                                    if playerSubs['startingTime'][subInd] < scoreFlowData_df['matchSeconds'][0]:
                                        teamStartScore =  0
                                        oppStartScore = 0
                                    else:
                                        scoreCheckStart = scoreFlowData_df.loc[scoreFlowData_df['matchSeconds'] > playerSubs['startingTime'][subInd],
                                                                               ].index[0] - 1
                                        #Identify score based on index
                                        if homeSquad:
                                            teamStartScore = scoreFlowData_df['homeSquadScore'][scoreCheckStart]
                                            oppStartScore = scoreFlowData_df['awaySquadScore'][scoreCheckStart]
                                        else:
                                            teamStartScore = scoreFlowData_df['awaySquadScore'][scoreCheckStart]
                                            oppStartScore = scoreFlowData_df['homeSquadScore'][scoreCheckStart]
                            #End scores
                            if len(scoreFlowData_df.loc[scoreFlowData_df['matchSeconds'] > playerSubs['finishTime'][subInd],]) == 0:
                                scoreCheckEnd = len(scoreFlowData_df) - 1
                                #Allocate based on index
                                if homeSquad:
                                    teamEndScore = scoreFlowData_df['homeSquadScore'][scoreCheckEnd]
                                    oppEndScore = scoreFlowData_df['awaySquadScore'][scoreCheckEnd]
                                else:
                                    teamEndScore = scoreFlowData_df['awaySquadScore'][scoreCheckEnd]
                                    oppEndScore = scoreFlowData_df['homeSquadScore'][scoreCheckEnd]
                            else:
                                #Check if end is actually before a score
                                if playerSubs['finishTime'][subInd] < scoreFlowData_df['matchSeconds'][0]:
                                    teamEndScore = 0
                                    oppEndScore = 0
                                else:
                                    scoreCheckEnd = scoreFlowData_df.loc[scoreFlowData_df['matchSeconds'] > playerSubs['finishTime'][subInd],
                                                                         ].index[0] - 1
                                    #Allocate based on index
                                    if homeSquad:
                                        teamEndScore = scoreFlowData_df['homeSquadScore'][scoreCheckEnd]
                                        oppEndScore = scoreFlowData_df['awaySquadScore'][scoreCheckEnd]
                                    else:
                                        teamEndScore = scoreFlowData_df['awaySquadScore'][scoreCheckEnd]
                                        oppEndScore = scoreFlowData_df['homeSquadScore'][scoreCheckEnd]
                            #Calculate current iterations plus/minus
                            playerPlusMinus.append((teamEndScore - teamStartScore) - (oppEndScore - oppStartScore))
                        #Append sum to overall list
                        plusMinus.append(np.sum(playerPlusMinus))
                        
                    else:
                        
                        #Allocate a nan to the plus/minus
                        plusMinus.append(np.nan)
                        
                #Add to dataframe
                playerStatsWide_df['plusMinus'] = plusMinus
                
                #Calculate plus minus per 60 mins played
                playerStatsWide_df['plusMinusPer60'] = playerStatsWide_df['plusMinus'] * (60 / playerStatsWide_df['minutesPlayed'])
                
                #Export player stats data to file
                playerStatsWide_df.to_csv(matchFileDir+str(quickMatchId)+'_'+'playerStats_'+jsonFile.split('.')[0]+'.csv', index = False)
            
            # %% Print confirmation
            
            #Display that current game has been processed
            print(f'{jsonFile.split(".")[0]} Complete! {jsonFileList.index(jsonFile)+1} of {len(jsonFileList)} total files complete!')

# %% ----- End of matchCentre_processMatches.py -----