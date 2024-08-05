# -*- coding: utf-8 -*-
'''Bulk Revisioning'''
__title__ = "Bulk Revisioning"
__author__ = "prajwalbkumar"


# Import Libraries
from pyrevit import revit
from pyrevit import forms, script, EXEC_PARAMS 

# Function to apply revisions
def reviseSheet(sheet, revision, apply):
    # Get Revisions
    revisions_sheets = sheet.GetAdditionalRevisionIds()
    outcome = 0

    # If applying a revision
    if apply:
        # Is revision not present
        if revision.Id not in revisions_sheets:
            revisions_sheets.Add(revision.Id) # Concept of Adding an item to the list
            sheet.SetAdditionalRevisionIds(revisions_sheets)
            outcome += 1
    
    # If removing a revision
    else:
        # Is revision present
        if revision.Id in revisions_sheets:
            revisions_sheets.Remove(revision.Id)
            sheet.SetAdditionalRevisionIds(revisions_sheets)
            outcome += 1
# Return the Outcome
    return outcome 
       

# Check if we are running alternatively
check = not(EXEC_PARAMS.config_mode)

# Make some action wordss
if check:
    action1 = "Apply Revisions"
    action2 = "Applying"
    action3 = "Applied to"
else:
    action1 = "Remove Revisions"
    action2 = "Removing"
    action3 = "Removed from"

# Ask the user for a revision
revision = forms.select_revisions(title = 'Select Revision', button_name = 'Select', width = 300, multiple = False)

# Check if we have a revision selected
if not revision:
    forms.alert("No Revision Selected", title='Script Cancelled')
    script.exit()

else:
    # Ask for sheets
    sheets = forms.select_sheets(title = 'Select Sheets', button_name = action1, include_placeholder = False, width = 600, use_selection = True, multiple = True)
    
    # Check if sheets are selected
    if sheets:
        # Create a Tracker
        revision_set = 0
        
        # Make a loading bar
        bar_step = 1
        bar_len = len(sheets)
        bar_count = 1
        with forms.ProgressBar(step = bar_step, title = action2 + " revisions... :") as bar:
            # Open a Transaction
            with revit.Transaction("Bulk Revisioning"):
                for sheet in sheets:
                    rev_check = reviseSheet(sheet, revision, check)
                    revision_set += rev_check
                    # Update Progress bar
                    bar.update_progress(bar_count, bar_len)
                    bar_count += 1
    else:
        forms.alert("No Sheets Selected", title='Script Cancelled')

# Primary Message
if revision_set > 0:
    main_message = r'"' + revision.Name + r'"' + " " + action3 + " " + str(revision_set) + " " + "Sheets"
    return_message = "\n\n"
else:
    main_message = ""
    return_message = ""

# Secondary Message
excess = len(sheets) - revision_set

if excess > 0:
    extra_message = return_message + str(excess) + " Sheet(s) did not Require a Change."
else:
    extra_message = ""

# Display Final Message
forms.alert(main_message + extra_message, title = "Script Completed", warn_icon = False)