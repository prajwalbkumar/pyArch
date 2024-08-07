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

# Function to get the bounding box of a grid
def get_bounding_box(grid):
    location_curve = grid.Curve
    curve_start = location_curve.GetEndPoint(0)
    curve_end = location_curve.GetEndPoint(1)
    
    # Create a bounding box that encompasses the curve
    bbox = BoundingBoxXYZ()
    
    # Extend the box to include the grid's full extent
    min_x = min(curve_start.X, curve_end.X) - 1
    min_y = min(curve_start.Y, curve_end.Y) - 1
    max_x = max(curve_start.X, curve_end.X) + 1
    max_y = max(curve_start.Y, curve_end.Y) + 1
    bbox.Min = XYZ(min_x, min_y, -10)  # Extend downward to cover vertical extent
    bbox.Max = XYZ(max_x, max_y, 10)   # Extend upward to cover vertical extent
    
    return bbox


# Collect all linked instances
linked_instance = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
link_name = []
for link in linked_instance:
    link_name.append(link.Name)

urs_instance_name = forms.SelectFromList.show(link_name, title = "Select URS File", width=600, height=300, button_name="Select File", multiselect=False)
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
for grid in urs_grids:
    failed_urs_grid = []
    if not grid.Name in active_grids_name:
        failed_urs_grid.append(grid.Id)
        failed_urs_grid.append(grid.Name) # Grid Name
        failed_urs_grid.append("GRID MISSING IN ACTIVE DOCUMENT") # Error Code
        failed_data.append(failed_urs_grid)

# Check if all Active Grid Names are present in the URS Doc Grids List
for grid in active_grids:
    failed_urs_grid = []
    if not grid.Name in urs_grids_name:
        failed_urs_grid.append(output.linkify(grid.Id))
        failed_urs_grid.append(grid.Name) # Grid Name
        failed_urs_grid.append("GRID MISSING IN URS DOCUMENT") # Error Code
        failed_data.append(failed_urs_grid)

# Check the location of all Active grids against the URS Grids
for active_grid in active_grids:
    failed_urs_grid = []
    for urs_grid in urs_grids:
        if active_grid.Name == urs_grid.Name:
            bbox = get_bounding_box(urs_grid)
            filter = BoundingBoxIntersectsFilter(Outline((bbox.Min),(bbox.Max))) 
            collector = FilteredElementCollector(doc).WherePasses(filter).OfCategory(BuiltInCategory.OST_Grids).ToElements()
            for item in collector:
                print (item.Name)
            if collector == active_grid:
                failed_urs_grid.append(output.linkify(active_grid.Id))
                failed_urs_grid.append(active_grid.Name) # Grid Name
                failed_urs_grid.append("GRID LOCATION INCORRECT") # Error Code
                failed_data.append(failed_urs_grid)


if failed_data:
    output.print_md("##⚠️ URS Checks Completed. Issues Found ☹️") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
    output.print_table(table_data=failed_data, columns=["ELEMENT ID", "GRID NAME", "ERROR CODE"]) # Print a Table
    print("\n\n")
    output.print_md("---") # Markdown Line Break
    output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
    output.print_md("---") # Markdown Line Break
    output.print_md("**GRID MISSING IN ACTIVE DOCUMENT**  - The active document has missing grids. It must match the URS.") # Print a Quote
    output.print_md("**GRID MISSING IN URS DOCUMENT**     - There are extra grids or grids with incorrect names in the active document. They must match the URS.") # Print a Quote
    output.print_md("**GRID LOCATION INCORRECT**          - The grid location in the active document is incorrect. It must match the URS!") # Print a Quote
    output.print_md("---") # Markdown Line Break

else:
    output.print_md("##✅ URS Checks Completed. No Issues Found 😃") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break