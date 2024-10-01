# -*- coding: utf-8 -*-
'''Copy Room Type'''
__title__ = "Copy Room Type"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from pyrevit import forms, script
import xlrd
import os

script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
excel_filename = "Door Design Database.xlsx"
excel_path = os.path.join(parent_dir, excel_filename)

doc = __revit__.ActiveUIDocument.Document # Get the Active Document
output = script.get_output()


# MAIN SCRIPT

# Get all the Doors in the Document
door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
room_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

if not door_collector:
    forms.alert("No doors found in the active document\n"
                            "Run the tool after creating a door", title = "Script Exiting", warn_icon = True)
    script.exit()

if not room_collector:
    forms.alert("No room found in the active document\n"
                            "Run the tool after creating a room", title = "Script Exiting", warn_icon = True)
    script.exit()

# Check if the Room_Type Parameter is added in the Document or not!
try:
    if door_collector[0].LookupParameter("Room_Type").AsString():
        pass
except:
    forms.alert("No Room_Type Parameter Found in Document\n"
                "Run the Add Room Type Parameter First!", title = "Script Exiting", warn_icon = True)
    script.exit()

try:
    if door_collector[0].LookupParameter("Room_Number").AsString():
        pass
except:
    forms.alert("No Room_Number Parameter Found in Document\n"
                "Add all DAR Shared Parameters first", title = "Script Exiting", warn_icon = True)
    script.exit()


# # Check if the Room_Type Parameters are filled according to the Excel File. 
# options = forms.alert("Select the Door Design Database Excel File", title = "Open Excel File", warn_icon = False, options=["Select File"])
# if options == "Select File":
#     excel_path =  forms.pick_excel_file()
# else:
#     script.exit()

excel_workbook = xlrd.open_workbook(excel_path)
excel_worksheet = excel_workbook.sheet_by_index(1)
excel_room_types = []
for row in range(1, excel_worksheet.nrows):
    excel_room_types.append(excel_worksheet.cell_value(row,0).lower())

failed_data = []
for room in room_collector:
    failed_room_data = []
    if not room.LookupParameter("Room_Type").HasValue:
        failed_room_data.append(output.linkify(room.Id))
        failed_room_data.append(room.LookupParameter("Level").AsValueString().upper())
        failed_room_data.append(room.LookupParameter("Name").AsString().upper())
        failed_room_data.append(room.LookupParameter("Number").AsString().upper())
        failed_room_data.append("ROOM_TYPE VALUE MISSING")

    elif room.LookupParameter("Room_Type").AsString() == "":
        failed_room_data.append(output.linkify(room.Id))
        failed_room_data.append(room.LookupParameter("Level").AsValueString().upper())
        failed_room_data.append(room.LookupParameter("Name").AsString().upper())
        failed_room_data.append(room.LookupParameter("Number").AsString().upper())
        failed_room_data.append("ROOM_TYPE VALUE MISSING")
    
    else:
        if room.LookupParameter("Room_Type").AsString().lower() in excel_room_types:
            continue
        else:
            failed_room_data.append(output.linkify(room.Id))
            failed_room_data.append(room.LookupParameter("Level").AsValueString().upper())
            failed_room_data.append(room.LookupParameter("Name").AsString().upper())
            failed_room_data.append(room.LookupParameter("Number").AsString().upper())
            failed_room_data.append("ROOM_TYPE VALUE MISMATCH")
    failed_data.append(failed_room_data)

if failed_data:
    report = forms.alert("Rooms must have a valid Room_Type Parameter.\n\n"
                "Set the Parameter as per the Design Database.", title="Room_Type Error", warn_icon=True, options=["Show Report"])
    if report == "Show Report":
        output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(__title__ )) # Markdown Heading 2
        output.print_md("---") # Markdown Line Break
        output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
        output.print_table(table_data=failed_data, columns=["ELEMENT ID", "LEVEL", "ROOM NAME", "ROOM NUMBER", "ERROR CODE"]) # Print a Table
        print("\n\n")
        output.print_md("---") # Markdown Line Break
        output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
        output.print_md("---") # Markdown Line Break
        output.print_md("**ROOM_TYPE VALUE MISSING**  - Empty Room Type Parameter. Refer to the Design Database for Values.") # Print a Quote
        output.print_md("**ROOM_TYPE VALUE MISMATCH** - Incorrect Room Rype Value. Refer to the Design Database for Values.") # Print a Quote
        output.print_md("---") # Markdown Line Break
        script.exit()
    else:
        script.exit()

# Access the Room_Number Parameter in the Door
t = Transaction(doc, "Transfer Room Type Data")
t.Start()

failed_data = []
for door in door_collector:
    failed_door_data = []
    if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "":
        failed_door_data.append(output.linkify(door.Id))
        failed_door_data.append(door.LookupParameter("Mark").AsString().upper())
        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
        failed_door_data.append("NO ROOM NUMBER DATA FOUND")
    else:
        continue
    failed_data.append(failed_door_data)

if failed_data:
    t.RollBack()
    result = forms.alert("There are Doors with Empty Room_Number Parameter\n\nCheck Report", title = "Aborting", warn_icon = True, options=["Show Report"])
    if result == "Show Report":
        output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(__title__ )) # Markdown Heading 2
        output.print_md("---") # Markdown Line Break
        output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
        output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK", "LEVEL", "ERROR CODE"]) # Print a Table
        print("\n\n")
        output.print_md("---") # Markdown Line Break
        output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
        output.print_md("---") # Markdown Line Break
        output.print_md("**NO ROOM NUMBER DATA FOUND**  - Empty Room Number Parameter. Run the DAR Door Add-In First.") # Print a Quote
        output.print_md("---") # Markdown Line Break
        script.exit()
    else:
        script.exit()

for door in door_collector:
    for room in room_collector:
        if door.LookupParameter("Room_Number").AsString() == room.LookupParameter("Number").AsString():
            door.LookupParameter("Room_Type").Set(room.LookupParameter("Room_Type").AsString().upper())

forms.alert("Room_Type Parameter filled in all Doors", title = "Script Completed", warn_icon = False)
t.Commit()
