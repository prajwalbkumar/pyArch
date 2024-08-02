# -*- coding: utf-8 -*-
'''Copy Room Type Data'''
__title__ = "Copy Room Type Data"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import xlrd

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
output = script.get_output()


# MAIN SCRIPT

# Get all the Doors in the Document
door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
room_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()


# Check if the Room_Type Parameter is added in the Document or not!
try:
    if door_collector[0].LookupParameter("Room_Type").AsString():
        pass
except:
    forms.alert("No Room_Type Parameter Found in Document\n\n"
                "Run the Add Room Type Parameter First!", title = "Script Exiting", warn_icon = True)
    script.exit()


# Check if the Room_Type Parameters are filled according to the Excel File. 
options = forms.alert("Select the Door Design Database Excel File", title = "Open Excel File", warn_icon = False, options=["Select File"])
if options == "Select File":
    excel_path =  forms.pick_excel_file()
else:
    script.exit()

excel_workbook = xlrd.open_workbook(excel_path)
excel_worksheet = excel_workbook.sheet_by_index(1)
excel_room_types = []
for row in range(1, excel_worksheet.nrows):
    excel_room_types.append(excel_worksheet.cell_value(row,0).lower())

failed_rooms_message = []
for room in room_collector:
    if not room.LookupParameter("Room_Type").HasValue:
        failed_rooms_message.append("Room with Element ID - {} does not have the Room Type Parameter Filled" .format(output.linkify(room.Id)))

    elif room.LookupParameter("Room_Type").AsString() == "":
        failed_rooms_message.append("Room with Element ID - {} does not have the Room Type Parameter Filled" .format(output.linkify(room.Id)))
    
    else:
        if room.LookupParameter("Room_Type").AsString().lower() in excel_room_types:
            continue
        else:
            failed_rooms_message.append("Room with Element ID - {} contains an incorrect Room_Type Parameter" .format(output.linkify(room.Id)))

if failed_rooms_message:
    report = forms.alert("Rooms must have a valid Room_Type Parameter.\n\n"
                "Set the Parameter as per the Design Database.", title="Room_Type Error", warn_icon=True, options=["Show Report"])
    if report == "Show Report":
        for line in failed_rooms_message:
            print(line)
        script.exit()
    else:
        script.exit()

# Access the Room_Number Parameter in the Door
t = Transaction(doc, "Transfer Room Type Data")
t.Start()

failed_doors_message = []
for door in door_collector:
    if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "":
        failed_doors_message.append("Door with Element ID - {} does not have a Room Number".format(output.linkify(door.Id)))

if failed_doors_message:
    t.RollBack()
    result = forms.alert("There are Doors with Empty Room_Number Parameter\n\nCheck Report", title = "Aborting", warn_icon = True, options=["Show Report"])
    if result == "Show Report":
        for line in failed_doors_message:
            print(line)
    script.exit()

for door in door_collector:
    for room in room_collector:
        if door.LookupParameter("Room_Number").AsString() == room.LookupParameter("Number").AsString():
            door.LookupParameter("Room_Type").Set(room.LookupParameter("Room_Type").AsString().upper())

forms.alert("Room_Type Parameter filled in all Doors", title = "Script Completed", warn_icon = False)
t.Commit()
