# -*- coding: utf-8 -*-
'''Check Discrepencies for Door & Room Relationship'''

__title__ = "Room Data Validator"
__author__ = "prajwalbkumar"

# IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import csv 
import os

script_dir = os.path.dirname(__file__)
ui_doc  = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
# FUNCTIONS

def convert_internal_units(value, get_internal=False, units="mm"):
    if rvt_year >= 2021:
        if units == "m":
            units = UnitTypeId.Meters
        elif units == "m2":
            units = UnitTypeId.SquareMeters
        elif units == "cm":
            units = UnitTypeId.Centimeters
        elif units == "mm":
            units = UnitTypeId.Millimeters

    if get_internal:
        return UnitUtils.ConvertToInternalUnits(value, units)
    return UnitUtils.ConvertFromInternalUnits(value, units)     


# MAIN
door_elements = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
test_list = ["Room Number Checks", "Room Name Checks", "Sequencing Checks", "Room Function Checks"]

# Choose a Test to Run
test = forms.SelectFromList.show(test_list, title = "Select Target Test", width=300, height=300, button_name="Select Test", multiselect=False)

# Door - Room Numbers Checks
if test == test_list[0]:
    for door in door_elements:
        door_mark = door.LookupParameter("Mark").AsString()
        door_room_number = door.LookupParameter("Room_Number")

        if not door_room_number.HasValue:
            print("{} - Door has no Room Number" .format(door_mark)) #Print the Element ID
            print ("\n")
        else:

            if door_mark[-1].isdigit():
                # Check if the Mark Value is equal to the Room_Number Parameter
                if not door_mark == door_room_number.AsString():
                    print("{} - Door has a mismatch with the Room Number" .format(door_mark))
            else:
                if not door_mark[:-1] == door_room_number.AsString():
                    print("{} - Door has a mismatch with the Room Number" .format(door_mark))
        print("\n")

# Door - Room Names Checks
if test == test_list[1]:
    for door in door_elements:
        door_mark = door.LookupParameter("Mark").AsString()
        door_room_number = door.LookupParameter("Room_Name")

        if not door_room_number.HasValue:
            print("{} - Door has no Room Number" .format(door_mark)) #Print the Element ID
            print ("\n")
        print ("\n")

# Door - Room Names Checks
else:
    forms.alert("No Check Selected", title="Script Cancelled")
    script.exit()