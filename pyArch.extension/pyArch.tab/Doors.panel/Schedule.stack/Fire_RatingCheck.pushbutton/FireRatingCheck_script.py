# -*- coding: utf-8 -*-
'''Fire Rating Check'''
__title__ = "Fire Rating Check"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from pyrevit import forms, script

doc = __revit__.ActiveUIDocument.Document # Get the Active Document
output = script.get_output()


# MAIN SCRIPT

# Get all the Doors
door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

if not door_collector:
    forms.alert("No doors found in the active document\n"
                            "Run the tool after creating a door", title = "Script Exiting", warn_icon = True)
    script.exit()

try:
    if door_collector[0].LookupParameter("Fire_Rating").AsString():
        pass
except:
    forms.alert("No Fire_Rating Parameter Found in Document\n\n"
                "Add all DAR Shared Parameters first", title = "Script Exiting", warn_icon = True)
    script.exit()

# Check if all Doors have Fire Rating. If Not:
failed_doors = []

for door in door_collector:
    door_rating_param = door.LookupParameter("Fire_Rating")

    if door_rating_param:
        hosted_wall_rating = door.Host.LookupParameter("Fire_Rating")
        if hosted_wall_rating:
            if hosted_wall_rating.HasValue:
                if hosted_wall_rating.AsString() == "" or hosted_wall_rating.AsString() == "0":
                    continue
                else:
                    if door_rating_param.AsString() == str(int(int(hosted_wall_rating.AsString())*0.75)):
                        continue
                    else:
                        failed_doors.append(door)


if failed_doors:
    report = forms.alert("Door fire ratings require attentions", title="Door Fire Rating Missing", warn_icon=True, options=["Show Report","Auto-Fill Values"]) 
    failed_data = []

    for door in failed_doors:
            hosted_wall_rating = door.Host.LookupParameter("Fire_Rating")
            if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                door_mark = "NONE"
            else:
                door_mark = door.LookupParameter("Mark").AsString().upper()
            
            if door.LookupParameter("Level"):
                door_level = door.LookupParameter("Level").AsValueString().upper()
            else:
                door_level = "NONE"
            
            if door.LookupParameter("Room_Name"):
                if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                    door_room_name = "NONE"
                else:
                    door_room_name = door.LookupParameter("Room_Name").AsString().upper()
            else:
                door_room_name = "NONE"
            
            if door.LookupParameter("Room_Number"):
                if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                    door_room_number = "NONE"
                else:
                    door_room_number = door.LookupParameter("Room_Number").AsString().upper()
            else:
                door_room_number = "NONE"

            failed_data.append([output.linkify(door.Id), door_level, door_room_name, door_room_number, hosted_wall_rating.AsString(), door.LookupParameter("Fire_Rating").AsString(), str(int(int(hosted_wall_rating.AsString())*0.75))])

    if report == "Show Report":
        output.print_md("##⚠️ {} Completed. Instances Need Attention ☹️" .format(__title__)) # Markdown Heading 2
        output.print_md("---") # Markdown Line Break
        output.print_md("❌ Some issues could not be resolved. Refer to the **Table Report** below for reference")  # Print a Line
        output.print_table(table_data=failed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "HOST WALL RATING", "CURRENT RATING", "CORRECT RATING"]) # Print a Table
        print("\n\n")
        output.print_md("---") # Markdown Line Break

    if report == "Auto-Fill Values":
        t = Transaction(doc, "Filling Door Fire Ratings")
        t.Start()
        for door in failed_doors:
            wall = door.Host
            wall_fire_param = wall.LookupParameter("Fire_Rating").AsString()
            door.LookupParameter("Fire_Rating").Set(str(int(int(wall_fire_param)*0.75)))
        t.Commit()
        
        success_message = "Fire Rating of " + str(len(failed_doors)) + " doors have been filled"
        success = forms.alert(success_message, title="Parameters Updated", warn_icon=False, options=["Show Report", "Ok"])

        if success == "Show Report":
            output.print_md("##✅ {} Completed. 😊" .format(__title__)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
            output.print_md("✅ Door ratings have been updated. Refer to the **Table Report** below for reference")  # Print a Line
            output.print_table(table_data=failed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "HOST WALL RATING", "PREVIOUS RATING", "UPDATED RATING"]) # Print a Table
            print("\n\n")
            output.print_md("---") # Markdown Line Break

else:
    forms.alert("All door ratings correct", title="Door Rating Check", warn_icon=False) 