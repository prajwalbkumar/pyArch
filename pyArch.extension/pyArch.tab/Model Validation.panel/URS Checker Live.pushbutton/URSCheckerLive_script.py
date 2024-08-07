# -*- coding: utf-8 -*-
'''URS Checker'''
__title__ = "URS Checker Live"
__author__ = "prakritisrimal - prajwalbkumar"

# IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script, output
import os
import xlrd

script_dir = os.path.dirname(__file__)
ui_doc  = __revit__.ActiveUIDocument
doc     = __revit__.ActiveUIDocument.Document # Get the Active Document
app     = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()

# Collect all linked instances
linked_instance = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
link_name = []
for link in linked_instance:
    link_name.append(link.Name)

urs_instance_name = forms.SelectFromList.show(link_name, title = "Select URS File", width=300, height=300, button_name="Select File", multiselect=False)
for link in linked_instance:
    if urs_instance_name == link.Name:
        urs_instance = link
        break

urs_doc = urs_instance.GetLinkDocument()

if not urs_doc:
    forms.alert("No instance found of the selected URS File.\n"
                "Use Manage Links to Load the Link in the File!", title = "Link Missing", warn_icon = False)
    script.exit()

# Check for Grids
active_grids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
urs_grids = FilteredElementCollector(urs_doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

if not active_grids:
    forms.alert("No grids found in the active document", title = "Grids Missing", warn_icon = False)
    script.exit()

active_grids_name = []
urs_grids_name = []
for grid in active_grids:
    active_grids_name.append(grid.Name)

for grid in urs_grids:
    urs_grids_name.append(grid.Name)


# Check if all URS Grid Names are present in the Active Doc Grids List
failed_data = []
for grid in urs_grids_name:
    failed_urs_grid = []
    if not grid in active_grids_name:
        failed_urs_grid.append(grid)
        failed_door_data.append(output.linkify(door.Id))
        failed_urs_grid.append("GRID MISSING IN ACTIVE DOCUMENT")
        failed_data.append(failed_urs_grid)


# Check 

if failed_data:
    output.print_md("##⚠️ URS Checks Completed. Issues Found ☹️") # Markdown Heading 2
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

else:
    output.print_md("##✅ URS Checks Completed. No Issues Found 😃") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break