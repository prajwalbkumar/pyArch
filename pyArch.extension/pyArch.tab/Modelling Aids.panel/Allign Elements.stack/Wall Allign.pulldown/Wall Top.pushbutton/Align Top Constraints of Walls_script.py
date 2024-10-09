# -*- coding: utf-8 -*-
'''Align wall top to slab/beam bottom'''

__title__ = "Wall Top"
__author__ = "prakritisrimal - prajwalbkumar"

from pyrevit import script, forms, revit
from Autodesk.Revit.DB import *
from System.Collections.Generic import List

output = script.get_output()
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

    
def filter_concrete_levels(levels):
    """Filter levels to find those named with 'CL'."""
    return [level for level in levels if "CL" in level.LookupParameter("Name").AsString()]

def find_next_concrete_level(base_level, concrete_levels):
    """Find the next concrete level above the base level."""
    return next((cl for cl in concrete_levels if cl.Elevation > base_level.Elevation), None)

minimum_wall_height = 1500 * 0.00328084

# Step 1: Prompt the user to select between 'Architecture' or 'Interior' adjustment types
adjustment_type = forms.SelectFromList.show(
    ["Architecture", "Interior"],
    title='Select Adjustment Type',
    button_name='Select',
    multiselect=False
)

if not adjustment_type:
    script.exit()



# Collect all linked instances
linked_instance = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
link_name = []


for link in linked_instance:
    link_name.append(link.Name)

target_instance_names = forms.SelectFromList.show(link_name, title = "Select Target File", width=600, height=600, button_name="Select File", multiselect=True)

if not target_instance_names:
    script.exit()

target_instances_type = List[ElementId]()
target_instance = []

for link in linked_instance:
    for name in target_instance_names:
        if name != link.Name:
            target_instance.append(link)
            target_instances_type.Add(link.GetTypeId())


# Prompt user to select walls for alignment
unique_wall_names = set()
wall_type_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

for wall_type in wall_type_collector:
    wall_name = wall_type.Name
    if wall_name:
        unique_wall_names.add(wall_name)

if not unique_wall_names:
    forms.alert("No walls found in the model. Exiting script.")
    script.exit()

sorted_wall_names = sorted(unique_wall_names)

selected_wall_names = forms.SelectFromList.show(sorted_wall_names, multiselect=True, title='Select Walls to Align')
if not selected_wall_names:
    script.exit()

wall_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
target_walls = []

for wall in wall_collector:
    try:
        if int(wall.SketchId.ToString()) > 0: # Filtering out Walls with profiles
            continue
        if wall.Name in selected_wall_names:
            try:
                if wall.LookupParameter("Unconnected Height").AsDouble() > minimum_wall_height:
                    target_walls.append(wall)
            except:
                continue
    except:
        continue


tg = TransactionGroup (doc, "Align Walls")
tg.Start()
t = Transaction(doc, "Shorten Wall")
t.Start()
failed_counter = 0
warning_counter = 0
skipped_counter = 0
failed_data = []
warning_data = []
skipped_data = []

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
            warning_counter = +1
            continue
        else:
            continue

    if unc_height_param:
        try:
            unc_height_value = unc_height_param.AsDouble()
            unc_height_mm = unc_height_value * 304.8  # Convert feet to millimeters
                
            if (-1500 <= unc_height_mm <= 1500):
                skipped_counter = +1
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

    if warning_counter:
        warning_wall_data = [
        output.linkify(wall.Id),
        wall.Name,
        "CHANGE IN CURTAIN PANEL DIVISON"
        ]
        warning_data.append(warning_wall_data)

    if skipped_counter:
        skipped_wall_data = [
            output.linkify(wall.Id),
            wall.Name,
            wall.LookupParameter("Unconnected Height").AsValueString(),
            wall.LookupParameter("Base Constraint").AsValueString(),
            "WALL TOP NOT ALIGNED"
        ]
        skipped_data.append(skipped_wall_data)

    if skipped_data:
        output.print_md("##⚠️ {} Completed. Issues Found ☹️".format(__title__))
        output.print_md("---")
        output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
        output.print_table(table_data=skipped_data, columns=["ELEMENT ID", "WALL NAME", "UNCONNECTED HEIGHT", "BASE CONSTRAINT", "ERROR CODE"])
        output.print_md("---")
        output.print_md("***✅ ERROR CODE REFERENCE***")
        output.print_md("---")
        output.print_md("**WALL TOP NOT ALIGNED** - Wall Top Aligned as no Element found above it")
        output.print_md("---")
    else:
        output.print_md("##✅ {} Completed. No Issues Found 😃".format(__title__))
        output.print_md("---")

    if warning_data:
        output.print_md("##⚠️ {} Completed. Warning ☹️".format(__title__))
        output.print_md("---")
        output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
        output.print_table(table_data=warning_data, columns=["ELEMENT ID", "WALL NAME", "ERROR CODE"])
        output.print_md("---")
        output.print_md("***✅ ERROR CODE REFERENCE***")
        output.print_md("---")
        output.print_md("**CHANGE IN CURTAIN PANEL DIVISION** - Check the wall manually")
        output.print_md("---")
    else:
        output.print_md("##✅ {} Completed. No Issues Found 😃".format(__title__))
        output.print_md("---")

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
        adjusted_walls.append(wall)

    else:
        failed_counter = +1

    if failed_counter:
        failed_wall_data = [
            output.linkify(wall.Id),
            wall.Name,
            wall.LookupParameter("Unconnected Height").AsValueString(),
            wall.LookupParameter("Base Constraint").AsValueString(),
            "WALL TOP NOT ALIGNED"
        ]
        failed_data.append(failed_wall_data)

    if failed_data:
        output.print_md("##⚠️ {} Completed. Issues Found ☹️".format(__title__))
        output.print_md("---")
        output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
        output.print_table(table_data=failed_data, columns=["ELEMENT ID", "WALL NAME", "UNCONNECTED HEIGHT", "BASE CONSTRAINT", "ERROR CODE"])
        output.print_md("---")
        output.print_md("***✅ ERROR CODE REFERENCE***")
        output.print_md("---")
        output.print_md("**WALL TOP NOT ALIGNED** - Unconnected height in the range -1500 to 1500mm \n")
        output.print_md("---")
    else:
        output.print_md("##✅ {} Completed. No Issues Found 😃".format(__title__))
        output.print_md("---")

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
                
    for wall in adjusted_walls:
        levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
        concrete_levels = filter_concrete_levels(levels)
        sorted_concrete_levels = sorted(concrete_levels, key=lambda lvl: lvl.Elevation)
        base_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
        base_level = doc.GetElement(base_level_id)
        next_concrete_level = find_next_concrete_level(base_level, sorted_concrete_levels)
        wall_geometry = wall.get_Geometry(options)
        wall_base_offset = wall.LookupParameter("Base Offset").AsDouble()

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
                    # top_offset_param = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)
                    # top_offset_param.Set(-new_offset)
                    break

    for ceiling in new_ceilings:
        doc.Delete(ceiling.Id)
    
    doc.Delete (analytical_view.Id)
    doc.Delete (view_analytical.Id)
    t.Commit()
tg.Assimilate()







                    


