# -*- coding: utf-8 -*-
'''Rename Types'''
__title__ = "Rename Types"
__author__ = "prajwalbkumar"


from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()

all_doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).OfClass(FamilySymbol)

if not all_doors:
    script.exit()


unique_doors = []
failed_data = []
t = Transaction(doc, "Rename Doors")
t.Start()

for door in all_doors:

    door_width = door.LookupParameter("Width").AsValueString()
    door_height = door.LookupParameter("Height").AsValueString()
    leaf_finish = door.LookupParameter("Leaf_Face_Finish").AsValueString()
    frame_finish = door.LookupParameter("Frame_Face_Finish").AsValueString()

    new_name = door_width + "X" + door_height + "-" + leaf_finish + "-" + frame_finish
    
    if new_name + " " + door.FamilyName not in unique_doors:
        unique_doors.append(new_name + " " + door.FamilyName)
        # Change the name of the family
        door.Name = new_name

    else:
        failed_data.append([door.FamilyName.upper(), door.LookupParameter("Type Name").AsValueString().upper(), new_name])
            
t.Commit()

if failed_data:
    output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(__title__)) # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ There are Duplicates door types in the model. Refer to the **Table Report** below for reference")  # Print a Line
    output.print_table(table_data=failed_data, columns=["FAMLIY NAME","EXISTING TYPE NAME", "CORRECT TYPE NAME"]) # Print a Table
    print("\n\n")
    output.print_md("---") # Markdown Line Break``
    output.print_md("***✅ REFERENCE***")  # Print a Line
    output.print_md("---") # Markdown Line Break
    output.print_md("** SIMILAR TYPE NAME FOUND**  - Replace the duplicate type with their unique types.")