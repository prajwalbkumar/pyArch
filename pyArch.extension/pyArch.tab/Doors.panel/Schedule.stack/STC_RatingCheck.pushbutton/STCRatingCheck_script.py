# -*- coding: utf-8 -*-
'''STC Rating Check'''
__title__ = "STC Rating Check"
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

# Check if the Host Wall has a STC Rating if not Throw an error
report_message = []
counter = 0
for door in door_collector:
    if not door.LookupParameter("STC_Rating").AsString() == "0":
        wall = door.Host
        wall_stc_param = wall.LookupParameter("STC_Rating")
        wall_element_id = wall.Id
        if wall_stc_param:
            if wall_stc_param.HasValue:
                if wall_stc_param.AsString() == "":
                    report_message.append("Wall with Element ID - {} has no STC_Rating. " .format(output.linkify(wall.Id)))
                else:
                    counter += 1
                    continue
            else:
                report_message.append("Wall with Element ID - {} has no STC_Rating. " .format(output.linkify(wall.Id)))
        else:
            report_message.append("Wall with Element ID - {} has no STC_Rating. " .format(output.linkify(wall.Id)))
    else:
        counter += 1

if not counter == door_count:
    report = forms.alert("All door-hosted walls need a STC_Rating.\n\n"
                "Set the rating to 0 if none.", title="Wall STC_Rating Missing", warn_icon=True, options=["Show Report","Check Manually"])
    
    if report == "Show Report":
        for line in report_message:       
            print (line)
        script.exit()
    else:
        script.exit()

# Check if all Doors have STC Rating. If Not:
counter = 0
report_message = []
failed_doors = []

for door in door_collector:
    door_stc_param = door.LookupParameter("STC_Rating")
    door_mark_param = door.LookupParameter("Mark").AsString()

    if door_stc_param:
        if door_stc_param.HasValue:
            if door_stc_param.AsString() == "":
                report_message.append("{} - Door does not have STC Rating" .format(output.linkify(door.Id)))
                failed_doors.append(door)
            else:
                counter += 1
                continue
        else:
            report_message.append("{} - Door does not have STC Rating" .format(output.linkify(door.Id)))
            failed_doors.append(door)
    else:
        report_message.append("{} - Door does not have STC Rating" .format(output.linkify(door.Id)))
        failed_doors.append(door)

if not counter == door_count:
    report = forms.alert("All doors need a STC Rating.\n\n"
                "Set the rating to 0 if none.", title="Door STC Rating Missing", warn_icon=True, options=["Show Report","Auto-Fill Correct Values [BETA]"])
    
    if report == "Show Report":
        for line in report_message:       
            print (line)
        script.exit()
    elif report =="Auto-Fill Correct Values [BETA]":
        t = Transaction(doc, "Filling Door STC Ratings")
        t.Start()
        for door in failed_doors:
            wall = door.Host
            wall_stc_param = wall.LookupParameter("STC_Rating").AsString()
            door.LookupParameter("STC_Rating").Set(str(int(int(wall_stc_param) - 15)))
        t.Commit()
        success_message = "STC Rating of " + str(len(failed_doors)) + " doors have been filled"
        success = forms.alert(success_message, title="Missing Parameters Filled", warn_icon=False, options=["Continue with Final Check"])
    else:
        script.exit()

# Check if the Door STC Rating == -15Db of Wall STC Rating
failed_counter = 0
failed_doors = []
report_message = []
for door in door_collector:
    if not door.LookupParameter("STC_Rating").AsString() == "0":
        wall = door.Host
        wall_stc_param = wall.LookupParameter("STC_Rating").AsString() 
        door_stc_param = door.LookupParameter("STC_Rating").AsString()

        # Check if the door_stc_param last digit is not a character. if yes, then strip off the last character
        if not door_stc_param[-1].isdigit():
            door_stc_param = door_stc_param[:-1]
        if not int(door_stc_param) == int(wall_stc_param) - 15:
            report_message.append("Door with Element ID {} does not meet the Wall - Door Criteria" .format(output.linkify(door.Id))) 
            failed_doors.append(door)
            failed_counter += 1

if failed_counter:

    report = forms.alert("Door STC Parameter should be 15dB less than that of the Wall Rating", title="Door STC Rating Missing", warn_icon=True, 
                         options=["Show Report","Auto Correct Values [BETA]"])  
    if report == "Show Report":
        for line in report_message:       
            print (line)
        script.exit()
    elif report =="Auto Correct Values [BETA]":
        t = Transaction(doc, "Filling Door STC Ratings")
        t.Start()
        for door in failed_doors:
            wall = door.Host
            wall_stc_param = wall.LookupParameter("STC_Rating").AsString()
            door.LookupParameter("STC_Rating").Set(str(int(int(wall_stc_param) - 15)))
        t.Commit()
        success_message = "STC Rating of " + str(len(failed_doors)) + " doors have been filled"
        success = forms.alert(success_message, title="Missing Parameters Filled", warn_icon=False, options=["OK"])

else:
    forms.alert("All Parameters are Correct!", title = "Script Exited", warn_icon = False) 