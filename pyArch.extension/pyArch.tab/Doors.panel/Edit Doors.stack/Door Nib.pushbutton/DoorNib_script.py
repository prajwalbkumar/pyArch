# -*- coding: utf-8 -*-
'''Door Nib'''
__title__ = "Door Nib"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter
from pyrevit import forms, script
import os
from System.Collections.Generic import List

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
def update_doors(door_ids, mimimum_nib_dimension, target_instances_type):
    base = 50

    view_family_types = FilteredElementCollector(doc).OfClass(ViewFamilyType)
    for view_type in view_family_types:
        if view_type.ViewFamily == ViewFamily.ThreeDimensional:
            target_type = view_type
            break
    
    analytical_view = View3D.CreateIsometric(doc, target_type.Id)
    try:
        analytical_view.HideElements(target_instances_type)
    except:
        pass

    view_analytical = analytical_view.Duplicate(ViewDuplicateOption.Duplicate)
    view_analytical = doc.GetElement(view_analytical)
    
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

        try:
            wall_direction = hosted_wall.Location.Curve.Direction.Normalize()
        except:
            run_log_code = run_log_code + "CODE A FAIL "
            continue

        directions.append(wall_direction)
        directions.append(wall_direction.Negate())

        intersector = ReferenceIntersector(view_analytical)
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

        if nib_calculation < mimimum_nib_dimension: # Check for Doors with less nib width

            if nib_calculation < 0:
                move_distance = abs(nib_calculation) + mimimum_nib_dimension
            else:
                move_distance = abs(nib_calculation - mimimum_nib_dimension)
        
            move_ray_direction = ray_direction_sorted[0].Negate()
            for i in range(1,len(rays_sorted)):
                if ray_direction_sorted[i].X == move_ray_direction.X and ray_direction_sorted[i].Y == move_ray_direction.Y and ray_direction_sorted[i].Z == move_ray_direction.Z:
                    if (door_proximities_sorted[i] - (rough_width / 2)) - move_distance >= mimimum_nib_dimension:
                        # Do the shifting and stop the loop
                        mid_point = rays_sorted[i].GetEndPoint(0)
                        offset_point = mid_point + XYZ(move_ray_direction.X * move_distance, move_ray_direction.Y * move_distance, direction.Z)

                        old_location = hosted_wall.Location.Curve.Project(mid_point).XYZPoint
                        new_location = hosted_wall.Location.Curve.Project(offset_point).XYZPoint

                        door.Location.Move(new_location - old_location)

                        run_log_code = run_log_code + "CODE A PASS "
                        break

                    else:
                        run_log_code = run_log_code + "CODE A FAIL "
                        break
        
        elif nib_calculation > mimimum_nib_dimension:
            nib_calculation =  nib_calculation * 304.8
            rounded_nib_calculation = int(base * round(float(nib_calculation)/base))

            nib_calculation_difference = nib_calculation - rounded_nib_calculation
            
            if int(nib_calculation_difference) == 0:
                run_log_code = run_log_code + "CODE NEUTRAL "
                continue

            elif nib_calculation_difference > 0:
                move_distance = nib_calculation_difference * 0.00328084
                move_ray_direction = ray_direction_sorted[0]
            
            else:
                move_distance = abs(nib_calculation_difference) * 0.00328084
                move_ray_direction = ray_direction_sorted[0].Negate()
            
            for i in range(1,len(rays_sorted)):
                if ray_direction_sorted[i].X == move_ray_direction.X and ray_direction_sorted[i].Y == move_ray_direction.Y and ray_direction_sorted[i].Z == move_ray_direction.Z:
                    if (door_proximities_sorted[i] - (rough_width / 2)) - move_distance >= mimimum_nib_dimension:
                        # Do the shifting and stop the loop
                        mid_point = rays_sorted[i].GetEndPoint(0)
                        offset_point = mid_point + XYZ(move_ray_direction.X * move_distance, move_ray_direction.Y * move_distance, direction.Z)

                        old_location = hosted_wall.Location.Curve.Project(mid_point).XYZPoint
                        new_location = hosted_wall.Location.Curve.Project(offset_point).XYZPoint

                        door.Location.Move(new_location - old_location)

                        run_log_code = run_log_code + "CODE A PASS "
                        break

                    else:
                        run_log_code = run_log_code + "CODE A FAIL "
                        break


            # TODO: SHIFT THE BELOW CODE TO THE DOOR ALLIGN TOOL
            # if move_code == 0:
            #     # For Doors with more nibs
            #     target_ray_direction = ray_direction_sorted[0]
            #     for i in range(1,len(rays_sorted)):
            #         if ray_direction_sorted[i].X == target_ray_direction.X and ray_direction_sorted[i].Y == target_ray_direction.Y and ray_direction_sorted[i].Z == target_ray_direction.Z:
            #             if (door_proximities_sorted[i] - (rough_width / 2)) - move_distance > mimimum_nib_dimension:
            #                 # Do the shifting and stop the loop
            #                 mid_point = rays_sorted[i].GetEndPoint(0)
            #                 offset_point = mid_point + XYZ(target_ray_direction.X * move_distance, target_ray_direction.Y * move_distance, direction.Z)

            #                 old_location = hosted_wall.Location.Curve.Project(mid_point).XYZPoint
            #                 new_location = hosted_wall.Location.Curve.Project(offset_point).XYZPoint

            #                 door.Location.Move(new_location - old_location)

            #                 run_log_code = run_log_code + "CODE A PASS "
            #                 break

            #             else:
            #                 run_log_code = run_log_code + "CODE A FAIL "
            #                 break


           

        run_door_ids.append(id)
        run_message.append(run_log_code)

    # Pair the proximity values with their corresponding rays
    run_log = list(zip(run_door_ids, run_message))
    doc.Delete(analytical_view.Id)
    doc.Delete(view_analytical.Id)
    return run_log

# Define a selection filter class for doors
class DoorSelectionFilter(ISelectionFilter):
    def AllowElement(self, element):
        if element.Category.Id.IntegerValue == int(BuiltInCategory.OST_Doors):
            return True
        return False
    
    def AllowReference(self, ref, point):
        return False
    
# MAIN SCRIPT
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
    #Custom selection 
    selection_options = forms.alert("This tool checks and updates door nibs.",
                                    title="Door Nib - Select Doors", 
                                    warn_icon=False, 
                                    options=["Check All Doors", "Choose Specific Doors"])

    if not selection_options:
        script.exit()

    elif selection_options == "Check All Doors":
        door_collector = doors_in_document()

    else:
        # Prompt user to select doors
        try:
            choices = ui_doc.Selection
            selected_elements = choices.PickObjects(ObjectType.Element, DoorSelectionFilter(), "Select doors only")
            
            for selected_element in selected_elements:
                door = doc.GetElement(selected_element.ElementId)
                door_collector.append(door)

        except:
            script.exit()

if not door_collector:
    forms.alert("No doors found in the active document", title="Script Exiting", warn_icon=True)
    script.exit()

mimimum_nib_dimension = forms.ask_for_string(
    title="Enter the Minimum Door Nib Dimension.",
    prompt="If the current nib dimension is smaller than this value, it will be\n"
            "updated to match.\n\n"
            "Else, will be rounded to the nearest 50mm.\n",
    default="150")

if not mimimum_nib_dimension:
    script.exit()

# Collect all linked instances
linked_instance = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()

target_instances_type = List[ElementId]()

if linked_instance:
    link_name = []
    for link in linked_instance:
        link_name.append(link.Name)

    target_instance_names = forms.SelectFromList.show(link_name, title = "Select Link File", width=600, height=600, button_name="Select File", multiselect=True)

    if not target_instance_names:
        script.exit()

    for link in linked_instance:
        for name in target_instance_names:
            if name != link.Name:
                target_instances_type.Add(link.GetTypeId())    

doors_excluded = ["ACCESS PANEL", "CLOSEST DOOR", "BIFOLD", "SLIDING", "OPENING", "ROLLING SHUTTER", "REVOLVING"]

skipped_doors = []
move_door_ids = []
for door in door_collector:
    error_code = ""
    failed_door = False
    error_message = ""
    symbol = door.Symbol
    try:
        door_type = symbol.LookupParameter("Door_Type").AsString()
        if not door_type.upper() in doors_excluded:
            move_door_ids.append(door.Id)
  
    except:
        skipped_doors.append(door)
        continue

failed_data = []
passed_data = []

t = Transaction(doc, "Update Door Position")
t.Start()

if move_door_ids:
    doors_run_log = update_doors(move_door_ids, mimimum_nib_dimension, target_instances_type)
    run_door_ids, run_message = zip(*doors_run_log)
    for index, id in enumerate(run_door_ids):
        try:
            if "FAIL" in run_message[index]:
                door = doc.GetElement(id)
                if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                    door_mark = "NONE"
                else:
                    door_mark = door.LookupParameter("Mark").AsString().upper()

                if door.LookupParameter("Level"):
                    door_level = door.LookupParameter("Level").AsValueString().upper()
                else:
                    door_level = "NONE"  

                if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                    door_room_name = "NONE"
                else:
                    door_room_name = door.LookupParameter("Room_Name").AsString().upper()

                if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                    door_room_number = "NONE"
                else:
                    door_room_number = door.LookupParameter("Room_Number").AsString().upper()

                failed_data.append([output.linkify(door.Id), door_mark, door_level, door_room_name, door_room_number, run_message[index]])

            if "PASS" in run_message[index]:
                door = doc.GetElement(id)
                if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                    door_mark = "NONE"
                else:
                    door_mark = door.LookupParameter("Mark").AsString().upper()

                if door.LookupParameter("Level"):
                    door_level = door.LookupParameter("Level").AsValueString().upper()
                else:
                    door_level = "NONE"    

                if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                    door_room_name = "NONE"
                else:
                    door_room_name = door.LookupParameter("Room_Name").AsString().upper()

                if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                    door_room_number = "NONE"
                else:
                    door_room_number = door.LookupParameter("Room_Number").AsString().upper()

                passed_data.append([output.linkify(door.Id), door_mark, door_level, door_room_name, door_room_number, run_message[index]])
        except:
            continue

t.Commit()


clashing_data = []

extra_checks = forms.alert("Would you like to check for any Door - Door Nib Clashes in the project?", title= "Door-Door Clash Test", warn_icon=False, options=["YES", "NO"])

if extra_checks == "YES":
    # Check for Doors that are too close to each other
    wall_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()



    door_minimum_clearance = 300
    door_door_clearance = door_minimum_clearance * 0.00328084
    for wall in wall_collector:
        wall_dependent_elements = wall.GetDependentElements(None)  # Get all dependent elements

        # Create a category filter to filter out door instances
        door_filter = ElementCategoryFilter(BuiltInCategory.OST_Doors)

        # Collect the dependent elements that are doors
        dependent_doors = []
        for element_id in wall_dependent_elements:
            element = doc.GetElement(element_id)
            if element and door_filter.PassesFilter(element):  # Check if the element is a door
                dependent_doors.append(element)
        
        if not len(dependent_doors) > 1:
            continue
        
        indexed_door = []
        for door in dependent_doors:
            host_parameter = door.HostParameter
            indexed_door.append((door, host_parameter))

        sorted_indexed_door = sorted(indexed_door, key=lambda x: x[1])

        doors = [item[0] for item in indexed_door]           # Extracting doors
        host_parameters = [item[1] for item in indexed_door] # Extracting host parameters
        
        for i in range(len(doors) - 1):
            current_door_rough_width = doors[i].Symbol.LookupParameter("Rough Width").AsDouble()
            next_door_rough_width = doors[i+1].Symbol.LookupParameter("Rough Width").AsDouble()
            
            current_door_end_parameter = host_parameters[i] + (current_door_rough_width/2)
            next_door_start_parameter = host_parameters[i+1] - (next_door_rough_width/2)


            if (current_door_end_parameter + door_door_clearance) > next_door_start_parameter:

                if not doors[i].LookupParameter("Mark").HasValue or doors[i].LookupParameter("Mark").AsString() == "": 
                    door_mark = "NONE"
                else:
                    door_mark = doors[i].LookupParameter("Mark").AsString().upper()
                
                if not doors[i].LookupParameter("Room_Name").HasValue or doors[i].LookupParameter("Room_Name").AsString() == "": 
                    door_room_name = "NONE"
                else:
                    door_room_name = doors[i].LookupParameter("Room_Name").AsString().upper()

                if door.LookupParameter("Level"):
                    door_level = doors[i].LookupParameter("Level").AsValueString().upper()
                else:
                    door_level = "NONE"

                if not doors[i].LookupParameter("Room_Number").HasValue or doors[i].LookupParameter("Room_Number").AsString() == "": 
                    door_room_number = "NONE"
                else:
                    door_room_number = doors[i].LookupParameter("Room_Number").AsString().upper()

                clashing_data.append([output.linkify(doors[i].Id), door_mark, door_level, door_room_name, door_room_number, "DOOR CLASH"])           

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

if clashing_data:
    output.print_md("##⚠️ {} Completed. Instances Need Attention ☹️" .format(__title__)) # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ Some issues could not be resolved. Refer to the **Table Report** below for reference")  # Print a Line
    output.print_table(table_data=clashing_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "ERROR CODE"]) # Print a Table
    print("\n\n")
    output.print_md("---") # Markdown Line Break
    output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
    output.print_md("---") # Markdown Line Break
    output.print_md("**DOOR CLASH**  - Keep adjacent doors atleast {} mm apart." .format(door_minimum_clearance))
    output.print_md("---") # Markdown Line Break

if skipped_doors:
    failed_data = []
    for door in skipped_doors:
        if door.LookupParameter("Mark"):
            if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                door_mark = "NONE"
            else:
                door_mark = door.LookupParameter("Mark").AsString().upper()
        else:
            door_mark = "NONE"
        
        if door.LookupParameter("Room_Name"):
            if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                door_room_name = "NONE"
            else:
                door_room_name = door.LookupParameter("Room_Name").AsString().upper()
        else:
            door_room_name = "NONE"

        if door.LookupParameter("Level"):
            door_level = door.LookupParameter("Level").AsValueString().upper()
        else:
            door_level = "NONE"

        if door.LookupParameter("Room_Number"):
            if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                door_room_number = "NONE"
            else:
                door_room_number = door.LookupParameter("Room_Number").AsString().upper()
        else:
            door_room_number = "NONE"

        failed_data.append([output.linkify(door.Id), door_mark, door_level, door_room_name, door_room_number])

    output.print_md("##⚠️ Doors Skipped ☹️") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ Make sure you have used DAR Families - Door_Type Parameter Missing or Empty. Refer to the **Table Report** below for reference")  # Print a Line
    output.print_table(table_data=failed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER"]) # Print a Table
    print("\n\n")
    output.print_md("---") # Markdown Line Break

if not failed_data and not skipped_doors and not clashing_data:
    output.print_md("##✅ {} Completed. No Issues Found 😃" .format(__title__)) # Markdown Heading 2
    output.print_md("---") # Markdown Line Break