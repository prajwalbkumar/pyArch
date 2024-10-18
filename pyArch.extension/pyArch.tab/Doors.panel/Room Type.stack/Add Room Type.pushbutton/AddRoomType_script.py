# -*- coding: utf-8 -*-
'''Add Room Type'''
__title__ = "Add Room Type"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from pyrevit import forms, script
import os
import xlrd
import random

import time
from datetime import datetime
from Extract.RunData import get_run_data

start_time = time.time()
manual_time = 0
total_element_count = 0

# Get the directory two levels above the current script directory
script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
excel_filename = "Door Design Database.xlsx"
excel_path = os.path.join(parent_dir, excel_filename)

doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object

def get_random_color(pastel_factor = 0.5):
    return [(int((x+pastel_factor)/(1.0+pastel_factor) * 255)) for x in [random.uniform(0,1.0) for i in [1,2,3]]]

def color_distance(c1,c2):
    return sum([abs(x[0]-x[1]) for x in zip(c1,c2)])

def generate_new_color(existing_colors,pastel_factor = 0.5):
    max_distance = None
    best_color = None
    for i in range(0,100):
        color = get_random_color(pastel_factor = pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color,c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color


try:
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

    # # Check if the Room_Type Parameters are filled according to the Excel File. 
    # options = forms.alert("Select the Door Design Database Excel File", title = "Open Excel File", warn_icon = False, options=["Select File"])
    # if options == "Select File":
    #     excel_path =  forms.pick_excel_file()
    # else:
    #     script.exit()

    excel_workbook = xlrd.open_workbook(excel_path)
    excel_worksheet = excel_workbook.sheet_by_index(1)
    excel_room_types = []
    for row in range(1, excel_worksheet.nrows):
        excel_room_types.append(excel_worksheet.cell_value(row,0).upper())

    t = Transaction(doc, "Add Room_Type Values")
    t.Start()

    # Binding Parameter to the Category
    newIB = app.Create.NewInstanceBinding(category_set)

    # Parameter Group Set to Text
    binding_map = doc.ParameterBindings
    if not binding_map.Insert(external_definition, newIB, BuiltInParameterGroup.PG_IDENTITY_DATA):
        binding_map.ReInsert(external_definition, newIB, BuiltInParameterGroup.PG_IDENTITY_DATA)

    color_schemes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ColorFillSchema)

    exisiting_scheme_names = []
    for scheme in color_schemes:
        exisiting_scheme_names.append(scheme.Name)
        

    for scheme in color_schemes:
        if not "Room Type" in exisiting_scheme_names:
            if scheme.CategoryId == Category.GetCategory(doc, BuiltInCategory.OST_Rooms).Id:
                color_fill_scheme = scheme
                room_type_scheme = doc.GetElement(color_fill_scheme.Duplicate("Room Type"))
                break
        else:
            if scheme.Name == "Room Type":
                room_type_scheme = scheme
                break

    room_type_parameter = FilteredElementCollector(doc).WhereElementIsNotElementType().OfClass(SharedParameterElement)

    for parameter in room_type_parameter:
        if parameter.Name == "Room_Type":
            room_type_parameter_id = parameter.Id
            break

    color_fill_scheme_entries = []
    colors = []
    for room_type in excel_room_types:
        total_element_count += 1
        entry_color = generate_new_color((colors),pastel_factor = 0.9)
        colors.append(entry_color)
        r, g, b, = entry_color
        color = Color(r, g, b)

        entry = ColorFillSchemeEntry(StorageType.String)
        entry.SetStringValue(room_type)
        entry.Color = color
        color_fill_scheme_entries.append(entry)



    room_type_scheme.ParameterDefinition = room_type_parameter_id
    room_type_scheme.SetEntries(color_fill_scheme_entries)



    t.Commit()
    app.SharedParametersFilename = original_shared_file

    forms.alert("Room_Type Parameter successfully added to Room and Door Categories!", title = "Script Completed", warn_icon = False)


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