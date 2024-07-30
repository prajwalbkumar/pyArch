# -*- coding: utf-8 -*-
'''Copy Room Type Data'''
__title__ = "Copy Room Type Data"
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


# MAIN SCRIPT

# Get all the Doors in the Document
door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
room_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

# Access the Room_NumberParameter in the Door
t = Transaction(doc, "Transfer Room Type Data")
t.Start()
for door in door_collector:
    if not door.LookupParameter("Room_Number").HasValue:
        forms.alert("Room Number for Doors is not filled, Run the DAR Door Addin First!", title = "Script Exited", warn_icon = True)
        t.Commit()
        script.exit()

    elif door.LookupParameter("Room_Number").AsString() == "":
        forms.alert("Room Number for Doors is not filled, Run the DAR Door Addin First!", title = "Script Exited", warn_icon = True)
        t.Commit()
        script.exit()        

    if door.LookupParameter("Room_Type") is None:
        forms.alert("No Room_Type Parameter Found, Run the Add Room Type Parameter Tool first!", title = "Script Exited", warn_icon = True)
        t.Commit()
        script.exit()
    
    else:
        for room in room_collector:
            if not room.LookupParameter("Room_Type").HasValue:
                forms.alert("Make sure all the Rooms have their Room_Type Parameter Filled", title = "Script Exited", warn_icon = True)
                t.Commit()
                script.exit()

            elif room.LookupParameter("Room_Type").AsString() == "":
                forms.alert("Make sure all the Rooms have their Room_Type Parameter Filled", title = "Script Exited", warn_icon = True)
                t.Commit()
                script.exit()  
            
            else:
                if door.LookupParameter("Room_Number") == room.LookupParameter("Number"):
                    door.LookupParamter("Room_Type").Set(room.LookupParameter("Room_Type").AsString())

t.Commit()

# Find the same Room with number "Room_Number" parameter
# Get the Room_Type parameter of the Room
# Copy it to the Door

