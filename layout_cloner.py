#!/usr/bin/env python

#Script for KiCAD Pcbnew to clone a part of a layout. The scipt clones a row or a matrce
#of similar layouts.
#WARNING: MAKE A BACKUP of your KiCad pcb before running this script. The operations CANNOT BE UNDONE!
#
#For now, there are no command line parameters given for the script, instead
#all the settings are written in this file. Before using this script, you must have your schema
#ready.
#1. Use hierarchical sheets for the subschemas to be cloned and annotate them 
#so that each sheet has module references starting with a different hundred.
#2. Import a netlist into Pcbnew and place all the components except the ones to be cloned.
#3. In the same board file, create also an optimal layout for the subschema to be used
#as the template for the clones.
#4. Surround the layout of the subchema with a zone in the comment layer.
#5. Save the .kicad_pcb file and run this script.
#
#The script has three main parts:
#First, the script moves the modules, which are already imported into the board file. They are
#moved by a predetermined offset amount compared to the template module. (A module with the same
#reference, except starting with a different hundred, eg. templatemodule = D201, clones = D301, D401, D501 etc.)
#Second, the script clones the zones inside the comment layer zone. It seems the zone to be cloned must
#be completely inside the comment zone. Zones have a net defined for them. The script searches for any
#pads inside the cloned zone and sets their net for the zone. So you may get a wrong zone for the net if
#there are pads with different nets inside the zone.
#Third, the script clones the tracks inside the comment zone. Any track touching the zone will be cloned.
#Tracks do not have nets defined for them so they should connect nicely to the modules they will be touching
#after the cloning process.
#
#This script has been tested with KiCAD version BZR 5382 with all scripting settings turned on. (Ubuntu and Python 2.7.6)
#The script can be run in Linux terminal with command $python pcbnew_cloner.py


import sys			
import re			#regexp
from pcbnew import *


#Settings, modify these to suit your project

#The schematic with the hierarchical sheets (not used currently, requires utilizing kipy to parse schematic)
#You can copy the schema parsing with kipy for example from klonor-kicad if you have enough components to justify it
#schemaTemplate = './boosterilevy/booster.sch'
#Instead the components to be cloned are currently given manually
templateReferences = ['U201', 'U202', 'U203', 'D201', 'D202',  'RV201', 'TP201', 'TP202', 'TP203', 'TP204', 'TP205', 'TP206',
                        'C201', 'C202', 'C203', 'C204', 'C205', 'C206', 'C207', 'C208', 'C209',
                        'R201', 'R202', 'R203', 'R204', 'R205', 'R206', 'R207', 'R208', 'R209', 'R210', 'R211', 'R212', 'R213', 'R214']
clonedSheetNumbers = [500, 600, 700, 800, 900, 1000, 1100]#not all sheets are in sequence for this case. NOTE: cannot have more than 99 elements of same type!
#The .kicad-pcb board with a ready layout for the area to be cloned.
#The cloned area must be surrounded by a (square) zone in the comment layer.
#inputBoard = './boosterilevy/16x_boosteri.kicad_pcb'
#Output file, original file remains unmodified
#outputBoardFile = './boosterilevy/skriptioutput.kicad_pcb'
#commented out input and output boards. I'll be doing this inside of KiCad. --RM
#to use this script within KiCad, enter the command `execfile("layout_cloner.py")` in the python console
#place the python script in 'C:\Program Files\KiCad' if you don't want to put a path in the above command

#templateRefModulo = 100;	#Difference in the reference numbers between hierarchical sheet. settings allow for 1000 or 100
#templateRefStart = 200;		#Starting point of numbering in the first hierarchical sheet. 100 is the parent sheet
move_dx = FromMM(26.416)		#Spacing between clones in x direction
move_dy = FromMM(0.0)		#Spacing between clones in y direction
clonesX = 8			#Number of clones in x direction
clonesY = 1			#Number of clones in y direction


numberOfClones = clonesX * clonesY
#board = LoadBoard(inputBoard)
board = pcbnew.GetBoard()

#Cloning the modules
for templateRef in templateReferences:							            #For each module in the template schema
    templateModule = board.FindModuleByReference(templateRef)				#Find the corresponding module in the input board
    if templateModule is not None:
        cloneReferences = []
        templateReferenceNumber = (re.findall(r"\d+", templateRef)).pop(0)	#Extract reference number (as string). Will be 201, 202, etc.

        for i in range(0, numberOfClones-1):						        #Create list of references to be cloned of this module from the template	
            #cloneRefNumber = int(templateReferenceNumber) + (i+1)*templateRefModulo	                        #Number of the next clone
            cloneRefNumber = int(templateReferenceNumber)%100 + clonedSheetNumbers[i]	                        #Number of the next clone
            cloneReferences.append(re.sub(templateReferenceNumber, "", templateRef) + str(cloneRefNumber))	#String reference of the next clone			
        print 'Original reference: ', templateRef, ', Generated clone reference values:', cloneReferences

        for counter, cloneRef in enumerate(cloneReferences):				#Move each of the clones to appropriate location
            templatePosition = templateModule.GetPosition()                 #get x,y coordinates of template module
            cloneModule = board.FindModuleByReference(cloneRef)				
            if cloneModule is not None:
                if cloneModule.GetLayer() is not templateModule.GetLayer(): #If the cloned module is not on the same layer as the template
                    cloneModule.Flip(wxPoint(1,1))						    #Flip it around arbitrary point to change the layer, will move it into position next
                vect = wxPoint(templatePosition.x+(counter+1)%clonesX*move_dx, templatePosition.y+(counter+1)//clonesX*move_dy) #Calculate new positions for x-direction array
                cloneModule.SetPosition(vect)						        #Set position
                cloneModule.SetOrientation(templateModule.GetOrientation())	#And copy orientation from template
            else:
                print 'Module to be moved (', cloneRef, ') is not found in the board.'
    else:
        print 'Module ', templateRef, ' was not found in the template board'
print 'Modules moved and oriented according to template.'

#Cloning zones inside the template area.
#First lets use the comment zone to define the area to be cloned.
for i in range(0, board.GetAreaCount()):                    #iterate through zones to find comment layer zone
    zone = board.GetArea(i)				
    if zone.GetLayer() == 41:								#Find the first comment zone encasing the template board area
        templateRect = zone.GetBoundingBox()
        #board.RemoveArea(zone)								#Removing comment zone does not work
	print 'Comment zone left top: ', templateRect.GetOrigin(), ' width: ', templateRect.GetWidth(), ' height: ', templateRect.GetHeight()

modules = board.GetModules()
#Then iterate through all the other zones and copy them
print 'Iterating through all the pads for each cloned zone, might take a few seconds...'
for i in range(0, board.GetAreaCount()):						#For all the zones in the board
    zone = board.GetArea(i)
    #print 'Original zone location', zone.GetPosition()
            
    if templateRect.Contains(zone.GetPosition()) and zone.GetLayer() is not 41:		#If the zone is inside the area to be cloned (the comment zone) and it is not the comment zone (layer 41)
        for i in range(1, numberOfClones):						                    #For each target clone areas
            zoneClone = zone.Duplicate()						                    #Make copy of the zone to be cloned
            zoneClone.Move(wxPoint(i%clonesX*move_dx, i//clonesX*move_dy))		    #Move it inside the target clone area
            for module in modules:								                    #Iterate through all the pads (also the cloned ones) in the board...
                for pad in module.Pads():
                    if zoneClone.HitTestInsideZone(pad.GetPosition()) and pad.IsOnLayer(zoneClone.GetLayer()): #To find the (last) one inside the cloned zone. pad.GetZoneConnection() could also be used
                        zoneClone.SetNetCode(pad.GetNet().GetNet())			#And set the (maybe) correct net for the zone
            board.Add(zoneClone)								            #Add zone to the board
print 'Zones cloned.'

#Cloning tracks inside the template area
tracks = board.GetTracks()
cloneTracks = []                                            #create array to store tracks we're going to clone
for track in tracks:                                        #iterate through all tracks in the board
    if track.HitTest(templateRect):							#Find tracks which are within the comment zone
        for i in range(1, numberOfClones):					                    #For each area to be cloned
            cloneTrack = track.Duplicate()					                    #Copy a track in the template area
            cloneTrack.Move(wxPoint(i%clonesX*move_dx, i//clonesX*move_dy))		#Move copy into position
            cloneTracks.append(cloneTrack)						#Add the track to temporary list
for track in cloneTracks:								        #Append the temporary list to board
    tracks.Append(track)
print 'Tracks cloned.'

#Save output file
#board.Save(outputBoardFile)
print 'Script completed'
