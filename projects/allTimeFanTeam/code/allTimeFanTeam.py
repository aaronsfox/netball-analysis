# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Code to analyse and create visual for the all time fan team
    
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
import string
from collections import Counter

# %% Set-up

#Colour settings for teams
colourDict = {'Fever': '#00953b',
              'Firebirds': '#4b2c69',
              'GIANTS': '#f57921',
              'Lightning': '#fdb61c',
              'Magpies': '#494b4a',
              'Swifts': '#ee3124',
              'Thunderbirds': '#e54078',
              'Vixens': '#00a68e',
              'Magic': '#000000',
              'Mystics': '#0000cd',
              'Pulse': '#006cb4',
              'Steel': '#00b7eb',
              'Tactix': '#ee161f'}

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
        
#Convert player lists with teams to just a named and teams list
#Create dictionary to store in for each player name and team
playerNames = {courtPos: [] for courtPos in courtPositions}
playerTeams = {courtPos: [] for courtPos in courtPositions}
#Loop through court positions and players
for courtPos in courtPositions:
    for player in playerLists[courtPos]:
        #Split player name up by first parentheses
        playerNames[courtPos].append(' '.join(player.split('(')[0].split(' ')[0:-1]))
        #Identify teams in between parentheses
        #Split by semi-colon
        #Drop punctuation, digits and spaces
        teams = [player[player.find('(')+1:player.find(')')].split(';')[ii].translate(
            str.maketrans('', '', string.punctuation)).translate(
                str.maketrans('', '', string.digits)).strip() for ii in range(len(player[player.find('(')+1:player.find(')')].split(';')))]
        #Reverse teams to ensure if there are any ties that the most recent team comes up
        teams.reverse()                
        #Do a count and append the highest team to the player teams dictionary
        playerTeams[courtPos].append(max(teams ,key = teams.count))

# %% Analyse vote data

#Create a dictionary to store vote data in for every player
voteCount = {courtPos: {player: 0 for player in playerNames[courtPos]} for courtPos in courtPositions}

#Loop through court positions and count votes
for courtPos in courtPositions:
    #Work through the column to count each vote
    for voteInd in voteData[courtPos].index:
        #Split the vote by the comma that separates the listed players
        #Identify the player using the same parenthese methods as before
        currVoteList = [' '.join(voteData[courtPos][voteInd].split(',')[ii].split('(')[0].split(' ')[0:-1]) for ii in range(len(voteData[courtPos][voteInd].split(',')))]
        #Add a vote for each selected player
        for player in currVoteList:
            voteCount[courtPos][player] += 1
        


# %% Create visual of percentage selections for each position

#Set court position
courtPos = 'GS'

#Create visual
fig,ax = plt.subplots(nrows = 1, ncols = 1, figsize = (6, len(playerNames[courtPos])))

#Set figure colouring
fig.patch.set_facecolor('#D5D8DC')

#Add title
fig.text(0.5, 0.97,
         f'ANZC/SSN ALL-TIME FAN TEAM: {courtPos}',
         font = "Charlie don't surf!", fontsize = 20,
         ha = 'center', va = 'center')

#Add descriptive text
fig.text(0.5, 0.94,
         'Proportion of votes containing selected player',
         font = "Arial", fontsize = 12,
         ha = 'center', va = 'center')

#Adjust subplots
plt.subplots_adjust(left = 0.05, right = 0.97,
                    bottom = 0.12, top = 0.92)

#Extract and sort vote data
sortedVotes = {player: votes for player, votes in sorted(voteCount[courtPos].items(),
                                                         key = lambda item: item[1],
                                                         reverse = True)}

#Extract values from dictionary
votedPlayers = [player for player in sortedVotes.keys()]
playerTally = [votes for votes in sortedVotes.values()]

#Normalise vote tally to total votes
playerProp = np.array(playerTally) / len(voteData) * 100

#Identify the squad of each player
votedSquads = [playerTeams[courtPos][playerNames[courtPos].index(player)] for player in votedPlayers]

#Get the associated squad colour
votedCol = [colourDict[squadName] for squadName in votedSquads]

#Plot the selection proportions
ax.barh(np.linspace(len(playerProp),1,len(playerProp)),
        playerProp,
        color = votedCol,
        edgecolor = votedCol,
        height = 0.5,
        zorder = 2)

#Set axis limits
ax.set_ylim([0,len(playerProp)+0.5])
ax.set_xlim([0,100.5])

#Plot the fill-up bars
ax.barh(np.linspace(len(playerProp),1,len(playerProp)),
        [100]*len(playerProp),
        color = 'none',
        edgecolor = votedCol,
        height = 0.5,
        alpha = 0.5,
        zorder = 1)

#Add text & vote no
for player in votedPlayers:
    #get relevant patch
    barPatch = ax.patches[votedPlayers.index(player)]
    #Get bar width
    widthVal = barPatch.get_width()
    #Add text annotation
    ax.text(0,
            barPatch.get_y()-0.1,
            ' '.join(player.split(' ')[1:]),
            color = votedCol[votedPlayers.index(player)],
            va = 'top', ha = 'left',
            font = 'JerrySport',
            fontsize = 155 / len(playerNames[courtPos]))
    #Add vote number
    ax.text(widthVal + 1,
            barPatch.get_y()+barPatch.get_height()/2,
            str(np.round(playerProp[votedPlayers.index(player)],1))+'%',
            color = votedCol[votedPlayers.index(player)],
            fontname = 'Arial', fontweight = 'bold',
            va = 'center', ha = 'left',
            fontsize = 220 / len(playerNames[courtPos]))

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
plt.savefig(f'..\\outputs\\{courtPos}_selectionProportion.png', format = 'png', 
            facecolor = fig.get_facecolor(), edgecolor = 'none',
            dpi = 300)

#Close figure
plt.close()

# %%% ----- End of allTimeFanTeam.py -----