# -*- coding: utf-8 -*-
'''Door Nib'''
__title__ = "Door Nib"
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

# Definition to Get all the Door Instances in the Document
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


# Definition to update doors and return failed doors
def update_doors(door_ids, mimimum_nib_dimension):
    mimimum_nib_dimension = int(mimimum_nib_dimension) * 0.00328084
    run_door_ids = []
    run_message = []
    for index, id in enumerate(door_ids):
        door_proximities = []
        rays = []
        ray_direction = []
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
                rays.append(Line.CreateBound(point, (point + XYZ(direction.X * proximity, direction.Y * proximity, direction.Z))))
                ray_direction.append(direction)

                # plane = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, point)
                # sketch_plane = SketchPlane.Create(doc, plane)
                # model_line = doc.Create.NewModelCurve(Line.CreateBound(point, (point + XYZ(direction.X * proximity, direction.Y * proximity, direction.Z))), sketch_plane)

        if not door_proximities:
            continue


        # Pair the proximity values with their corresponding rays
        paired_proximity_rays = list(zip(door_proximities, rays, ray_direction))

        # Sort the pairs based on proximity values (first element in the pair)
        paired_proximity_rays.sort(key=lambda x: x[0])

        # Unzip the sorted pairs back into two separate lists
        door_proximities_sorted, rays_sorted, ray_direction_sorted = zip(*paired_proximity_rays)

        # Convert the tuples back to lists, if needed
        door_proximities_sorted = list(door_proximities_sorted)
        rays_sorted = list(rays_sorted)
        ray_direction_sorted = list(ray_direction_sorted)

        run_log_code = ""
        
        # Check if the smallest proximity distance can accomodate for the increase in the door width
        rough_width = door.Symbol.LookupParameter("Rough Width").AsDouble()

        nib_calculation = door_proximities_sorted[0] - (rough_width / 2)

        if nib_calculation < 0:
            move_distance = abs(nib_calculation) + mimimum_nib_dimension
        else:
            move_distance = abs(nib_calculation - mimimum_nib_dimension)
        
        if nib_calculation < mimimum_nib_dimension: # Check for Doors with less nib width
            opposite_ray_direction = ray_direction_sorted[0].Negate()
            for i in range(1,len(rays_sorted)):
                if ray_direction_sorted[i].X == opposite_ray_direction.X and ray_direction_sorted[i].Y == opposite_ray_direction.Y and ray_direction_sorted[i].Z == opposite_ray_direction.Z:
                    if (door_proximities_sorted[i] - (rough_width / 2)) - move_distance > mimimum_nib_dimension:
                        # Do the shifting and stop the loop
                        mid_point = rays_sorted[i].GetEndPoint(0)
                        offset_point = mid_point + XYZ(opposite_ray_direction.X * move_distance, opposite_ray_direction.Y * move_distance, direction.Z)

                        old_location = hosted_wall.Location.Curve.Project(mid_point).XYZPoint
                        new_location = hosted_wall.Location.Curve.Project(offset_point).XYZPoint

                        door.Location.Move(new_location - old_location)

                        run_log_code = run_log_code + "CODE A PASS "
                        break

                    else:
                        run_log_code = run_log_code + "CODE A FAIL "
                        break

        run_door_ids.append(id)
        run_message.append(run_log_code)

    # Pair the proximity values with their corresponding rays
    run_log = list(zip(run_door_ids, run_message))
    return run_log


# MAIN SCRIPT
view = doc.ActiveView
type = str(type(view))

if not type == "<type 'View3D'>":
    forms.alert("Active View must be a 3D View \n\n"
                        "Make sure that the 3D View contains all Model Elements", title = "Script Exiting", warn_icon = True)

    script.exit()

door_collector = []
selection = ui_doc.Selection.GetElementIds()
if len(selection) > 0:
    for id in selection:
        element = doc.GetElement(id)
        try:
            if element.LookupParameter("Category").AsValueString() == "Doors":
               door_collector.append(element)
        except:
            continue

else:
    door_collector = doors_in_document()
    
minimum_door_nib = 100

mimimum_nib_dimension = forms.ask_for_string(
    title="Minimum Door Nib Dimension",
    prompt="Enter Minimum Door Nib Dimension\n", 
    default="150")

if not mimimum_nib_dimension:
    script.exit()

doors_excluded = ["ACCESS PANEL", "CLOSEST DOOR", "BIFOLD", "SLIDING", "OPENING", "ROLLING SHUTTER", "REVOLVING"]

skipped_doors = []
move_door_ids = []
for door in door_collector:
    error_code = ""
    failed_door = False
    error_message = ""
    symbol = door.Symbol
    try:
        door_type = symbol.LookupParameter("Door_Type").AsString() # A Possible Attribute Error here. Door might not have Door Type Parameter sometimes.
        if not door_type.upper() in doors_excluded:
            move_door_ids.append(door.Id)
  
    except:
        skipped_doors.append(door)
        continue

failed_data = []
passed_data = []
t = Transaction(doc, "Update Door Families")
t.Start()
if move_door_ids:
    doors_run_log = update_doors(move_door_ids, mimimum_nib_dimension)
    run_door_ids, run_message = zip(*doors_run_log)
    for index, id in enumerate(run_door_ids):
        if "FAIL" in run_message[index]:
            door = doc.GetElement(id)
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

            failed_data.append([output.linkify(door.Id), door_mark, door.LookupParameter("Level").AsValueString().upper(), door_room_name, door_room_number, run_message[index]])

        if "PASS" in run_message[index]:
            door = doc.GetElement(id)
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

            passed_data.append([output.linkify(door.Id), door_mark, door.LookupParameter("Level").AsValueString().upper(), door_room_name, door_room_number, run_message[index]])

t.Commit()

# Display all list of failed doors, including unequal doors
if passed_data:
    output.print_md("##✅ {} Completed. Instances Have Been Updated 😃" .format(__title__)) # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("✔️ Some issues have been resolved. Refer to the **Table Report** below for reference")  # Print a Line
    output.print_table(table_data=passed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "SUCCESS CODE"]) # Print a Table
    print("\n\n")
    output.print_md("---") # Markdown Line Break
    output.print_md("***✅ SUCCESS CODE REFERENCE***")  # Print a Line
    output.print_md("---") # Markdown Line Break
    output.print_md("**CODE A PASS**  - Door Moved")
    output.print_md("---") # Markdown Line Break


if failed_data:
    output.print_md("##⚠️ {} Completed. Instances Need Attention ☹️" .format(__title__)) # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ Some issues could not be resolved. Refer to the **Table Report** below for reference")  # Print a Line
    output.print_table(table_data=failed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "ERROR CODE"]) # Print a Table
    print("\n\n")
    output.print_md("---") # Markdown Line Break
    output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
    output.print_md("---") # Markdown Line Break
    output.print_md("**CODE A FAIL**  - Door could not be moved")
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


if not failed_data and not skipped_doors:
    output.print_md("##✅ {} Completed. No Issues Found 😃" .format(__title__)) # Markdown Heading 2
    output.print_md("---") # Markdown Line Break