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

# Find the View that Equals to "Failed Doors Schedule"
views = (FilteredElementCollector(doc)
         .OfClass(ViewSchedule)
         .WhereElementIsNotElementType()
         .ToElements())
for view in views:
    if view.Name == "Failed Doors Schedule":

        t = Transaction(doc, "Delete Schedule")
        t.Start()

        doc.Delete(view.Id)

        t.Commit()

# Clear all values from the "FLS_Comment" parameter

doors = (FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
        .ToElements())

t = Transaction(doc, "Clear FLS_Comment Values")
t.Start()
for door in doors:
    parameter = door.LookupParameter("FLS_Comment")
    if parameter.HasValue:
        parameter.ClearValue()
t.Commit()