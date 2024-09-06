# -*- coding: utf-8 -*-
'''3D to 2D Grids'''
__title__ = "3D-2D Grids"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import os

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()
view = doc.ActiveView


# MAIN
grids_collector = FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

t = Transaction(doc, "Convert to 2D Grids")
t.Start()

# Convert all Grids to ViewSpecific Grids
for grid in grids_collector:
    grid.SetDatumExtentType(DatumEnds.End0, view, DatumExtentType.ViewSpecific)
    grid.SetDatumExtentType(DatumEnds.End1, view, DatumExtentType.ViewSpecific)


t.Commit()