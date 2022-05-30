#Load packages
library(shiny)
library(shinyWidgets)
library(shinythemes)
library(reactable)

#Create dataframe with starting ladder
#Columns for dataframe
Team <- c("Vixens", "Fever", "GIANTS", "Firebirds",
          "Thunderbirds", "Swifts", "Magpies", "Lightning")
P <- c(12,12,12,12,12,12,12,12)
W <- c(10,8,6,5,5,5,5,4)
D <- c(0,0,0,0,0,0,0,0)
L <- c(2,4,6,7,7,7,7,8)
GF <- c(758,870,754,799,620,681,758,738)
GA <- c(723,796,749,792,628,704,784,802)
Pts <- c(40,32,24,20,20,20,20,16)
Per <- c(104.84,109.30,100.67,100.88,98.73,96.73,96.68,92.02)
#Construct the dataframe
ladderData <- data.frame(Team, P, W, D, L, GF, GA, Pts, Per)

#Set colours for teams
feverCol <- "#00953b"
firebirdsCol <- "#4b2c69"
giantsCol <- "#f57921"
lightningCol <- "#fdb61c"
magpiesCol <- "#494b4a"
swiftsCol <- "#0082cd"
thunderbirdsCol <- "#e54078"
vixensCol <- "#00a68e"

#Set list for generic game labels
gameLabels <- c("G1", "G2", "G3", "G4")

#Set list for remaining rounds
# roundLabels <- c("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14")
roundLabels <- c("R13", "R14")

#Set list for games within round
matchUpLabels <- list(
    
#   #Round 1
#     list(c("Thunderbirds", "Magpies"), c("Swifts", "GIANTS"), c("Firebirds", "Vixens"), c("Fever", "Lightning")),
# 	
# 	#Round 2
#     list(c("Swifts", "Vixens"), c("Lightning", "Firebirds"), c("Magpies", "Fever"), c("Thunderbirds", "GIANTS")),
# 	
# 	#Round 3
#     list(c("Vixens", "GIANTS"), c("Swifts", "Magpies"), c("Firebirds", "Fever"), c("Thunderbirds", "Lightning")),
# 	
# 	#Round 4
#     list(c("Vixens", "Fever"), c("GIANTS", "Firebirds"), c("Magpies", "Lightning"), c("Thunderbirds", "Swifts")),
# 	
# 	#Round 5
#     list(c("Lightning", "Vixens"), c("GIANTS", "Magpies"), c("Fever", "Swifts"), c("Firebirds", "Thunderbirds")),
# 	
# 	#Round 6
#     list(c("Swifts", "Lightning"), c("Vixens", "Thunderbirds"), c("Firebirds", "Magpies"), c("GIANTS", "Fever")),
# 	
# 	#Round 7
#     list(c("Firebirds", "Swifts"), c("Thunderbirds", "Fever"), c("Lightning", "GIANTS"), c("Vixens", "Magpies")),
# 	
# 	#Round 8
#     list(c("Vixens", "Firebirds"), c("Lightning", "Thunderbirds"), c("Fever", "Magpies"), c("GIANTS", "Swifts")),
# 	
# 	#Round 9
#     list(c("Lightning", "Fever"), c("GIANTS", "Vixens"), c("Magpies", "Firebirds"), c("Swifts", "Thunderbirds")),
# 	
# 	#Round 10
#     list(c("Lightning", "Swifts"), c("Fever", "Vixens"), c("Magpies", "GIANTS"), c("Thunderbirds", "Firebirds")),
#     
#     #Round 11
#     list(c("Firebirds", "Lightning"), c("Vixens", "Swifts"), c("Fever", "GIANTS"), c("Magpies", "Thunderbirds")),
    # 
    # #Round 12
    # list(c("Magpies", "Swifts"), c("Fever", "Firebirds"), c("Vixens", "Lightning"), c("GIANTS", "Thunderbirds")),
    
    #Round 13
    list(c("Firebirds", "GIANTS"), c("Thunderbirds", "Vixens"), c("Swifts", "Fever"), c("Lightning", "Magpies")),
    
    #Round 14
    list(c("GIANTS", "Lightning"), c("Fever", "Thunderbirds"), c("Swifts", "Firebirds"), c("Magpies", "Vixens"))
    
  )

#Set match-up labels to round names
names(matchUpLabels) <- roundLabels

#Create the round tabs and game tabs within these

#Create empty list to store tabs in
matchTabsetList <- list()

for (rr in 1:length(roundLabels)) {

  #Append a list within the broader matchup list for the current round
  #Also rename it to current round
  matchTabsetList[[length(matchTabsetList)+1]] <- list()
  names(matchTabsetList)[length(matchTabsetList)] <- roundLabels[rr]

  #Loop through the games within a round
  for (gg in 1:length(matchUpLabels[rr][[1]])) {

    #Create the tab panel for current game and append to round list
    matchTabsetList[rr][[1]][[length(matchTabsetList[rr][[1]])+1]] <- tabPanel(gameLabels[gg],
                                                                               #Header for game
                                                                               h4(paste(matchUpLabels[rr][[1]][[gg]][1],matchUpLabels[rr][[1]][[gg]][2], sep = ' vs. ')),
                                                                               #Radio button for including game
                                                                               radioButtons(paste(roundLabels[rr],gameLabels[gg], sep = "_"),
                                                                                            "Include?", c("Yes", "No"), selected = "No"),
                                                                               #Slider input for the two teams
                                                                               #Team 1
                                                                               sliderInput(paste(matchUpLabels[rr][[1]][[gg]][1], roundLabels[rr], sep = ""),
                                                                                           paste(matchUpLabels[rr][[1]][[gg]][1], "Score", sep = " "),
                                                                                           value = 0, min = 0, max = 100),
                                                                               #Team 2
                                                                               sliderInput(paste(matchUpLabels[rr][[1]][[gg]][2], roundLabels[rr], sep = ""),
                                                                                           paste(matchUpLabels[rr][[1]][[gg]][2], "Score", sep = " "),
                                                                                           value = 0, min = 0, max = 100)
    )
  }
}



# Define UI for application that draws a histogram
fluidPage(
  
  # #Set theme
  # theme = shinytheme("cosmo"),
  
  #Add css tags
  tags$style(type = 'text/css',
             
             "h4 {font-weight: bold}"),
  
  # Application title
  titlePanel("Super Netball 2022: Ladder Predictor"),
  
  # Sidebar with a slider input for number of bins 
  sidebarLayout(
    
    sidebarPanel(
      
      #Set colours for sliders
      #This is based on match ordering
      setSliderColor(c(
					   # #Round 1
					   # thunderbirdsCol, magpiesCol, swiftsCol, giantsCol, firebirdsCol, vixensCol, feverCol, lightningCol,
					   # #Round 2
					   # swiftsCol, vixensCol, lightningCol, firebirdsCol, magpiesCol, feverCol, thunderbirdsCol, giantsCol,
					   # #Round 3
					   # vixensCol, giantsCol, swiftsCol, magpiesCol, firebirdsCol, feverCol, thunderbirdsCol, lightningCol,
					   # #Round 4
					   # vixensCol, feverCol, giantsCol, firebirdsCol, magpiesCol, lightningCol, thunderbirdsCol, swiftsCol,
					   # #Round 5
					   # lightningCol, vixensCol, giantsCol, magpiesCol, feverCol, swiftsCol, firebirdsCol, thunderbirdsCol,
					   # #Round 6
					   # swiftsCol, lightningCol, vixensCol, thunderbirdsCol, firebirdsCol, magpiesCol, giantsCol, feverCol,
					   # #Round 7
					   # firebirdsCol, swiftsCol, thunderbirdsCol, feverCol, lightningCol, giantsCol, vixensCol, magpiesCol,
					   # #Round 8
					   # vixensCol, firebirdsCol, lightningCol, thunderbirdsCol, feverCol, magpiesCol, giantsCol, swiftsCol,
					   # #Round 9
					   # lightningCol, feverCol, giantsCol, vixensCol, magpiesCol, firebirdsCol, swiftsCol, thunderbirdsCol,
					   # #Round 10
					   # lightningCol, swiftsCol, feverCol, vixensCol, magpiesCol, giantsCol, thunderbirdsCol, firebirdsCol,
					   # #Round 11
					   # firebirdsCol, lightningCol, vixensCol, swiftsCol, feverCol, giantsCol, magpiesCol, thunderbirdsCol,
					   # #Round 12
					   # magpiesCol, swiftsCol, feverCol, firebirdsCol, vixensCol, lightningCol, giantsCol, thunderbirdsCol,
					   #Round 13
					   firebirdsCol, giantsCol, thunderbirdsCol, vixensCol, swiftsCol, feverCol, lightningCol, magpiesCol,
					   #Round 14
					   giantsCol, lightningCol, feverCol, thunderbirdsCol, swiftsCol, firebirdsCol, magpiesCol, vixensCol),
					   # c(seq(1, 14*4, length.out = 14*4))
					   c(seq(1, 4*4, length.out = 4*4))
					   ),
      
      #Add tab panel for game/round selection
      tabsetPanel(type = "tabs",
	  
# 				  #Round 1 panel
#                   tabPanel("R1",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R1[[1]],
#                                        #Game 2
#                                        matchTabsetList$R1[[2]],
#                                        #Game 3
#                                        matchTabsetList$R1[[3]],
#                                        #Game 4
#                                        matchTabsetList$R1[[4]]
#                                        
#                            )
#                   ),
#                   
#                   
#                   #Round 2 panel
#                   tabPanel("R2",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R2[[1]],
#                                        #Game 2
#                                        matchTabsetList$R2[[2]],
#                                        #Game 3
#                                        matchTabsetList$R2[[3]],
#                                        #Game 4
#                                        matchTabsetList$R2[[4]]
#                                        
#                            )
#                   ),
# 	  
# 				  #Round 3 panel
#                   tabPanel("R3",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R3[[1]],
#                                        #Game 2
#                                        matchTabsetList$R3[[2]],
#                                        #Game 3
#                                        matchTabsetList$R3[[3]],
#                                        #Game 4
#                                        matchTabsetList$R3[[4]]
#                                        
#                            )
#                   ),
#                   
#                   #Round 4 panel
#                   tabPanel("R4",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R4[[1]],
#                                        #Game 2
#                                        matchTabsetList$R4[[2]],
#                                        #Game 3
#                                        matchTabsetList$R4[[3]],
#                                        #Game 4
#                                        matchTabsetList$R4[[4]]
#                                        
#                            )
#                   ),
#                   
#                   #Round 5 panel
#                   tabPanel("R5",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R5[[1]],
#                                        #Game 2
#                                        matchTabsetList$R5[[2]],
#                                        #Game 3
#                                        matchTabsetList$R5[[3]],
#                                        #Game 4
#                                        matchTabsetList$R5[[4]]
#                                        
#                            )
#                   ),
#                   
#                   
#                   #Round 6 panel
#                   tabPanel("R6",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R6[[1]],
#                                        #Game 2
#                                        matchTabsetList$R6[[2]],
#                                        #Game 3
#                                        matchTabsetList$R6[[3]],
#                                        #Game 4
#                                        matchTabsetList$R6[[4]]
#                                        
#                            )
#                   ),
# 	  
# 				  #Round 7 panel
#                   tabPanel("R7",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R7[[1]],
#                                        #Game 2
#                                        matchTabsetList$R7[[2]],
#                                        #Game 3
#                                        matchTabsetList$R7[[3]],
#                                        #Game 4
#                                        matchTabsetList$R7[[4]]
#                                        
#                            )
#                   ),
#                   
#                   #Round 8 panel
#                   tabPanel("R8",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R8[[1]],
#                                        #Game 2
#                                        matchTabsetList$R8[[2]],
#                                        #Game 3
#                                        matchTabsetList$R8[[3]],
#                                        #Game 4
#                                        matchTabsetList$R8[[4]]
#                                        
#                            )
#                   ),
#                   
#                   #Round 9 panel
#                   tabPanel("R9",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R9[[1]],
#                                        #Game 2
#                                        matchTabsetList$R9[[2]],
#                                        #Game 3
#                                        matchTabsetList$R9[[3]],
#                                        #Game 4
#                                        matchTabsetList$R9[[4]]
#                                        
#                            )
#                   ),
#                   
#                   
#                   #Round 10 panel
#                   tabPanel("R10",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R10[[1]],
#                                        #Game 2
#                                        matchTabsetList$R10[[2]],
#                                        #Game 3
#                                        matchTabsetList$R10[[3]],
#                                        #Game 4
#                                        matchTabsetList$R10[[4]]
#                                        
#                            )
#                   ),
#                   
#                   #Round 11 panel
#                   tabPanel("R11",
#                            
#                            tabsetPanel(type = "tabs",
#                                        
#                                        #Game 1
#                                        matchTabsetList$R11[[1]],
#                                        #Game 2
#                                        matchTabsetList$R11[[2]],
#                                        #Game 3
#                                        matchTabsetList$R11[[3]],
#                                        #Game 4
#                                        matchTabsetList$R11[[4]]
#                                        
#                            )
#                   ),
                  # 
                  # #Round 12 panel
                  # tabPanel("R12",
                  #          
                  #          tabsetPanel(type = "tabs",
                  #                      
                  #                      #Game 1
                  #                      matchTabsetList$R12[[1]],
                  #                      #Game 2
                  #                      matchTabsetList$R12[[2]],
                  #                      #Game 3
                  #                      matchTabsetList$R12[[3]],
                  #                      #Game 4
                  #                      matchTabsetList$R12[[4]]
                  #                      
                  #          )
                  # ),
                  
                  #Round 13 panel
                  tabPanel("R13",
                           
                           tabsetPanel(type = "tabs",
                                       
                                       #Game 1
                                       matchTabsetList$R13[[1]],
                                       #Game 2
                                       matchTabsetList$R13[[2]],
                                       #Game 3
                                       matchTabsetList$R13[[3]],
                                       #Game 4
                                       matchTabsetList$R13[[4]]
                                       
                           )
                  ),
                  
                  
                  #Round 14 panel
                  tabPanel("R14",
                           
                           tabsetPanel(type = "tabs",
                                       
                                       #Game 1
                                       matchTabsetList$R14[[1]],
                                       #Game 2
                                       matchTabsetList$R14[[2]],
                                       #Game 3
                                       matchTabsetList$R14[[3]],
                                       #Game 4
                                       matchTabsetList$R14[[4]]
                                       
                           )
                  )
                  
      ),
      
    ),
    
    # Show a plot of the generated distribution
    mainPanel(
      
      #Tab panels for current and predicted ladders
      tabsetPanel(
        
        #Tab for current ladder
        tabPanel("Current Ladder",
                 
                 reactableOutput("currentLadderTable")
                 
        ),
        
        #Tab panel for predicted ladder
        tabPanel("Predicted Ladder",
                 
                 #Add blank header buffer and button for predictions
                 h5(" "),
                 actionButton("runPrediction", "Run Prediction!"),
                 h5(" "),
                 
                 #Add the predicted table
                 reactableOutput("predictedLadderTable")
                 
                 
        )
        
      )
      
    )
  )
)