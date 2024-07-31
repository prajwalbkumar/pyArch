# -*- coding: utf-8 -*-
'''Add Room Type Parameter'''
__title__ = "Add Room Type Parameter"
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

# Setting up the Shared Parameter
door_category = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Doors) # Returns a Category Obejct that contains all categories. In this case a Category of just Doors. doc.Settings accesse all the settings in the Revit Applcaition. Here specifically asking the categories to be listed
room_category = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Rooms)
category_set = app.Create.NewCategorySet() # Creates a Category Set (Group of Categories) to perform function on them. This is an empty Category Set now
category_set.Insert(door_category)
category_set.Insert(room_category)

shared_parameter_file_name = "DoorAutomationSharedParameter.txt"
shared_parameter_file_path = os.path.join(script_dir, shared_parameter_file_name) 
original_shared_file = r"K:\BIM\2021\Revit\Dar\Shared_txt_files\All Trades-Shared Parameters.txt"

app.SharedParametersFilename = shared_parameter_file_path # Give the path to the Shared Parameter File
shared_parameter_file = app.OpenSharedParameterFile() # Access the Shared Parameter File
# Returns a DefinitionFile 

if shared_parameter_file is None:
    raise ValueError("Shared parameter file not found")

group = shared_parameter_file.Groups.get_Item("Room") # Retrieve a specific Parameter Group

if group is None:
    raise ValueError("Group 'Room' not found in shared parameter file")

external_definition = group.Definitions.get_Item("Room_Type")
if external_definition is None:
    raise ValueError("Definition 'Room_Type' not found in shared parameter file")

t = Transaction(doc, "Create Shared Parameter")
t.Start()

# Binding Parameter to the Category
newIB = app.Create.NewInstanceBinding(category_set)

# Parameter Group Set to Text
binding_map = doc.ParameterBindings
if not binding_map.Insert(external_definition, newIB, BuiltInParameterGroup.PG_IDENTITY_DATA):
    binding_map.ReInsert(external_definition, newIB, BuiltInParameterGroup.PG_IDENTITY_DATA)

t.Commit()
app.SharedParametersFilename = original_shared_file

forms.alert("Room_Type Parameter successfully added to Room and Door Categories!", title = "Script Completed", warn_icon = False)