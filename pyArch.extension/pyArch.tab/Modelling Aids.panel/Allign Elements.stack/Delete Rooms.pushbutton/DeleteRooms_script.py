# -*- coding: utf-8 -*-
'''Delete Rooms'''
__title__ = "Delete Rooms"
__author__ = "prajwalbkumar"

# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import os
from System.Collections.Generic import List

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()

# MAIN
all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

not_placed_rooms = []
not_enclosed_rooms = []

for room in all_rooms:
    if room.Area == 0:
        if not room.Location:
            not_placed_rooms.append(room)
        else:
            not_enclosed_rooms.append(room)

input1 = ""
input2 = ""

if not_placed_rooms:
    input1 = forms.alert("There are NOT PLACED rooms in the model \n"
                        "Would you like to delete them?", title = "Delete Rooms", warn_icon = True, options = ["Ok", "No"])

if not_enclosed_rooms:
    input2 = forms.alert("There are NOT ENCLOSED rooms in the model \n"
                        "Would you like to delete them?", title = "Delete Rooms", warn_icon = True, options = ["Ok", "Show Report"])

if input2 == "Show Report":
    failed_data = []
    for room in not_enclosed_rooms:
        failed_data.append([output.linkify(room.Id),room.Level.Name.upper(),room.LookupParameter("Name").AsString().upper(),room.LookupParameter("Number").AsString().upper()])
        
    output.print_md("##⚠️ Not Enclosed Rooms Found ☹️") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ There are Issues in your Model.")  # Print a Line
    output.print_table(table_data=failed_data, columns=["ELEMENT ID","LEVEL", "ROOM NAME", "ROOM NUMBER"]) # Print a Table
    output.print_md("---") # Markdown Line Break

count = 0

if input1 == "Ok":
    t = Transaction(doc, "Delete Not Placed Rooms")
    t.Start()
    for room in not_placed_rooms:
        count += 1
        doc.Delete(room.Id)
    t.Commit()

if input2 == "Ok":
    t = Transaction(doc, "Delete Not Enclosed Rooms")
    t.Start()
    for room in not_enclosed_rooms:
        count += 1
        doc.Delete(room.Id)
    t.Commit()

if count:
    forms.alert("{} Room(s) have been deleted" .format(count), title = "Rooms Deleted", warn_icon = False)
if not count:
    forms.alert("No Rooms Deleted", title = "Run Successful", warn_icon = False)





