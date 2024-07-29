# -*- coding: utf-8 -*-
'''Fire Rating Checks'''
__title__ = "Fire Rating Checks"
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

# Check if all Doors have Fire Rating. If Not:
door_count = len(door_collector)
counter = 0
for door in door_collector:
    door_fire_param = door.LookupParameter("Fire_Rating")
    door_mark_param = door.LookupParameter("Mark").AsString()

    if door_fire_param:
        if door_fire_param.HasValue:
            if door_fire_param.AsString() == "":
                print("{} - Door does not have Fire Rating" .format(door_mark_param))
            else:
                counter += 1
                continue
        else:
            print("{} - Door does not have Fire Rating" .format(door_mark_param))
    else:
        print("{} - Door does not have Fire Rating" .format(door_mark_param))

if not counter == door_count:
    forms.alert("Check if all doors have the Fire_Rating parameter filled. If not, set the rating to 0.---- Check Report!", title = "Script Exited", warn_icon = True)
    script.exit() 

# Check for Fire Ratings of Doors according to their Room Name / Functions
# IF any Door Doesn't have the Room Name Parameter filled up, then throw an error to run the Door Number/Name Check first


# Check if the Host Wall has a Fire Rating if not Throw an error
counter = 0
for door in door_collector:
    if not door.LookupParameter("Fire_Rating").AsString() == "0":
        wall = door.Host
        wall_fire_param = wall.LookupParameter("Fire_Rating")
        wall_element_id = wall.Id
        if wall_fire_param:
            if wall_fire_param.HasValue:
                if wall_fire_param.AsString() == "":
                    print("Wall with Element ID - {} has no Fire Rating" .format(wall_element_id))
                else:
                    counter += 1
                    continue
            else:
                print("Wall with Element ID - {} has no Fire Rating" .format(wall_element_id))
        else:
            print("Wall with Element ID - {} has no Fire Rating" .format(wall_element_id))
    else:
        counter += 1

if not counter == door_count:
    forms.alert("Check if all walls have the Fire_Rating parameter filled. If not, set the rating to 0.-- Check Report! --", title = "Script Exited", warn_icon = True)
    script.exit() 


# Check if the Door Fire Rating == 3/4 of Wall Fire Rating
failed_counter = 0
for door in door_collector:
    if not door.LookupParameter("Fire_Rating").AsString() == "0":
        wall = door.Host
        wall_fire_param = wall.LookupParameter("Fire_Rating").AsString() 
        door_fire_param = door.LookupParameter("Fire_Rating").AsString()

        # Check if the door_fire_param last digit is not a character. if yes, then strip off the last character
        if not door_fire_param[-1].isdigit():
            door_fire_param = door_fire_param[:-1]
        if not int(door_fire_param) == 0.75 * int(wall_fire_param):
            print("Door with Element ID {} doesnot meet the Wall - Door Criteria" .format(door.Id))   
            failed_counter += 1

if failed_counter:
    forms.alert("Door Fire Parameter should be 3/4th of the Wall Rating -- Check Report! --", title = "Script Exited", warn_icon = True)
    script.exit() 
else:
    forms.alert("All Parameters are Correct!", title = "Script Exited", warn_icon = False)
    script.exit()     