# -*- coding: utf-8 -*-
'''Check Discrepencies for Door & Room Relationship'''

__title__ = "Room Data Validator"
__author__ = "prajwalbkumar"

# IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script, output
import os
import xlrd

script_dir = os.path.dirname(__file__)
ui_doc  = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()

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
test_list = ["Check Room_Number Parameter", "Check Room_Name Parameter", "Check Sequencing"]

# Choose a Test to Run
test = forms.SelectFromList.show(test_list, title = "Select Door Test", width=300, height=300, button_name="Select Test", multiselect=False)

# Error
if not test:
    script.exit()

# Door - Room Numbers Checks
elif test == test_list[0]:
    for door in door_elements:
        door_mark = door.LookupParameter("Mark").AsString()
        door_room_number = door.LookupParameter("Room_Number")
        if not door_room_number.HasValue:
            print("{} - Door has no Room Number" .format(door_mark)) #Print the Element ID
            print ("\n")
        elif door_room_number.AsString() == "":
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
    forms.alert("Room Number Checks Completed. Refer to the Report if any errors!", title = "Script Completed", warn_icon = False)
    script.exit()

# Door - Room Names Checks
elif test == test_list[1]:
    for door in door_elements:
        door_mark = door.LookupParameter("Mark").AsString()
        door_room_name = door.LookupParameter("Room_Name")
        if not door_room_name.HasValue:
            print("{} - Door has no Room Name" .format(door_mark)) #Print the Element ID
            print ("\n")
        elif door_room_name.AsString() == "":
            print("{} - Door has no Room Name" .format(door_mark)) #Print the Element ID
            print ("\n")
    forms.alert("Room Name Checks Completed. Refer to the Report if any errors!", title = "Script Completed", warn_icon = False)
    script.exit()

# Door - Sequence Checks
elif test == test_list[2]:
    all_room_numbers = []
    # print(len(door_elements))
    for door in door_elements:
        door_mark = door.LookupParameter("Mark").AsString()
        door_room_number = door.LookupParameter("Room_Number")

        if not door_room_number.HasValue:
            forms.alert("Missing Room Numbers in Doors. Run the Room Number Check First", title="Script Cancelled")
            script.exit()
        
        elif door_room_number.AsString() == "":
            forms.alert("Missing Room Numbers in Doors. Run the Room Number Check First", title="Script Cancelled")
            script.exit()

        else:
            all_room_numbers.append(door_room_number.AsString())

    #Get the list of all unique Door Room Numbers
    unique_room_numbers = list(set(all_room_numbers))

    for unq_room_number in unique_room_numbers:
        # Store the Indices of unique occurances of the "Room Number" in "All Room Numbers"
        unq_indices = []
        for (index, item) in enumerate(all_room_numbers):
            if item == unq_room_number:
                unq_indices.append(index)
        # print(unq_indices)

        if len(unq_indices) > 1:
            mark_character = []
            flag = False
            for index in unq_indices:
                # Check the Last Character of the Mark Value.
                door_mark = door_elements[index].LookupParameter("Mark").AsString()
                door_mark = door_mark.lower()
                # print(door_mark)
                # If Last Character is a Digit, Tell the user that not all doors in [ROOM NUMBER] are sequenced with characters
                if door_mark[-1].isdigit():
                    print("Doors in Room {} should have an alphabetical sequence." .format(unq_room_number))
                    flag = True
                # If not then append the character to the mark_character list
                else:
                    mark_character.append(door_mark[-1])

            if flag:
                continue
            
            mark_character_string = "".join(sorted(mark_character))
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            index = 0
            for char in mark_character_string:
                if not char == alphabet[index]:
                    print("Doors in Room {} have incorrect sequencing." .format(unq_room_number))
                index += 1
    forms.alert("Room Sequencing Checks Completed. Refer to the Report if any errors!", title = "Script Completed", warn_icon = False)
    script.exit()
