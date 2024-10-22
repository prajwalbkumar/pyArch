# -*- coding: utf-8 -*-
'''Rename Types'''
__title__ = "Rename Types"
__author__ = "prajwalbkumar"


from Autodesk.Revit.DB import *
from pyrevit import script, forms

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()

import time
from datetime import datetime
from Extract.RunData import get_run_data

start_time = time.time()
manual_time = 0
total_element_count = 0

try:

    all_doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).OfClass(FamilySymbol)

    if not all_doors:
        script.exit()


    unique_doors = []
    failed_data = []
    t = Transaction(doc, "Rename Doors")
    t.Start()

    manual_time = manual_time + 180
    total_door = []
    for door in all_doors:
        total_door.append(door)
        
    total_element_count = total_element_count + len(total_door) 

    for door in all_doors:
        try:
            door_width = str(int(door.LookupParameter("Width").AsValueString()))
            door_height = str(int(door.LookupParameter("Height").AsValueString()))
            leaf_finish = door.LookupParameter("Leaf_Face_Finish").AsValueString()
            frame_finish = door.LookupParameter("Frame_Face_Finish").AsValueString()
        except:
            failed_data.append([door.FamilyName.upper(), door.LookupParameter("Type Name").AsValueString().upper(), "NONE"])
            continue

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
        output.print_md("** SIMILAR TYPE NAME FOUND**  - Replace the duplicate type with their correct types.")


    end_time = time.time()
    runtime = end_time - start_time
            
    run_result = "Tool ran successfully"
    if total_element_count:
        element_count = total_element_count
    else:
        element_count = 0

    error_occured ="Nil"

    get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)

except Exception as e:
    
  
    end_time = time.time()
    runtime = end_time - start_time

    error_occured = "Error occurred: {}".format(str(e))
    run_result = "Error"
    element_count = 0
    
    get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)
    forms.alert(
        "An error has occurred.\n"
        "Please reach out to the author.\n\n"
        "Author - {}.".format(__author__),
        title="{} - Script Terminated".format(__title__),
        warn_icon=True
    )