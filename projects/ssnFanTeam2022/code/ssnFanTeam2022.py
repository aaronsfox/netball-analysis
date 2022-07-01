# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to analyse and create visual for the SSN Fan Team of 2022
    
    Winner for each:
        GS - Fowler
        GA - Bueta
        WA - Watson
        C - Proud
        WD - Parmenter
        GD - Weston
        GK - Sterling
    
"""

# %% Import packages

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib import gridspec
from matplotlib.patches import Circle
import os
import numpy as np
from PIL import Image

# %% Set-up

#Set reveal dictionary
reveal = {'GS': True,
          'GA': True,
          'WA': True,
          'C': True,
          'WD': True,
          'GD': True,
          'GK': True}

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

#Colour settings for teams
colourDict = {'Fever': '#00953b',
              'Firebirds': '#4b2c69',
              'GIANTS': '#f57921',
              'Lightning': '#fdb61c',
              'Magpies': '#494b4a',
              'Swifts': '#ee3124',
              'Thunderbirds': '#e54078',
              'Vixens': '#00a68e'}

#Set matplotlib parameters
#Note that these will probably be manually manipulated later anyway
from matplotlib import rcParams
# rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Arial'
rcParams['font.weight'] = 'bold'
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 16
rcParams['axes.linewidth'] = 1.5
rcParams['axes.labelweight'] = 'bold'
rcParams['legend.fontsize'] = 10
rcParams['xtick.major.width'] = 1.5
rcParams['ytick.major.width'] = 1.5
rcParams['legend.framealpha'] = 0.0
rcParams['savefig.dpi'] = 300
rcParams['savefig.format'] = 'pdf'

#Add custom fonts for use with matplotlib
#Navigate to directory
os.chdir('..\\fonts\\')
#Add fonts
for font in font_manager.findSystemFonts(os.getcwd()):
    font_manager.fontManager.addfont(font)
#Return to base directory
os.chdir('..\\code\\')
    
#Set-up court positions variable
courtPositions = ['GS','GA','WA','C','WD','GD','GK']

#Read in data
voteData = pd.read_csv('..\\data\\fanVotes.csv')

#Read in position lists
#Create dictionary to store in for each position
playerLists = {courtPos: [] for courtPos in courtPositions}
#Loop through positions
for courtPos in courtPositions:
    with open(f'..\\lists\\eligiblePlayers_{courtPos}.txt') as f:
        playerLists[courtPos] = f.read().splitlines()
        
#Create a player list to match up squads to
#Read in data
allPlayers = collatestats.getSeasonStats(baseDir = baseDir,
                                         years = [2022],
                                         fileStem = 'playerList',
                                         matchOptions = ['regular'])
allPlayers = allPlayers[2022]

# %% Analyse vote data

#Sum data to create total votes
totalVotes = voteData.sum(axis = 0).reset_index(drop = False)

#Rename columns for ease of use
totalVotes.rename(columns = {'index': 'playerLabel', 0: 'votes'}, inplace = True)

#Match up player name from lists to create a name variable
#Also create position & squad variables
playerName = []
position = []
squad = []
nBest = []
for playerLabel in totalVotes['playerLabel']:
    #Get position
    pos = playerLabel.split('_')[0]
    #Get player index (subtract one to match up with Python indexing)
    ind = int(playerLabel.split('_')[1]) - 1
    #Extract player name 
    name = playerLists[pos][ind]
    #Identify squad Id from all player list
    squadId = allPlayers.loc[(allPlayers['firstname'] == name.split(' ')[0]) &
                             (allPlayers['surname'] == name.split(' ')[1]),
                             ]['squadId'].unique()[0]
    #Identify number of best votes allocated to player
    bestFreq = np.count_nonzero(voteData[playerLabel].to_numpy() == 3)    
    #Append data to lists
    playerName.append(name)
    position.append(pos)
    squad.append(squadId)
    nBest.append(bestFreq)
#Append to dataframe
totalVotes['playerName'] = playerName
totalVotes['position'] = position
totalVotes['squad'] = squad
totalVotes['nBest'] = nBest

#Replace squad Id with name
totalVotes['squad'].replace(squadDict, inplace = True)

#Get max votes value for sharing data axes
maxVotes = totalVotes['votes'].max()

#Get max votes to nearest hundred for rounding
voteAxLim = maxVotes
voteAxTickLim = int(np.floor(maxVotes/100)*100)

# %% Create visual

#Set-up figure
fig = plt.figure(figsize = (12, 8))

#Create the desired grid for axes to work with

#Set grid size for axes
gridSpec = gridspec.GridSpec(3, 6)

#Update spacing of grid
gridSpec.update(left = 0.02, right = 0.98,
                bottom = 0.08, top = 0.83, 
                wspace = 0.05, hspace = 0.2)

#Set figure colouring
fig.patch.set_facecolor('#D5D8DC')

# %% Add figure annotations

#Add title
fig.text(0.5, 0.95,
         'SSN 2022 FAN TEAM',
         font = "Charlie don't surf!", fontsize = 40,
         ha = 'center', va = 'center')

#Add descriptive text
#Voting
fig.text(0.5, 0.9,
         'Fans used a 3-2-1 voting system to select their favourites for the year across each position.',
         font = "Arial", fontsize = 12,
         ha = 'center', va = 'center')
#Eligibility
fig.text(0.5, 0.875,
         'Players were eligible at a position if they played one-third of total season minutes and one-third of their minutes at the given position.',
         font = "Arial", fontsize = 12,
         ha = 'center', va = 'center')

# %% Goal shooter

#Create axes
gsImg = plt.subplot(gridSpec.new_subplotspec((0,1), colspan = 1, rowspan = 1))
gsDat = plt.subplot(gridSpec.new_subplotspec((0,2), colspan = 1, rowspan = 1))

#Plot data

#Set court position
courtPos = 'GS'
    
#Extract data for current court position
currPosData = totalVotes.loc[totalVotes['position'] == courtPos,]

#Sort by votes and reset index
sortedVotes = currPosData.sort_values(by = 'votes',
                                      ascending = False).reset_index(drop = True)

#Extract the top 5 data into variables
votes = sortedVotes.iloc[0:5]['votes'].to_numpy()
names = sortedVotes.iloc[0:5]['playerName'].to_list()
squads = sortedVotes.iloc[0:5]['squad'].to_list()
bests = sortedVotes.iloc[0:5]['nBest'].to_numpy()

#Plot data
if reveal['GS']:

    #Plot image of top vote getter
    #Get name
    posWinnerName = names[0].split(' ')[-1]
    #Read image
    playerImg = Image.open(f'..\\images\\{posWinnerName}.png')
    #Get axes positioning in figure coordinates
    x0,y0 = gsImg.transData.transform((0.5,0))
    x1,y1 = gsImg.transData.transform((1,1))
    #Get scaling offset based on image height
    scaleOffset = (y1-y0) / playerImg.size[1]
    #Resize the image
    playerImgResize = playerImg.resize((int(playerImg.size[0]*scaleOffset),
                                        int(playerImg.size[1]*scaleOffset)))
    #Plot image on figure at appropriate axes location
    fImg = gsImg.figure.figimage(playerImgResize,
                                 x0 - playerImgResize.size[0]/2,
                                 y0)
    fImg.set_zorder(0)
    
    #Add line to bottom of image
    gsImg.axhline(y = 0, ls = '-', lw = 2, c = colourDict[squads[0]], clip_on = False)
    
    #Set image label
    gsImg.text(0.5, -0.1, names[0],
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = colourDict[squads[0]],
               clip_on = False)
    
    #Map squad colours against dictionary
    barColours = [colourDict[ii] for ii in squads]
    
    #Plot data
    gsDat.barh(np.linspace(5,1,5),
               votes,
               color = barColours,
               height = 0.4)
    
    #Set limits
    gsDat.set_xlim([0,voteAxLim])
    gsDat.set_ylim([0.2,5.5])
    
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = gsDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        gsDat.text(0,
                   barPatch.get_y()-0.05,
                   playerText,
                   color = barColours[names.index(playerName)],
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        gsDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
    
else:
    
    #Plot question mark
    qCircle = plt.Circle((0.5, 0.5), 0.49,
                         facecolor = 'black', edgecolor = 'black',
                         clip_on = False)
    gsImg.add_patch(qCircle)
    gsImg.text(0.5, 0.5, '?',
               fontsize = 80, fontname = "Charlie don't surf!",
               va = 'center', ha = 'center', color = 'white',
               clip_on = False)
    
    #Add line to bottom of image
    gsImg.axhline(y = 0, ls = '-', lw = 2, c = 'black', clip_on = False)
    
    #Set image label
    gsImg.text(0.5, -0.1, 'Goal Shooter',
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = 'black',
               clip_on = False)
    
    #Plot data
    gsDat.barh(np.linspace(5,1,5),
               votes,
               color = 'black',
               height = 0.4)
    
    #Set limits
    gsDat.set_ylim([0.2,5.5])
        
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = gsDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        gsDat.text(0,
                   barPatch.get_y()-0.05,
                   '???',
                   color = 'black',
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        gsDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
        
#Set axis ordering above figure
gsImg.set_zorder(1)

#Turn off axis lines
gsImg.axis('off')
        
#Turn off axis borders
gsDat.spines['left'].set_visible(False)
gsDat.spines['top'].set_visible(False)
gsDat.spines['right'].set_visible(False)

#Turn off y-ticks
gsDat.set_yticks([])

#Set x-ticks & parameters
gsDat.set_xticks(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int))
gsDat.set_xticklabels(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int),
                      fontsize = 7)
gsDat.set_xlim([0,voteAxLim])
gsDat.spines['bottom'].set_color('#808B96')
gsDat.tick_params(axis = 'x', colors = '#808B96')

#Set axis label
gsDat.set_xlabel('Total Votes', fontsize = 7, color = '#808B96')

#Set axis face colour
gsDat.set_facecolor('#D5D8DC')

# %% Goal attack

#Create axes
gaImg = plt.subplot(gridSpec.new_subplotspec((0,3), colspan = 1, rowspan = 1))
gaDat = plt.subplot(gridSpec.new_subplotspec((0,4), colspan = 1, rowspan = 1))

#Plot data

#Set court position
courtPos = 'GA'
    
#Extract data for current court position
currPosData = totalVotes.loc[totalVotes['position'] == courtPos,]

#Sort by votes and reset index
sortedVotes = currPosData.sort_values(by = 'votes',
                                      ascending = False).reset_index(drop = True)

#Extract the top 5 data into variables
votes = sortedVotes.iloc[0:5]['votes'].to_numpy()
names = sortedVotes.iloc[0:5]['playerName'].to_list()
squads = sortedVotes.iloc[0:5]['squad'].to_list()
bests = sortedVotes.iloc[0:5]['nBest'].to_numpy()

#Plot data
if reveal['GA']:

    #Plot image of top vote getter
    #Get name
    posWinnerName = names[0].split(' ')[-1]
    #Read image
    playerImg = Image.open(f'..\\images\\{posWinnerName}.png')
    #Get axes positioning in figure coordinates
    x0,y0 = gaImg.transData.transform((0.5,0))
    x1,y1 = gaImg.transData.transform((1,1))
    #Get scaling offset based on image height
    scaleOffset = (y1-y0) / playerImg.size[1]
    #Resize the image
    playerImgResize = playerImg.resize((int(playerImg.size[0]*scaleOffset),
                                        int(playerImg.size[1]*scaleOffset)))
    #Plot image on figure at appropriate axes location
    fImg = gaImg.figure.figimage(playerImgResize,
                                 x0 - playerImgResize.size[0]/2,
                                 y0)
    fImg.set_zorder(0)
    
    #Add line to bottom of image
    gaImg.axhline(y = 0, ls = '-', lw = 2, c = colourDict[squads[0]], clip_on = False)
    
    #Set image label
    gaImg.text(0.5, -0.1, names[0],
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = colourDict[squads[0]],
               clip_on = False)
    
    #Map squad colours against dictionary
    barColours = [colourDict[ii] for ii in squads]
    
    #Plot data
    gaDat.barh(np.linspace(5,1,5),
               votes,
               color = barColours,
               height = 0.4)
    
    #Set limits
    gaDat.set_xlim([0,voteAxLim])
    gaDat.set_ylim([0.2,5.5])
    
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = gaDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        gaDat.text(0,
                   barPatch.get_y()-0.05,
                   playerText,
                   color = barColours[names.index(playerName)],
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        gaDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
    
else:
    
    #Plot question mark
    qCircle = plt.Circle((0.5, 0.5), 0.49,
                         facecolor = 'black', edgecolor = 'black',
                         clip_on = False)
    gaImg.add_patch(qCircle)
    gaImg.text(0.5, 0.5, '?',
               fontsize = 80, fontname = "Charlie don't surf!",
               va = 'center', ha = 'center', color = 'white',
               clip_on = False)
    
    #Add line to bottom of image
    gaImg.axhline(y = 0, ls = '-', lw = 2, c = 'black', clip_on = False)
    
    #Set image label
    gaImg.text(0.5, -0.1, 'Goal Attack',
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = 'black',
               clip_on = False)
    
    #Plot data
    gaDat.barh(np.linspace(5,1,5),
               votes,
               color = 'black',
               height = 0.4)
    
    #Set limits
    gaDat.set_ylim([0.2,5.5])
        
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = gaDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        gaDat.text(0,
                   barPatch.get_y()-0.05,
                   '???',
                   color = 'black',
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        gaDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
        
#Set axis ordering above figure
gaImg.set_zorder(1)

#Turn off axis lines
gaImg.axis('off')
        
#Turn off axis borders
gaDat.spines['left'].set_visible(False)
gaDat.spines['top'].set_visible(False)
gaDat.spines['right'].set_visible(False)

#Turn off y-ticks
gaDat.set_yticks([])

#Set x-ticks & parameters
gaDat.set_xticks(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int))
gaDat.set_xticklabels(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int),
                      fontsize = 7)
gaDat.set_xlim([0,voteAxLim])
gaDat.spines['bottom'].set_color('#808B96')
gaDat.tick_params(axis = 'x', colors = '#808B96')

#Set axis label
gaDat.set_xlabel('Total Votes', fontsize = 7, color = '#808B96')

#Set axis face colour
gaDat.set_facecolor('#D5D8DC')

# %% Wing attack

#Create axes
waImg = plt.subplot(gridSpec.new_subplotspec((1,0), colspan = 1, rowspan = 1))
waDat = plt.subplot(gridSpec.new_subplotspec((1,1), colspan = 1, rowspan = 1))

#Set court position
courtPos = 'WA'
    
#Extract data for current court position
currPosData = totalVotes.loc[totalVotes['position'] == courtPos,]

#Sort by votes and reset index
sortedVotes = currPosData.sort_values(by = 'votes',
                                      ascending = False).reset_index(drop = True)

#Extract the top 5 data into variables
votes = sortedVotes.iloc[0:5]['votes'].to_numpy()
names = sortedVotes.iloc[0:5]['playerName'].to_list()
squads = sortedVotes.iloc[0:5]['squad'].to_list()
bests = sortedVotes.iloc[0:5]['nBest'].to_numpy()

#Plot data
if reveal['WA']:

    #Plot image of top vote getter
    #Get name
    posWinnerName = names[0].split(' ')[-1]
    #Read image
    playerImg = Image.open(f'..\\images\\{posWinnerName}.png')
    #Get axes positioning in figure coordinates
    x0,y0 = waImg.transData.transform((0.5,0))
    x1,y1 = waImg.transData.transform((1,1))
    #Get scaling offset based on image height
    scaleOffset = (y1-y0) / playerImg.size[1]
    #Resize the image
    playerImgResize = playerImg.resize((int(playerImg.size[0]*scaleOffset),
                                        int(playerImg.size[1]*scaleOffset)))
    #Plot image on figure at appropriate axes location
    fImg = waImg.figure.figimage(playerImgResize,
                                 x0 - playerImgResize.size[0]/2,
                                 y0)
    fImg.set_zorder(0)
    
    #Add line to bottom of image
    waImg.axhline(y = 0, ls = '-', lw = 2, c = colourDict[squads[0]], clip_on = False)
    
    #Set image label
    waImg.text(0.5, -0.1, names[0],
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = colourDict[squads[0]],
               clip_on = False)
    
    #Map squad colours against dictionary
    barColours = [colourDict[ii] for ii in squads]
    
    #Plot data
    waDat.barh(np.linspace(5,1,5),
               votes,
               color = barColours,
               height = 0.4)
    
    #Set limits
    waDat.set_xlim([0,voteAxLim])
    waDat.set_ylim([0.2,5.5])
    
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = waDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        waDat.text(0,
                   barPatch.get_y()-0.05,
                   playerText,
                   color = barColours[names.index(playerName)],
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        waDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
    
else:
    
    #Plot question mark
    qCircle = plt.Circle((0.5, 0.5), 0.49,
                         facecolor = 'black', edgecolor = 'black',
                         clip_on = False)
    waImg.add_patch(qCircle)
    waImg.text(0.5, 0.5, '?',
               fontsize = 80, fontname = "Charlie don't surf!",
               va = 'center', ha = 'center', color = 'white',
               clip_on = False)
    
    #Add line to bottom of image
    waImg.axhline(y = 0, ls = '-', lw = 2, c = 'black', clip_on = False)
    
    #Set image label
    waImg.text(0.5, -0.1, 'Wing Attack',
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = 'black',
               clip_on = False)
    
    #Plot data
    waDat.barh(np.linspace(5,1,5),
               votes,
               color = 'black',
               height = 0.4)
    
    #Set limits
    waDat.set_ylim([0.2,5.5])

    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = waDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        waDat.text(0,
                   barPatch.get_y()-0.05,
                   '???',
                   color = 'black',
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        waDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
        
#Set axis ordering above figure
waImg.set_zorder(1)

#Turn off axis lines
waImg.axis('off')
        
#Turn off axis borders
waDat.spines['left'].set_visible(False)
waDat.spines['top'].set_visible(False)
waDat.spines['right'].set_visible(False)

#Turn off y-ticks
waDat.set_yticks([])

#Set x-ticks & parameters
waDat.set_xticks(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int))
waDat.set_xticklabels(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int),
                      fontsize = 7)
waDat.set_xlim([0,voteAxLim])
waDat.spines['bottom'].set_color('#808B96')
waDat.tick_params(axis = 'x', colors = '#808B96')

#Set axis label
waDat.set_xlabel('Total Votes', fontsize = 7, color = '#808B96')

#Set axis face colour
waDat.set_facecolor('#D5D8DC')

# %% Centre

#Create axes
cImg = plt.subplot(gridSpec.new_subplotspec((1,2), colspan = 1, rowspan = 1))
cDat = plt.subplot(gridSpec.new_subplotspec((1,3), colspan = 1, rowspan = 1))

#Set court position
courtPos = 'C'
    
#Extract data for current court position
currPosData = totalVotes.loc[totalVotes['position'] == courtPos,]

#Sort by votes and reset index
sortedVotes = currPosData.sort_values(by = 'votes',
                                      ascending = False).reset_index(drop = True)

#Extract the top 5 data into variables
votes = sortedVotes.iloc[0:5]['votes'].to_numpy()
names = sortedVotes.iloc[0:5]['playerName'].to_list()
squads = sortedVotes.iloc[0:5]['squad'].to_list()
bests = sortedVotes.iloc[0:5]['nBest'].to_numpy()

#Plot data
if reveal['C']:

    #Plot image of top vote getter
    #Get name
    posWinnerName = names[0].split(' ')[-1]
    #Read image
    playerImg = Image.open(f'..\\images\\{posWinnerName}.png')
    #Get axes positioning in figure coordinates
    x0,y0 = cImg.transData.transform((0.5,0))
    x1,y1 = cImg.transData.transform((1,1))
    #Get scaling offset based on image height
    scaleOffset = (y1-y0) / playerImg.size[1]
    #Resize the image
    playerImgResize = playerImg.resize((int(playerImg.size[0]*scaleOffset),
                                        int(playerImg.size[1]*scaleOffset)))
    #Plot image on figure at appropriate axes location
    fImg = cImg.figure.figimage(playerImgResize,
                                 x0 - playerImgResize.size[0]/2,
                                 y0)
    fImg.set_zorder(0)
    
    #Add line to bottom of image
    cImg.axhline(y = 0, ls = '-', lw = 2, c = colourDict[squads[0]], clip_on = False)
    
    #Set image label
    cImg.text(0.5, -0.1, names[0],
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = colourDict[squads[0]],
               clip_on = False)
    
    #Map squad colours against dictionary
    barColours = [colourDict[ii] for ii in squads]
    
    #Plot data
    cDat.barh(np.linspace(5,1,5),
               votes,
               color = barColours,
               height = 0.4)
    
    #Set limits
    cDat.set_xlim([0,voteAxLim])
    cDat.set_ylim([0.2,5.5])
    
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = cDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        cDat.text(0,
                   barPatch.get_y()-0.05,
                   playerText,
                   color = barColours[names.index(playerName)],
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        cDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
    
else:
    
    #Plot question mark
    qCircle = plt.Circle((0.5, 0.5), 0.49,
                         facecolor = 'black', edgecolor = 'black',
                         clip_on = False)
    cImg.add_patch(qCircle)
    cImg.text(0.5, 0.5, '?',
               fontsize = 80, fontname = "Charlie don't surf!",
               va = 'center', ha = 'center', color = 'white',
               clip_on = False)
    
    #Add line to bottom of image
    cImg.axhline(y = 0, ls = '-', lw = 2, c = 'black', clip_on = False)
    
    #Set image label
    cImg.text(0.5, -0.1, 'Centre',
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = 'black',
               clip_on = False)
    
    #Plot data
    cDat.barh(np.linspace(5,1,5),
               votes,
               color = 'black',
               height = 0.4)
    
    #Set limits
    cDat.set_ylim([0.2,5.5])
        
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = cDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        cDat.text(0,
                   barPatch.get_y()-0.05,
                   '???',
                   color = 'black',
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        cDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
        
#Set axis ordering above figure
cImg.set_zorder(1)

#Turn off axis lines
cImg.axis('off')
        
#Turn off axis borders
cDat.spines['left'].set_visible(False)
cDat.spines['top'].set_visible(False)
cDat.spines['right'].set_visible(False)

#Turn off y-ticks
cDat.set_yticks([])

#Set x-ticks & parameters
cDat.set_xticks(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int))
cDat.set_xticklabels(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int),
                      fontsize = 7)
cDat.set_xlim([0,voteAxLim])
cDat.spines['bottom'].set_color('#808B96')
cDat.tick_params(axis = 'x', colors = '#808B96')

#Set axis label
cDat.set_xlabel('Total Votes', fontsize = 7, color = '#808B96')

#Set axis face colour
cDat.set_facecolor('#D5D8DC')


# %% Wing defence

#Create axes
wdImg = plt.subplot(gridSpec.new_subplotspec((1,4), colspan = 1, rowspan = 1))
wdDat = plt.subplot(gridSpec.new_subplotspec((1,5), colspan = 1, rowspan = 1))

#Set court position
courtPos = 'WD'
    
#Extract data for current court position
currPosData = totalVotes.loc[totalVotes['position'] == courtPos,]

#Sort by votes and reset index
sortedVotes = currPosData.sort_values(by = 'votes',
                                      ascending = False).reset_index(drop = True)

#Extract the top 5 data into variables
votes = sortedVotes.iloc[0:5]['votes'].to_numpy()
names = sortedVotes.iloc[0:5]['playerName'].to_list()
squads = sortedVotes.iloc[0:5]['squad'].to_list()
bests = sortedVotes.iloc[0:5]['nBest'].to_numpy()

#Plot data
if reveal['WD']:

    #Plot image of top vote getter
    #Get name
    posWinnerName = names[0].split(' ')[-1]
    #Read image
    playerImg = Image.open(f'..\\images\\{posWinnerName}.png')
    #Get axes positioning in figure coordinates
    x0,y0 = wdImg.transData.transform((0.5,0))
    x1,y1 = wdImg.transData.transform((1,1))
    #Get scaling offset based on image height
    scaleOffset = (y1-y0) / playerImg.size[1]
    #Resize the image
    playerImgResize = playerImg.resize((int(playerImg.size[0]*scaleOffset),
                                        int(playerImg.size[1]*scaleOffset)))
    #Plot image on figure at appropriate axes location
    fImg = wdImg.figure.figimage(playerImgResize,
                                 x0 - playerImgResize.size[0]/2,
                                 y0)
    fImg.set_zorder(0)
    
    #Add line to bottom of image
    wdImg.axhline(y = 0, ls = '-', lw = 2, c = colourDict[squads[0]], clip_on = False)
    
    #Set image label
    wdImg.text(0.5, -0.1, names[0],
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = colourDict[squads[0]],
               clip_on = False)
    
    #Map squad colours against dictionary
    barColours = [colourDict[ii] for ii in squads]
    
    #Plot data
    wdDat.barh(np.linspace(5,1,5),
               votes,
               color = barColours,
               height = 0.4)
    
    #Set limits
    wdDat.set_xlim([0,voteAxLim])
    wdDat.set_ylim([0.2,5.5])
    
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = wdDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        wdDat.text(0,
                   barPatch.get_y()-0.05,
                   playerText,
                   color = barColours[names.index(playerName)],
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        wdDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
    
else:
    
    #Plot question mark
    qCircle = plt.Circle((0.5, 0.5), 0.49,
                         facecolor = 'black', edgecolor = 'black',
                         clip_on = False)
    wdImg.add_patch(qCircle)
    wdImg.text(0.5, 0.5, '?',
               fontsize = 80, fontname = "Charlie don't surf!",
               va = 'center', ha = 'center', color = 'white',
               clip_on = False)
    
    #Add line to bottom of image
    wdImg.axhline(y = 0, ls = '-', lw = 2, c = 'black', clip_on = False)
    
    #Set image label
    wdImg.text(0.5, -0.1, 'Wing Defence',
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = 'black',
               clip_on = False)
    
    #Plot data
    wdDat.barh(np.linspace(5,1,5),
               votes,
               color = 'black',
               height = 0.4)
    
    #Set limits
    wdDat.set_ylim([0.2,5.5])
        
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = wdDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        wdDat.text(0,
                   barPatch.get_y()-0.05,
                   '???',
                   color = 'black',
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        wdDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
        
#Set axis ordering above figure
wdImg.set_zorder(1)

#Turn off axis lines
wdImg.axis('off')
        
#Turn off axis borders
wdDat.spines['left'].set_visible(False)
wdDat.spines['top'].set_visible(False)
wdDat.spines['right'].set_visible(False)

#Turn off y-ticks
wdDat.set_yticks([])

#Set x-ticks & parameters
wdDat.set_xticks(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int))
wdDat.set_xticklabels(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int),
                      fontsize = 7)
wdDat.set_xlim([0,voteAxLim])
wdDat.spines['bottom'].set_color('#808B96')
wdDat.tick_params(axis = 'x', colors = '#808B96')

#Set axis label
wdDat.set_xlabel('Total Votes', fontsize = 7, color = '#808B96')

#Set axis face colour
wdDat.set_facecolor('#D5D8DC')

# %% Goal defence

#Create axes
gdImg = plt.subplot(gridSpec.new_subplotspec((2,1), colspan = 1, rowspan = 1))
gdDat = plt.subplot(gridSpec.new_subplotspec((2,2), colspan = 1, rowspan = 1))

#Set court position
courtPos = 'GD'
    
#Extract data for current court position
currPosData = totalVotes.loc[totalVotes['position'] == courtPos,]

#Sort by votes and reset index
sortedVotes = currPosData.sort_values(by = 'votes',
                                      ascending = False).reset_index(drop = True)

#Extract the top 5 data into variables
votes = sortedVotes.iloc[0:5]['votes'].to_numpy()
names = sortedVotes.iloc[0:5]['playerName'].to_list()
squads = sortedVotes.iloc[0:5]['squad'].to_list()
bests = sortedVotes.iloc[0:5]['nBest'].to_numpy()

#Plot data
if reveal['GD']:

    #Plot image of top vote getter
    #Get name
    posWinnerName = names[0].split(' ')[-1]
    #Read image
    playerImg = Image.open(f'..\\images\\{posWinnerName}.png')
    #Get axes positioning in figure coordinates
    x0,y0 = gdImg.transData.transform((0.5,0))
    x1,y1 = gdImg.transData.transform((1,1))
    #Get scaling offset based on image height
    scaleOffset = (y1-y0) / playerImg.size[1]
    #Resize the image
    playerImgResize = playerImg.resize((int(playerImg.size[0]*scaleOffset),
                                        int(playerImg.size[1]*scaleOffset)))
    #Plot image on figure at appropriate axes location
    fImg = gdImg.figure.figimage(playerImgResize,
                                 x0 - playerImgResize.size[0]/2,
                                 y0)
    fImg.set_zorder(0)
    
    #Add line to bottom of image
    gdImg.axhline(y = 0, ls = '-', lw = 2, c = colourDict[squads[0]], clip_on = False)
    
    #Set image label
    gdImg.text(0.5, -0.1, names[0],
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = colourDict[squads[0]],
               clip_on = False)
    
    #Map squad colours against dictionary
    barColours = [colourDict[ii] for ii in squads]
    
    #Plot data
    gdDat.barh(np.linspace(5,1,5),
               votes,
               color = barColours,
               height = 0.4)
    
    #Set limits
    gdDat.set_xlim([0,voteAxLim])
    gdDat.set_ylim([0.2,5.5])
    
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = gdDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        gdDat.text(0,
                   barPatch.get_y()-0.05,
                   playerText,
                   color = barColours[names.index(playerName)],
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        gdDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
    
else:
    
    #Plot question mark
    qCircle = plt.Circle((0.5, 0.5), 0.49,
                         facecolor = 'black', edgecolor = 'black',
                         clip_on = False)
    gdImg.add_patch(qCircle)
    gdImg.text(0.5, 0.5, '?',
               fontsize = 80, fontname = "Charlie don't surf!",
               va = 'center', ha = 'center', color = 'white',
               clip_on = False)
    
    #Add line to bottom of image
    gdImg.axhline(y = 0, ls = '-', lw = 2, c = 'black', clip_on = False)
    
    #Set image label
    gdImg.text(0.5, -0.1, 'Goal Defence',
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = 'black',
               clip_on = False)
    
    #Plot data
    gdDat.barh(np.linspace(5,1,5),
               votes,
               color = 'black',
               height = 0.4)
    
    #Set limits
    gdDat.set_ylim([0.2,5.5])
        
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = gdDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        gdDat.text(0,
                   barPatch.get_y()-0.05,
                   '???',
                   color = 'black',
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        gdDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
        
#Set axis ordering above figure
gdImg.set_zorder(1)

#Turn off axis lines
gdImg.axis('off')
        
#Turn off axis borders
gdDat.spines['left'].set_visible(False)
gdDat.spines['top'].set_visible(False)
gdDat.spines['right'].set_visible(False)

#Turn off y-ticks
gdDat.set_yticks([])

#Set x-ticks & parameters
gdDat.set_xticks(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int))
gdDat.set_xticklabels(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int),
                      fontsize = 7)
gdDat.set_xlim([0,voteAxLim])
gdDat.spines['bottom'].set_color('#808B96')
gdDat.tick_params(axis = 'x', colors = '#808B96')

#Set axis label
gdDat.set_xlabel('Total Votes', fontsize = 7, color = '#808B96')

#Set axis face colour
gdDat.set_facecolor('#D5D8DC')

# %% Goal keeper

#Create axes
gkImg = plt.subplot(gridSpec.new_subplotspec((2,3), colspan = 1, rowspan = 1))
gkDat = plt.subplot(gridSpec.new_subplotspec((2,4), colspan = 1, rowspan = 1))

#Set court position
courtPos = 'GK'
    
#Extract data for current court position
currPosData = totalVotes.loc[totalVotes['position'] == courtPos,]

#Sort by votes and reset index
sortedVotes = currPosData.sort_values(by = 'votes',
                                      ascending = False).reset_index(drop = True)

#Extract the top 5 data into variables
votes = sortedVotes.iloc[0:5]['votes'].to_numpy()
names = sortedVotes.iloc[0:5]['playerName'].to_list()
squads = sortedVotes.iloc[0:5]['squad'].to_list()
bests = sortedVotes.iloc[0:5]['nBest'].to_numpy()

#Plot data
if reveal['GK']:

    #Plot image of top vote getter
    #Get name
    posWinnerName = names[0].split(' ')[-1]
    #Read image
    playerImg = Image.open(f'..\\images\\{posWinnerName}.png')
    #Get axes positioning in figure coordinates
    x0,y0 = gkImg.transData.transform((0.5,0))
    x1,y1 = gkImg.transData.transform((1,1))
    #Get scaling offset based on image height
    scaleOffset = (y1-y0) / playerImg.size[1]
    #Resize the image
    playerImgResize = playerImg.resize((int(playerImg.size[0]*scaleOffset),
                                        int(playerImg.size[1]*scaleOffset)))
    #Plot image on figure at appropriate axes location
    fImg = gkImg.figure.figimage(playerImgResize,
                                 x0 - playerImgResize.size[0]/2,
                                 y0)
    fImg.set_zorder(0)
    
    #Add line to bottom of image
    gkImg.axhline(y = 0, ls = '-', lw = 2, c = colourDict[squads[0]], clip_on = False)
    
    #Set image label
    gkImg.text(0.5, -0.1, names[0],
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = colourDict[squads[0]],
               clip_on = False)
    
    #Map squad colours against dictionary
    barColours = [colourDict[ii] for ii in squads]
    
    #Plot data
    gkDat.barh(np.linspace(5,1,5),
               votes,
               color = barColours,
               height = 0.4)
    
    #Set limits
    gkDat.set_xlim([0,voteAxLim])
    gkDat.set_ylim([0.2,5.5])
    
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = gkDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        gkDat.text(0,
                   barPatch.get_y()-0.05,
                   playerText,
                   color = barColours[names.index(playerName)],
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        gkDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
    
else:
    
    #Plot question mark
    qCircle = plt.Circle((0.5, 0.5), 0.49,
                         facecolor = 'black', edgecolor = 'black',
                         clip_on = False)
    gkImg.add_patch(qCircle)
    gkImg.text(0.5, 0.5, '?',
               fontsize = 80, fontname = "Charlie don't surf!",
               va = 'center', ha = 'center', color = 'white',
               clip_on = False)
    
    #Add line to bottom of image
    gkImg.axhline(y = 0, ls = '-', lw = 2, c = 'black', clip_on = False)
    
    #Set image label
    gkImg.text(0.5, -0.1, 'Goal Keeper',
               fontsize = 11, fontname = "Charlie don't surf!",
               va = 'bottom', ha = 'center', color = 'black',
               clip_on = False)
    
    #Plot data
    gkDat.barh(np.linspace(5,1,5),
               votes,
               color = 'black',
               height = 0.4)
    
    #Set limits
    gkDat.set_ylim([0.2,5.5])
        
    #Add text & vote no
    for playerName in names:
        #get relevant patch
        barPatch = gkDat.patches[names.index(playerName)]
        #Get bar width
        widthVal = barPatch.get_width()
        #Get player text
        playerText = playerName.split(' ')[-1]
        #Add text annotation
        gkDat.text(0,
                   barPatch.get_y()-0.05,
                   '???',
                   color = 'black',
                   va = 'top', ha = 'left',
                   font = 'JerrySport',
                   fontsize = 7)
        #Add vote number
        gkDat.text(widthVal - 1,
                   barPatch.get_y()+barPatch.get_height()/2,
                   str(int(votes[names.index(playerName)])),
                   color = 'white',
                   fontname = 'Arial', fontweight = 'bold',
                   va = 'center', ha = 'right',
                   fontsize = 7)
        
#Set axis ordering above figure
gkImg.set_zorder(1)

#Turn off axis lines
gkImg.axis('off')
        
#Turn off axis borders
gkDat.spines['left'].set_visible(False)
gkDat.spines['top'].set_visible(False)
gkDat.spines['right'].set_visible(False)

#Turn off y-ticks
gkDat.set_yticks([])

#Set x-ticks & parameters
gkDat.set_xticks(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int))
gkDat.set_xticklabels(np.linspace(0, voteAxTickLim, int(voteAxTickLim/100+1), dtype = int),
                      fontsize = 7)
gkDat.set_xlim([0,voteAxLim])
gkDat.spines['bottom'].set_color('#808B96')
gkDat.tick_params(axis = 'x', colors = '#808B96')

#Set axis label
gkDat.set_xlabel('Total Votes', fontsize = 7, color = '#808B96')

#Set axis face colour
gkDat.set_facecolor('#D5D8DC')

# %% Export figure

#Create string based on reveal data for labelling
revealList = [str(int(reveal[courtPos])) for courtPos in courtPositions]
revealString = ''.join([ii for ii in revealList])

#Save figure
plt.savefig(f'..\\outputs\\fanTeam_{revealString}.png', format = 'png', 
            facecolor = fig.get_facecolor(), edgecolor = 'none',
            dpi = fig.get_dpi())

#Close figure
plt.close()

# %% Summarise total votes for each team

#Group by squad, sort and display
totalVotes.groupby('squad').sum().sort_values(by = 'votes', ascending = False)['votes']

# %% Review voter selection of players

#Create a copy of the vote data
voteDataCopy = voteData.reset_index(drop = True)

#Check for double-ups for Proud & Hadley
for voteInd in voteDataCopy.index:
    #Do Proud first
    #Get WA vote
    waVote = voteDataCopy.at[voteInd,'WA_9']
    #Get C vote
    cVote = voteDataCopy.at[voteInd,'C_6']
    #Check to see if both have values
    if not np.isnan(waVote) and not np.isnan(cVote):
        #Replace the wa vote with a nan
        voteDataCopy.at[voteInd,'WA_9'] = np.nan
    #Now Hadley
    #Get WA vote
    waVote = voteDataCopy.at[voteInd,'WA_10']
    #Get C vote
    cVote = voteDataCopy.at[voteInd,'C_9']
    #Check to see if both have values
    if not np.isnan(waVote) and not np.isnan(cVote):
        #Replace the wa vote with a nan
        voteDataCopy.at[voteInd,'WA_10'] = np.nan

#Transpose voting data to count
voteTrans = voteDataCopy.transpose().reset_index()

#Rename columns for ease of use
voteTrans.rename(columns = {'index': 'playerLabel'}, inplace = True)

#Match up player name from lists to create a name variable
#Also create position & squad variables
playerName = []
position = []
squad = []
for playerLabel in voteTrans['playerLabel']:
    #Get position
    pos = playerLabel.split('_')[0]
    #Get player index (subtract one to match up with Python indexing)
    ind = int(playerLabel.split('_')[1]) - 1
    #Extract player name 
    name = playerLists[pos][ind]
    #Identify squad Id from all player list
    squadId = allPlayers.loc[(allPlayers['firstname'] == name.split(' ')[0]) &
                             (allPlayers['surname'] == name.split(' ')[1]),
                             ]['squadId'].unique()[0]
    #Append data to lists
    playerName.append(name)
    position.append(pos)
    squad.append(squadId)
#Append to dataframe
voteTrans['playerName'] = playerName
voteTrans['position'] = position
voteTrans['squad'] = squad

#Replace squad Id with name
voteTrans['squad'].replace(squadDict, inplace = True)

#Group by playername and squad to link up players across positions
selectVotes = voteTrans.groupby(['playerName','squad']).count()

#Drop the player label
selectVotes.drop(labels = ['playerLabel', 'position'], axis = 1, inplace = True)

#Get the count of select votes for each player
selectVotes = selectVotes.sum(axis = 1).reset_index()
selectVotes.rename(columns = {0: 'n'}, inplace = True)

#Get the number of complete voteds (ignoring ones with no selections)
nVoters = len(voteData.dropna(how = 'all'))

#Calculate proportion of selections for each player
selectVotes['selectProp'] = selectVotes['n'] / nVoters * 100

#Keep players > 10%
selectVotes = selectVotes.loc[selectVotes['selectProp'] >= 10,]

#Create visual
fig,ax = plt.subplots(nrows = 1, ncols = 1, figsize = (6, 30))

#Set figure colouring
fig.patch.set_facecolor('#D5D8DC')

#Add title
fig.text(0.5, 0.97,
         'SSN 2022 FAN TEAM',
         font = "Charlie don't surf!", fontsize = 30,
         ha = 'center', va = 'center')

#Add descriptive text
fig.text(0.5, 0.94,
         'Proportion of selections (i.e. any 3-2-1 vote) across players.',
         font = "Arial", fontsize = 12,
         ha = 'center', va = 'center')

#Adjust subplots
plt.subplots_adjust(left = 0.05, right = 0.97,
                    bottom = 0.12, top = 0.92)

#Extract data
#Proportion
selectProp = selectVotes.sort_values(by = 'selectProp',
                                     ascending = False)['selectProp'].to_numpy()
#Player
selectPlayer = selectVotes.sort_values(by = 'selectProp',
                                       ascending = False)['playerName'].to_list()
selectPlayerName = [player.split(' ')[-1] for player in selectPlayer]
#Squad
selectSquad = selectVotes.sort_values(by = 'selectProp',
                                      ascending = False)['squad'].to_list()
selectCol = [colourDict[squadName] for squadName in selectSquad]

#Plot the selection proportions
ax.barh(np.linspace(len(selectProp),1,len(selectProp)),
        selectProp,
        color = selectCol,
        edgecolor = selectCol,
        height = 0.5,
        zorder = 2)

#Set axis limits
ax.set_ylim([0,len(selectProp)+0.5])
ax.set_xlim([0,100.5])

#Add text & vote no
for playerName in selectPlayerName:
    #get relevant patch
    barPatch = ax.patches[selectPlayerName.index(playerName)]
    #Get bar width
    widthVal = barPatch.get_width()
    #Add text annotation
    ax.text(0,
            barPatch.get_y()-0.05,
            playerName,
            color = selectCol[selectPlayerName.index(playerName)],
            va = 'top', ha = 'left',
            font = 'JerrySport',
            fontsize = 5)
    #Add vote number
    ax.text(widthVal - 1,
            barPatch.get_y()+barPatch.get_height()/2,
            str(np.round(selectProp[selectPlayerName.index(playerName)],1))+'%',
            color = 'white',
            fontname = 'Arial', fontweight = 'bold',
            va = 'center', ha = 'right',
            fontsize = 7)

#Plot the fill-up bars
ax.barh(np.linspace(len(selectProp),1,len(selectProp)),
        [100]*len(selectProp),
        color = 'none',
        edgecolor = selectCol,
        height = 0.5,
        alpha = 0.5,
        zorder = 1)

#Turn off axis borders
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

#Turn off y-ticks
ax.set_yticks([])

#Set x-ticks & parameters
ax.set_xticks(np.linspace(0, 100, 5, dtype = int))
ax.set_xticklabels(np.linspace(0, 100, 5, dtype = int),
                   fontsize = 10)
ax.spines['bottom'].set_color('#808B96')
ax.tick_params(axis = 'x', colors = '#808B96')

#Set axis label
ax.set_xlabel('% of Selections', fontsize = 10, color = '#808B96')

#Set axis face colour
ax.set_facecolor('#D5D8DC')

#Save figure
plt.savefig('..\\outputs\\selectionProportion.png', format = 'png', 
            facecolor = fig.get_facecolor(), edgecolor = 'none',
            dpi = 600)

#Close figure
plt.close()

# %%% ----- End of ssnFanTeam2022.py -----