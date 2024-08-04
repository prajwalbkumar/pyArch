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

# Choose a Test to Run
test_list = ["Check Room_Number Parameter", "Check Room_Name Parameter", "Check Door Sequencing"]
selected_test = forms.SelectFromList.show(test_list, title = "Select Door Test", width=300, height=300, button_name="Select Test", multiselect=True)

# Error
if not selected_test:
    script.exit()

# No Error
for test in selected_test:
    # Door - Room Numbers Checks
    if test == test_list[0]:
        failed_data = []
        for door in door_elements:
            failed_door_data = []
            door_mark = door.LookupParameter("Mark").AsString()
            door_room_number = door.LookupParameter("Room_Number")
            if not door_room_number.HasValue:
                failed_door_data.append(output.linkify(door.Id))
                failed_door_data.append(door_mark.upper())
                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                failed_door_data.append("NO ROOM NUMBER FOUND")
                failed_data.append(failed_door_data)
                continue
            elif door_room_number.AsString() == "":
                failed_door_data.append(output.linkify(door.Id))
                failed_door_data.append(door_mark.upper())
                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                failed_door_data.append("NO ROOM NUMBER FOUND")
                failed_data.append(failed_door_data)
                continue
            else:
                if door_mark[-1].isdigit():
                    # Check if the Mark Value is equal to the Room_Number Parameter
                    if not door_mark == door_room_number.AsString():
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door_mark.upper())
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                        failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                        failed_door_data.append("MARK & ROOM_NUMBER MISMATCH")
                        failed_data.append(failed_door_data)
                        continue
                else:
                    if not door_mark[:-1] == door_room_number.AsString():
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door_mark.upper())
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                        failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                        failed_door_data.append("MARK & ROOM_NUMBER MISMATCH")
                        failed_data.append(failed_door_data)

        # Print Reports
        if failed_data:
            output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(test)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM NAME", "ROOM NUMBER", "ERROR CODE"]) # Print a Table
            print("\n\n")
            output.print_md("---") # Markdown Line Break
            output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
            output.print_md("---") # Markdown Line Break
            output.print_md("**NO ROOM NUMBER FOUND**         - Room_Number Parameter Empty in the Door. Run the DAR Door Add-In.") # Print a Quote
            output.print_md("**MARK & ROOM_NUMBER MISMATCH**  - Room_Number & Mark Value do not Match for the Door. Run the DAR Door Add-In.") # Print a Quote
            output.print_md("---") # Markdown Line Break
        else:
            output.print_md("##✅ {} Completed. No Issues Found 😃" .format(test)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
            

    # Door - Room Names Checks
    elif test == test_list[1]:
        failed_data = []
        for door in door_elements:
            failed_door_data = []
            door_mark = door.LookupParameter("Mark").AsString()
            door_room_name = door.LookupParameter("Room_Name")
            if not door_room_name.HasValue:
                failed_door_data.append(output.linkify(door.Id))
                failed_door_data.append(door_mark.upper())
                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                failed_door_data.append("NO ROOM NAME FOUND")
                failed_data.append(failed_door_data)
                continue
            elif door_room_name.AsString() == "":
                failed_door_data.append(output.linkify(door.Id))
                failed_door_data.append(door_mark.upper())
                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                failed_door_data.append("NO ROOM NAME FOUND")
                failed_data.append(failed_door_data)

        # Print Reports
        if failed_data:
            output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(test)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
            output.print_table(table_data=failed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "ERROR CODE"]) # Print a Table
            print("\n\n")
            output.print_md("---") # Markdown Line Break
            output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
            output.print_md("---") # Markdown Line Break
            output.print_md("**NO ROOM NAME FOUND** - Room_Name Parameter Empty in the Door. Run the DAR Door Add-In.") # Print a Quote
            output.print_md("---") # Markdown Line Break
        else:
            output.print_md("##✅ {} Completed. No Issues Found 😃" .format(test)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break

    # Door - Sequence Checks
    elif test == test_list[2]:
        failed_data = []
        all_room_numbers = []
        # print(len(door_elements))
        for door in door_elements:
            failed_door_data = []
            door_mark = door.LookupParameter("Mark").AsString()
            door_room_number = door.LookupParameter("Room_Number")

            if not door_room_number.HasValue:
                failed_door_data.append(output.linkify(door.Id))
                failed_door_data.append(door_mark.upper())
                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                failed_door_data.append("NO ROOM NUMBER FOUND")
                failed_data.append(failed_door_data)
                continue
            
            elif door_room_number.AsString() == "":
                failed_door_data.append(output.linkify(door.Id))
                failed_door_data.append(door_mark.upper())
                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                failed_door_data.append("NO ROOM NUMBER FOUND")
                failed_data.append(failed_door_data)
                continue

            else:
                all_room_numbers.append(door_room_number.AsString())

        if failed_data:
            output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(test)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK", "LEVEL",  "ROOM NAME", "ROOM NUMBER", "ERROR CODE"]) # Print a Table
            print("\n\n")
            output.print_md("---") # Markdown Line Break
            output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
            output.print_md("---") # Markdown Line Break
            output.print_md("**NO ROOM NUMBER FOUND** - Having Room Numbers in Doors is critical to test the Door Sequencing\n") # Print a Quote
            output.print_md("---") # Markdown Line Break
            script.exit()

        #Get the list of all unique Door Room Numbers
        unique_room_numbers = list(set(all_room_numbers))
        failed_data = []
        for unq_room_number in unique_room_numbers:
            failed_door_data = []
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
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door_mark.upper())
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                        failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                        failed_door_data.append("ALPHABETICAL SEQUENING REQUIRED")
                        failed_data.append(failed_door_data)
                        flag = True
                    # If not then append the character to the mark_character list
                    else:
                        mark_character.append(door_mark[-1])

                if flag:
                    continue
                
                mark_character_string = "".join(sorted(mark_character))
                alphabet = "abcdefghijklmnopqrstuvwxyz"
                for char in mark_character_string:
                    failed_door_data = []
                    if not char == alphabet[index]:
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door_mark.upper())
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        failed_door_data.append(door.LookupParameter("Room_Name").AsString().upper())
                        failed_door_data.append(door.LookupParameter("Room_Number").AsString().upper())
                        failed_door_data.append("INCORRECT SEQUENCING")
                        failed_data.append(failed_door_data)
        if failed_data:
            output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(test)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "ERROR CODE"]) # Print a Table
            print("\n\n")
            output.print_md("---") # Markdown Line Break
            output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
            output.print_md("---") # Markdown Line Break
            output.print_md("**ALPHABETICAL SEQUENING REQUIRED** - Sequencing must be Alphabetical\n") # Print a Quote
            output.print_md("**INCORRECT SEQUENCING**            - Sequencing skips few ordered characters.\n") # Print a Quote
            output.print_md("---") # Markdown Line Break
            script.exit()

        else:
            output.print_md("##✅ {} Completed. No Issues Found 😃" .format(test)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
    
        script.exit()
