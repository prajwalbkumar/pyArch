# -*- coding: utf-8 -*-
'''Clear the Schedule Created by the FLS Door Validator Tool'''

__title__ = "Purge Validated Data"
__author__ = "prajwalbkumar"

# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import csv 
import os

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)

# Clear all values from the "FLS_Comment" parameter

doors = (FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
        .ToElements())

t = Transaction(doc, "Clear FLS_Comment Values")
t.Start()
for door in doors:
    parameter = door.LookupParameter("FLS_Comment")
    try:
        if parameter.HasValue:
            parameter.ClearValue()

    except:
        forms.alert("No FLS_Comment Parameter Found. Run the FLS Door Validator Tool First!", title='Script Cancelled')
        t.Commit()
        script.exit()
t.Commit()

# Find all the Schedule Views
views = (FilteredElementCollector(doc)
         .OfClass(ViewSchedule)
         .WhereElementIsNotElementType()
         .ToElements())

for view in views:
    if view.Name == "Failed Doors Schedule": 
        target_view_id = view.Id


# Close the Schedule View
open_views = ui_doc.GetOpenUIViews()
for open_view in open_views:
    try:
        if target_view_id:
            if open_view.ViewId == target_view_id: # ID of the View == ID of the Failed Doors Schedule View
                open_view.Close()
                break
    except:
        forms.alert("This is the Only Open View in the Document, Open another view and Run the tool again!", title='Script Cancelled') # THIS MESSAGE is unexpecctedly thrown
        script.exit()

# Find the View that Equals to "Failed Doors Schedule" and Delete
for view in views:
    if view.Name == "Failed Doors Schedule":  
        t = Transaction(doc, "Delete Schedule")
        t.Start()
        doc.Delete(view.Id)
        t.Commit()
        break