# -*- coding: utf-8 -*-
'''Align wall top to slab/beam bottom'''

__title__ = "Wall Top"
__author__ = "prakritisrimal"

from pyrevit import script, forms
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

selected_wall_names = forms.SelectFromList.show(unique_wall_names, multiselect=True, title='Select Walls to Align')
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

t = Transaction(doc, "Shorten Wall")
t.Start()

levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
concrete_levels = filter_concrete_levels(levels)
sorted_concrete_levels = sorted(concrete_levels, key=lambda lvl: lvl.Elevation)

reset_walls = []
for wall in target_walls:   
    # print ("Wall Name: {}; Wall ID:{}".format(wall.Name, output.linkify(wall.Id)))
    base_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
    base_level = doc.GetElement(base_level_id)
    
    unc_height_param = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
    wall_type = doc.GetElement(wall.WallType.Id)
    if wall_type:
        if wall_type.FamilyName == 'Curtain Wall':
            print("Warning: Wall '{}' (ID: {}) is a curtain wall. Moving the wall might have changed the divisions of the panels.".format(wall.Name, output.linkify(wall.Id)))
            continue
    else:
        forms.alert("Error: Wall type is None for wall Name {}".format(wall.Name))
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

for wall in reset_walls:
    wall_geometry = wall.get_Geometry(options)
    upper_faces = []

    for solid in wall_geometry:
        if (solid.ToString() == "Autodesk.Revit.DB.Solid"):
            all_faces = solid.Faces
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

    for i in range(1, 10):
        point = curve.Evaluate((i * 0.1), True)
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

        unc_height_param = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
        current_height = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()

        unc_height_param.Set(current_height + proximities[0])

t.Commit()