# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Set of functions to assist in collating match centre datasets
    
"""

# %% Import packages

import pandas as pd
import os
from glob import glob

# %% Set-up

"""

TODO: currently only have ANZC & SSN squad Id's--- need international, mens, pathway etc.

"""

#Create dictionary to map squad names to ID's
squadDict = {804: 'Vixens',
             806: 'Swifts',
             807: 'Firebirds',
             8117: 'Lightning',
             810: 'Fever',
             8119: 'Magpies',
             801: 'Thunderbirds',
             8118: 'GIANTS',
             9698: 'Mavericks',
             809:'Magic',
             805: 'Mystics',
             803: 'Pulse',
             808: 'Steel',
             802: 'Tactix'}

# %% Function to get seasonal stats

def getSeasonStats(baseDir = None,
                   years = 'all',
                   fileStem = None,
                   matchOptions = 'all',
                   joined = False,
                   addSquadNames = False):

    """
    Function gets the desired years of relevant stats and compiles into dictionary
    
    Inputs:
        > baseDir - the directory folder that stores all the processed data folders in (str). No trailling slashes at end.
        > years - the desired years to collate into dictionary. Defaults to 'all' if note provided (list of int)
        > fileStem - the file type name to grab (e.g. 'teamStats') [***TODO: ADD OPTIONS***]
        > matchOptions - list of available types (i.e. 'regular', 'final', 'preseason') [***TODO: NEED TO FIX PRESEASON TYPO***]
        > joined - when False provides output with year as key in dictionary; when True provides output as singular dataframe
        > addSquadNames - when True adds squad name labels to dataset
        
    Outputs:
        > data - dictionary with nested dataframes of data year to year
    
    """
    
    #Get starting directory to return to
    homeDir = os.getcwd()
    
    #Check for baseDir input which is needed
    if baseDir is None:
        raise ValueError('The base directory where processed data folders are stored is required.')
    
    #Check for stat type input
    if fileStem is None:
        raise ValueError('The string of the stat type file is required.')
    
    #Navigate to base directory
    try:
        os.chdir(baseDir)
    except:
        raise ValueError('The base directory provided does not appear to exist.')
        
    #Return back to home directory
    os.chdir(homeDir)
    
    #Set a dictionary to identify regular, finals and TGC competition Id's
    compIdCheck = {
        'regular': [8005, 8012, 8018, 8028, 8035, 9084, 9563, 9818, 
                    10083, 10393, 10724, 11108, 11391, 11665, 12045, 12438],
        'final': [8006, 8013, 8019, 8029, 8036, 9085, 9564, 9819,
                  10084, 10394, 10725, 11109, 11392, 11666, 12046, 12439],
        'preseason': [11706, 11707, 11708, 12125, 12205, 12126],
        'pathway': [11915],
        'pathway final': [11916],
        'international': [9315, 9355, 9663, 9644, 9843, 9953, 9973,
                          10200, 10293, 10294, 10423, 10564, 10565, 10734, 10985, 11315,
                          11695, 11946],
        'international mens': [11995]
        }
    
    #Check for years input and specify all years if not listed
    if years == 'all':
        
        #Grab the years from all folders in the directory
        allFolders = glob(baseDir+'\\*\\', recursive = True)
        
        #Grab the years in each folder
        allYears = [int(folder.split('_')[1]) for folder in allFolders] 
        
        #Get unique values
        years = list(set(allYears))
        
    #Sort years numerically    
    years.sort()
    
    #Loop through years and stash in dictionaries
    #These need to be kept separately as they have different stats
    #They can be manipulated later on after extracting
    
    #Create dictionary to store dataframes in
    data = {}
    
    #Loop through years
    for year in years:
        
        #Get all folders from current year
        yearFolders = glob(baseDir+'\\*_'+str(year)+'_*\\', recursive = True)
        
        #Create list of team stats files based on folder specifications
        fileList = [folder+folder.split('_')[0].split('\\')[-1]+'_'+fileStem+folder.split(folder.split('_')[0])[1].replace('\\','.csv') for folder in yearFolders]
        
        #Loop through folders and extract team stats data
        data[year] = pd.concat(pd.read_csv(file) for file in fileList)
        
        #Reset the indices in concatenated dataframe
        data[year].reset_index(drop = True, inplace = True)
        
        #Create a column that specifies regular season, finals or preseason
        #Specify round and game too
        #Do competition type too
        matchType = []
        roundNo = []
        gameNo = []
        compType= []
        for matchId in data[year]['matchId']:
            
            #Get the comp Id by removing the final 4 ints from the Id
            compId = int(str(matchId)[0:-4])
            #Check for presence iteratively in list
            if compId in compIdCheck['regular']:
                matchType.append('regular')
            elif compId in compIdCheck['final']:
                matchType.append('final')
            elif compId in compIdCheck['preseason']:
                matchType.append('preseason')
            elif compId in compIdCheck['pathway']:
                matchType.append('pathway')
            elif compId in compIdCheck['pathway final']:
                matchType.append('pathway final')
            elif compId in compIdCheck['international']:
                matchType.append('international')
            elif compId in compIdCheck['international mens']:
                matchType.append('international mens')
            else:
                raise ValueError('Unable to identify competition Id and type in file.')
                
            #Get the round and game number by extracting the final 4 digits
            roundGameId = str(matchId)[-4:]
            roundNo.append(int(roundGameId[0:2]))
            gameNo.append(int(roundGameId[-2:]))
            
            #Identify where the match Id is in the file list
            checkFile = [str(matchId) in file for file in fileList]
            #Get the index of the selected file
            fileInd = [ii for ii, xx in enumerate(checkFile) if xx][0]
            #Extract and append the competition from this file
            compType.append(fileList[fileInd].split('\\')[-2].split('_')[2])
            
        #Append to dataframe
        data[year]['matchType'] = matchType
        data[year]['roundNo'] = roundNo
        data[year]['gameNo'] = gameNo
        data[year]['compType'] = compType
        
        #Select match types
        if matchOptions != 'all':
            
            #Grab the requested match types from list
            data[year] = data[year].loc[data[year]['matchType'].isin(matchOptions), ]
            
        #Check for adding squad names
        if addSquadNames:
            
            #Try to add squad Id's
            #Raise error if can't be found
            try:
                #Add in squad Id. This is relevant to all dataset
                data[year]['squadName'] = [squadDict[squadId] for squadId in data[year]['squadId']]
                #Check for opposition squad Id as this isn't in every dataset
                if 'oppSquadId' in list(data[year].columns):
                    data[year]['oppSquadName'] = [squadDict[oppSquadId] for oppSquadId in data[year]['oppSquadId']]
            except:
                raise ValueError('Not all squad IDs in dataset can be found...')
            
    #Check for joined output
    if joined:
        
        #Add year column to dataframes to identify
        for year in data.keys():
            data[year]['year'] = [year] * len(data[year])
        
        #Concatenate to singular dataframe
        data_all = pd.concat([data[year] for year in data.keys()]).reset_index(drop = True)
        
    # #Return to home directory
    # os.chdir(homeDir)
    
    #Return the extracted data from function
    if joined:
        return data_all
    else:
        return data

# %%% ----- End of collatestats.py -----