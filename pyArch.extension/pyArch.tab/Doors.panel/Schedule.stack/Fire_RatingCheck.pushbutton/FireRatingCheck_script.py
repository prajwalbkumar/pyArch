# -*- coding: utf-8 -*-
'''Fire Rating Check'''
__title__ = "Fire Rating Check"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
output = script.get_output()


# MAIN SCRIPT

# To Do: Create a check if doors and walls contain the required parameters.

# Get all the Doors
door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
door_count = len(door_collector)

# Check if the Host Wall has a Fire Rating if not Throw an error
report_message = []
counter = 0
for door in door_collector:
    if not door.LookupParameter("Fire_Rating").AsString() == "0":
        wall = door.Host
        wall_fire_param = wall.LookupParameter("Fire_Rating")
        wall_element_id = wall.Id
        if wall_fire_param:
            if wall_fire_param.HasValue:
                if wall_fire_param.AsString() == "":
                    report_message.append("Wall with Element ID - {} has no Fire Rating. " .format(output.linkify(wall.Id)))
                else:
                    counter += 1
                    continue
            else:
                report_message.append("Wall with Element ID - {} has no Fire Rating. " .format(output.linkify(wall.Id)))
        else:
            report_message.append("Wall with Element ID - {} has no Fire Rating. " .format(output.linkify(wall.Id)))
    else:
        counter += 1

if not counter == door_count:
    report = forms.alert("All door-hosted walls need a Fire Rating.\n\n"
                "Set the rating to 0 if none.", title="Wall Fire Rating Missing", warn_icon=True, options=["Show Report"])
    
    if report == "Show Report":
        for line in report_message:       
            print (line)
        script.exit()
    else:
        script.exit()

# Check if all Doors have Fire Rating. If Not:
counter = 0
report_message = []
failed_doors = []

for door in door_collector:
    door_fire_param = door.LookupParameter("Fire_Rating")
    door_mark_param = door.LookupParameter("Mark").AsString()

    if door_fire_param:
        if door_fire_param.HasValue:
            if door_fire_param.AsString() == "":
                report_message.append("{} - Door does not have Fire Rating" .format(output.linkify(door.Id)))
                failed_doors.append(door)
            else:
                counter += 1
                continue
        else:
            report_message.append("{} - Door does not have Fire Rating" .format(output.linkify(door.Id)))
            failed_doors.append(door)
    else:
        report_message.append("{} - Door does not have Fire Rating" .format(output.linkify(door.Id)))
        failed_doors.append(door)

if not counter == door_count:
    report = forms.alert("All doors need a Fire Rating.\n\n"
                "Set the rating to 0 if none.", title="Door Fire Rating Missing", warn_icon=True, options=["Show Report","Auto-Fill Correct Values [BETA]"])
    
    if report == "Show Report":
        for line in report_message:       
            print (line)
        script.exit()
    elif report =="Auto-Fill Correct Values [BETA]":
        t = Transaction(doc, "Filling Door Fire Ratings")
        t.Start()
        for door in failed_doors:
            wall = door.Host
            wall_fire_param = wall.LookupParameter("Fire_Rating").AsString()
            door.LookupParameter("Fire_Rating").Set(str(int(int(wall_fire_param)*0.75)))
        t.Commit()
        success_message = "Fire Rating of " + str(len(failed_doors)) + " doors have been filled"
        success = forms.alert(success_message, title="Missing Parameters Filled", warn_icon=False, options=["Continue with Final Check"])
    else:
        script.exit()

try:
    if not success == "Continue with Final Checks":
        script.exit()
except:
    pass

# Check if the Door Fire Rating == 3/4 of Wall Fire Rating
failed_counter = 0
failed_doors = []
report_message = []
for door in door_collector:
    if not door.LookupParameter("Fire_Rating").AsString() == "0":
        wall = door.Host
        wall_fire_param = wall.LookupParameter("Fire_Rating").AsString() 
        door_fire_param = door.LookupParameter("Fire_Rating").AsString()

        # Check if the door_fire_param last digit is not a character. if yes, then strip off the last character
        if not door_fire_param[-1].isdigit():
            door_fire_param = door_fire_param[:-1]
        if not int(door_fire_param) == 0.75 * int(wall_fire_param):
            report_message.append("Door with Element ID {} does not meet the Wall - Door Criteria" .format(output.linkify(door.Id))) 
            failed_doors.append(door)
            failed_counter += 1

if failed_counter:

    report = forms.alert("Door Fire Parameter should be 3/4th of the Wall Rating", title="Door Fire Rating Missing", warn_icon=True, 
                         options=["Show Report","Auto Correct Values [BETA]"])  
    if report == "Show Report":
        for line in report_message:       
            print (line)
        script.exit()
    elif report =="Auto Correct Values [BETA]":
        print("XXXXXX")
        t = Transaction(doc, "Filling Door Fire Ratings")
        t.Start()
        for door in failed_doors:
            wall = door.Host
            wall_fire_param = wall.LookupParameter("Fire_Rating").AsString()
            door.LookupParameter("Fire_Rating").Set(str(int(int(wall_fire_param)*0.75)))
        t.Commit()
        success_message = "Fire Rating of " + str(len(failed_doors)) + " doors have been filled"
        success = forms.alert(success_message, title="Missing Parameters Filled", warn_icon=False, options=["OK"])
    else:
        script.exit()

else:
    forms.alert("All Parameters are Correct!", title = "Script Exited", warn_icon = False)
    script.exit()     