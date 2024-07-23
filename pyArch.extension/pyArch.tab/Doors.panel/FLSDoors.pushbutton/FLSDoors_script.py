# -*- coding: utf-8 -*-
'''FLS Doors Validator'''

__title__ = "FLS Doors Validator"
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


def convert_internal_units(value, get_internal=False, units="mm"):
    if rvt_year >= 2021:
        if units == "m":
            units = UnitTypeId.Meters
        elif units == "m2":
            units = UnitTypeId.SquareMeters
        elif units == "cm":
            units = UnitTypeId.Centimeters
        elif units == "mm":
            units = UnitTypeId.Millimeters

    if get_internal:
        return UnitUtils.ConvertToInternalUnits(value, units)
    return UnitUtils.ConvertFromInternalUnits(value, units)


# Definition to Get all the Door Instances in the Document
def doors_in_document():
    doors = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    return doors


# Definition to extract data from the CSV File
def code_csv_reader():
    try:
        csv_filename = "FLS Door Codes.csv"
        file = os.path.join(script_dir, csv_filename) 
        # file = r"C:\Users\pkumar2\Desktop\pyRevit Toolbars\UnBlunder\unBlunder.extension\unBlunder.tab\Doors.panel\FLSDoors.pushbutton\FLS Door Codes.csv"
        with open(file, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)

            code = []
            min_single_leaf = []
            min_unq_main_leaf = []
            min_unq_side_leaf = []
            min_double_leaf = []
            max_single_leaf = []
            max_unq_main_leaf = []
            max_unq_side_leaf = []
            max_double_leaf = []
            min_height = []

            for row in csv_reader:
                code.append(row["CODE"])
                min_single_leaf.append(row["MIN SINGLE LEAF"])
                min_unq_main_leaf.append(row["MIN UNQ MAIN LEAF"])
                min_unq_side_leaf.append(row["MIN UNQ SIDE LEAF"])
                min_double_leaf.append(row["MIN DOUBLE LEAF"])
                max_single_leaf.append(row["MAX SINGLE LEAF"])
                max_unq_main_leaf.append(row["MAX UNQ MAIN LEAF"])
                max_unq_side_leaf.append(row["MAX UNQ SIDE LEAF"])
                max_double_leaf.append(row["MAX DOUBLE LEAF"])
                min_height.append(row["MIN HEIGHT"])

            return (
                code,
                min_single_leaf,
                min_unq_main_leaf,
                min_unq_side_leaf,
                min_double_leaf,
                max_single_leaf,
                max_unq_main_leaf,
                max_unq_side_leaf,
                max_double_leaf,
                min_height,
            )
    except:
        forms.alert("CSV Not Found - Contact the Author to Troubleshoot!", title='Script Cancelled')
        script.exit()


# MAIN SCRIPT
(
    code,
    min_single_leaf,
    min_unq_main_leaf,
    min_unq_side_leaf,
    min_double_leaf,
    max_single_leaf,
    max_unq_main_leaf,
    max_unq_side_leaf,
    max_double_leaf,
    min_height,
) = code_csv_reader()

# UI to Select the Code
user_code = forms.SelectFromList.show(
    code, title="Select Relevent Code", width=300, height=500, button_name="Select Code", multiselect=False
)

if not user_code:
    forms.alert("No Code Selected", title="Script Cancelled")
    script.exit()

# Find the Index Values of the Code Selected from the Main Code List
code_row = code.index(user_code)

# Get the Value of the Rows against the Code Selected
min_single_leaf = int(min_single_leaf[code_row])
min_unq_main_leaf = int(min_unq_main_leaf[code_row])
min_unq_side_leaf = int(min_unq_side_leaf[code_row])
min_double_leaf = int(min_double_leaf[code_row])

max_single_leaf = int(max_single_leaf[code_row])
max_unq_main_leaf = int(max_unq_main_leaf[code_row])
max_unq_side_leaf = int(max_unq_side_leaf[code_row])
max_double_leaf = int(max_double_leaf[code_row])

min_height = int(min_height[code_row])

door_collector = doors_in_document()

# Setting up the Shared Parameter
door_category = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Doors) # Returns a Category Obejct that contains all categories. In this case a Category of just Doors. doc.Settings accesse all the settings in the Revit Applcaition. Here specifically asking the categories to be listed
category_set = app.Create.NewCategorySet() # Creates a Category Set (Group of Categories) to perform function on them. This is an empty Category Set now
category_set.Insert(door_category)

shared_parameter_file_name = "DoorAutomationSharedParameter.txt"
shared_parameter_file_path = os.path.join(script_dir, shared_parameter_file_name) 
original_shared_file = r"K:\BIM\2021\Revit\Dar\Shared_txt_files\All Trades-Shared Parameters.txt"

app.SharedParametersFilename = shared_parameter_file_path # Give the path to the Shared Parameter File
shared_parameter_file = app.OpenSharedParameterFile() # Access the Shared Parameter File
# Returns a DefinitionFile 

if shared_parameter_file is None:
    raise ValueError("Shared parameter file not found")

group = shared_parameter_file.Groups.get_Item("Door") # Retrieve a specific Parameter Group

if group is None:
    raise ValueError("Group 'Door' not found in shared parameter file")

external_definition = group.Definitions.get_Item("FLS_Comment")
if external_definition is None:
    raise ValueError("Definition 'FLS_Comment' not found in shared parameter file")

external_definition.HideWhenNoValue = True

t = Transaction(doc, "Create Shared Parameter")
t.Start()

# Binding Parameter to the Category
newIB = app.Create.NewInstanceBinding(category_set)

# Parameter Group Set to Text
binding_map = doc.ParameterBindings
if not binding_map.Insert(external_definition, newIB, BuiltInParameterGroup.PG_TEXT):
    binding_map.ReInsert(external_definition, newIB, BuiltInParameterGroup.PG_TEXT)

t.Commit()
app.SharedParametersFilename = original_shared_file

# TO DO : CREATE AN EXCLUSION FOR CUBICLE DOORS AS WELL
doors_excluded = ["ACCESS PANELS","ACCESS PANEL", "CLOSEST DOOR", "BIFOLD", "SLIDING", "OPENING", "ROLLING SHUTTER", "REVOLVING"]
t = Transaction(doc, "Find Failed Doors")
t.Start()
for door in door_collector:
    symbol = door.Symbol
    error_message = "Error: "
    door_type = symbol.LookupParameter("Door_Type").AsString()
    if not door_type.upper() in doors_excluded:
        # Check if the Door is Single Panel or More
        if symbol.LookupParameter("Leaf_Number").AsInteger() == 1:
            # Check Width and Height Requirements
            door_width = convert_internal_units(symbol.LookupParameter("Width").AsDouble(), False, "mm")
            door_height = convert_internal_units(symbol.LookupParameter("Height").AsDouble(), False, "mm")

            if not (door_width > min_single_leaf):
                error_message += "The Door Width should be larger than " + str(min_single_leaf) + ". "

            if not (door_width < max_single_leaf):
                error_message += "The Door Width should be smaller than " + str(max_single_leaf) + ". "

            if not (door_height > min_height):
                error_message += "The Door Height should be larger than " + str(min_height) + ". "
            
        else:
            # Check if the Door has equal leaves
            if symbol.LookupParameter("Equal_Leaves").AsInteger() == 1:
                door_width = convert_internal_units(symbol.LookupParameter("Width").AsDouble(), False, "mm")
                door_height = convert_internal_units(symbol.LookupParameter("Height").AsDouble(), False, "mm")

                no_of_leaves = symbol.LookupParameter("Leaf_Number").AsInteger()
                if not ((door_width / no_of_leaves) > min_double_leaf):
                    error_message += "The Leaf Width should be larger than " + str(min_double_leaf) + ". "

                if not ((door_width / no_of_leaves) < max_double_leaf):
                    error_message += "The Leaf Width should be smaller than " + str(max_double_leaf) + ". "

                if not (door_height > min_height):
                    error_message += "The Door Height should be larger than " + str(min_height) + ". "
                
            else:
                door_thickness = convert_internal_units(symbol.LookupParameter("Thickness").AsDouble(), False, "mm")

                main_leaf = convert_internal_units(symbol.LookupParameter("Main Panel Width").AsDouble(), False, "mm") - door_thickness
                side_leaf = convert_internal_units(symbol.LookupParameter("Side Panel Width").AsDouble(), False, "mm") - door_thickness

                door_height = convert_internal_units(symbol.LookupParameter("Height").AsDouble(), False, "mm")

                if not (main_leaf > min_unq_main_leaf):
                    error_message += "The Main Leaf Width should be larger than " + str(min_unq_main_leaf) + ". "

                if not (main_leaf < max_unq_main_leaf):
                    error_message += "The Main Leaf Width should be smaller than " + str(max_unq_main_leaf) + ". "

                if not (side_leaf > min_unq_side_leaf):
                    error_message += "The Side Leaf Width should be larger than " + str(min_unq_side_leaf) + ". "

                if not (side_leaf < max_unq_side_leaf):
                    error_message += "The Side Leaf Width should be smaller than " + str(max_unq_side_leaf) + ". "

                if not (door_height > min_height):
                    error_message += "The Door Height should be larger than " + str(min_height) + ". "

        door.LookupParameter("FLS_Comment").Set(error_message)

t.Commit()

# Find all the Schedule Views
views = (FilteredElementCollector(doc)
         .OfClass(ViewSchedule)
         .WhereElementIsNotElementType()
         .ToElements())

# Find the View that Equals to "Failed Doors Schedule" and Delete
for view in views:
    if view.Name == "Failed Doors Schedule":  
        forms.alert("Failed Doors Schedule already in the Document, Run the Purge Validated Data Tool First ", title='Script Cancelled')
        script.exit()
        break

# Start a transaction
t = Transaction(doc, "Create Schedule")
t.Start()

# Get Door Category
door_category_id = Category.GetCategory(doc, BuiltInCategory.OST_Doors).Id

# Create a schedule for the Door category
view_schedule = ViewSchedule.CreateSchedule(doc, door_category_id)
view_schedule.Name = "Failed Doors Schedule"

# Get all fields that can be added to the schedule
schedulable_fields = view_schedule.Definition.GetSchedulableFields()

# Add specific fields to the schedule
for field in schedulable_fields:
    if field.GetName(doc) == "FLS_Comment":
        schedule_field = view_schedule.Definition.AddField(field)
        schedule_filter = ScheduleFilter(schedule_field.FieldId, ScheduleFilterType.Contains, "Error: The")
        view_schedule.Definition.AddFilter(schedule_filter)  # Add the filter to the schedule
        continue
    if field.GetName(doc) == "Mark":
        schedule_field = view_schedule.Definition.AddField(field)
        continue
    if field.GetName(doc) == "Family and Type":
        schedule_field = view_schedule.Definition.AddField(field)
        schedule_sort = ScheduleSortGroupField(schedule_field.FieldId, ScheduleSortOrder.Ascending)
        view_schedule.Definition.AddSortGroupField(schedule_sort)
        continue

# Commit the transaction
t.Commit()

# Set the Active View to the Created Schedule
ui_doc.ActiveView = view_schedule