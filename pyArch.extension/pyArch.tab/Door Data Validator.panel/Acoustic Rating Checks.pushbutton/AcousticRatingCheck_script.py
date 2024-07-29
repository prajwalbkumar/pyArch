# -*- coding: utf-8 -*-
'''Acoustic Rating Checks'''
__title__ = "Acoustic Rating Checks"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document

# MAIN SCRIPT

# Get all the Doors
door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

# Check if all Doors have STC Rating. If Not:
door_count = len(door_collector)
counter = 0
for door in door_collector:
    door_stc_param = door.LookupParameter("STC_Rating")
    door_mark_param = door.LookupParameter("Mark").AsString()

    if door_stc_param:
        if door_stc_param.HasValue:
            if door_stc_param.AsString() == "":
                print("{} - Door does not have STC Rating" .format(door_mark_param))
            else:
                counter += 1
                continue
        else:
            print("{} - Door does not have STC Rating" .format(door_mark_param))
    else:
        print("{} - Door does not have STC Rating" .format(door_mark_param))

if not counter == door_count:
    forms.alert("Check if all doors have the STC_Rating parameter filled. If not, set the rating to 0.---- Check Report!", title = "Script Exited", warn_icon = True)
    script.exit() 

# Check for STC Ratings of Doors according to their Room Name / Functions
# IF any Door Doesn't have the Room Name Parameter filled up, then throw an error to run the Door Number/Name Check first


# Check if the Host Wall has a STC Rating if not Throw an error
counter = 0
for door in door_collector:
    if not door.LookupParameter("STC_Rating").AsString() == "0":
        wall = door.Host
        wall_stc_param = wall.LookupParameter("STC_Rating")
        wall_element_id = wall.Id
        if wall_stc_param:
            if wall_stc_param.HasValue:
                if wall_stc_param.AsString() == "":
                    print("Wall with Element ID - {} has no STC Rating" .format(wall_element_id))
                else:
                    counter += 1
                    continue
            else:
                print("Wall with Element ID - {} has no STC Rating" .format(wall_element_id))
        else:
            print("Wall with Element ID - {} has no STC Rating" .format(wall_element_id))
    else:
        counter += 1

if not counter == door_count:
    forms.alert("Check if all walls have the STC_Rating parameter filled. If not, set the rating to 0.-- Check Report! --", title = "Script Exited", warn_icon = True)
    script.exit() 


# Check if the Door STC Rating == 3/4 of Wall STC Rating
failed_counter = 0
for door in door_collector:
    if not door.LookupParameter("STC_Rating").AsString() == "0":
        wall = door.Host
        wall_stc_param = wall.LookupParameter("STC_Rating").AsString() 
        door_stc_param = door.LookupParameter("STC_Rating").AsString()

        if not int(door_stc_param) == int(wall_stc_param) - 20:
            print("Door with Element ID {} doesnot meet the Wall - Door Criteria" .format(door.Id))   
            failed_counter += 1

if failed_counter:
    forms.alert("Door STC Parameter should be 20db less than the Wall Rating -- Check Report! --", title = "Script Exited", warn_icon = True)
    script.exit() 
else:
    forms.alert("All Parameters are Correct!", title = "Script Exited", warn_icon = False)
    script.exit()     