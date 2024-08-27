# -*- coding: utf-8 -*-
'''FLS Doors Validator'''
__title__ = "FLS Compliance Validator"
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
output = script.get_output()

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

view = doc.ActiveView
type = str(type(view))

if not type == "<type 'View3D'>":
    forms.alert("Active View must be a 3D View \n\n"
                        "Make sure that the 3D View contains all Model Elements", title = "Script Exiting", warn_icon = True)

    script.exit()

minimum_door_nib = 100

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
    code, title="Select Relevent Code", width=300, height=300, button_name="Select Code", multiselect=False
)

if not user_code:
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

doors_excluded = ["ACCESS PANEL", "CLOSEST DOOR", "BIFOLD", "SLIDING", "OPENING", "ROLLING SHUTTER", "REVOLVING"]

# Checks for Single Doors
failed_data = []
skipped_doors = []
failed_single_door_ids = []
failed_single_door_error_code= []
failed_double_door_ids = []
failed_double_door_error_code= []
for door in door_collector:
    error_code = ""
    failed_door = False
    error_message = ""
    symbol = door.Symbol
    try:
        door_type = symbol.LookupParameter("Door_Type").AsString() # A Possible Attribute Error here. Door might not have Door Type Parameter sometimes.
        if not door_type.upper() in doors_excluded:
            # Check if the Door is Single Panel or More
            if symbol.LookupParameter("Leaf_Number").AsInteger() == 1:
                # Check Width and Height Requirements
                door_width = convert_internal_units(symbol.LookupParameter("Width").AsDouble(), False, "mm")
                door_height = convert_internal_units(symbol.LookupParameter("Height").AsDouble(), False, "mm")
                if not (door_width >= min_single_leaf):
                    error_message += "The Door Width should be larger than or equal to " + str(min_single_leaf) + ". "
                    failed_door = True
                    error_code += "A"

                if not (door_width <= max_single_leaf):
                    error_message += "The Door Width should be smaller than or equal to " + str(max_single_leaf) + ". "
                    failed_door = True
                    error_code += "B"

                if not (door_height >= min_height):
                    error_message += "The Door Height should be larger than or equal to " + str(min_height) + ". "
                    failed_door = True
                    error_code += "C"

                if error_code:
                    failed_single_door_error_code.append(error_code)
                    failed_single_door_ids.append(door.Id)
                  

            else:
                # Check if the Door has equal leaves
                if symbol.LookupParameter("Equal_Leaves").AsInteger() == 1:
                    door_width = convert_internal_units(symbol.LookupParameter("Width").AsDouble(), False, "mm")
                    door_height = convert_internal_units(symbol.LookupParameter("Height").AsDouble(), False, "mm")

                    no_of_leaves = symbol.LookupParameter("Leaf_Number").AsInteger()
                    if not ((door_width / no_of_leaves) >= min_double_leaf):
                        error_message += "The Leaf Width should be larger than or equal to " + str(min_double_leaf) + ". "
                        failed_door = True
                        error_code += "A"

                    if not ((door_width / no_of_leaves) <= max_double_leaf):
                        error_message += "The Leaf Width should be smaller than or equal to " + str(max_double_leaf) + ". "
                        failed_door = True
                        error_code += "B"

                    if not (door_height >= min_height):
                        error_message += "The Door Height should be larger than or equal to " + str(min_height) + ". "
                        failed_door = True
                        error_code += "C"
                    
                    if error_code:
                        failed_double_door_error_code.append(error_code)
                        failed_double_door_ids.append(door.Id)
                    
                else:
                    door_thickness = convert_internal_units(symbol.LookupParameter("Thickness").AsDouble(), False, "mm")

                    main_leaf = convert_internal_units(symbol.LookupParameter("Main Panel Width").AsDouble(), False, "mm") - door_thickness
                    side_leaf = convert_internal_units(symbol.LookupParameter("Side Panel Width").AsDouble(), False, "mm") - door_thickness

                    door_height = convert_internal_units(symbol.LookupParameter("Height").AsDouble(), False, "mm")

                    if not (main_leaf >= min_unq_main_leaf):
                        error_message += "The Main Leaf Width should be larger than or equal to " + str(min_unq_main_leaf) + ". "
                        failed_door = True

                    if not (main_leaf <= max_unq_main_leaf):
                        error_message += "The Main Leaf Width should be smaller than or equal to " + str(max_unq_main_leaf) + ". "
                        failed_door = True

                    if not (side_leaf >= min_unq_side_leaf):
                        error_message += "The Side Leaf Width should be larger than or equal to " + str(min_unq_side_leaf) + ". "
                        failed_door = True

                    if not (side_leaf <= max_unq_side_leaf):
                        error_message += "The Side Leaf Width should be smaller than or equal to " + str(max_unq_side_leaf) + ". "
                        failed_door = True

                    if not (door_height >= min_height):
                        error_message += "The Door Height should be larger than or equal to " + str(min_height) + ". "
                        failed_door = True

        if failed_door:
            if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                door_mark = "NONE"
            else:
                door_mark = door.LookupParameter("Mark").AsString().upper()
            
            if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                door_room_name = "NONE"
            else:
                door_room_name = door.LookupParameter("Room_Name").AsString().upper()

            if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                door_room_number = "NONE"
            else:
                door_room_number = door.LookupParameter("Room_Number").AsString().upper()

            failed_data.append([output.linkify(door.Id), door_mark, door.LookupParameter("Level").AsValueString().upper(), door_room_name, door_room_number, error_message])

    except:
        skipped_doors.append(door)
        continue

if failed_data or skipped_doors:
    user_action = forms.alert("Few Doors have Errors. Refer to the Report for more information", title = "Errors Found", warn_icon = True, options = ["Show Report", "Auto - Correct Doors"])

    if user_action == "Show Report":
        if failed_data:
            output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(__title__)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
            output.print_table(table_data=failed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "ERROR CODE"]) # Print a Table
            print("\n\n")
            output.print_md("---") # Markdown Line Break

        if skipped_doors:
            failed_data = []
            for door in skipped_doors:
                if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                    door_mark = "NONE"
                else:
                    door_mark = door.LookupParameter("Mark").AsString().upper()
                
                if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                    door_room_name = "NONE"
                else:
                    door_room_name = door.LookupParameter("Room_Name").AsString().upper()

                if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                    door_room_number = "NONE"
                else:
                    door_room_number = door.LookupParameter("Room_Number").AsString().upper()

                failed_data.append([output.linkify(door.Id), door_mark, door.LookupParameter("Level").AsValueString().upper(), door_room_name, door_room_number])

            output.print_md("##⚠️ Doors Skipped ☹️") # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
            output.print_md("❌ Make sure you have used DAR Families - Door_Type Parameter Missing or Empty. Refer to the **Table Report** below for reference")  # Print a Line
            output.print_table(table_data=failed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER"]) # Print a Table
            print("\n\n")
            output.print_md("---") # Markdown Line Break

        if user_action == "Auto - Correct Doors":
            pass


if not failed_data and not skipped_doors:
    output.print_md("##✅ {} Completed. No Issues Found 😃" .format(__title__)) # Markdown Heading 2
    output.print_md("---") # Markdown Line Break

t = Transaction(doc, "Test")
t.Start()
for index, id in enumerate(failed_single_door_ids):
    door_proximities = []
    calculation_points = []
    door = doc.GetElement(id)

    options = Options()
    options.IncludeNonVisibleObjects = True
    door_geometry = door.get_Geometry(options)
    for component in door_geometry:
        geometry_element = component.GetInstanceGeometry()
        for geometry in geometry_element:
            if geometry.ToString() == "Autodesk.Revit.DB.NurbSpline":
                calculation_points.append(geometry.GetEndPoint(1))
                

    hosted_wall = door.Host
    directions = []
    wall_direction = hosted_wall.Location.Curve.Direction.Normalize()
    directions.append(wall_direction)
    # print(wall_direction)
    # print(wall_direction.Negate())
    directions.append(wall_direction.Negate())

    intersector = ReferenceIntersector(view)
    intersector.FindReferencesInRevitLinks = True
    for point in calculation_points:    
        for direction in directions:
            result = intersector.FindNearest(XYZ(point.X, point.Y, (point.Z)), direction)

            if not result: 
                continue
            proximity = (result.Proximity)
            door_proximities.append(proximity)       

            # plane = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, point)
            # sketch_plane = SketchPlane.Create(doc, plane)
            # model_line = doc.Create.NewModelCurve(Line.CreateBound(point, (point + XYZ(direction.X * proximity, direction.Y * proximity, direction.Z))), sketch_plane)

    if not door_proximities:
        continue

    door_proximities.sort()
    closest_object_distance = door_proximities[0]
    
    if "A" in failed_single_door_error_code[index]:
        # Check if the smallest proximity distance can accomodate for the increase in the door width
        updated_rough_width = (door.Symbol.LookupParameter("Rough Width").AsDouble() - door.Symbol.LookupParameter("Width").AsDouble()) + (min_single_leaf * 0.00328084)

        if abs(closest_object_distance - (updated_rough_width / 2)) < 0.492126:
            print(abs(closest_object_distance - (updated_rough_width / 2)))
            print("Cannot Update")
        
        else:
            print(abs(closest_object_distance - (updated_rough_width / 2)))
            print("YAY")

    
    # print("Door ID {} and Code {}" .format(id, failed_single_door_error_code[index]))

t.Commit()