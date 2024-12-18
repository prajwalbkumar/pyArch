# -*- coding: utf-8 -*-
'''FLS Doors Validator'''
__title__ = "FLS Compliance"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import Selection, ObjectType, ISelectionFilter
from pyrevit import forms, script
import csv 
import os
from System.Collections.Generic import List

import time
from datetime import datetime
from Extract.RunData import get_run_data

start_time = time.time()
manual_time = 0
total_element_count = 0

script_dir = os.path.dirname(__file__)
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
ui_doc = __revit__.ActiveUIDocument
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

# Definition to update doors and return failed doors
def update_doors(door_ids, door_error_code, mimimum_nib_dimension, min_height, min_leaf, max_leaf, target_instances_type):
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
        wall_direction = hosted_wall.Location.Curve.Direction.Normalize()
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
        
        if "A" in door_error_code[index]:
            # Check if the smallest proximity distance can accomodate for the increase in the door width
            updated_rough_width = (door.Symbol.LookupParameter("Rough Width").AsDouble() - door.Symbol.LookupParameter("Width").AsDouble()) + (min_leaf * 0.00328084)

            nib_calculation = door_proximities_sorted[0] - (updated_rough_width / 2)

            if nib_calculation < 0:
                move_distance = abs(nib_calculation) + mimimum_nib_dimension
            else:
                move_distance = abs(nib_calculation - mimimum_nib_dimension)
            
            if nib_calculation < mimimum_nib_dimension: # Check to see if Door doesn't exceed the minimum nib length. 
                opposite_ray_direction = ray_direction_sorted[0].Negate()
                for i in range(1,len(rays_sorted)):
                    if ray_direction_sorted[i].X == opposite_ray_direction.X and ray_direction_sorted[i].Y == opposite_ray_direction.Y and ray_direction_sorted[i].Z == opposite_ray_direction.Z:
                        if (door_proximities_sorted[i] - (updated_rough_width / 2)) - move_distance >= mimimum_nib_dimension:
                            # Do the shifting and stop the loop
                            mid_point = rays_sorted[i].GetEndPoint(0)
                            offset_point = mid_point + XYZ(opposite_ray_direction.X * move_distance, opposite_ray_direction.Y * move_distance, direction.Z)

                            old_location = hosted_wall.Location.Curve.Project(mid_point).XYZPoint
                            new_location = hosted_wall.Location.Curve.Project(offset_point).XYZPoint

                            door.Location.Move(new_location - old_location)

                            # Update the Door Values
                            door.Symbol.LookupParameter("Width").Set(min_leaf * 0.00328084)
                            
                            # plane = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, point)
                            # sketch_plane = SketchPlane.Create(doc, plane)
                            # model_line = doc.Create.NewModelCurve(Line.CreateBound(mid_point, new_location), sketch_plane)
                            run_log_code = run_log_code + "CODE A PASS "
                            break

                        else:
                            run_log_code = run_log_code + "CODE A FAIL "
                            break
                            
            else: # These doors are smaller in size and can be updated to their larger versions.
                door.Symbol.LookupParameter("Width").Set(min_leaf * 0.00328084)
                run_log_code = run_log_code + "CODE A PASS "
        
        if "B" in door_error_code[index]:
            door.Symbol.LookupParameter("Width").Set(max_leaf * 0.00328084)
            run_log_code = run_log_code + "CODE B PASS "

        if "C" in door_error_code[index]:
            door.Symbol.LookupParameter("Height").Set(min_height * 0.00328084)
            run_log_code = run_log_code + "CODE C PASS "

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
    
try:
    # MAIN SCRIPT
    door_collector = []
    model_group_collector = []

    selection = ui_doc.Selection.GetElementIds()
    if len(selection) > 0:
        for id in selection:
            element = doc.GetElement(id)
            try:
                if element.LookupParameter("Category").AsValueString() == "Doors":
                    if element.GroupId.IntegerValue > 0:
                        model_group_collector.append(element)
                        continue
                    else:
                        door_collector.append(element)
            except:
                continue

    else:
        #Custom selection 
        selection_options = forms.alert("This tool checks and updates doors against FLS Codes.",
                                        title="FLS Compliance - Select Doors", 
                                        warn_icon=False, 
                                        options=["Check All Doors", "Choose Specific Doors"])

        if not selection_options:
            script.exit()

        elif selection_options == "Check All Doors":
            buffer = doors_in_document()
            for door in buffer:
                if door.GroupId.IntegerValue > 0:
                    model_group_collector.append(door)
                    continue
                else:
                    door_collector.append(door)

        else:
            # Prompt user to select doors
            try:
                choices = ui_doc.Selection
                selected_elements = choices.PickObjects(ObjectType.Element, DoorSelectionFilter(), "Select doors only")
                
                for selected_element in selected_elements:
                    door = doc.GetElement(selected_element.ElementId)
                    if door.GroupId.IntegerValue > 0:
                        model_group_collector.append(door)
                        continue
                    else:
                        door_collector.append(door)

            except:
                script.exit()

    if not door_collector and not model_group_collector:
        forms.alert("No doors found in the active document", title="Script Exiting", warn_icon=True)
        script.exit()
    
    if model_group_collector:
        input_option = forms.alert("Doors in Model Groups will not be processed", title="Script Exiting", warn_icon=True)

    if model_group_collector or not door_collector:
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
        code, title="Select Relevent Code", width=300, height=400, button_name="Select Code", multiselect=True
    )

    if not user_code:
        script.exit()

    if len(user_code) == 1:
        for input_code in user_code:
            # Find the Index Values of the Code Selected from the Main Code List
            code_row = code.index(input_code)

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

    else:
        list_min_single_leaf = []
        list_min_unq_main_leaf = []
        list_min_unq_side_leaf = []
        list_min_double_leaf = []

        list_max_single_leaf = []
        list_max_unq_main_leaf = []
        list_max_unq_side_leaf = []
        list_max_double_leaf = []

        list_min_height = []

        for input_code in user_code:
            code_row = code.index(input_code)
            list_min_single_leaf.append(int(min_single_leaf[code_row]))
            list_min_unq_main_leaf.append(int(min_unq_main_leaf[code_row]))
            list_min_unq_side_leaf.append(int(min_unq_side_leaf[code_row]))
            list_min_double_leaf.append(int(min_double_leaf[code_row]))

            list_max_single_leaf.append(int(max_single_leaf[code_row]))
            list_max_unq_main_leaf.append(int(max_unq_main_leaf[code_row]))
            list_max_unq_side_leaf.append(int(max_unq_side_leaf[code_row]))
            list_max_double_leaf.append(int(max_double_leaf[code_row]))

            list_min_height.append(int(min_height[code_row]))

        min_single_leaf = sorted(list_min_single_leaf)[-1]
        min_unq_main_leaf = sorted(list_min_unq_main_leaf)[-1]
        min_unq_side_leaf = sorted(list_min_unq_side_leaf)[-1]
        min_double_leaf = sorted(list_min_double_leaf)[-1]


        max_single_leaf = sorted(list_max_single_leaf)[0]
        max_unq_main_leaf = sorted(list_max_unq_main_leaf)[0]
        max_unq_side_leaf = sorted(list_max_unq_side_leaf)[0]
        max_double_leaf = sorted(list_max_double_leaf)[0]
        
        min_height = sorted(list_min_height)[-1]

    doors_excluded = ["ACCESS PANEL", "CLOSEST DOOR", "BIFOLD", "SLIDING", "OPENING", "ROLLING SHUTTER", "REVOLVING"]

    # Checks for Single Doors
    failed_data = []
    skipped_doors = []
    failed_single_door_ids = []
    failed_single_door_error_code= []
    failed_double_door_ids = []
    failed_double_door_error_code= []
    failed_unequal_door_ids = []
    failed_unequal_door_error_code = []

    unowned_elements = []
    if doc.IsWorkshared:
        move_door_ids = []
        elements_to_checkout = List[ElementId]()

        for element in door_collector:
            elements_to_checkout.Add(element.Id)

        checkedout_door_collector = []

        WorksharingUtils.CheckoutElements(doc, elements_to_checkout)
        for element in door_collector: 
            worksharingStatus = WorksharingUtils.GetCheckoutStatus(doc, element.Id)
            if not worksharingStatus == CheckoutStatus.OwnedByOtherUser:
                checkedout_door_collector.append(element)
            else:
                unowned_elements.append(element)

        door_collector = checkedout_door_collector

    manual_time = manual_time + 600
    total_element_count = total_element_count + len(door_collector) 

    # print("min_single_leaf {}" .format(min_single_leaf))
    # print("min_unq_main_leaf {}" .format(min_unq_main_leaf))
    # print("min_unq_side_leaf {}" .format(min_unq_side_leaf))
    # print("min_double_leaf {}" .format(min_double_leaf))
    # print("max_single_leaf {}" .format(max_single_leaf))
    # print("max_unq_main_leaf {}" .format(max_unq_main_leaf))
    # print("max_unq_side_leaf {}" .format(max_unq_side_leaf))
    # print("max_double_leaf {}" .format(max_double_leaf))
    # print("min_height {}" .format(min_height))


    for door in door_collector:
        error_code = ""
        failed_door = False
        error_message = ""
        symbol = door.Symbol
        try:
            door_type = symbol.LookupParameter("Door_Type").AsString() # A Possible Attribute Error here. Door might not have Door Type Parameter sometimes.
            if not door_type.upper() in doors_excluded and not "AP" in symbol.Family.Name and not "OP" in symbol.Family.Name:
                # Check if the Door is Single Panel or More
                if symbol.LookupParameter("Leaf_Number").AsInteger() == 1:
                    # Check Width and Height Requirements
                    door_width = int(convert_internal_units(symbol.LookupParameter("Width").AsDouble(), False, "mm"))
                    door_height = int(convert_internal_units(symbol.LookupParameter("Height").AsDouble(), False, "mm"))
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
                        door_width = int(convert_internal_units(symbol.LookupParameter("Width").AsDouble(), False, "mm"))
                        door_height = int(convert_internal_units(symbol.LookupParameter("Height").AsDouble(), False, "mm"))

                        no_of_leaves = symbol.LookupParameter("Leaf_Number").AsInteger()
                        if not ((door_width) >= min_double_leaf):
                            error_message += "The Door Width should be larger than or equal to " + str(min_double_leaf) + ". "
                            failed_door = True
                            error_code += "A"

                        if not ((door_width) <= max_double_leaf):
                            error_message += "The Door Width should be smaller than or equal to " + str(max_double_leaf) + ". "
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

                        if not (door_height >= min_height):
                            error_message += "The Door Height should be larger than or equal to " + str(min_height) + ". "
                            error_code += "CODE C FAIL "
                            failed_door = True
                        if not (main_leaf >= min_unq_main_leaf):
                            error_message += "The Main Leaf Width should be larger than or equal to " + str(min_unq_main_leaf) + ". "
                            error_code += "CODE D FAIL "
                            failed_door = True

                        if not (main_leaf <= max_unq_main_leaf):
                            error_message += "The Main Leaf Width should be smaller than or equal to " + str(max_unq_main_leaf) + ". "
                            error_code += "CODE E FAIL "
                            failed_door = True

                        if not (side_leaf >= min_unq_side_leaf):
                            error_message += "The Side Leaf Width should be larger than or equal to " + str(min_unq_side_leaf) + ". "
                            error_code += "CODE F FAIL "
                            failed_door = True

                        if not (side_leaf <= max_unq_side_leaf):
                            error_message += "The Side Leaf Width should be smaller than or equal to " + str(max_unq_side_leaf) + ". "
                            error_code += "CODE G FAIL "
                            failed_door = True


                        if error_message:
                            failed_unequal_door_error_code.append(error_code)
                            failed_unequal_door_ids.append(door.Id)

            if failed_door:
                if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                    door_mark = "NONE"
                else:
                    door_mark = door.LookupParameter("Mark").AsString().upper()

                if door.LookupParameter("Level"):
                    door_level = door.LookupParameter("Level").AsValueString().upper()
                else:
                    door_level = "NONE"
                
                if door.LookupParameter("Room_Name"):
                    if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                        door_room_name = "NONE"
                    else:
                        door_room_name = door.LookupParameter("Room_Name").AsString().upper()
                else:
                    door_room_name = "NONE"

                if door.LookupParameter("Room_Number"):
                    if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                        door_room_number = "NONE"
                    else:
                        door_room_number = door.LookupParameter("Room_Number").AsString().upper()
                else:
                    door_room_number = "NONE"

                failed_data.append([output.linkify(door.Id), door_mark, door_level, door_room_name, door_room_number, error_message])

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
                    
                    if door.LookupParameter(" "):
                        door_level = door.LookupParameter("Level").AsValueString().upper()
                    else:
                        door_level = "NONE"

                    if door.LookupParameter("Room_Name"):
                        if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                            door_room_name = "NONE"
                        else:
                            door_room_name = door.LookupParameter("Room_Name").AsString().upper()
                    else:
                        door_room_name = "NONE"

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

        elif user_action == "Auto - Correct Doors":
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
            
            mimimum_nib_dimension = forms.ask_for_string(
                title="Minimum Door Nib Dimension",
                prompt="Enter Minimum Door Nib Dimension\n", 
                default="150")

            failed_data = []
            passed_data = []
            t = Transaction(doc, "Update Door Families")
            t.Start()
            if failed_single_door_ids:
                single_doors_run_log = update_doors(failed_single_door_ids, failed_single_door_error_code, mimimum_nib_dimension, min_height, min_single_leaf, max_single_leaf, target_instances_type)
                run_door_ids, run_message = zip(*single_doors_run_log)
                for index, id in enumerate(run_door_ids):
                    if "FAIL" in run_message[index]:
                        door = doc.GetElement(id)
                        if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                            door_mark = "NONE"
                        else:
                            door_mark = door.LookupParameter("Mark").AsString().upper()
                        
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

                        if door.LookupParameter("Room_Name"):
                            if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                                door_room_name = "NONE"
                            else:
                                door_room_name = door.LookupParameter("Room_Name").AsString().upper()
                        else:
                            door_room_name = "NONE"

                        if door.LookupParameter("Room_Number"):
                            if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                                door_room_number = "NONE"
                            else:
                                door_room_number = door.LookupParameter("Room_Number").AsString().upper()
                        else:
                            door_room_number = "NONE"

                        passed_data.append([output.linkify(door.Id), door_mark, door_level, door_room_name, door_room_number, run_message[index]])


            if failed_double_door_ids:
                double_doors_run_log = update_doors(failed_double_door_ids, failed_double_door_error_code, mimimum_nib_dimension, min_height, min_double_leaf, max_double_leaf, target_instances_type)
                run_door_ids, run_message = zip(*double_doors_run_log)
                for index, id in enumerate(run_door_ids):
                    if "FAIL" in run_message[index]:
                        door = doc.GetElement(id)
                        if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                            door_mark = "NONE"
                        else:
                            door_mark = door.LookupParameter("Mark").AsString().upper()
                        
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
                        
                        if door.LookupParameter("Room_Name"):
                            if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                                door_room_name = "NONE"
                            else:
                                door_room_name = door.LookupParameter("Room_Name").AsString().upper()
                        else:
                            door_room_name = "NONE"

                        if door.LookupParameter("Room_Number"):
                            if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                                door_room_number = "NONE"
                            else:
                                door_room_number = door.LookupParameter("Room_Number").AsString().upper()
                        else:
                            door_room_number = "NONE"

                        passed_data.append([output.linkify(door.Id), door_mark, door_level, door_room_name, door_room_number, run_message[index]])

            if failed_unequal_door_ids:
                for index, id in enumerate(failed_unequal_door_ids):
                    door = doc.GetElement(id)
                    if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                        door_mark = "NONE"
                    else:
                        door_mark = door.LookupParameter("Mark").AsString().upper()
                    
                    if door.LookupParameter("Level"):
                        door_level = door.LookupParameter("Level").AsValueString().upper()
                    else:
                        door_level = "NONE"
                        
                    if door.LookupParameter("Room_Name"):
                        if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                            door_room_name = "NONE"
                        else:
                            door_room_name = door.LookupParameter("Room_Name").AsString().upper()
                    else:
                        door_room_name = "NONE"

                    if door.LookupParameter("Room_Number"):
                        if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                            door_room_number = "NONE"
                        else:
                            door_room_number = door.LookupParameter("Room_Number").AsString().upper()
                    else:
                        door_room_number = "NONE"

                    failed_data.append([output.linkify(door.Id), door_mark, door_level, door_room_name, door_room_number, failed_unequal_door_error_code[index]])


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
                output.print_md("**CODE A PASS**  - Leaf width updated to {}." .format(str(min_single_leaf)))
                output.print_md("**CODE B PASS**  - Leaf width updated to {}." .format(str(max_single_leaf)))
                output.print_md("**CODE C PASS**  - Clear Height updated to {}." .format(str(min_height)))
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
                output.print_md("**CODE A FAIL**  - Each Leaf Width should be larger than or equal to {}." .format(str(min_single_leaf)))
                output.print_md("**CODE B FAIL**  - Each Leaf Width should be smaller than or equal to {}." .format(str(max_single_leaf)))
                output.print_md("**CODE C FAIL**  - Clear Height should be smaller than or equal to {}." .format(str(min_height)))
                output.print_md("**CODE D FAIL**  - The Main Leaf Width should be larger than or equal to {}." .format(str(min_unq_main_leaf)))
                output.print_md("**CODE E FAIL**  - The Main Leaf Width should be smaller than or equal to {}." .format(str(max_unq_main_leaf)))
                output.print_md("**CODE F FAIL**  - The Side Leaf Width should be larger than or equal to {}." .format(str(min_unq_side_leaf)))
                output.print_md("**CODE G FAIL**  - The Side Leaf Width should be smaller than or equal to {}." .format(str(max_unq_side_leaf)))
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

        if not user_action:
            script.exit()

    if not failed_data and not skipped_doors and not unowned_elements:
        output.print_md("##✅ {} Completed. No Issues Found 😃" .format(__title__)) # Markdown Heading 2
        output.print_md("---") # Markdown Line Break

    if unowned_elements:
        unowned_element_data = []
        for element in unowned_elements:
            try:
                unowned_element_data.append([output.linkify(element.Id), element.Category.Name.upper(), "REQUEST OWNERSHIP", WorksharingUtils.GetWorksharingTooltipInfo(doc, element.Id).Owner])
            except:
                pass

        output.print_md("##⚠️ Elements Skipped ☹️") # Markdown Heading 2
        output.print_md("---") # Markdown Line Break
        output.print_md("❌ Make sure you have Ownership of the Elements - Request access. Refer to the **Table Report** below for reference")  # Print a Line
        output.print_table(table_data = unowned_element_data, columns=["ELEMENT ID", "CATEGORY", "TO-DO", "CURRENT OWNER"]) # Print a Table
        print("\n\n")
        output.print_md("---") # Markdown Line Break end_time = time.time()

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