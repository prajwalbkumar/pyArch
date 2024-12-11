# -*- coding: utf-8 -*-
'''Align wall top to slab/beam bottom'''

__title__ = "Wall Top"
__author__ = "prakritisrimal - prajwalbkumar"

from pyrevit import script, forms, revit
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import Selection, ObjectType, ISelectionFilter
from Extract.RunData import get_run_data
import time
from datetime import datetime
from System.Collections.Generic import List
# Record the start time
start_time = time.time()
manual_time = 10

output = script.get_output()
doc = __revit__.ActiveUIDocument.Document
ui_doc = __revit__.ActiveUIDocument

def filter_concrete_levels(levels):
    """Filter levels to find those named with 'CL'."""
    lvl = []
    for level in levels:
        level_type = doc.GetElement(level.GetTypeId())
        if "CL" in level_type.LookupParameter("Type Name").AsString():
            lvl.append(level)
    return lvl
            

        
def find_next_concrete_level(base_level, concrete_levels):
    """Find the next concrete level above the base level."""
    return next((cl for cl in concrete_levels if cl.Elevation > base_level.Elevation), None)

# Define a selection filter class for walls
class WallSelectionFilter(ISelectionFilter):
    def AllowElement(self, element):
        if element.Category.Id.IntegerValue == int(BuiltInCategory.OST_Walls):
            return True
        return False
    
    def AllowReference(self, ref, point):
        return False

target_walls = []

#Pre-Selected Walls
selection = ui_doc.Selection.GetElementIds()
if len(selection) > 0:
    for id in selection:
        element = doc.GetElement(id)
        try:
            if element.LookupParameter("Category").AsValueString() == "Walls":
               target_walls.append(element)
        except:
            continue

else:
    #Custom selection 
    selection_options = forms.alert("This Tool Aligns Wall Top.",
                                    title="Align Wall Top - Select Walls", 
                                    warn_icon=False, 
                                    options=["Select All Walls", "Select Specific Walls"])

    if not selection_options:
        script.exit()

    elif selection_options == "Select All Walls":

        unique_wall_names = set()
        wall_type_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

        for wall_type in wall_type_collector:
            wall_name = wall_type.Name
            if wall_name:
                unique_wall_names.add(wall_name)

        if not unique_wall_names:
            #forms.alert("No walls found in the model. Exiting script.")
            script.exit()

        sorted_wall_names = sorted(unique_wall_names)
        
        wall_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
        
        selected_wall_names = forms.SelectFromList.show(sorted_wall_names, multiselect=True, title='Select Walls to Align')
        if not selected_wall_names:
            script.exit()

        for wall in wall_collector:
            if wall.Name in selected_wall_names:
                target_walls.append(wall)

    else:
        # Prompt user to select walls
        try:
            choices = ui_doc.Selection
            selected_elements = choices.PickObjects(ObjectType.Element, WallSelectionFilter(), "Select walls only")
            
            for selected_element in selected_elements:
                wall = doc.GetElement(selected_element.ElementId)
                target_walls.append(wall)

        except:
            script.exit()

# Filter out not owned element
collected_elements = target_walls  #List of Elements that the Tool Targets
owned_elements = []
unowned_elements = []
elements_to_checkout = List[ElementId]()

for element in collected_elements:
    elements_to_checkout.Add(element.Id)

WorksharingUtils.CheckoutElements(doc, elements_to_checkout)

for element in collected_elements:    
    worksharingStatus = WorksharingUtils.GetCheckoutStatus(doc, element.Id)
    if not worksharingStatus == CheckoutStatus.OwnedByOtherUser:
        owned_elements.append(element)
    else:
        unowned_elements.append(element)

checkedout_target_walls = owned_elements

adjustment_type = forms.alert("Select the Discipline",
                                title="Align Wall Top - Select Discipline", 
                                warn_icon=False, 
                                options=["Architecture", "Interior"])
                                
if not adjustment_type:
    script.exit()

if adjustment_type == "Interior":
    forms.alert ("The Unconnected Height to 150mm above the ceiling top. If no ceiling is found, aligns with the slab or beam bottom.")

# Collect all linked instances
linked_instance = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
link_name = []
for link in linked_instance:
    link_name.append(link.Name)
target_instances_type = List[ElementId]()
# target_instance = []
selected_link_name = forms.SelectFromList.show(link_name, title = "Select Structure Link File(s)", width=600, height=600, button_name="Select File", multiselect=False)
if not selected_link_name:
    script.exit()
for link in linked_instance:
    # for name in target_instance_names:
    if selected_link_name != link.Name:
        # target_instance.append(link)
        target_instances_type.Add(link.GetTypeId())


skipped_data = []
target_walls = []

# Filter out walls with Profile
for wall in checkedout_target_walls:
    try:
        if int(wall.SketchId.ToString()) > 0: # Filtering out Walls with profiles
            skipped_wall_data = [
                output.linkify(wall.Id),
                wall.Name,
                wall.LookupParameter("Unconnected Height").AsValueString(),
                wall.LookupParameter("Base Constraint").AsValueString(),
                "WALL WITH PROFILE"
                ]
            skipped_data.append(skipped_wall_data)
            continue
        target_walls.append(wall)
    except:
        continue

wall_updated = 0
tg = TransactionGroup (doc, "Align Walls")
try:
    tg.Start()
    t = Transaction(doc, "Shorten Wall")
    t.Start()

    failed_data = []
    large_unc_height_data = []

    levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    concrete_levels = filter_concrete_levels(levels)
    sorted_concrete_levels = sorted(concrete_levels, key=lambda lvl: lvl.Elevation)

    reset_walls = []
    for wall in target_walls:   
        # print ("Wall Name: {}; Wall ID:{}".format(wall.Name, output.linkify(wall.Id)))
        base_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
        base_level = doc.GetElement(base_level_id)
        next_concrete_level = find_next_concrete_level(base_level, sorted_concrete_levels)
        unc_height_param = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
        wall_type = doc.GetElement(wall.WallType.Id)
        if wall_type:
            if wall_type.FamilyName == 'Curtain Wall':
                curtain_wall_data = [
                output.linkify(wall.Id),
                wall.Name,
                wall.LookupParameter("Unconnected Height").AsValueString(),
                wall.LookupParameter("Base Constraint").AsValueString(),
                "CURTAIN WALL"
                ]
                skipped_data.append(curtain_wall_data)
                continue
        else:
            continue

        if unc_height_param:
            try:
                unc_height_value = unc_height_param.AsDouble()
                unc_height_mm = unc_height_value * 304.8  # Convert feet to millimeters
                    
                if (-1500 <= unc_height_mm <= 1500):
                    unconnected_wall_data = [ output.linkify(wall.Id),
                                            wall.Name, 
                                            wall.LookupParameter("Unconnected Height").AsValueString(), 
                                            wall.LookupParameter("Base Constraint").AsValueString(),
                                            "INSUFFICIENT UNCONNECTED HEIGHT"]
                    skipped_data.append(unconnected_wall_data)
                    continue  # Skip to the next wall
            except Exception as e:
                continue
        else:
            continue

        wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(ElementId.InvalidElementId)

        base_offset_param = wall.LookupParameter("Base Offset").AsDouble()
        unc_height_param_value = (1800/304.8) - base_offset_param
        unc_height_param.Set(unc_height_param_value)
        reset_walls.append(wall)

    t.Commit()

    t = Transaction(doc, "Create Points")
    t.Start()

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

    options = Options()
    options.View = view_analytical

    adjusted_walls = []
    for wall in reset_walls:
        levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
        concrete_levels = filter_concrete_levels(levels)
        sorted_concrete_levels = sorted(concrete_levels, key=lambda lvl: lvl.Elevation)
        base_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
        base_level = doc.GetElement(base_level_id)
        next_concrete_level = find_next_concrete_level(base_level, sorted_concrete_levels)
        wall_geometry = wall.get_Geometry(options)
        upper_faces = []

        for wall_solid in wall_geometry:
            if (wall_solid.ToString() == "Autodesk.Revit.DB.Solid"):
                all_faces = wall_solid.Faces
                for face in all_faces:
                    try:
                        vector_z = int(face.FaceNormal.Z)
                        if vector_z == 1:
                            upper_faces.append((face.Origin.Z, face))
                    except:
                        continue

        sorted_upper_faces = sorted(upper_faces, key=lambda x: x[1])
        sorted_faces = []
        for item in sorted_upper_faces:
            sorted_faces.append(item[1])
        
        upper_face = sorted_faces[0]
        upper_face_z = upper_face.Evaluate(UV(0.5,0.5)).Z

        curve = wall.Location.Curve

        point_array = []
        # point_division = int((curve_length) / point_precision)

        for i in range(1, 20):
            point = curve.Evaluate((i * 0.05), True)
            point = XYZ(point.X, point.Y, upper_face_z)
            point_array.append(point)

        proximities = []
        direction = XYZ(0,0,1)
        for point in point_array:

            intersector = ReferenceIntersector(view_analytical)
            intersector.FindReferencesInRevitLinks = True
            
            result = intersector.FindNearest(XYZ(point.X, point.Y, (point.Z + 0.1)), direction)
            if not result: 
                continue
            
            reference_element_id = result.GetReference().ElementId
            
            if (doc.GetElement(reference_element_id)).ToString() == "Autodesk.Revit.DB.FamilyInstance":
                continue
            
            proximities.append(result.Proximity + 0.1)
        
            # plane = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, point)
            # circle = Arc.Create(plane, 2, 0, 6.28319)
            # sketch_plane = SketchPlane.Create(doc, plane)
            # model_line = doc.Create.NewModelCurve(circle, sketch_plane)

        if proximities:
            sorted(proximities)
            
            base_offset_param_value = wall.LookupParameter("Base Offset").AsDouble()
            unc_height_param = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
            current_height = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()

            unc_height_param.Set(current_height + proximities[0] + base_offset_param_value)
            unc_height_param_value = unc_height_param.AsDouble()

            if next_concrete_level:
                wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(next_concrete_level.Id)
                level_elevation = next_concrete_level.Elevation
                base_level_elevation = base_level.Elevation
                level_difference = level_elevation - base_level_elevation
                top_offset_param = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)
                top_offset_value = level_difference - unc_height_param_value
                top_offset_param.Set(-top_offset_value) 
                wall_updated +=1
            adjusted_walls.append(wall)

        else:
            failed_wall_data = [
                output.linkify(wall.Id),
                wall.Name,
                wall.LookupParameter("Unconnected Height").AsValueString(),
                wall.LookupParameter("Base Constraint").AsValueString(),
                "MISSING ELEMENT ABOVE"
            ]
            failed_data.append(failed_wall_data)

        unc_height = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()
        if (unc_height * 304.8) > 10000:
            large_unc_wall_data = [output.linkify(wall.Id), wall.Name, wall.LookupParameter("Unconnected Height").AsValueString(), 
                                    wall.LookupParameter("Base Constraint").AsValueString(),"LARGE UNCONNECTED HEIGHT"]
            skipped_data.append(large_unc_wall_data)

    t.Commit()

    if adjustment_type == "Interior":
        t = Transaction(doc, "Increase Ceiling Size")
        t.Start()
        offset_distance = float(float(5)/304.8)
        # Get all ceiling elements in the current document
        ceilings = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElements()
        new_ceilings = []
        for ceiling in ceilings:
            # Get the sketch element associated with the ceiling
            ceiling_height_offset = ceiling.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM).AsDouble()
            sketch = doc.GetElement(ceiling.SketchId)
            profiles = sketch.Profile  # These are CurveArrays (collections of curves)
            loops = []

            # Loop through each profile (each profile is a CurveArray)
            for profile in profiles:
                new_loop = []
                loop = CurveLoop()

                for curve in profile:
                    loop.Append(curve)
                
                if loop.IsCounterclockwise(XYZ(0,0,1)):
                    new_loop.append(CurveLoop.CreateViaOffset(loop, offset_distance, XYZ(0, 0, 1)))
                
                else:
                    new_loop.append(CurveLoop.CreateViaOffset(loop, -offset_distance, XYZ(0, 0, 1))) 
            
                new_ceiling = Ceiling.Create(doc, new_loop, ceiling.GetTypeId(), ceiling.LevelId)
                new_ceiling.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM).Set(ceiling_height_offset)
                new_ceilings.append(new_ceiling)

        t.Commit()

        t = Transaction(doc, "Create Points")
        t.Start()
        concrete_levels = filter_concrete_levels(levels)

        for wall in adjusted_walls:
            levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
            sorted_concrete_levels = sorted(concrete_levels, key=lambda lvl: lvl.Elevation)
            base_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
            base_level = doc.GetElement(base_level_id)
            base_level_type = doc.GetElement(base_level.GetTypeId())
            next_concrete_level = find_next_concrete_level(base_level, sorted_concrete_levels)
            wall_geometry = wall.get_Geometry(options)
            wall_base_offset = wall.LookupParameter("Base Offset").AsDouble()

            if "CL" in base_level_type.LookupParameter("Type Name").AsString():
                incorrect_base_data = [output.linkify(wall.Id), wall.Name, wall.LookupParameter("Unconnected Height").AsValueString(), 
                                        wall.LookupParameter("Base Constraint").AsValueString(),"INCORRECT WALL BASE CONSTRAINT"]
                skipped_data.append(incorrect_base_data)
                continue
                

            for wall_solid in wall_geometry:
                intersect_filter = ElementIntersectsSolidFilter(wall_solid)
                intersect_ceilings = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WherePasses(intersect_filter).WhereElementIsNotElementType().ToElements() 
                if intersect_ceilings:
                    for ceiling in intersect_ceilings:
                        ceiling_height_offset = ceiling.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM).AsDouble()
                        ceiling_thickness = doc.GetElement(ceiling.GetTypeId()).LookupParameter("Thickness").AsDouble()
                        ceiling_top_elevation = ceiling_height_offset + ceiling_thickness + (150 / 304.8) - wall_base_offset

                        wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(ElementId.InvalidElementId)
                        wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(ceiling_top_elevation)
                        wall_updated +=1
                        break

            unc_height = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()
            if (unc_height * 304.8) > 10000:
                large_unc_wall_data = [output.linkify(wall.Id), wall.Name, wall.LookupParameter("Unconnected Height").AsValueString(), 
                                        wall.LookupParameter("Base Constraint").AsValueString(),"LARGE UNCONNECTED HEIGHT"]
                skipped_data.append(large_unc_wall_data)

        for ceiling in new_ceilings:
            doc.Delete(ceiling.Id)
        
        doc.Delete (analytical_view.Id)
        doc.Delete (view_analytical.Id)
        t.Commit()
    tg.Assimilate()
    # Record the end time
    end_time = time.time()
    runtime = end_time - start_time

    run_result = "Tool ran successfully"
    element_count = wall_updated
    error_occured = "Nil"
    get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)

except Exception as e:
    forms.alert("An error occurred: {}".format(e))

    #Record the end time and runtime
    end_time = time.time()
    runtime = end_time - start_time

    # Log the error details
    error_occured = "Error occurred: {}".format(str(e))
    run_result = "Error"
    element_count = 10

    # Function to log run data in case of error
    get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)

 

if skipped_data:
    output.print_md("##⚠️ {} Completed. Some Walls were Skipped ☹️".format(__title__))
    output.print_md("---")
    output.print_md("❌ Some Walls were Skipped. Refer to the **Table Report** below for reference")
    output.print_table(table_data=skipped_data, columns=["ELEMENT ID", "WALL NAME", "UNCONNECTED HEIGHT", "BASE CONSTRAINT", "ERROR CODE"])
    output.print_md("---")
    output.print_md("***✅ ERROR CODE REFERENCE***")
    output.print_md("---")
    output.print_md("**WALL WITH PROFILE** - Wall has a profile \n")
    output.print_md("**CURTAIN WALL** - Curtain Walls remain unaltered \n")
    output.print_md("**INSUFFICIENT UNCONNECTED HEIGHT** -  Unconnected height in the range -1500 to 1500mm \n")
    output.print_md("**LARGE UNCONNECTED HEIGHT** - Wall has unconnected height greater than 10,000mm \n")
    output.print_md("**INCORRECT WALL BASE CONSTRAINT** - Wall base constraint should be at FFL. Please run the Wall Base tool first \n")
    output.print_md("---")

if failed_data:
    output.print_md("##⚠️ {} Completed. Issues Found ☹️".format(__title__))
    output.print_md("---")
    output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
    output.print_table(table_data=failed_data, columns=["ELEMENT ID", "WALL NAME", "UNCONNECTED HEIGHT", "BASE CONSTRAINT", "ERROR CODE"])
    output.print_md("---")
    output.print_md("***✅ ERROR CODE REFERENCE***")
    output.print_md("---")
    output.print_md("**MISSING ELEMENT ABOVE** - Wall Top not Aligned as no Element found above it \n")
    output.print_md("---")

unowned_element_data = []
if unowned_elements: 
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
    output.print_md("---") # Markdown Line Break

if not skipped_data and not failed_data and not unowned_element_data:
    output.print_md("##✅ {} Completed. No Issues Found 😃".format(__title__))
    output.print_md("---")








                    


