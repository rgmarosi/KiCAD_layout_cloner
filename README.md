# KiCAD_layout_cloner
A python script to clone a part of a layout in Pcbnew

This script is made to work on hierarchical sheet designs only. When assigning references, choose sheet numbering in multiples of 100 or 1000.


1. Edit the following parameters of the script to clone layouts: (`move_dx` and `move_dy` dimensions are in mm)
`templateReferences`, `clonedSheetNumbers`, `move_dx`, `move_dy`, `clonesX`, `clonesY`

2. **CREATE A BACKUP BEFORE RUNNING THIS SCRIPT!** You cannot undo the operations. However, you can still close without saving to revert back.

3. To select the layout you wish to copy: create a filled zone around your template using the `Cmts.User` layer.

4. To run the script, open the Python console in Pcbnew and execute the following command: `execfile('C:\yourPathGoesHere\layout_cloner.py')`

5. Zoom in and out to redraw and see the results. If you're happy with the results, save the layout and reopen Pcbnew.


**Known issue:** Cloned zones don't have the same net as the template. It needs to be manually changed back
(or programmatically if it's doable and saves time)

