# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This file contains various functions used in the stats predictions and calculations
    processes. It separates a number of useful functions out from the main script.
    
"""

# %% Import packages

import pandas as pd
import os
from difflib import SequenceMatcher
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.weightstats import DescrStatsW
from statsmodels.stats.moment_helpers import corr2cov
from scipy.stats import multivariate_normal
from scipy.optimize import minimize
import random

# %% Calculate fantasy score using 2022 system

#Function calculates NetballScoop fantasy score from a data series using 2022 scoring system
def calcFantasyScore2022(statsData = None, playerId = None, playerPos = None):
    
    """
    
    Inputs:
        
        statsData - a pandas series object that contains the values for relevant stats
        playerId - the unique playerId for the player
        playerPos - string of the players primary court playing position
        
    Outputs:
        
        fantasyScore - calculated fantasy score value
    
    """
    
    #Function input checks
    
    #Check for all variables
    if statsData is None or playerId is None or playerPos is None:
        raise ValueError('All inputs are required for function to run.')
        
    #Check for appropriate court position
    if playerPos not in ['GS', 'GA', 'WA', 'C', 'WD', 'GD', 'GK']:
        raise ValueError("Player position must be one of 'GS', 'GA', 'WA', 'C', 'WD', 'GD' or 'GK'")
    
    #Set the 2022 scoring system
    pointVals = {'goal1': 2, 'goal2': 5, 'goalMisses': -5,
                 'goalAssists': 3, 'feedWithAttempt': 1,
                 'gain': 5, 'intercepts': 7, 'deflections': 6,
                 'rebounds': 5, 'pickups': 7,
                 'generalPlayTurnovers': -5, 'interceptPassThrown': -2,
                 'badHands': -2, 'badPasses': -2, 'offsides': -2}
        
    #Set a variable to calculate fantasy score
    fantasyScore = 0

    #Calculate score if player is predicted to have played
    if statsData['minutesPlayed'] > 0:
        
        #Add to fantasy score for getting on court
        fantasyScore += 16 #starting score allocated to those who get on court
        
        #Predict how many quarters the player was on for
        #Rough way of doing this is diving by quarter length of 15
        #Take the rounded ceiling of this to estimate quarters played
        fantasyScore += int(np.ceil(statsData['minutesPlayed'] / 15) * 4)
        
        #Loop through the scoring elements and add the scoring for these
        for stat in list(pointVals.keys()):
            fantasyScore += statsData[stat] * pointVals[stat]
            
        #Calculate centre pass receives points
        #This requires different point values across the various positions
        #Here we make an estimate that attacking players would be in the GA/WA group
        #and that defensive players would be in the GD/WD group
        if playerPos in ['GS', 'GA', 'WA', 'C']:
            fantasyScore += np.floor(statsData['centrePassReceives'] / 2) * 1
        elif playerPos in ['WD', 'GD', 'GK']:
            fantasyScore += statsData['centrePassReceives'] * 3
        
        #Calculate penalty points
        fantasyScore += np.floor((statsData['obstructionPenalties'] + statsData['contactPenalties']) / 2) * -1
        
        #Estimate the time played in WD based on player position
        #8 points for half a game at WD / 16 points for a full game at WD
        #Here we'll provide partial points on the basis of minutes played
        #alongside the fantasy position. If a player is exclusively a WD then
        #we'll allocate all of the partial points, but if they're DPP then
        #we'll allocate half of the partial points. This gives an inexact
        #estimate, but may be the best we can do.
        if playerPos == 'WD':
            #Check if minutes played is > than a half of play (i.e. 30 mins)
            if statsData['minutesPlayed'] > 30:
                fantasyScore += ((16-8) * (statsData['minutesPlayed'] - 30) / 30) + 8
            else:
                fantasyScore += (((16-8) * (statsData['minutesPlayed'] - 30) / 30) + 8) / 2
                    
    #Return the final calculated fantasy score
    return fantasyScore

# %%% ----- End of helperFunctions.py -----